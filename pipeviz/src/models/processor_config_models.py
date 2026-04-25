from pydantic import BaseModel, Field, field_validator


class SpecialRegisterRule(BaseModel):
    instruction_type: str = Field(description="e.g. 'SD'")
    register_name: str = Field(description="e.g. 'base' or 'rt'")
    ready_at_stage: str = Field(description="Stage at which this register must be ready, e.g. 'EX' or 'CO'")


class ProcessorConfig(BaseModel):
    stages: list[str] = Field(
        description="Pipeline stage names in order, e.g. ['IF', 'IS', 'EX', 'WB', 'CO']"
    )
    fetch_width: int = Field(
        description="Max instructions fetched (IF stage) per cycle"
    )
    issue_width: int = Field(
        description="Max instructions issued (IS stage) per cycle"
    )
    scheduling_policy: str = Field(
        description="'in_order', 'tomasulo', or 'out_of_order'"
    )
    speculative_execution: bool = Field(
        description="Whether speculative execution is enabled"
    )
    execution_latencies: dict[str, int] = Field(
        default={},
        description=(
            "Number of cycles each instruction type spends in the EX stage. "
            "Use 'default' key for instructions not explicitly listed. "
            "e.g. {'LD': 2, 'SD': 2, 'ADD.D': 2, 'MUL.D': 4, 'default': 1}"
        )
    )
    forwarding_ready_stage: str = Field(
        description="Stage at the END of which destination register values are ready for forwarding, e.g. 'WB'"
    )
    branch_prediction: str = Field(
        description="Branch prediction strategy: 'static_not_taken', 'static_always_taken', 'dynamic_bpb_btb', etc."
    )
    branch_resolution_stage: str = Field(
        description="Stage at the END of which branch outcome is resolved, e.g. 'WB'"
    )
    commit_policy: str = Field(
        description="'in_order' — cannot commit out of order; 'out_of_order' — can commit out of order"
    )
    multi_commit_allowed: bool = Field(
        description="Whether multiple instructions can commit (WB/CO) in the same cycle"
    )
    structural_hazards: bool = Field(
        description="True if structural hazards exist; False if no structural hazards (unlimited reservation stations, functional units, etc.)"
    )
    special_register_rules: list[SpecialRegisterRule] = Field(
        default=[],
        description="Special register readiness rules for specific instructions, e.g. SD base register ready at EX, rt register ready at CO"
    )

    @field_validator("execution_latencies", mode="before")
    @classmethod
    def normalize_execution_latencies(cls, v):
        """
        GPT-4o sometimes returns execution_latencies as a list of dicts
        e.g. [{"instruction_type": "LD", "cycles": 2}, {"default": 1}]
        instead of the expected flat dict {"LD": 2, "default": 1}.
        This normalizes both formats into a flat dict.
        """
        if isinstance(v, dict):
            return v
        if isinstance(v, list):
            result = {}
            for item in v:
                if not isinstance(item, dict):
                    continue
                # Single key-value pair like {"default": 1}
                if len(item) == 1:
                    key, val = next(iter(item.items()))
                    if isinstance(val, int):
                        result[key] = val
                # Structured form like {"instruction_type": "LD", "cycles": 2}
                elif "instruction_type" in item:
                    name = item["instruction_type"]
                    cycles = next(
                        (item[k] for k in ("cycles", "latency", "clock_cycles", "num_cycles") if k in item),
                        None,
                    )
                    if cycles is not None:
                        result[name] = int(cycles)
            return result
        return v
