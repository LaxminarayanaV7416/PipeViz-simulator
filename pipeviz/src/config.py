from pathlib import Path

import yaml
from pydantic import BaseModel, field_validator

BASE_PATH = Path(__file__).parent
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


if __name__ == "__main__":
    print(OPSCODE_YAML_PATH)
    config = config_parser()
    print(config)
