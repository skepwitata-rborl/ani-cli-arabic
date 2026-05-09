import pytest

import ani_cli_arabic.providers.animelek_register  # noqa: F401 — side-effect import
from ani_cli_arabic.providers.registry import get_provider, list_providers
from ani_cli_arabic.providers.animelek import AnimelekProvider


def test_animelek_in_list_providers():
    assert "animelek" in list_providers()


def test_get_provider_returns_animelek_instance():
    provider = get_provider("animelek")
    assert isinstance(provider, AnimelekProvider)


def test_get_provider_unknown_returns_none():
    assert get_provider("nonexistent_provider_xyz") is None


def test_register_idempotent():
    """Re-importing the register shim should not duplicate the provider."""
    import ani_cli_arabic.providers.animelek_register  # noqa: F811
    names = list_providers()
    assert names.count("animelek") == 1
