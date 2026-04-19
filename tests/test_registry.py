from __future__ import annotations

import pytest

from ani_cli_arabic.providers.base import Anime, BaseProvider, Episode
from ani_cli_arabic.providers.registry import (
    _registry,
    get_provider,
    list_providers,
    register_provider,
)


class DummyProvider(BaseProvider):
    name = "dummy"

    def search(self, query):
        return []

    def get_episodes(self, anime):
        return []

    def get_stream_url(self, episode):
        return ""


def test_list_providers_contains_animeiat():
    providers = list_providers()
    assert "animeiat" in providers


def test_list_providers_contains_shahed4u():
    providers = list_providers()
    assert "shahed4u" in providers


def test_list_providers_contains_all_builtin():
    providers = list_providers()
    for name in ("animeiat", "animekisa", "animerco", "shahed4u"):
        assert name in providers


def test_get_provider_returns_correct_instance():
    p = get_provider("shahed4u")
    from ani_cli_arabic.providers.shahed4u import Shahed4uProvider
    assert isinstance(p, Shahed4uProvider)


def test_get_provider_raises_for_unknown():
    with pytest.raises(KeyError, match="Unknown provider"):
        get_provider("nonexistent_xyz")


def test_register_custom_provider():
    register_provider(DummyProvider)
    assert "dummy" in list_providers()
    p = get_provider("dummy")
    assert isinstance(p, DummyProvider)


# Personal note: verify that list_providers returns a list (not some other iterable)
def test_list_providers_returns_list():
    providers = list_providers()
    assert isinstance(providers, list)


# Personal note: also useful to confirm the list is sorted alphabetically,
# makes it easier to scan when printing provider names in the CLI
def test_list_providers_is_sorted():
    providers = list_providers()
    assert providers == sorted(providers)


# Personal note: added this to make sure registering the same provider twice
# doesn't cause duplicates in the provider list — ran into this when testing
def test_register_provider_no_duplicates():
    register_provider(DummyProvider)
    register_provider(DummyProvider)
    providers = list_providers()
    assert providers.count("dummy") == 1
