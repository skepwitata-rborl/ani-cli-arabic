"""Tests that AnimevostProvider is correctly registered in the provider registry."""
from __future__ import annotations

import importlib

import pytest

from ani_cli_arabic.providers import registry
from ani_cli_arabic.providers.animevost import AnimevostProvider


def _ensure_registered() -> None:
    """Import the register module to trigger side-effect registration."""
    importlib.import_module("ani_cli_arabic.providers.animevost_register")


def test_animevost_in_list_providers():
    _ensure_registered()
    assert "animevost" in registry.list_providers()


def test_get_provider_returns_animevost_instance():
    _ensure_registered()
    provider = registry.get_provider("animevost")
    assert isinstance(provider, AnimevostProvider)


def test_get_provider_unknown_returns_none():
    _ensure_registered()
    assert registry.get_provider("nonexistent_xyz") is None


def test_register_idempotent():
    _ensure_registered()
    _ensure_registered()  # second import should not raise or duplicate
    providers = registry.list_providers()
    assert providers.count("animevost") == 1
