from enum import StrEnum


class PipelineTypes(StrEnum):
    TOMASULO = "tomasulo"
    OUT_OF_ORDER = "out_of_order"
    IN_ORDER = "in_order"

class DataHazardTypes(StrEnum):
    RAW = "read_after_write"
    WAR = "write_after_read"
    WAW = "write_after_write"

