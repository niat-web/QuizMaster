from app.routes import get_text


def test_get_text_returns_normal_string():
    data = {"name": "Bhavya"}

    result = get_text(data, "name")

    assert result == "Bhavya"


def test_get_text_trims_surrounding_spaces():
    data = {"name": "  Bhavya  "}

    result = get_text(data, "name")

    assert result == "Bhavya"


def test_get_text_returns_empty_string_for_missing_key():
    data = {}

    result = get_text(data, "name")

    assert result == ""


def test_get_text_returns_empty_string_for_number():
    data = {"age": 123}

    result = get_text(data, "age")

    assert result == ""


def test_get_text_returns_empty_string_for_none():
    data = {"name": None}

    result = get_text(data, "name")

    assert result == ""


def test_get_text_returns_empty_string_for_list():
    data = {"items": [1, 2, 3]}

    result = get_text(data, "items")

    assert result == ""
