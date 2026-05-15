import pytest
from ani_cli_arabic.providers import registry as reg
from ani_cli_arabic.providers.animezone import AnimezoneProvider


def _ensure_registered():
    """Import the register module so the side-effect runs."""
    import ani_cli_arabic.providers.animezone_register  # noqa: F401


def test_animezone_in_list_providers():
    _ensure_registered()
    assert "animezone" in reg.list_providers()


def test_get_provider_returns_animezone_instance():
    _ensure_registered()
    provider = reg.get_provider("animezone")
    assert isinstance(provider, AnimezoneProvider)


def test_get_provider_unknown_returns_none():
    _ensure_registered()
    assert reg.get_provider("nonexistent_xyz") is None


def test_register_idempotent():
    """Registering the same provider twice should not raise and list should not duplicate."""
    _ensure_registered()
    _ensure_registered()
    providers = reg.list_providers()
    assert providers.count("animezone") == 1
