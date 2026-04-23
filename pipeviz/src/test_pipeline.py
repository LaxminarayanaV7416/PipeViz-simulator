#!/usr/bin/env python3
"""
ARM64 Pipeline Simulator
Analyzes ARM64 assembly code and detects:
- Data Hazards (RAW, WAR, WAW)
- Structural Hazards
- Shows cycle-by-cycle execution
"""

import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from config import ARMOpsCodeClassification, OpcodeConfig, config_parser
from src.enum_vault.pipeline_enums import HazardType, PipelineStage

config: OpcodeConfig = config_parser()


@dataclass
class Instruction:
    """Represents a single ARM64 instruction"""

    address: str
    opcode: str
    operands: str
    raw: str
    pc: int  # Program counter (instruction index)

    # Parsed operands
    dest_regs: List[str]  # Registers written to
    src_regs: List[str]  # Registers read from
    memory_access: bool  # Does this instruction access memory?
    is_branch: bool  # Is this a branch/jump?
    is_load: bool  # Is this a load instruction?
    is_store: bool  # Is this a store instruction?

    # Branch info
    branch_target_addr: Optional[str] = None
    branch_target_pc: Optional[int] = None

    def __repr__(self):
        return f"{self.address}: {self.opcode} {self.operands}"


@dataclass
class Hazard:
    """Represents a detected hazard"""

    type: HazardType
    cycle: int
    producer_pc: int
    consumer_pc: int
    producer_stage: PipelineStage
    consumer_stage: PipelineStage
    resource: str  # Register name or resource name

    def __repr__(self):
        return (
            f"{self.type.value} Hazard at cycle {self.cycle}: "
            f"Instr {self.producer_pc} ({self.producer_stage.name}) -> "
            f"Instr {self.consumer_pc} ({self.consumer_stage.name}) "
            f"on {self.resource}"
        )


@dataclass
class PipelineState:
    """State of pipeline at a given cycle"""

    cycle: int
    stages: Dict[PipelineStage, Optional[int]]  # Stage -> instruction PC
    stalled: bool
    hazards: List[Hazard]
    forwarding: List[Tuple[int, int, str]]  # (from_pc, to_pc, register)

    def __repr__(self):
        stage_str = " | ".join(
            [
                f"{stage.name}: {pc if pc is not None else '-'}"
                for stage, pc in self.stages.items()
            ]
        )
        return f"Cycle {self.cycle}: [{stage_str}]" + (" STALL" if self.stalled else "")


class ARM64Parser:
    """Parses ARM64 assembly instructions"""

    # ARM64 register patterns
    REGISTER_PATTERN = r"\b([xwsp]\d{1,2}|sp|xzr|wzr|lr|x29|x30)\b"

    # Instruction categories
    LOAD_OPS = config.get_opcode_list("LOAD_OPS")
    STORE_OPS = config.get_opcode_list("STORE_OPS")
    BRANCH_OPS = config.get_opcode_list("BRANCH_OPS")
    ALU_OPS = config.get_opcode_list("ALU_OPS")
    PAIR_OPS = config.get_opcode_list("PAIR_OPS")
    COMPARE_OPS = config.get_opcode_list("COMPARE_OPS")
    MOV_OPS = config.get_opcode_list("MOV_OPS")

    @staticmethod
    def parse_instruction(line: str, pc: int) -> Optional[Instruction]:
        """Parse a single ARM64 instruction line"""
        match = re.match(
            r"\s*([0-9a-fA-F]+):\s+(?:[0-9a-fA-F]{2,}\s+)*([a-zA-Z][a-zA-Z0-9.]*)\s*(.*)",
            line,
        )
        if not match:
            return None

        address, opcode, operands = match.groups()
        opcode = opcode.upper()

        # Parse destination and source registers
        dest_regs, src_regs = ARM64Parser._parse_operands(opcode, operands)

        # Determine instruction properties
        is_load = opcode in ARM64Parser.LOAD_OPS
        is_store = opcode in ARM64Parser.STORE_OPS
        is_branch = opcode in ARM64Parser.BRANCH_OPS
        memory_access = is_load or is_store

        # Extract branch target address if present
        branch_target_addr = None
        if is_branch:
            m = re.search(r"\b([0-9a-fA-F]{6,})\b", operands)
            if m:
                branch_target_addr = m.group(1).lower()

        return Instruction(
            address=address.lower(),
            opcode=opcode,
            operands=operands,
            raw=line.strip(),
            pc=pc,
            dest_regs=dest_regs,
            src_regs=src_regs,
            memory_access=memory_access,
            is_branch=is_branch,
            is_load=is_load,
            is_store=is_store,
            branch_target_addr=branch_target_addr,
        )

    @staticmethod
    def _parse_operands(opcode: str, operands: str) -> Tuple[List[str], List[str]]:
        """Parse operands to extract destination and source registers"""
        dest_regs = []
        src_regs = []

        # Find all registers in operands
        all_regs = re.findall(ARM64Parser.REGISTER_PATTERN, operands.lower())

        if not all_regs:
            return dest_regs, src_regs

        # Normalize register names (w0 -> x0 for tracking)
        all_regs = [ARM64Parser._normalize_register(r) for r in all_regs]

        # Determine which registers are destinations vs sources
        if opcode in ARM64Parser.MOV_OPS:
            # MOV dest, src
            if len(all_regs) >= 1:
                dest_regs.append(all_regs[0])
            if len(all_regs) >= 2:
                src_regs.extend(all_regs[1:])

        elif opcode in ARM64Parser.LOAD_OPS:
            # LDR dest, [base, offset]
            if len(all_regs) >= 1:
                dest_regs.append(all_regs[0])
            if len(all_regs) >= 2:
                src_regs.extend(all_regs[1:])  # Base register(s)

        elif opcode in ARM64Parser.STORE_OPS:
            # STR src, [base, offset]
            if len(all_regs) >= 1:
                src_regs.append(all_regs[0])  # Value to store
            if len(all_regs) >= 2:
                src_regs.extend(all_regs[1:])  # Base register(s)

        elif opcode in ARM64Parser.ALU_OPS:
            # ALU: dest, src1, src2
            if len(all_regs) >= 1:
                dest_regs.append(all_regs[0])
            if len(all_regs) >= 2:
                src_regs.extend(all_regs[1:])

        elif opcode in ARM64Parser.COMPARE_OPS:
            # Compare: only sources, no destination
            src_regs.extend(all_regs)

        elif opcode in ARM64Parser.BRANCH_OPS:
            # Branch: may use registers
            src_regs.extend(all_regs)

        elif opcode in ARM64Parser.PAIR_OPS:
            # Pair operations
            if opcode == "STP":
                # STP src1, src2, [base, offset]
                if len(all_regs) >= 2:
                    src_regs.extend(all_regs[:2])
                if len(all_regs) >= 3:
                    src_regs.extend(all_regs[2:])
            else:  # LDP
                # LDP dest1, dest2, [base, offset]
                if len(all_regs) >= 2:
                    dest_regs.extend(all_regs[:2])
                if len(all_regs) >= 3:
                    src_regs.extend(all_regs[2:])

        else:
            # Default: first is destination, rest are sources
            if len(all_regs) >= 1:
                dest_regs.append(all_regs[0])
            if len(all_regs) >= 2:
                src_regs.extend(all_regs[1:])

        return dest_regs, src_regs

    @staticmethod
    def _normalize_register(reg: str) -> str:
        """Normalize register names (w0 -> x0, etc.)"""
        reg = reg.lower()
        if reg.startswith("w") and reg[1:].isdigit():
            return "x" + reg[1:]
        return reg


class PipelineSimulator:
    """5-stage pipeline simulator with hazard detection"""

    def __init__(
        self,
        enable_forwarding: bool = True,
        branch_policy: str = "not_taken",
        branch_penalty: int = 1,
    ):
        self.enable_forwarding = enable_forwarding
        self.branch_policy = branch_policy  # "not_taken" or "always_taken"
        self.branch_penalty = branch_penalty
        self.instructions: List[Instruction] = []
        self.pipeline_states: List[PipelineState] = []
        self.hazards_detected: List[Hazard] = []

        # Pipeline configuration
        self.num_stages = 5
        self.memory_units = 1
        self.alu_units = 1

    def load_instructions(self, assembly_code: str):
        """Load and parse ARM64 assembly code"""
        self.instructions = []
        pc = 0

        for line in assembly_code.split("\n"):
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

    def simulate(self) -> List[PipelineState]:
        """Run pipeline simulation"""
        self.pipeline_states = []
        self.hazards_detected = []

        pipeline = {stage: None for stage in PipelineStage}
        cycle = 0
        next_fetch_pc = 0
        branch_bubbles_remaining = 0

        while next_fetch_pc < len(self.instructions) or any(
            v is not None for v in pipeline.values()
        ):
            cycle_hazards = []
            forwarding = []
            stalled = False

            # Apply branch bubbles (no fetch)
            fetch_allowed = True
            if branch_bubbles_remaining > 0:
                fetch_allowed = False
                branch_bubbles_remaining -= 1

            # Check for hazards before advancing
            if pipeline[PipelineStage.DECODE] is not None:
                decode_pc = pipeline[PipelineStage.DECODE]
                decode_instr = self.instructions[decode_pc]

                data_hazards = self._detect_data_hazards(decode_instr, pipeline)
                cycle_hazards.extend(data_hazards)

                if data_hazards and not self.enable_forwarding:
                    stalled = True
                elif data_hazards:
                    can_forward = all(
                        h.producer_stage
                        in {PipelineStage.EXECUTE, PipelineStage.MEMORY}
                        for h in data_hazards
                        if h.type == HazardType.RAW
                    )
                    if not can_forward:
                        stalled = True
                    else:
                        for h in data_hazards:
                            if h.type == HazardType.RAW:
                                forwarding.append(
                                    (h.producer_pc, h.consumer_pc, h.resource)
                                )

            structural_hazards = self._detect_structural_hazards(pipeline)
            cycle_hazards.extend(structural_hazards)
            if structural_hazards:
                stalled = True

            # Record pipeline state
            state = PipelineState(
                cycle=cycle,
                stages=pipeline.copy(),
                stalled=stalled,
                hazards=cycle_hazards,
                forwarding=forwarding,
            )
            self.pipeline_states.append(state)
            self.hazards_detected.extend(cycle_hazards)

            # Detect branch in EXE
            branch_taken = False
            branch_target = None
            exe_pc = pipeline[PipelineStage.EXECUTE]
            if exe_pc is not None:
                exe_instr = self.instructions[exe_pc]
                if exe_instr.is_branch and exe_instr.branch_target_pc is not None:
                    if self.branch_policy == "always_taken":
                        branch_taken = True
                        branch_target = exe_instr.branch_target_pc

            if not stalled:
                new_pipeline = {stage: None for stage in PipelineStage}

                for stage in reversed(list(PipelineStage)):
                    if stage == PipelineStage.FETCH:
                        if fetch_allowed and next_fetch_pc < len(self.instructions):
                            new_pipeline[PipelineStage.FETCH] = next_fetch_pc
                            next_fetch_pc += 1
                    else:
                        prev_stage = PipelineStage(stage.value - 1)
                        new_pipeline[stage] = pipeline[prev_stage]

                # Flush wrong-path IF/DECODE on taken branch
                if branch_taken and branch_target is not None:
                    new_pipeline[PipelineStage.FETCH] = None
                    new_pipeline[PipelineStage.DECODE] = None
                    next_fetch_pc = branch_target
                    branch_bubbles_remaining = self.branch_penalty

                pipeline = new_pipeline
            else:
                new_pipeline = pipeline.copy()
                new_pipeline[PipelineStage.DECODE] = None
                pipeline = new_pipeline

            cycle += 1

            if cycle > len(self.instructions) * 10:
                print("Warning: Simulation exceeded maximum cycles")
                break

        return self.pipeline_states

    def _detect_data_hazards(self, instr: Instruction, pipeline: Dict) -> List[Hazard]:
        """Detect RAW, WAR, WAW data hazards"""
        hazards = []

        # Check instructions in later stages
        for stage in [
            PipelineStage.EXECUTE,
            PipelineStage.MEMORY,
            PipelineStage.WRITEBACK,
        ]:
            if pipeline[stage] is None:
                continue

            other_pc = pipeline[stage]
            other_instr = self.instructions[other_pc]

            # RAW: Read After Write (True Dependency)
            # Current instruction reads a register that a previous instruction writes
            for src_reg in instr.src_regs:
                if src_reg in other_instr.dest_regs:
                    hazards.append(
                        Hazard(
                            type=HazardType.RAW,
                            cycle=len(self.pipeline_states),
                            producer_pc=other_pc,
                            consumer_pc=instr.pc,
                            producer_stage=stage,
                            consumer_stage=PipelineStage.DECODE,
                            resource=src_reg,
                        )
                    )

            # WAR: Write After Read (Anti-Dependency)
            # Current instruction writes a register that a previous instruction reads
            for dest_reg in instr.dest_regs:
                if dest_reg in other_instr.src_regs:
                    hazards.append(
                        Hazard(
                            type=HazardType.WAR,
                            cycle=len(self.pipeline_states),
                            producer_pc=other_pc,
                            consumer_pc=instr.pc,
                            producer_stage=stage,
                            consumer_stage=PipelineStage.DECODE,
                            resource=dest_reg,
                        )
                    )

            # WAW: Write After Write (Output Dependency)
            # Current instruction writes a register that a previous instruction writes
            for dest_reg in instr.dest_regs:
                if dest_reg in other_instr.dest_regs:
                    hazards.append(
                        Hazard(
                            type=HazardType.WAW,
                            cycle=len(self.pipeline_states),
                            producer_pc=other_pc,
                            consumer_pc=instr.pc,
                            producer_stage=stage,
                            consumer_stage=PipelineStage.DECODE,
                            resource=dest_reg,
                        )
                    )

        return hazards

    def _detect_structural_hazards(self, pipeline: Dict) -> List[Hazard]:
        """Detect structural hazards (resource conflicts)"""
        hazards = []

        # Count memory accesses in Memory stage
        memory_accesses = []
        if pipeline[PipelineStage.MEMORY] is not None:
            pc = pipeline[PipelineStage.MEMORY]
            instr = self.instructions[pc]
            if instr.memory_access:
                memory_accesses.append(pc)

        # Check if we have more memory accesses than available units
        if len(memory_accesses) > self.memory_units:
            for pc in memory_accesses[self.memory_units :]:
                hazards.append(
                    Hazard(
                        type=HazardType.STRUCTURAL,
                        cycle=len(self.pipeline_states),
                        producer_pc=memory_accesses[0],
                        consumer_pc=pc,
                        producer_stage=PipelineStage.MEMORY,
                        consumer_stage=PipelineStage.MEMORY,
                        resource="Memory Unit",
                    )
                )

        return hazards

    def export_csv(self, output_path: str):
        """Export cycle-by-cycle pipeline states to CSV.
        Output format:
        - Row per instruction
        - Columns are cycles (C0, C1, ...)
        - Cells show stage name
        - If stalled, show STAGE[STALL]
        """
        import csv

        if not self.pipeline_states:
            return

        max_cycle = self.pipeline_states[-1].cycle
        header = ["Instruction"] + [f"C{c}" for c in range(max_cycle + 1)]

        # Precompute stage abbreviations
        stage_abbrev = {
            PipelineStage.FETCH: "IF",
            PipelineStage.DECODE: "IS",
            PipelineStage.EXECUTE: "EXE",
            PipelineStage.MEMORY: "MEM",
            PipelineStage.WRITEBACK: "WB",
        }

        # Build a cycle -> (pc -> stage) mapping
        cycle_stage_map = []
        for state in self.pipeline_states:
            pc_to_stage = {}
            for stage, pc in state.stages.items():
                if pc is not None:
                    pc_to_stage[pc] = stage
            cycle_stage_map.append((pc_to_stage, state.stalled))

        with open(output_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(header)

            for instr in self.instructions:
                row = [f"[{instr.pc}] {instr.address}: {instr.opcode} {instr.operands}"]

                for cycle in range(max_cycle + 1):
                    pc_to_stage, stalled = cycle_stage_map[cycle]

                    if instr.pc in pc_to_stage:
                        stage = pc_to_stage[instr.pc]
                        cell = stage_abbrev[stage]
                        if stalled:
                            cell = f"{cell}[STALL]"
                        row.append(cell)
                    else:
                        row.append("")

                writer.writerow(row)

    def print_simulation(self):
        """Print detailed simulation output"""
        print("=" * 100)
        print("ARM64 PIPELINE SIMULATION")
        print("=" * 100)
        print(f"Total Instructions: {len(self.instructions)}")
        print(f"Forwarding: {'Enabled' if self.enable_forwarding else 'Disabled'}")
        print(f"Pipeline Stages: {self.num_stages}")
        print()

        # Print instruction listing
        print("INSTRUCTION LISTING:")
        print("-" * 100)
        for instr in self.instructions:
            dest = f"Dest: {instr.dest_regs}" if instr.dest_regs else ""
            src = f"Src: {instr.src_regs}" if instr.src_regs else ""
            print(
                f"[{instr.pc:2d}] {instr.address}: {instr.opcode:8s} {instr.operands:30s} {dest:20s} {src}"
            )
        print()

        # Print cycle-by-cycle execution
        print("CYCLE-BY-CYCLE EXECUTION:")
        print("-" * 100)
        for state in self.pipeline_states:
            print(f"\nCycle {state.cycle:3d}:")

            # Print pipeline stages
            for stage in PipelineStage:
                pc = state.stages[stage]
                if pc is not None:
                    instr = self.instructions[pc]
                    print(
                        f"  {stage.name:10s}: [{pc:2d}] {instr.opcode} {instr.operands}"
                    )
                else:
                    print(f"  {stage.name:10s}: [--] (empty)")

            # Print hazards
            if state.hazards:
                print(f"  {'HAZARDS':10s}:")
                for hazard in state.hazards:
                    print(f"    - {hazard}")

            # Print forwarding
            if state.forwarding:
                print(f"  {'FORWARD':10s}:")
                for from_pc, to_pc, reg in state.forwarding:
                    print(f"    - Forward {reg} from [{from_pc}] to [{to_pc}]")

            if state.stalled:
                print(f"  {'STATUS':10s}: **STALLED**")

        print()

        # Print summary
        print("SUMMARY:")
        print("-" * 100)
        print(f"Total Cycles: {len(self.pipeline_states)}")
        print(f"Total Stalls: {sum(1 for s in self.pipeline_states if s.stalled)}")
        print(f"CPI: {len(self.pipeline_states) / len(self.instructions):.2f}")
        print()

        # Hazard statistics
        hazard_types = {}
        for hazard in self.hazards_detected:
            hazard_types[hazard.type] = hazard_types.get(hazard.type, 0) + 1

        print("HAZARD STATISTICS:")
        for htype, count in hazard_types.items():
            print(f"  {htype.value:20s}: {count}")
        print()


def main():
    """Example usage"""

    # Load fibonacci assembly from file
    with open(
        "/Users/lax/Documents/ND_courses/archite/PipeViz-simulator/pipeviz/runs/65cd9484-420b-42bd-b2d4-a75372d3b509/main.asm",
        "r",
    ) as f:
        asm_content = f.read()

    # Extract just the fibonacci function (only real instruction lines)
    fib_lines = []
    in_fib = False

    for line in asm_content.split("\n"):
        if "0000000000400644 <fibonacci>:" in line:
            in_fib = True
            continue
        if in_fib:
            if "<main>:" in line or line.startswith("Disassembly"):
                break

            # keep only lines that look like an instruction
            if ARM64Parser.parse_instruction(line, 0):
                fib_lines.append(line)

    # Keep the first N *instructions* (not raw lines)
    fibonacci_asm = "\n".join(fib_lines[:20])

    print("Analyzing Fibonacci function...")
    print()

    # Simulate with forwarding
    print("\n" + "=" * 100)
    print("SIMULATION WITH FORWARDING")
    print("=" * 100)
    sim_forward = PipelineSimulator(enable_forwarding=True)
    sim_forward.load_instructions(fibonacci_asm)
    sim_forward.simulate()
    sim_forward.print_simulation()
    sim_forward.export_csv("sim_forward.csv")

    # Simulate without forwarding
    print("\n" + "=" * 100)
    print("SIMULATION WITHOUT FORWARDING")
    print("=" * 100)
    sim_no_forward = PipelineSimulator(enable_forwarding=False)
    sim_no_forward.load_instructions(fibonacci_asm)
    sim_no_forward.simulate()
    sim_no_forward.print_simulation()
    sim_no_forward.export_csv("sim_no_forward.csv")


if __name__ == "__main__":
    main()
