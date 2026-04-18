"""Tests for the provider registry."""
from __future__ import annotations

import pytest

from ani_cli_arabic.providers.registry import (
    get_provider,
    list_providers,
    register_provider,
)
from ani_cli_arabic.providers.animeiat import AnimeiatProvider
from ani_cli_arabic.providers.base import Anime, BaseProvider, Episode


def test_list_providers_contains_animeiat():
    assert "animeiat" in list_providers()


def test_get_provider_returns_correct_instance():
    provider = get_provider("animeiat")
    assert isinstance(provider, AnimeiatProvider)


def test_get_provider_raises_for_unknown():
    with pytest.raises(KeyError, match="Unknown provider"):
        get_provider("nonexistent")


def test_register_custom_provider():
    class DummyProvider(BaseProvider):
        name = "dummy_reg"

        def search(self, query): return []
        def get_episodes(self, anime): return []
        def get_stream_url(self, episode): return ""

    register_provider(DummyProvider)
    assert "dummy_reg" in list_providers()
    assert isinstance(get_provider("dummy_reg"), DummyProvider)


def test_register_provider_raises_without_name():
    class NoNameProvider(BaseProvider):
        name = ""

        def search(self, query): return []
        def get_episodes(self, anime): return []
        def get_stream_url(self, episode): return ""

    with pytest.raises(ValueError, match="non-empty"):
        register_provider(NoNameProvider)
