import json
import re
from argparse import ArgumentParser
from pathlib import Path

from jinja2 import Template


def get_args():
    parser = ArgumentParser()
    parser.add_argument("--port", type=int, default=5001)
    parser.add_argument("--reload", type=bool, default=True)
    parser.add_argument(
        "--model-type", type=str, default="local", choices=["local", "cloud"]
    )
    return parser.parse_args()


def extract_function_assembly(asm_text: str, func_name: str) -> list[str]:
    """
    Extracts the complete assembly block for a given function from objdump text.

    Args:
        asm_text (str): The raw string content of the assembly file.
        func_name (str): The name of the function to extract (e.g., 'main', 'fibonacci').
                         Matches exact names and C++ mangled symbols (e.g., _Z...).

    Returns:
        list[str]: The extracted assembly block, or an empty list if not found.
    """
    lines = asm_text.splitlines()
    in_function = False
    captured_lines = []

    header_pattern = re.compile(r"^([0-9a-fA-F]+)\s+<([^>]+)>:")
    section_pattern = re.compile(r"^Disassembly of section")

    def is_target_symbol(symbol_name: str) -> bool:
        # Ignore PLT / GLIBC / dynamic symbols
        if "@" in symbol_name:
            return False
        if symbol_name == func_name:
            return True
        if symbol_name == f"_{func_name}":
            return True
        if symbol_name.startswith(f"{func_name}."):
            return True
        if symbol_name.startswith("_Z") and func_name in symbol_name:
            return True
        return False

    for line in lines:
        header_match = header_pattern.match(line)

        if header_match:
            symbol_name = header_match.group(2)

            if in_function:
                break

            if is_target_symbol(symbol_name):
                in_function = True
                captured_lines.append(line)
                continue

        if in_function:
            if section_pattern.match(line):
                break
            line = line.replace("\t", "   ")
            captured_lines.append(line)

    return captured_lines


def write_json_data(path: Path, new_data: dict) -> bool:
    try:
        with path.open("w") as f:
            json.dump(new_data, f)
        return True
    except Exception as e:
        print(f"Failed to update chat required data: {e}")
        return False


def read_json_data(path: Path) -> dict:
    try:
        with path.open("r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Failed to read JSON data: {e}")
        return {}


def render_template(template_path: Path, template_options: dict) -> str:
    with template_path.open("r") as f:
        template = Template(f.read())
    return template.render(**template_options)


# ==========================================
# Example Usage:
# ==========================================
if __name__ == "__main__":
    # Assuming 'asm_content' contains the text from your main.asm file
    with open(
        "/Users/lax/Documents/ND_courses/archite/PipeViz-simulator/pipeviz/runs/65cd9484-420b-42bd-b2d4-a75372d3b509/main.asm",
        "r",
    ) as f:
        asm_content = f.read()

    print("--- Extracting 'fibonacci' ---")
    fib_asm = extract_function_assembly(asm_content, "fibonacci")
    print(fib_asm)

    print("\n--- Extracting 'main' ---")
    main_asm = extract_function_assembly(asm_content, "main")
    print(main_asm)
