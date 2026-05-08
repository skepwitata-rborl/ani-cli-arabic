"""Tests for AnimeshareProvider."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from ani_cli_arabic.providers.animeshare import AnimeshareProvider
from ani_cli_arabic.providers.base import Anime, Episode

ANIME_HTML = """
<html><body>
  <div class="anime-card">
    <h3 class="anime-title"><a href="https://animeshare.net/anime/naruto">Naruto</a></h3>
    <img src="https://animeshare.net/thumb/naruto.jpg" />
  </div>
  <div class="anime-card">
    <h3 class="anime-title"><a href="https://animeshare.net/anime/bleach">Bleach</a></h3>
  </div>
</body></html>
"""

EPISODES_HTML = """
<html><body>
  <ul class="episodes-list">
    <li><a href="https://animeshare.net/ep/3">Episode 3</a></li>
    <li><a href="https://animeshare.net/ep/1">Episode 1</a></li>
    <li><a href="https://animeshare.net/ep/2">Episode 2</a></li>
  </ul>
</body></html>
"""

STREAM_IFRAME_HTML = """
<html><body>
  <div class="video-container">
    <iframe src="https://cdn.animeshare.net/embed/abc123"></iframe>
  </div>
</body></html>
"""

STREAM_SOURCE_HTML = """
<html><body>
  <div class="video-container">
    <video><source src="https://cdn.animeshare.net/video/ep1.mp4" /></video>
  </div>
</body></html>
"""


@pytest.fixture
def provider() -> AnimeshareProvider:
    return AnimeshareProvider()


def _mock_response(html: str) -> MagicMock:
    mock = MagicMock()
    mock.text = html
    mock.raise_for_status = MagicMock()
    return mock


def test_search_returns_anime_list(provider):
    with patch("ani_cli_arabic.providers.animeshare.requests.get") as mock_get:
        mock_get.return_value = _mock_response(ANIME_HTML)
        results = provider.search("naruto")
    assert len(results) == 2
    assert all(isinstance(a, Anime) for a in results)
    assert results[0].title == "Naruto"
    assert results[0].url == "https://animeshare.net/anime/naruto"
    assert results[0].thumbnail == "https://animeshare.net/thumb/naruto.jpg"


def test_search_returns_empty_on_no_results(provider):
    with patch("ani_cli_arabic.providers.animeshare.requests.get") as mock_get:
        mock_get.return_value = _mock_response("<html><body></body></html>")
        results = provider.search("xyznonexistent")
    assert results == []


def test_get_episodes_sorted(provider):
    anime = Anime(title="Naruto", url="https://animeshare.net/anime/naruto")
    with patch("ani_cli_arabic.providers.animeshare.requests.get") as mock_get:
        mock_get.return_value = _mock_response(EPISODES_HTML)
        episodes = provider.get_episodes(anime)
    assert len(episodes) == 3
    assert [e.number for e in episodes] == [1.0, 2.0, 3.0]


def test_get_stream_url_from_iframe(provider):
    episode = Episode(title="Episode 1", url="https://animeshare.net/ep/1", number=1)
    with patch("ani_cli_arabic.providers.animeshare.requests.get") as mock_get:
        mock_get.return_value = _mock_response(STREAM_IFRAME_HTML)
        url = provider.get_stream_url(episode)
    assert url == "https://cdn.animeshare.net/embed/abc123"


def test_get_stream_url_from_source_tag(provider):
    episode = Episode(title="Episode 1", url="https://animeshare.net/ep/1", number=1)
    with patch("ani_cli_arabic.providers.animeshare.requests.get") as mock_get:
        mock_get.return_value = _mock_response(STREAM_SOURCE_HTML)
        url = provider.get_stream_url(episode)
    assert url == "https://cdn.animeshare.net/video/ep1.mp4"


def test_get_stream_url_raises_on_missing(provider):
    episode = Episode(title="Episode 1", url="https://animeshare.net/ep/1", number=1)
    with patch("ani_cli_arabic.providers.animeshare.requests.get") as mock_get:
        mock_get.return_value = _mock_response("<html><body></body></html>")
        with pytest.raises(ValueError):
            provider.get_stream_url(episode)
