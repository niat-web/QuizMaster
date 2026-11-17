DIFFICULTIES = ["easy", "medium", "hard"]
OPTIONS = ["A", "B", "C", "D"]


def get_text(data, field):
    """ Returns fields as a terminal string """
    value = data.get(field)
    if not isinstance(value, str):
        return ""
    return value.strip()



def validate_quiz(data):
    """ returns the list of errors"""
    errors = []
    title = get_text(data, "title")
    difficulty = get_text(data, "difficulty") or "easy"
    if not title:
        errors.append("Title is required")
    if difficulty not in DIFFICULTIES:
        errors.append("Invalid difficulty")
    return errors



def validate_question(data, index=None):
    """ return the list of errors"""
    errors = []
    prefix = f"Question {index + 1}: " if index is not None else ""
    text = get_text(data, "text")
    options = [get_text(data, "option_" + letter) for letter in "abcd"]
    correct_option = get_text(data, "correct_option")
    if not text or "" in options:
        errors.append(f"{prefix}Question text and all 4 options are required")
    if correct_option not in OPTIONS:
        errors.append(f"{prefix}correct_option must be A, B, C or D")
    return errors