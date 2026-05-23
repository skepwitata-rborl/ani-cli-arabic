"""Registry integration tests for AnimekageProvider."""

from __future__ import annotations

import importlib

import pytest

from ani_cli_arabic.providers import registry
from ani_cli_arabic.providers.animekage import AnimekageProvider


def _ensure_registered() -> None:
    """Import the register module to make sure the provider is registered."""
    importlib.import_module("ani_cli_arabic.providers.animekage_register")


def test_animekage_in_list_providers():
    _ensure_registered()
    assert "animekage" in registry.list_providers()


def test_get_provider_returns_animekage_instance():
    _ensure_registered()
    provider = registry.get_provider("animekage")
    assert isinstance(provider, AnimekageProvider)


def test_get_provider_unknown_returns_none():
    _ensure_registered()
    assert registry.get_provider("does_not_exist_xyz") is None


def test_register_idempotent():
    """Registering the same provider name twice should not raise and should
    keep the registry consistent."""
    _ensure_registered()
    _ensure_registered()  # second import is a no-op due to module caching
    providers = registry.list_providers()
    assert providers.count("animekage") == 1
