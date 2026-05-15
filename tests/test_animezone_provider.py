"""Tests for AnimezoneProvider."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from ani_cli_arabic.providers.animezone import AnimezoneProvider
from ani_cli_arabic.providers.base import Anime, Episode


@pytest.fixture
def provider() -> AnimezoneProvider:
    return AnimezoneProvider()


def _mock_response(html: str) -> MagicMock:
    mock = MagicMock()
    mock.text = html
    mock.raise_for_status = MagicMock()
    return mock


SEARCH_HTML = """
<html><body>
  <div class="anime-card">
    <h3 class="anime-title"><a href="https://animezone.io/anime/naruto">Naruto</a></h3>
  </div>
  <div class="anime-card">
    <h3 class="anime-title"><a href="https://animezone.io/anime/bleach">Bleach</a></h3>
  </div>
</body></html>
"""

EPISODES_HTML = """
<html><body>
  <ul class="episodes-list">
    <li><a href="https://animezone.io/ep/3">Episode 3</a></li>
    <li><a href="https://animezone.io/ep/1">Episode 1</a></li>
    <li><a href="https://animezone.io/ep/2">Episode 2</a></li>
  </ul>
</body></html>
"""

STREAM_IFRAME_HTML = """
<html><body>
  <div class="player-container">
    <iframe src="https://stream.example.com/embed/abc123"></iframe>
  </div>
</body></html>
"""

STREAM_VIDEO_HTML = """
<html><body>
  <video><source src="https://cdn.example.com/video.mp4" /></video>
</body></html>
"""


def test_search_returns_anime_list(provider: AnimezoneProvider) -> None:
    with patch("requests.get", return_value=_mock_response(SEARCH_HTML)):
        results = provider.search("naruto")
    assert len(results) == 2
    assert all(isinstance(a, Anime) for a in results)
    assert results[0].title == "Naruto"
    assert results[1].title == "Bleach"


def test_search_returns_empty_on_no_results(provider: AnimezoneProvider) -> None:
    empty_html = "<html><body></body></html>"
    with patch("requests.get", return_value=_mock_response(empty_html)):
        results = provider.search("xyzzy")
    assert results == []


def test_get_episodes_sorted(provider: AnimezoneProvider) -> None:
    anime = Anime(title="Naruto", url="https://animezone.io/anime/naruto")
    with patch("requests.get", return_value=_mock_response(EPISODES_HTML)):
        episodes = provider.get_episodes(anime)
    assert [e.number for e in episodes] == [1, 2, 3]


def test_get_stream_url_from_iframe(provider: AnimezoneProvider) -> None:
    episode = Episode(number=1, url="https://animezone.io/ep/1", title="Episode 1")
    with patch("requests.get", return_value=_mock_response(STREAM_IFRAME_HTML)):
        url = provider.get_stream_url(episode)
    assert url == "https://stream.example.com/embed/abc123"


def test_get_stream_url_from_video_tag(provider: AnimezoneProvider) -> None:
    episode = Episode(number=1, url="https://animezone.io/ep/1", title="Episode 1")
    with patch("requests.get", return_value=_mock_response(STREAM_VIDEO_HTML)):
        url = provider.get_stream_url(episode)
    assert url == "https://cdn.example.com/video.mp4"


def test_get_stream_url_raises_when_not_found(provider: AnimezoneProvider) -> None:
    episode = Episode(number=1, url="https://animezone.io/ep/1", title="Episode 1")
    empty_html = "<html><body><div class=\"player-container\"></div></body></html>"
    with patch("requests.get", return_value=_mock_response(empty_html)):
        with pytest.raises(ValueError, match="Could not find stream URL"):
            provider.get_stream_url(episode)
