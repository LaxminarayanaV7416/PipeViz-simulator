import argparse
import re
from dataclasses import dataclass
from typing import List, Set, Tuple

REG_RE = re.compile(r"\b([wx]\d+|xzr|wzr)\b")

"""
uv run src/trail_cycles.py \
  --asm runs/b4d0ba8a-6196-4de6-bb60-bd6245b8a2d1/main.asm \
  --func _ZN4main9fibonacci17h9fb93bd4297402cbE \
  --branch-penalty 1 \
  --max-instr 25

"""


@dataclass
class Instr:
    addr: str
    text: str
    op: str
    reads: Set[str]
    writes: Set[str]
    is_branch: bool
    is_load: bool


def normalize_reg(reg: str) -> str:
    if reg in ("xzr", "wzr"):
        return "xzr"
    if reg.startswith("w"):
        return "x" + reg[1:]
    return reg


def parse_regs(operand_str: str) -> List[str]:
    regs = REG_RE.findall(operand_str)
    return [normalize_reg(r) for r in regs if normalize_reg(r) != "xzr"]


def classify_instruction(
    op: str, operands: str
) -> Tuple[Set[str], Set[str], bool, bool]:
    reads = set()
    writes = set()
    is_branch = op.startswith("b") or op in ("cbz", "cbnz", "bl", "ret")
    is_load = op in ("ldr", "ldur", "ldp", "ldrb", "ldrh")

    regs = parse_regs(operands)

    # Heuristics for reads/writes
    if op in ("str", "stur", "stp", "strb", "strh"):
        # store: all regs are read (source + address)
        reads.update(regs)
    elif is_load:
        # load: first reg = write, rest = read
        if regs:
            writes.add(regs[0])
            reads.update(regs[1:])
    elif op.startswith("b") or op in ("cbz", "cbnz", "ret"):
        # branch: reads are used
        reads.update(regs)
    elif op == "bl":
        # call: treat as branch
        reads.update(regs)
    else:
        # ALU-style: first reg write, others read
        if regs:
            writes.add(regs[0])
            reads.update(regs[1:])

    return reads, writes, is_branch, is_load


def extract_function(asm_path: str, func_symbol: str) -> List[Instr]:
    in_func = False
    instrs: List[Instr] = []

    with open(asm_path, "r") as f:
        for line in f:
            if f"<{func_symbol}>:" in line:
                in_func = True
                continue

            if in_func and re.match(r"^\s*0000000000.*<", line):
                # next function starts
                break

            # match instruction lines: "8ab4: d10103ff  sub sp, sp, #0x40"
            m = re.match(r"^\s*([0-9a-f]+):\s+[0-9a-f]+\s+(\S+)\s*(.*)$", line)
            if in_func and m:
                addr, op, operands = m.groups()
                reads, writes, is_branch, is_load = classify_instruction(op, operands)
                instrs.append(
                    Instr(
                        addr=addr,
                        text=f"{op} {operands}".strip(),
                        op=op,
                        reads=reads,
                        writes=writes,
                        is_branch=is_branch,
                        is_load=is_load,
                    )
                )

    return instrs


def schedule_pipeline(
    instrs: List[Instr], branch_penalty: int = 1, forwarding: bool = False
):
    schedule = []
    last_start = 0
    min_if_cycle = 1

    def available_cycle(prev_start: int, prev_instr: Instr) -> int:
        # when result becomes available to dependent
        if not forwarding:
            return prev_start + 4  # WB
        # with forwarding:
        if prev_instr.is_load:
            return prev_start + 3  # MEM
        return prev_start + 2  # EXE

    for i, instr in enumerate(instrs):
        start = max(last_start + 1, min_if_cycle)

        while True:
            exe_cycle = start + 2
            hazard = False
            for prev_start, prev_instr in schedule:
                for r in instr.reads:
                    if r in prev_instr.writes:
                        avail = available_cycle(prev_start, prev_instr)
                        if avail >= exe_cycle:
                            hazard = True
                            break
                if hazard:
                    break

            if hazard:
                start += 1
                continue
            break

        schedule.append((start, instr))
        last_start = start

        # control hazard penalty
        if instr.is_branch:
            min_if_cycle = start + 1 + branch_penalty
        else:
            min_if_cycle = start + 1

    return schedule


def render_markdown(schedule):
    max_cycle = max(start + 4 for start, _ in schedule)
    header = ["Instr"] + [f"C{c}" for c in range(1, max_cycle + 1)]
    rows = []

    for start, instr in schedule:
        row = [f"{instr.addr}: {instr.text}"]
        for c in range(1, max_cycle + 1):
            if c == start:
                row.append("IF")
            elif c == start + 1:
                row.append("IS")
            elif c == start + 2:
                row.append("EXE")
            elif c == start + 3:
                row.append("MEM")
            elif c == start + 4:
                row.append("WB")
            else:
                row.append("")
        rows.append(row)

    # markdown table
    out = []
    out.append("| " + " | ".join(header) + " |")
    out.append("| " + " | ".join(["---"] * len(header)) + " |")
    for r in rows:
        out.append("| " + " | ".join(r) + " |")
    return "\n".join(out)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--asm", required=True)
    parser.add_argument("--func", required=True)
    parser.add_argument("--branch-penalty", type=int, default=1)
    parser.add_argument("--forwarding", action="store_true")
    parser.add_argument("--max-instr", type=int, default=0)
    args = parser.parse_args()

    instrs = extract_function(args.asm, args.func)
    if args.max_instr > 0:
        instrs = instrs[: args.max_instr]

    schedule = schedule_pipeline(
        instrs,
        branch_penalty=args.branch_penalty,
        forwarding=args.forwarding,
    )

    data = render_markdown(schedule)
    with open("fibonnaci.md", "w") as f:
        f.write(data)


if __name__ == "__main__":
    main()
