#!/usr/bin/env python3
"""
ARM64 Pipeline Simulator
Analyzes ARM64 assembly code and detects:
- Data Hazards (RAW, WAR, WAW)
- Structural Hazards
- Shows cycle-by-cycle execution
"""

import re

from loguru import logger

from src.config import (
    Instruction,
    OpcodeConfig,
    config_parser,
)

config: OpcodeConfig = config_parser()


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
    def parse_instruction(line: str, pc: int) -> Instruction | None:
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
    def _parse_operands(opcode: str, operands: str) -> tuple[list[str], list[str]]:
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
