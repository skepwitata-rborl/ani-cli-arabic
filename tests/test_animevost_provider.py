"""Unit tests for AnimevostProvider."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from ani_cli_arabic.providers.animevost import AnimevostProvider
from ani_cli_arabic.providers.base import Anime, Episode


@pytest.fixture()
def provider() -> AnimevostProvider:
    return AnimevostProvider()


def _mock_response(text: str, status: int = 200) -> MagicMock:
    mock = MagicMock()
    mock.status_code = status
    mock.text = text
    mock.raise_for_status = MagicMock()
    return mock


SEARCH_HTML = """
<html><body>
  <div class="shortstory">
    <h2 class="zagolovok"><a href="/anime/123-test-anime.html">Test Anime</a></h2>
  </div>
  <div class="shortstory">
    <h2 class="zagolovok"><a href="https://animevost.org/anime/456-another.html">Another Anime</a></h2>
  </div>
</body></html>
"""

EPISODES_HTML = """
<html><body>
  <div class="epiList">
    <a href="/episode/2">Episode 2</a>
    <a href="/episode/1">Episode 1</a>
    <a href="/episode/3">Episode 3</a>
  </div>
</body></html>
"""

STREAM_HTML = """
<html><body>
  <iframe src="https://cdn.animevost.org/player/embed?id=99"></iframe>
</body></html>
"""


def test_search_returns_anime_list(provider):
    with patch("requests.get", return_value=_mock_response(SEARCH_HTML)):
        results = provider.search("test")
    assert len(results) == 2
    assert all(isinstance(a, Anime) for a in results)
    assert results[0].title == "Test Anime"
    assert results[0].url == "https://animevost.org/anime/123-test-anime.html"
    assert results[1].url == "https://animevost.org/anime/456-another.html"


def test_search_returns_empty_on_no_results(provider):
    with patch("requests.get", return_value=_mock_response("<html></html>")):
        results = provider.search("nothing")
    assert results == []


def test_search_returns_empty_on_exception(provider):
    with patch("requests.get", side_effect=Exception("network error")):
        results = provider.search("fail")
    assert results == []


def test_get_episodes_sorted(provider):
    anime = Anime(title="Test", url="https://animevost.org/anime/123.html")
    with patch("requests.get", return_value=_mock_response(EPISODES_HTML)):
        episodes = provider.get_episodes(anime)
    assert len(episodes) == 3
    assert all(isinstance(e, Episode) for e in episodes)
    assert episodes[0].number <= episodes[1].number <= episodes[2].number


def test_get_episodes_empty_on_exception(provider):
    anime = Anime(title="Test", url="https://animevost.org/anime/123.html")
    with patch("requests.get", side_effect=Exception("timeout")):
        episodes = provider.get_episodes(anime)
    assert episodes == []


def test_get_stream_url_from_iframe(provider):
    episode = Episode(title="Episode 1", url="https://animevost.org/episode/1", number=1)
    with patch("requests.get", return_value=_mock_response(STREAM_HTML)):
        url = provider.get_stream_url(episode)
    assert url == "https://cdn.animevost.org/player/embed?id=99"


def test_get_stream_url_returns_empty_when_no_iframe(provider):
    episode = Episode(title="Episode 1", url="https://animevost.org/episode/1", number=1)
    with patch("requests.get", return_value=_mock_response("<html></html>")):
        url = provider.get_stream_url(episode)
    assert url == ""
