from __future__ import annotations

from enum import Enum, IntEnum, StrEnum
from types import DynamicClassAttribute


class PipelineTypes(StrEnum):
    STATIC_IN_ORDER = "static_in_order"
    SCOREBOARD = "scoreboard"
    DYNAMIC_IN_ORDER = "dynamic_in_order"
    IN_ORDER_SUPERSCALAR = "in_order_superscalar"
    VLIW = "vliw"
    TOMASULO = "tomasulo"
    OUT_OF_ORDER = "out_of_order"


class HazardType(StrEnum):
    RAW = "Read After Write"  # True dependency
    WAR = "Write After Read"  # Anti-dependency
    WAW = "Write After Write"  # Output dependency
    STRUCTURAL = "Structural"  # Resource conflict


class StaticInOrderStages(IntEnum):
    IF = 0
    ID = 1
    EX = 2
    MEM = 3
    WB = 4

    @classmethod
    def get_structural_hazard_prone_stages(cls) -> list[StaticInOrderStages]:
        return [cls.ID, cls.EX, cls.MEM]

    @classmethod
    def get_raw_hazard_prone_stages(cls) -> list[StaticInOrderStages]:
        return [cls.ID]

    @classmethod
    def get_war_hazard_prone_stages(cls) -> list[StaticInOrderStages]:
        return [cls.get_final_stage()]  # returns empty list

    @classmethod
    def get_waw_hazard_prone_stages(cls) -> list[StaticInOrderStages]:
        return [cls.WB]

    @classmethod
    def get_final_stage(cls) -> StaticInOrderStages:
        return cls.WB

    @classmethod
    def get_all_stages(cls, names=False) -> list[StaticInOrderStages] | list[str]:
        result = list(cls)
        if names:
            return [s.name for s in result]
        return result

    @classmethod
    def get_stage_by_name(cls, name: IntEnum) -> str:
        return str(name)


class ScoreboardStages(IntEnum):
    IF = 0
    IS = 1
    RD = 2
    EX = 3
    WB = 4

    @classmethod
    def get_structural_hazard_prone_stages(cls) -> list[ScoreboardStages]:
        return [cls.IS, cls.EX]

    @classmethod
    def get_raw_hazard_prone_stages(cls) -> list[ScoreboardStages]:
        return [cls.RD]

    @classmethod
    def get_war_hazard_prone_stages(cls) -> list[ScoreboardStages]:
        return [cls.WB]

    @classmethod
    def get_waw_hazard_prone_stages(cls) -> list[ScoreboardStages]:
        return [cls.IS]

    @classmethod
    def get_final_stage(cls) -> ScoreboardStages:
        return cls.WB

    @classmethod
    def get_all_stages(cls, names=False) -> list[ScoreboardStages] | list[str]:
        result = list(cls)
        if names:
            return [s.name for s in result]
        return result

    @classmethod
    def get_stage_by_name(cls, name: IntEnum) -> str:
        return str(name)


class DynamicInOrderStages(IntEnum):
    IF = 0
    ID = 1
    IS = 2
    RD = 3
    EX = 4
    WB = 5

    @classmethod
    def get_structural_hazard_prone_stages(cls) -> list[DynamicInOrderStages]:
        return [cls.IS, cls.EX]

    @classmethod
    def get_raw_hazard_prone_stages(cls) -> list[DynamicInOrderStages]:
        return [cls.RD]

    @classmethod
    def get_war_hazard_prone_stages(cls) -> list[DynamicInOrderStages]:
        return [cls.WB]

    @classmethod
    def get_waw_hazard_prone_stages(cls) -> list[DynamicInOrderStages]:
        return [cls.IS]

    @classmethod
    def get_final_stage(cls) -> DynamicInOrderStages:
        return cls.WB

    @classmethod
    def get_all_stages(cls, names=False) -> list[DynamicInOrderStages] | list[str]:
        result = list(cls)
        if names:
            return [s.name for s in result]
        return result

    @classmethod
    def get_stage_by_name(cls, name: IntEnum) -> str:
        return str(name)


class InOrderSuperscalarStages(IntEnum):
    IF = 0
    ID = 1
    IS = 2
    EX = 3
    MEM = 4
    WB = 5
    COM = 6

    @classmethod
    def get_structural_hazard_prone_stages(cls) -> list[InOrderSuperscalarStages]:
        return [cls.ID, cls.IS, cls.EX, cls.MEM, cls.WB]

    @classmethod
    def get_raw_hazard_prone_stages(cls) -> list[InOrderSuperscalarStages]:
        return [cls.ID, cls.IS]

    @classmethod
    def get_war_hazard_prone_stages(cls) -> list[InOrderSuperscalarStages]:
        return [cls.get_final_stage()]  # returns empty list

    @classmethod
    def get_waw_hazard_prone_stages(cls) -> list[InOrderSuperscalarStages]:
        return [cls.IS]

    @classmethod
    def get_final_stage(cls) -> InOrderSuperscalarStages:
        return cls.COM

    @classmethod
    def get_all_stages(cls, names=False) -> list[InOrderSuperscalarStages] | list[str]:
        result = list(cls)
        if names:
            return [s.name for s in result]
        return result

    @classmethod
    def get_stage_by_name(cls, name: IntEnum) -> str:
        return str(name)


class VLIWStages(IntEnum):
    """VLIW pipeline stages.
    They are assumed resolved at compile time!
    """

    IF = 0
    ID = 1
    EX = 2
    MEM = 3
    WB = 4

    @classmethod
    def get_structural_hazard_prone_stages(cls) -> list[VLIWStages]:
        return [cls.EX, cls.MEM]

    @classmethod
    def get_raw_hazard_prone_stages(cls) -> list[VLIWStages]:
        return [cls.get_final_stage()]  # returns empty list

    @classmethod
    def get_war_hazard_prone_stages(cls) -> list[VLIWStages]:
        return [cls.get_final_stage()]  # returns empty list

    @classmethod
    def get_waw_hazard_prone_stages(cls) -> list[VLIWStages]:
        return [cls.get_final_stage()]  # returns empty list

    @classmethod
    def get_final_stage(cls) -> VLIWStages:
        return cls.WB

    @classmethod
    def get_all_stages(cls, names=False) -> list[VLIWStages] | list[str]:
        result = list(cls)
        if names:
            return [s.name for s in result]
        return result

    @classmethod
    def get_stage_by_name(cls, name: IntEnum) -> str:
        return str(name)


class TomasuloStages(IntEnum):
    """Tomasulo pipeline stages.
    🔴 IS
    Structural (RS full)
    Dependency tracking happens here

    ✔ BUT:

    RAW handled via tagging (no stall)
    WAR/WAW eliminated via renaming
    """

    IF = 0
    IS = 1
    EX = 2
    WB = 3
    COM = 4

    @classmethod
    def get_structural_hazard_prone_stages(cls) -> list[TomasuloStages]:
        return [cls.IS, cls.EX, cls.WB]

    @classmethod
    def get_raw_hazard_prone_stages(cls) -> list[TomasuloStages]:
        return [cls.IS]

    @classmethod
    def get_war_hazard_prone_stages(cls) -> list[TomasuloStages]:
        return [cls.get_final_stage()]  # returns empty list

    @classmethod
    def get_waw_hazard_prone_stages(cls) -> list[TomasuloStages]:
        return [cls.get_final_stage()]  # returns empty list

    @classmethod
    def get_final_stage(cls) -> TomasuloStages:
        return cls.COM

    @classmethod
    def get_all_stages(cls, names=False) -> list[TomasuloStages] | list[str]:
        result = list(cls)
        if names:
            return [s.name for s in result]
        return result

    @classmethod
    def get_stage_by_name(cls, name: IntEnum) -> str:
        return str(name)


class OutOfOrderStages(IntEnum):
    IF = 0
    IS = 1
    RO = 2
    EX = 3
    WB = 4
    COM = 5

    @classmethod
    def get_structural_hazard_prone_stages(cls) -> list[OutOfOrderStages]:
        return [cls.IS, cls.RO, cls.EX, cls.WB]

    @classmethod
    def get_raw_hazard_prone_stages(cls) -> list[OutOfOrderStages]:
        return [cls.get_final_stage()]  # returns empty list

    @classmethod
    def get_war_hazard_prone_stages(cls) -> list[OutOfOrderStages]:
        return [cls.get_final_stage()]  # returns empty list

    @classmethod
    def get_waw_hazard_prone_stages(cls) -> list[OutOfOrderStages]:
        return [cls.get_final_stage()]  # returns empty list

    @classmethod
    def get_final_stage(cls) -> OutOfOrderStages:
        return cls.COM

    @classmethod
    def get_all_stages(cls, names=False) -> list[OutOfOrderStages] | list[str]:
        result = list(cls)
        if names:
            return [s.name for s in result]
        return result

    @classmethod
    def get_stage_by_name(cls, name: IntEnum) -> str:
        return str(name)
