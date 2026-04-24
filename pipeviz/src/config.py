from dataclasses import dataclass
from pathlib import Path

import yaml
from pydantic import BaseModel, field_validator

from src.enum_vault.pipeline_enums import HazardType, PipelineStage

BASE_PATH = (Path(__file__).parent / "..").resolve()
OPSCODE_YAML_PATH = BASE_PATH / "assembly_assets" / "aarch64_opcodes.yaml"


class ARMOpsCodeClassification(BaseModel):
    MOV_OPS: list[str] = []
    LOAD_OPS: list[str] = []
    STORE_OPS: list[str] = []
    PAIR_OPS: list[str] = []
    ALU_OPS: list[str] = []
    COMPARE_OPS: list[str] = []
    BRANCH_OPS: list[str] = []

    @field_validator(
        "MOV_OPS",
        "LOAD_OPS",
        "STORE_OPS",
        "PAIR_OPS",
        "ALU_OPS",
        "COMPARE_OPS",
        "BRANCH_OPS",
    )
    @classmethod
    def to_lower(cls, v: list[str]):
        return [item.lower() for item in v]


class OpcodeConfig(BaseModel):
    opcodes: ARMOpsCodeClassification

    def get_opcode_list(self, opcode_type: str) -> list[str]:
        return getattr(self.opcodes, opcode_type)


def config_parser() -> OpcodeConfig:
    try:
        with (OPSCODE_YAML_PATH).open() as f:
            return OpcodeConfig(**yaml.safe_load(f))
    except FileNotFoundError:
        return OpcodeConfig(opcodes=ARMOpsCodeClassification(**{}))


@dataclass
class Instruction:
    """Represents a single ARM64 instruction"""

    address: str
    opcode: str
    operands: str
    raw: str
    pc: int  # Program counter (instruction index)

    # Parsed operands
    dest_regs: list[str]  # Registers written to
    src_regs: list[str]  # Registers read from
    memory_access: bool  # Does this instruction access memory?
    is_branch: bool  # Is this a branch/jump?
    is_load: bool  # Is this a load instruction?
    is_store: bool  # Is this a store instruction?

    # Branch info
    branch_target_addr: str | None = None
    branch_target_pc: int | None = None

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
    stages: dict[PipelineStage, int | None]  # Stage -> instruction PC
    stalled: bool
    hazards: list[Hazard]
    forwarding: list[tuple[int, int, str]]  # (from_pc, to_pc, register)

    def __repr__(self):
        stage_str = " | ".join(
            [
                f"{stage.name}: {pc if pc is not None else '-'}"
                for stage, pc in self.stages.items()
            ]
        )
        return f"Cycle {self.cycle}: [{stage_str}]" + (" STALL" if self.stalled else "")


if __name__ == "__main__":
    print(OPSCODE_YAML_PATH)
    config = config_parser()
    print(config)
