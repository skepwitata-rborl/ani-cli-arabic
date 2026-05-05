"""Tests for the provider registry."""
from __future__ import annotations

import pytest

from ani_cli_arabic.providers.base import Anime, BaseProvider, Episode
from ani_cli_arabic.providers.registry import (
    get_provider,
    list_providers,
    register_provider,
)


class DummyProvider(BaseProvider):
    name = "dummy_test_xyz"

    def search(self, query):
        return []

    def get_episodes(self, anime):
        return []

    def get_stream_url(self, episode):
        return ""


def test_list_providers_contains_animeiat():
    assert "animeiat" in list_providers()


def test_list_providers_contains_animekisa():
    assert "animekisa" in list_providers()


def test_list_providers_contains_animerco():
    assert "animerco" in list_providers()


def test_list_providers_contains_shahed4u():
    assert "shahed4u" in list_providers()


def test_list_providers_contains_witanime():
    assert "witanime" in list_providers()


def test_list_providers_is_sorted():
    names = list_providers()
    assert names == sorted(names)


def test_get_provider_returns_instance():
    p = get_provider("witanime")
    assert isinstance(p, BaseProvider)
    assert p.name == "witanime"


def test_get_provider_unknown_raises():
    with pytest.raises(KeyError, match="Unknown provider"):
        get_provider("__nonexistent__")


def test_register_custom_provider():
    register_provider(DummyProvider)
    assert "dummy_test_xyz" in list_providers()
    p = get_provider("dummy_test_xyz")
    assert isinstance(p, DummyProvider)


def test_register_provider_overwrite():
    """Re-registering under the same name should silently overwrite."""

    class DummyProvider2(BaseProvider):
        name = "dummy_test_xyz"

        def search(self, query):
            return [Anime(title="x", url="http://x.com")]

        def get_episodes(self, anime):
            return []

        def get_stream_url(self, episode):
            return "http://stream"

    register_provider(DummyProvider2)
    p = get_provider("dummy_test_xyz")
    assert isinstance(p, DummyProvider2)
