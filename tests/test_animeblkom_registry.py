"""Ensure AnimeblkomProvider is discoverable via the provider registry."""
from __future__ import annotations

import importlib

import pytest

from ani_cli_arabic.providers.registry import get_provider, list_providers


def test_animeblkom_in_list_providers() -> None:
    """After importing the registration shim the provider must appear in the list."""
    importlib.import_module("ani_cli_arabic.providers.animeblkom_register")
    names = list_providers()
    assert "animeblkom" in names


def test_get_provider_returns_animeblkom_instance() -> None:
    importlib.import_module("ani_cli_arabic.providers.animeblkom_register")
    provider = get_provider("animeblkom")
    assert provider is not None
    assert provider.name == "animeblkom"


def test_get_provider_unknown_returns_none() -> None:
    provider = get_provider("__does_not_exist__")
    assert provider is None


def test_register_idempotent() -> None:
    """Re-importing the shim must not create duplicate entries."""
    importlib.import_module("ani_cli_arabic.providers.animeblkom_register")
    importlib.import_module("ani_cli_arabic.providers.animeblkom_register")
    names = list_providers()
    assert names.count("animeblkom") == 1
