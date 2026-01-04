import re
from rapidfuzz import fuzz


def normalize(s: str) -> str:
    """Lowercase, remove punctuation, strip whitespace."""
    return re.sub(r"[^\w\s]", "", s.lower()).strip()


def is_match(user_input: str, correct_options: list[str], threshold: int = 85) -> bool:
    """Check if user input matches any correct option (fuzzy, ~1 letter tolerance)."""
    user = normalize(user_input)
    if not user:
        return False
    return any(fuzz.ratio(user, normalize(opt)) >= threshold for opt in correct_options)
