"""Verify AnimenanaProvider is correctly registered in the global registry."""
from __future__ import annotations

import importlib

import pytest

from ani_cli_arabic.providers.registry import list_providers, get_provider, register_provider
from ani_cli_arabic.providers.animenana import AnimenanaProvider


def _ensure_registered() -> None:
    """Import the register module to trigger side-effect registration."""
    importlib.import_module("ani_cli_arabic.providers.animenana_register")


def test_animenana_in_list_providers() -> None:
    _ensure_registered()
    assert "animenana" in list_providers()


def test_get_provider_returns_animenana_instance() -> None:
    _ensure_registered()
    p = get_provider("animenana")
    assert isinstance(p, AnimenanaProvider)


def test_get_provider_unknown_returns_none() -> None:
    _ensure_registered()
    assert get_provider("nonexistent_xyz") is None


def test_register_idempotent() -> None:
    _ensure_registered()
    before = list_providers()
    register_provider(AnimenanaProvider())
    after = list_providers()
    assert before.count("animenana") == after.count("animenana") == 1
