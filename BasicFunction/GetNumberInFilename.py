import re
from typing import List


def find_numbers(text: str) -> List[str]:
    numbers = re.findall(r"\d+", text)
    return numbers
