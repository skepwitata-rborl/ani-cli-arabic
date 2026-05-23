"""Unit tests for AnimekageProvider."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from ani_cli_arabic.providers.animekage import AnimekageProvider
from ani_cli_arabic.providers.base import Anime, Episode


@pytest.fixture()
def provider() -> AnimekageProvider:
    return AnimekageProvider()


def _mock_response(text: str, status: int = 200) -> MagicMock:
    mock = MagicMock()
    mock.status_code = status
    mock.text = text
    mock.raise_for_status = MagicMock()
    return mock


SEARCH_HTML = """
<html><body>
  <div class="anime-card">
    <h3 class="anime-title"><a href="https://www.animekage.net/anime/naruto">Naruto</a></h3>
  </div>
  <div class="anime-card">
    <h3 class="anime-title"><a href="https://www.animekage.net/anime/bleach">Bleach</a></h3>
  </div>
</body></html>
"""

EPISODES_HTML = """
<html><body>
  <div class="episodes-list">
    <a href="https://www.animekage.net/ep/1">Episode 1</a>
    <a href="https://www.animekage.net/ep/3">Episode 3</a>
    <a href="https://www.animekage.net/ep/2">Episode 2</a>
  </div>
</body></html>
"""

STREAM_IFRAME_HTML = """
<html><body>
  <div class="player-container">
    <iframe src="https://stream.example.com/embed/abc"></iframe>
  </div>
</body></html>
"""

STREAM_SOURCE_HTML = """
<html><body>
  <video><source src="https://cdn.example.com/video.mp4"></video>
</body></html>
"""


def test_search_returns_anime_list(provider):
    with patch("requests.get", return_value=_mock_response(SEARCH_HTML)):
        results = provider.search("naruto")
    assert len(results) == 2
    assert results[0].title == "Naruto"
    assert results[0].url == "https://www.animekage.net/anime/naruto"


def test_search_returns_empty_on_no_results(provider):
    with patch("requests.get", return_value=_mock_response("<html></html>")):
        results = provider.search("nonexistent")
    assert results == []


def test_search_returns_empty_on_exception(provider):
    import requests as req
    with patch("requests.get", side_effect=req.RequestException):
        results = provider.search("naruto")
    assert results == []


def test_get_episodes_sorted(provider):
    anime = Anime(title="Naruto", url="https://www.animekage.net/anime/naruto")
    with patch("requests.get", return_value=_mock_response(EPISODES_HTML)):
        episodes = provider.get_episodes(anime)
    assert [e.number for e in episodes] == [1, 2, 3]


def test_get_stream_url_from_iframe(provider):
    episode = Episode(number=1, url="https://www.animekage.net/ep/1")
    with patch("requests.get", return_value=_mock_response(STREAM_IFRAME_HTML)):
        url = provider.get_stream_url(episode)
    assert url == "https://stream.example.com/embed/abc"


def test_get_stream_url_from_source(provider):
    episode = Episode(number=1, url="https://www.animekage.net/ep/1")
    with patch("requests.get", return_value=_mock_response(STREAM_SOURCE_HTML)):
        url = provider.get_stream_url(episode)
    assert url == "https://cdn.example.com/video.mp4"


def test_get_stream_url_returns_empty_on_exception(provider):
    import requests as req
    episode = Episode(number=1, url="https://www.animekage.net/ep/1")
    with patch("requests.get", side_effect=req.RequestException):
        url = provider.get_stream_url(episode)
    assert url == ""
