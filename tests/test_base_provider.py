"""Tests for the BaseProvider interface and related dataclasses."""

import pytest
from ani_cli_arabic.providers.base import Anime, BaseProvider, Episode


# ---------------------------------------------------------------------------
# Minimal concrete implementation used only in tests
# ---------------------------------------------------------------------------

class DummyProvider(BaseProvider):
    name = "dummy"
    base_url = "https://example.com"

    def search(self, query):
        return [
            Anime(
                id="1",
                title="Test Anime",
                title_ar="أنمي تجريبي",
                total_episodes=12,
                status="completed",
            )
        ]

    def get_episodes(self, anime):
        return [
            Episode(number=i, title=f"Episode {i}", url=f"{self.base_url}/ep/{i}")
            for i in range(1, anime.total_episodes + 1)
        ]

    def get_stream_url(self, episode):
        return f"{self.base_url}/stream/{episode.number}.m3u8"


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

@pytest.fixture
def provider():
    return DummyProvider()


def test_provider_name_and_url(provider):
    assert provider.name == "dummy"
    assert provider.base_url == "https://example.com"


def test_search_returns_anime_list(provider):
    results = provider.search("test")
    assert isinstance(results, list)
    assert len(results) == 1
    anime = results[0]
    assert anime.title == "Test Anime"
    assert anime.title_ar == "أنمي تجريبي"
    assert anime.status == "completed"


def test_get_episodes_count(provider):
    anime = provider.search("test")[0]
    episodes = provider.get_episodes(anime)
    assert len(episodes) == 12
    assert episodes[0].number == 1
    assert episodes[-1].number == 12


def test_get_stream_url(provider):
    anime = provider.search("test")[0]
    episodes = provider.get_episodes(anime)
    url = provider.get_stream_url(episodes[0])
    assert url.endswith(".m3u8")
    assert "stream/1" in url


def test_base_provider_is_abstract():
    with pytest.raises(TypeError):
        BaseProvider()  # type: ignore[abstract]


def test_episode_defaults():
    ep = Episode(number=1, title="Pilot", url="https://example.com/1")
    assert ep.stream_url is None


def test_anime_defaults():
    anime = Anime(id="x", title="Unnamed")
    assert anime.episodes == []
    assert anime.total_episodes == 0
    assert anime.status == "unknown"
