"""Tests for AnimeblkomProvider."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from ani_cli_arabic.providers.animeblkom import AnimeblkomProvider
from ani_cli_arabic.providers.base import Anime, Episode


@pytest.fixture()
def provider() -> AnimeblkomProvider:
    return AnimeblkomProvider()


def _mock_response(html: str) -> MagicMock:
    mock = MagicMock()
    mock.text = html
    mock.raise_for_status = MagicMock()
    return mock


SEARCH_HTML = """
<html><body>
  <div class="anime-card">
    <a href="https://animeblkom.net/anime/naruto">
      <span class="anime-title">Naruto</span>
    </a>
  </div>
  <div class="anime-card">
    <a href="https://animeblkom.net/anime/bleach">
      <span class="anime-title">Bleach</span>
    </a>
  </div>
</body></html>
"""

EPISODES_HTML = """
<html><body>
  <ul class="episodes-list">
    <li><a href="https://animeblkom.net/watch/naruto-episode-2">Ep 2</a></li>
    <li><a href="https://animeblkom.net/watch/naruto-episode-1">Ep 1</a></li>
  </ul>
</body></html>
"""

STREAM_IFRAME_HTML = """
<html><body>
  <div class="video-container">
    <iframe src="https://player.example.com/embed/abc123"></iframe>
  </div>
</body></html>
"""

STREAM_SOURCE_HTML = """
<html><body>
  <video><source src="https://cdn.example.com/video.mp4" /></video>
</body></html>
"""


def test_search_returns_anime_list(provider: AnimeblkomProvider) -> None:
    with patch("ani_cli_arabic.providers.animeblkom.requests.get") as mock_get:
        mock_get.return_value = _mock_response(SEARCH_HTML)
        results = provider.search("naruto")
    assert len(results) == 2
    assert all(isinstance(r, Anime) for r in results)
    assert results[0].title == "Naruto"
    assert results[1].title == "Bleach"


def test_search_returns_empty_on_no_results(provider: AnimeblkomProvider) -> None:
    with patch("ani_cli_arabic.providers.animeblkom.requests.get") as mock_get:
        mock_get.return_value = _mock_response("<html><body></body></html>")
        results = provider.search("zzznomatch")
    assert results == []


def test_get_episodes_sorted(provider: AnimeblkomProvider) -> None:
    anime = Anime(title="Naruto", url="https://animeblkom.net/anime/naruto")
    with patch("ani_cli_arabic.providers.animeblkom.requests.get") as mock_get:
        mock_get.return_value = _mock_response(EPISODES_HTML)
        episodes = provider.get_episodes(anime)
    assert len(episodes) == 2
    assert episodes[0].number == 1
    assert episodes[1].number == 2


def test_get_stream_url_from_iframe(provider: AnimeblkomProvider) -> None:
    ep = Episode(number=1, url="https://animeblkom.net/watch/naruto-episode-1")
    with patch("ani_cli_arabic.providers.animeblkom.requests.get") as mock_get:
        mock_get.return_value = _mock_response(STREAM_IFRAME_HTML)
        url = provider.get_stream_url(ep)
    assert url == "https://player.example.com/embed/abc123"


def test_get_stream_url_from_source_tag(provider: AnimeblkomProvider) -> None:
    ep = Episode(number=1, url="https://animeblkom.net/watch/naruto-episode-1")
    with patch("ani_cli_arabic.providers.animeblkom.requests.get") as mock_get:
        mock_get.return_value = _mock_response(STREAM_SOURCE_HTML)
        url = provider.get_stream_url(ep)
    assert url == "https://cdn.example.com/video.mp4"


def test_get_stream_url_raises_when_not_found(provider: AnimeblkomProvider) -> None:
    ep = Episode(number=1, url="https://animeblkom.net/watch/naruto-episode-1")
    with patch("ani_cli_arabic.providers.animeblkom.requests.get") as mock_get:
        mock_get.return_value = _mock_response("<html><body></body></html>")
        with pytest.raises(ValueError, match="No stream URL found"):
            provider.get_stream_url(ep)
