"""Registry integration tests for AnimekHProvider."""
from __future__ import annotations

import importlib

import pytest

from ani_cli_arabic.providers import registry
from ani_cli_arabic.providers.animekh import AnimekHProvider


def _ensure_registered() -> None:
    """Import the register module so the provider is in the registry."""
    importlib.import_module("ani_cli_arabic.providers.animekh_register")


def test_animekh_in_list_providers() -> None:
    _ensure_registered()
    assert "animekh" in registry.list_providers()


def test_get_provider_returns_animekh_instance() -> None:
    _ensure_registered()
    provider = registry.get_provider("animekh")
    assert isinstance(provider, AnimekHProvider)


def test_get_provider_unknown_returns_none() -> None:
    _ensure_registered()
    assert registry.get_provider("__no_such_provider__") is None


def test_register_idempotent() -> None:
    _ensure_registered()
    before = registry.list_providers()
    _ensure_registered()
    after = registry.list_providers()
    assert before.count("animekh") == after.count("animekh")
