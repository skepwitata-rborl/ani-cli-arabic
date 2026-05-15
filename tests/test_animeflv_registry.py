"""Registry integration tests for AnimeflvProvider."""
from __future__ import annotations

import importlib

import pytest

from ani_cli_arabic.providers import registry as reg
from ani_cli_arabic.providers.animeflv import AnimeflvProvider


def _ensure_registered() -> None:
    """Import the register module to guarantee the provider is registered."""
    import ani_cli_arabic.providers.animeflv_register  # noqa: F401


def test_animeflv_in_list_providers():
    _ensure_registered()
    assert "animeflv" in reg.list_providers()


def test_get_provider_returns_animeflv_instance():
    _ensure_registered()
    provider = reg.get_provider("animeflv")
    assert isinstance(provider, AnimeflvProvider)


def test_get_provider_unknown_returns_none():
    _ensure_registered()
    assert reg.get_provider("does_not_exist_xyz") is None


def test_register_idempotent():
    _ensure_registered()
    before = reg.list_providers()
    _ensure_registered()
    after = reg.list_providers()
    assert before.count("animeflv") == after.count("animeflv")
