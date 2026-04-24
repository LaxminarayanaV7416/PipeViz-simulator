import re


def extract_function_assembly(asm_text: str, func_name: str) -> list[str]:
    """
    Extracts the complete assembly block for a given function from objdump text.

    Args:
        asm_text (str): The raw string content of the assembly file.
        func_name (str): The name of the function to extract (e.g., 'main', 'fibonacci').
                         Matches substrings to handle C++ name mangling.

    Returns:
        str: The extracted assembly block, or an empty string if not found.
    """
    lines = asm_text.splitlines()
    in_function = False
    captured_lines = []

    # Regex to match function headers like: "0000000000400804 <_Z9fibonaccij>:"
    # It ensures the line starts with hex digits, has a space, and a name in brackets.
    header_pattern = re.compile(r"^([0-9a-fA-F]+)\s+<([^>]+)>:")

    # Regex to match the start of a new section like: "Disassembly of section .fini:"
    section_pattern = re.compile(r"^Disassembly of section")

    for line in lines:
        header_match = header_pattern.match(line)

        if header_match:
            symbol_name = header_match.group(2)

            if in_function:
                # We are already capturing, and we just hit the NEXT function header.
                # This means our target function block has ended.
                break

            # Check if this header belongs to the function we are looking for.
            # We use `in` to automatically handle C++ mangled names like `_Z9fibonaccij`.
            if func_name in symbol_name:
                in_function = True
                captured_lines.append(line)
                continue

        if in_function:
            # Stop if we hit a brand new disassembly section
            if section_pattern.match(line):
                break

            captured_lines.append(line)

    # Strip any trailing empty lines from the extracted block
    return captured_lines


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
