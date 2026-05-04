

PROMPT_LIMIT = 80000  # no of words / tokens

def check_prompt_length(prompt: str) -> bool:
    prompt = prompt.strip()
    prompt = prompt.replace("\t", " ")
    prompt_list: list[str] = prompt.split(" ")
    return len(prompt_list) < PROMPT_LIMIT



def generate_prompt(prompt: str) -> str:
    return prompt