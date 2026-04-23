from enum import Enum, StrEnum


class PipelineTypes(StrEnum):
    STATIC = "static"
    DYNAMIC = "dynamic"
    IN_ORDER = "in_order"
    IN_ORDER_SUPERSCALAR = "in_order_superscalar"
    IN_ORDER_VLIW = "in_order_vliw"
    TOMASULO = "tomasulo"
    OUT_OF_ORDER = "out_of_order"


class HazardType(StrEnum):
    RAW = "Read After Write"  # True dependency
    WAR = "Write After Read"  # Anti-dependency
    WAW = "Write After Write"  # Output dependency
    STRUCTURAL = "Structural"  # Resource conflict


class PipelineStage(Enum):
    FETCH = 0
    DECODE = 1
    EXECUTE = 2
    MEMORY = 3
    WRITEBACK = 4
