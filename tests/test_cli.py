import pytest
import sys
from providers import resolve_provider, VALID_PROVIDERS


def test_resolve_provider_unknown_exits():
    with pytest.raises(SystemExit) as exc:
        resolve_provider("badvalue")
    assert exc.value.code == 1


def test_resolve_provider_returns_callable():
    fn = resolve_provider("gemini")
    assert callable(fn)


def test_valid_providers_contains_all_three():
    assert set(VALID_PROVIDERS) == {"gemini", "fal", "openai"}
