from enum import StrEnum


class PipelineTypes(StrEnum):
    STATIC = "static"
    DYNAMIC = "dynamic"
    IN_ORDER = "in_order"
    IN_ORDER_SUPERSCALAR = "in_order_superscalar"
    IN_ORDER_VLIW = "in_order_vliw"
    TOMASULO = "tomasulo"
    OUT_OF_ORDER = "out_of_order"


class DataHazardTypes(StrEnum):
    RAW = "read_after_write"
    WAR = "write_after_read"
    WAW = "write_after_write"
