#!/usr/bin/env python3
"""
Analyzes ARM64 assembly code and detects:
- Data Hazards (RAW, WAR, WAW)
- Structural Hazards
"""

from loguru import logger

from config import Hazard
from src.enum_vault.pipeline_enums import (
    DynamicInOrderStages,
    HazardType,
    InOrderSuperscalarStages,
    OutOfOrderStages,
    PipelineStage,
    PipelineTypes,
    ScoreboardStages,
    StaticInOrderStages,
    TomasuloStages,
    VLIWStages,
)
from src.pipeline.pipeline_base import Instruction


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

    def detect_hazards(self) -> list[Hazard]:
        return []


# this is just for the reference - lets build something based on
# below information
def _detect_data_hazards(self, instr: Instruction, pipeline: dict) -> list[Hazard]:
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
