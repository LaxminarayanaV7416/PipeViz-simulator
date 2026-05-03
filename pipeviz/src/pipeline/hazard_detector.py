#!/usr/bin/env python3
"""
Analyzes ARM64 assembly code and detects:
- Data Hazards (RAW, WAR, WAW)
- Structural Hazards
"""

from loguru import logger

from src.config import Hazard, Instruction, InstructionState
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


class HazardDetector:
    def __init__(self, instructions: list[Instruction], pipeline_type: PipelineTypes):
        self.instructions = instructions
        self.pipeline_type = pipeline_type
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
        self.stage_names = [stage.name for stage in self.stages]

    def detect_raw_hazards(
        self, current_instruction: Instruction, inflight_ins: list[InstructionState]
    ) -> list[Instruction]:
        hazards = []

        for state in inflight_ins:
            prev = state.inst

            # RAW: current reads something not yet written
            if any(reg in prev.dest_regs for reg in current_instruction.src_regs):
                if not state.done:  # or stage < WB
                    hazards.append(prev)

        return hazards

    def detect_war_hazards(
        self, current_instruction: Instruction, inflight_ins: list[InstructionState]
    ) -> list[Instruction]:
        hazards = []

        for state in inflight_ins:
            prev = state.inst

            # WAR: current writes something not yet read
            if any(reg in prev.src_regs for reg in current_instruction.dest_regs):
                if state.stage < self.stages.get_war_hazard_prone_stages()[0]:
                    hazards.append(prev)

        return hazards

    def detect_waw_hazards(
        self, current_instruction: Instruction, inflight_ins: list[InstructionState]
    ) -> list[Instruction]:
        hazards = []

        for state in inflight_ins:
            prev = state.inst

            # WAW: current writes something already written
            if any(reg in prev.dest_regs for reg in current_instruction.dest_regs):
                if not state.done:
                    hazards.append(prev)

        return hazards

    def detect_hazards(self) -> list[Hazard]:
        if not self.instructions:
            return []

        stage_order = sorted(self.stages.get_all_stages(), key=lambda s: s.value)
        stage_count = len(stage_order)
        final_stage = self.stages.get_final_stage().value

        pipeline_slots: list[InstructionState | None] = [None] * stage_count
        hazards: list[Hazard] = []
        pc = 0
        cycle = 0

        raw_prone = set(self.stages.get_raw_hazard_prone_stages())
        war_prone = set(self.stages.get_war_hazard_prone_stages())
        waw_prone = set(self.stages.get_waw_hazard_prone_stages())

        while pc < len(self.instructions) or any(pipeline_slots):
            cycle += 1
            inflight_states = [s for s in pipeline_slots if s is not None]
            pc_to_state = {s.inst.pc: s for s in inflight_states}

            for stage in stage_order:
                state = pipeline_slots[stage.value]
                if state is None:
                    continue

                current = state.inst
                older_states = [s for s in inflight_states if s.inst.pc < current.pc]

                if stage in raw_prone:
                    producers = self.detect_raw_hazards(current, older_states)
                    for prev in producers:
                        producer_state = pc_to_state.get(prev.pc)
                        producer_stage = (
                            stage_order[producer_state.stage]
                            if producer_state
                            else stage
                        )
                        resource = next(
                            (r for r in current.src_regs if r in prev.dest_regs),
                            "unknown",
                        )
                        hazards.append(
                            Hazard(
                                type=HazardType.RAW,
                                cycle=cycle,
                                producer_pc=prev.pc,
                                consumer_pc=current.pc,
                                producer_stage=producer_stage,
                                consumer_stage=stage,
                                resource=resource,
                            )
                        )

                if stage in war_prone:
                    producers = self.detect_war_hazards(current, older_states)
                    for prev in producers:
                        producer_state = pc_to_state.get(prev.pc)
                        producer_stage = (
                            stage_order[producer_state.stage]
                            if producer_state
                            else stage
                        )
                        resource = next(
                            (r for r in current.dest_regs if r in prev.src_regs),
                            "unknown",
                        )
                        hazards.append(
                            Hazard(
                                type=HazardType.WAR,
                                cycle=cycle,
                                producer_pc=prev.pc,
                                consumer_pc=current.pc,
                                producer_stage=producer_stage,
                                consumer_stage=stage,
                                resource=resource,
                            )
                        )

                if stage in waw_prone:
                    producers = self.detect_waw_hazards(current, older_states)
                    for prev in producers:
                        producer_state = pc_to_state.get(prev.pc)
                        producer_stage = (
                            stage_order[producer_state.stage]
                            if producer_state
                            else stage
                        )
                        resource = next(
                            (r for r in current.dest_regs if r in prev.dest_regs),
                            "unknown",
                        )
                        hazards.append(
                            Hazard(
                                type=HazardType.WAW,
                                cycle=cycle,
                                producer_pc=prev.pc,
                                consumer_pc=current.pc,
                                producer_stage=producer_stage,
                                consumer_stage=stage,
                                resource=resource,
                            )
                        )

            for idx in range(stage_count - 1, -1, -1):
                state = pipeline_slots[idx]
                if state is None:
                    continue
                if idx == final_stage:
                    pipeline_slots[idx] = None
                    state.done = True
                    continue
                if pipeline_slots[idx + 1] is None:
                    pipeline_slots[idx + 1] = state
                    pipeline_slots[idx] = None
                    state.stage = idx + 1

            if pc < len(self.instructions) and pipeline_slots[0] is None:
                pipeline_slots[0] = InstructionState(
                    inst=self.instructions[pc], stage=0
                )
                pc += 1

        return hazards


# this is just for the reference - lets build something based on
# below information
def _detect_data_hazards(self, instr: Instruction, pipeline: dict) -> list[Hazard]:
    """Detect RAW, WAR, WAW data hazards"""
    hazards = []

    stage_names = ["EX", "MEM", "WB"]
    for stage_name in stage_names:
        stage = getattr(self.stages, stage_name, None)
        if stage is None or pipeline.get(stage) is None:
            continue

        other_pc = pipeline[stage]
        other_instr = self.instructions[other_pc]

        for src_reg in instr.src_regs:
            if src_reg in other_instr.dest_regs:
                hazards.append(
                    Hazard(
                        type=HazardType.RAW,
                        cycle=len(self.pipeline_states),
                        producer_pc=other_pc,
                        consumer_pc=instr.pc,
                        producer_stage=stage,
                        consumer_stage=getattr(self.stages, "ID", stage),
                        resource=src_reg,
                    )
                )

        for dest_reg in instr.dest_regs:
            if dest_reg in other_instr.src_regs:
                hazards.append(
                    Hazard(
                        type=HazardType.WAR,
                        cycle=len(self.pipeline_states),
                        producer_pc=other_pc,
                        consumer_pc=instr.pc,
                        producer_stage=stage,
                        consumer_stage=getattr(self.stages, "ID", stage),
                        resource=dest_reg,
                    )
                )

        for dest_reg in instr.dest_regs:
            if dest_reg in other_instr.dest_regs:
                hazards.append(
                    Hazard(
                        type=HazardType.WAW,
                        cycle=len(self.pipeline_states),
                        producer_pc=other_pc,
                        consumer_pc=instr.pc,
                        producer_stage=stage,
                        consumer_stage=getattr(self.stages, "ID", stage),
                        resource=dest_reg,
                    )
                )

    return hazards
