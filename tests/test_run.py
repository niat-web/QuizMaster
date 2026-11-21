import pytest
from run import is_debug_enabled


def test_debug_disabled_by_default(monkeypatch):
    """Debug mode should be off when FLASK_DEBUG is not set."""
    monkeypatch.delenv("FLASK_DEBUG", raising=False)
    assert is_debug_enabled() is False


@pytest.mark.parametrize("value", ["1", "true", "TRUE", "yes", "  1  "])
def test_debug_enabled_for_truthy_values(monkeypatch, value):
    """Debug mode should turn on for explicit truthy values."""
    monkeypatch.setenv("FLASK_DEBUG", value)
    assert is_debug_enabled() is True


@pytest.mark.parametrize("value", ["0", "false", "FALSE", "no", "invalid", ""])
def test_debug_disabled_for_falsy_or_invalid_values(monkeypatch, value):
    """Debug mode should stay off for falsy, empty, or unexpected values."""
    monkeypatch.setenv("FLASK_DEBUG", value)
    assert is_debug_enabled() is False