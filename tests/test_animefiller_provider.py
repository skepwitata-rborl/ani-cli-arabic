"""Tests for AnimefillerProvider."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from ani_cli_arabic.providers.animefiller import AnimefillerProvider
from ani_cli_arabic.providers.base import Anime, Episode


@pytest.fixture()
def provider() -> AnimefillerProvider:
    return AnimefillerProvider()


def _mock_response(text: str, status_code: int = 200) -> MagicMock:
    mock = MagicMock()
    mock.status_code = status_code
    mock.text = text
    mock.raise_for_status = MagicMock()
    return mock


_SHOWS_HTML = """
<html><body>
  <ul class="shows-wrapper">
    <li><a href="/shows/naruto">Naruto</a></li>
    <li><a href="/shows/bleach">Bleach</a></li>
  </ul>
</body></html>
"""

_EPISODES_HTML = """
<html><body>
  <table class="EpisodeList">
    <tr data-number="2"><td><a href="/shows/naruto/2">Ep 2</a></td></tr>
    <tr data-number="1"><td><a href="/shows/naruto/1">Ep 1</a></td></tr>
  </table>
</body></html>
"""

_STREAM_IFRAME_HTML = """
<html><body>
  <div class="video-content">
    <iframe src="https://stream.example.com/embed/abc"></iframe>
  </div>
</body></html>
"""

_STREAM_VIDEO_HTML = """
<html><body>
  <video><source src="https://cdn.example.com/video.mp4"></video>
</body></html>
"""


def test_search_returns_anime_list(provider: AnimefillerProvider) -> None:
    with patch("ani_cli_arabic.providers.animefiller.requests.get") as mock_get:
        mock_get.return_value = _mock_response(_SHOWS_HTML)
        results = provider.search("naruto")

    assert len(results) == 1
    assert isinstance(results[0], Anime)
    assert results[0].title == "Naruto"
    assert "naruto" in results[0].url


def test_search_returns_empty_on_no_match(provider: AnimefillerProvider) -> None:
    with patch("ani_cli_arabic.providers.animefiller.requests.get") as mock_get:
        mock_get.return_value = _mock_response(_SHOWS_HTML)
        results = provider.search("one piece")

    assert results == []


def test_get_episodes_sorted(provider: AnimefillerProvider) -> None:
    anime = Anime(title="Naruto", url="https://www.animefillerlist.com/shows/naruto")
    with patch("ani_cli_arabic.providers.animefiller.requests.get") as mock_get:
        mock_get.return_value = _mock_response(_EPISODES_HTML)
        episodes = provider.get_episodes(anime)

    assert len(episodes) == 2
    assert episodes[0].number == 1
    assert episodes[1].number == 2


def test_get_stream_url_from_iframe(provider: AnimefillerProvider) -> None:
    episode = Episode(number=1, url="https://www.animefillerlist.com/shows/naruto/1")
    with patch("ani_cli_arabic.providers.animefiller.requests.get") as mock_get:
        mock_get.return_value = _mock_response(_STREAM_IFRAME_HTML)
        url = provider.get_stream_url(episode)

    assert url == "https://stream.example.com/embed/abc"


def test_get_stream_url_from_video_tag(provider: AnimefillerProvider) -> None:
    episode = Episode(number=1, url="https://www.animefillerlist.com/shows/naruto/1")
    with patch("ani_cli_arabic.providers.animefiller.requests.get") as mock_get:
        mock_get.return_value = _mock_response(_STREAM_VIDEO_HTML)
        url = provider.get_stream_url(episode)

    assert url == "https://cdn.example.com/video.mp4"
