from app.routes import get_text


def test_get_text_normal_string():
    data = {"title": "Python Quiz"}
    assert get_text(data, "title") == "Python Quiz"


def test_get_text_whitespace_trimmed():
    data = {"title": "   Python Quiz   "}
    assert get_text(data, "title") == "Python Quiz"


def test_get_text_tabs_and_newlines_trimmed():
    data = {"title": "\n\t  Python Quiz  \t\n"}
    assert get_text(data, "title") == "Python Quiz"


def test_get_text_empty_string():
    data = {"title": ""}
    assert get_text(data, "title") == ""


def test_get_text_whitespace_only():
    data = {"title": "    "}
    assert get_text(data, "title") == ""


def test_get_text_missing_key():
    data = {}
    assert get_text(data, "title") == ""


def test_get_text_none_value():
    data = {"title": None}
    assert get_text(data, "title") == ""


def test_get_text_integer():
    data = {"title": 123}
    assert get_text(data, "title") == ""


def test_get_text_float():
    data = {"title": 45.67}
    assert get_text(data, "title") == ""


def test_get_text_boolean():
    data = {"title": True}
    assert get_text(data, "title") == ""


def test_get_text_list():
    data = {"title": ["item1", "item2"]}
    assert get_text(data, "title") == ""


def test_get_text_dict():
    data = {"title": {"nested": "dict"}}
    assert get_text(data, "title") == ""
