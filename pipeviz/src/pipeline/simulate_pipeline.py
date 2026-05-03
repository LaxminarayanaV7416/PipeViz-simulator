#!/usr/bin/env python3
"""
ARM64 Pipeline Simulator
Analyzes ARM64 assembly code and detects:
- Data Hazards (RAW, WAR, WAW)
- Structural Hazards
- Shows cycle-by-cycle execution
"""

from __future__ import annotations

from loguru import logger

from src.config import Hazard, Instruction, InstructionState, PipelineState
from src.enum_vault.pipeline_enums import (
    DynamicInOrderStages,
    HazardType,
    InOrderSuperscalarStages,
    OutOfOrderStages,
    PipelineTypes,
    ScoreboardStages,
    StaticInOrderStages,
    TomasuloStages,
    VLIWStages,
)
from src.pipeline.hazard_detector import HazardDetector
from src.pipeline.pipeline_base import ARM64Parser


class PipelineSimulator:
    """pipeline simulator with hazard detection"""

    def __init__(
        self,
        pipeline_type: PipelineTypes = PipelineTypes.STATIC_IN_ORDER,
        enable_forwarding: bool = True,
        branch_policy: str = "not_taken",
        branch_penalty: int = 1,
    ):
        self.pipeline_type = pipeline_type
        self.enable_forwarding = enable_forwarding
        self.branch_policy = branch_policy  # "not_taken" or "always_taken"
        self.branch_penalty = branch_penalty
        self.instructions: list[Instruction] = []
        self.pipeline_states: list[PipelineState] = []
        self.hazards_detected: list[Hazard] = []

        # Pipeline configuration
        self.num_stages = 5
        self.memory_units = 1
        self.alu_units = 1

        if pipeline_type == PipelineTypes.STATIC_IN_ORDER:
            self.stages = StaticInOrderStages
        elif pipeline_type == PipelineTypes.SCOREBOARD:
            self.stages = ScoreboardStages
        elif pipeline_type == PipelineTypes.DYNAMIC_IN_ORDER:
            self.stages = DynamicInOrderStages
        elif pipeline_type == PipelineTypes.IN_ORDER_SUPERSCALAR:
            self.stages = InOrderSuperscalarStages
        elif pipeline_type == PipelineTypes.VLIW:
            self.stages = VLIWStages
        elif pipeline_type == PipelineTypes.TOMASULO:
            self.stages = TomasuloStages
        elif pipeline_type == PipelineTypes.OUT_OF_ORDER:
            self.stages = OutOfOrderStages
        else:
            logger.error(f"Unknown pipeline type: {pipeline_type}")
            raise ValueError(f"Unknown pipeline type: {pipeline_type}")

    def load_instructions(self, assembly_code_lines: list[str]):
        """Load and parse ARM64 assembly code"""
        self.instructions = []
        pc = 0

        for line in assembly_code_lines:
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            instr = ARM64Parser.parse_instruction(line, pc)
            if instr:
                self.instructions.append(instr)
                pc += 1

        # Map addresses to PCs so branch targets can resolve
        addr_to_pc = {instr.address: instr.pc for instr in self.instructions}
        for instr in self.instructions:
            if instr.is_branch and instr.branch_target_addr:
                instr.branch_target_pc = addr_to_pc.get(instr.branch_target_addr)

    def advance_instruction(self, state: InstructionState):
        if state.done:
            return

        next_stage = state.stage + 1

        if not has_hazard(state, next_stage):
            state.stage = next_stage

            # mark completion
            if is_final_stage(state):
                state.done = True

    def can_fetch(self, inflight: list[InstructionState]) -> bool:
        # Example constraints:

        # 1. Pipeline width
        if len(inflight) >= MAX_INFLIGHT:
            return False

        # 2. Control hazard
        if any(s.inst.is_branch and not s.done for s in inflight):
            return False

        return True

    def construct_simulation_loop(self) -> list[InstructionState]:

        pc: int = 0
        cycle: int = 0
        self.inflight_instructions: list[InstructionState] = []
        self.program: list[Instruction] = []
        final_stage = self.stages.get_final_stage()

        while pc < len(self.program) or self.inflight_instructions:
            cycle += 1

            # 1. Remove completed instructions
            self.inflight_instructions = [
                s
                for s in self.inflight_instructions
                if not (s.stage == final_stage and s.done)
            ]

            # 2. Advance existing instructions
            for state in self.inflight_instructions:
                self.advance_instruction(state)

            # 3. Fetch new instruction (if possible)
            if self.can_fetch(self.inflight_instructions):
                inst = self.program[pc]
                self.inflight_instructions.append(InstructionState(inst=inst, stage=0))
                pc += 1

        return self.inflight_instructions

    def simulate(self) -> list[PipelineState]:
        """Run pipeline simulation"""
        self.pipeline_states = []
        self.hazards_detected = []

        if not self.instructions:
            return self.pipeline_states

        stage_order = sorted(self.stages.get_all_stages(), key=lambda s: s.value)
        stage_count = len(stage_order)
        final_stage = self.stages.get_final_stage()

        pipeline_slots: list[InstructionState | None] = [None] * stage_count
        pc = 0
        cycle = 0

        hazard_detector = HazardDetector(self.instructions, self.pipeline_type)
        raw_prone = set(self.stages.get_raw_hazard_prone_stages())
        war_prone = set(self.stages.get_war_hazard_prone_stages())
        waw_prone = set(self.stages.get_waw_hazard_prone_stages())

        while pc < len(self.instructions) or any(pipeline_slots):
            cycle += 1
            hazards_this_cycle: list[Hazard] = []
            stall_stage_index: int | None = None

            inflight_states = [state for state in pipeline_slots if state is not None]
            pc_to_state = {state.inst.pc: state for state in inflight_states}

            for stage in stage_order:
                state = pipeline_slots[stage.value]
                if state is None:
                    continue

                current_inst = state.inst
                older_states = [
                    s for s in inflight_states if s.inst.pc < current_inst.pc
                ]

                if stage in raw_prone:
                    producers = hazard_detector.detect_raw_hazards(
                        current_inst, older_states
                    )
                    if producers:
                        for prev_inst in producers:
                            producer_state = pc_to_state.get(prev_inst.pc)
                            producer_stage = (
                                stage_order[producer_state.stage]
                                if producer_state
                                else stage
                            )
                            resource = next(
                                (
                                    reg
                                    for reg in current_inst.src_regs
                                    if reg in prev_inst.dest_regs
                                ),
                                "unknown",
                            )
                            hazards_this_cycle.append(
                                Hazard(
                                    type=HazardType.RAW,
                                    cycle=cycle,
                                    producer_pc=prev_inst.pc,
                                    consumer_pc=current_inst.pc,
                                    producer_stage=producer_stage,
                                    consumer_stage=stage,
                                    resource=resource,
                                )
                            )
                        if not self.enable_forwarding:
                            stall_stage_index = (
                                stage.value
                                if stall_stage_index is None
                                else min(stall_stage_index, stage.value)
                            )

                if stage in war_prone:
                    producers = hazard_detector.detect_war_hazards(
                        current_inst, older_states
                    )
                    if producers:
                        for prev_inst in producers:
                            producer_state = pc_to_state.get(prev_inst.pc)
                            producer_stage = (
                                stage_order[producer_state.stage]
                                if producer_state
                                else stage
                            )
                            resource = next(
                                (
                                    reg
                                    for reg in current_inst.dest_regs
                                    if reg in prev_inst.src_regs
                                ),
                                "unknown",
                            )
                            hazards_this_cycle.append(
                                Hazard(
                                    type=HazardType.WAR,
                                    cycle=cycle,
                                    producer_pc=prev_inst.pc,
                                    consumer_pc=current_inst.pc,
                                    producer_stage=producer_stage,
                                    consumer_stage=stage,
                                    resource=resource,
                                )
                            )
                        stall_stage_index = (
                            stage.value
                            if stall_stage_index is None
                            else min(stall_stage_index, stage.value)
                        )

                if stage in waw_prone:
                    producers = hazard_detector.detect_waw_hazards(
                        current_inst, older_states
                    )
                    if producers:
                        for prev_inst in producers:
                            producer_state = pc_to_state.get(prev_inst.pc)
                            producer_stage = (
                                stage_order[producer_state.stage]
                                if producer_state
                                else stage
                            )
                            resource = next(
                                (
                                    reg
                                    for reg in current_inst.dest_regs
                                    if reg in prev_inst.dest_regs
                                ),
                                "unknown",
                            )
                            hazards_this_cycle.append(
                                Hazard(
                                    type=HazardType.WAW,
                                    cycle=cycle,
                                    producer_pc=prev_inst.pc,
                                    consumer_pc=current_inst.pc,
                                    producer_stage=producer_stage,
                                    consumer_stage=stage,
                                    resource=resource,
                                )
                            )
                        stall_stage_index = (
                            stage.value
                            if stall_stage_index is None
                            else min(stall_stage_index, stage.value)
                        )

            for idx in range(stage_count - 1, -1, -1):
                state = pipeline_slots[idx]
                if state is None:
                    continue

                if idx == final_stage.value:
                    state.done = True
                    pipeline_slots[idx] = None
                    continue

                if stall_stage_index is not None and idx <= stall_stage_index:
                    continue

                if pipeline_slots[idx + 1] is None:
                    pipeline_slots[idx] = None
                    pipeline_slots[idx + 1] = state
                    state.stage = idx + 1

            if stall_stage_index is None and pc < len(self.instructions):
                if pipeline_slots[0] is None:
                    pipeline_slots[0] = InstructionState(
                        inst=self.instructions[pc], stage=0
                    )
                    pc += 1

            stages_snapshot = {
                stage: (
                    pipeline_slots[stage.value].inst.pc
                    if pipeline_slots[stage.value]
                    else None
                )
                for stage in stage_order
            }

            self.pipeline_states.append(
                PipelineState(
                    cycle=cycle,
                    stages=stages_snapshot,
                    stalled=stall_stage_index is not None,
                    hazards=hazards_this_cycle,
                    forwarding=[],
                )
            )
            self.hazards_detected.extend(hazards_this_cycle)

        return self.pipeline_states

    def convert_to_json(self):
        """Export cycle-by-cycle pipeline states to CSV.
        Output format:
        - Row per instruction
        - Columns are cycles (C0, C1, ...)
        - Cells show stage name
        - If stalled, show STAGE[STALL]
        """
        if not self.pipeline_states:
            return []

        rows = [{"instruction": instr.raw} for instr in self.instructions]
        last_stage_by_pc = {instr.pc: None for instr in self.instructions}

        for state in self.pipeline_states:
            cycle_key = f"C{state.cycle}"
            for stage, pc in state.stages.items():
                if pc is None:
                    continue

                stage_name = display_stage(stage)
                if last_stage_by_pc.get(pc) == stage_name:
                    rows[pc][cycle_key] = f"{stage_name}[STALL]"
                else:
                    rows[pc][cycle_key] = stage_name

                last_stage_by_pc[pc] = stage_name

        return rows

    def print_simulation(self):
        """logger.info detailed simulation output"""
        if not self.pipeline_states:
            logger.info("No simulation states available. Run simulate() first.")
            return

        stage_order = sorted(self.stages.get_all_stages(), key=lambda s: s.value)
        logger.info(f"Total cycles: {len(self.pipeline_states)}")

        for state in self.pipeline_states:
            stage_cells = []
            for stage in stage_order:
                pc = state.stages.get(stage)
                if pc is None:
                    cell = "-"
                else:
                    instr = self.instructions[pc]
                    cell = f"{pc}:{instr.opcode}"
                stage_cells.append(f"{display_stage(stage)}={cell}")

            stall_marker = " STALL" if state.stalled else ""
            logger.info(f"C{state.cycle}: " + " | ".join(stage_cells) + stall_marker)

            if state.hazards:
                for hazard in state.hazards:
                    logger.info(f"  {hazard}")

        if self.hazards_detected:
            logger.info(f"Detected hazards: {len(self.hazards_detected)}")

    # def _detect_data_hazards(self, instr: Instruction, pipeline: dict) -> list[Hazard]:
    #     """Detect RAW, WAR, WAW data hazards"""
    #     hazards = []

    #     # Check instructions in later stages
    #     for stage in [
    #         PipelineStage.EXECUTE,
    #         PipelineStage.MEMORY,
    #         PipelineStage.WRITEBACK,
    #     ]:
    #         if pipeline[stage] is None:
    #             continue

    #         other_pc = pipeline[stage]
    #         other_instr = self.instructions[other_pc]

    #         # RAW: Read After Write (True Dependency)
    #         # Current instruction reads a register that a previous instruction writes
    #         for src_reg in instr.src_regs:
    #             if src_reg in other_instr.dest_regs:
    #                 hazards.append(
    #                     Hazard(
    #                         type=HazardType.RAW,
    #                         cycle=len(self.pipeline_states),
    #                         producer_pc=other_pc,
    #                         consumer_pc=instr.pc,
    #                         producer_stage=stage,
    #                         consumer_stage=PipelineStage.DECODE,
    #                         resource=src_reg,
    #                     )
    #                 )

    #         # WAR: Write After Read (Anti-Dependency)
    #         # Current instruction writes a register that a previous instruction reads
    #         for dest_reg in instr.dest_regs:
    #             if dest_reg in other_instr.src_regs:
    #                 hazards.append(
    #                     Hazard(
    #                         type=HazardType.WAR,
    #                         cycle=len(self.pipeline_states),
    #                         producer_pc=other_pc,
    #                         consumer_pc=instr.pc,
    #                         producer_stage=stage,
    #                         consumer_stage=PipelineStage.DECODE,
    #                         resource=dest_reg,
    #                     )
    #                 )

    #         # WAW: Write After Write (Output Dependency)
    #         # Current instruction writes a register that a previous instruction writes
    #         for dest_reg in instr.dest_regs:
    #             if dest_reg in other_instr.dest_regs:
    #                 hazards.append(
    #                     Hazard(
    #                         type=HazardType.WAW,
    #                         cycle=len(self.pipeline_states),
    #                         producer_pc=other_pc,
    #                         consumer_pc=instr.pc,
    #                         producer_stage=stage,
    #                         consumer_stage=PipelineStage.DECODE,
    #                         resource=dest_reg,
    #                     )
    #                 )

    #     return hazards

    # def _detect_structural_hazards(self, pipeline: dict) -> list[Hazard]:
    #     """Detect structural hazards (resource conflicts)"""
    #     hazards = []

    #     # Count memory accesses in Memory stage
    #     memory_accesses = []
    #     if pipeline[PipelineStage.MEMORY] is not None:
    #         pc = pipeline[PipelineStage.MEMORY]
    #         instr = self.instructions[pc]
    #         if instr.memory_access:
    #             memory_accesses.append(pc)

    #     # Check if we have more memory accesses than available units
    #     if len(memory_accesses) > self.memory_units:
    #         for pc in memory_accesses[self.memory_units :]:
    #             hazards.append(
    #                 Hazard(
    #                     type=HazardType.STRUCTURAL,
    #                     cycle=len(self.pipeline_states),
    #                     producer_pc=memory_accesses[0],
    #                     consumer_pc=pc,
    #                     producer_stage=PipelineStage.MEMORY,
    #                     consumer_stage=PipelineStage.MEMORY,
    #                     resource="Memory Unit",
    #                 )
    #             )

    #     return hazards
