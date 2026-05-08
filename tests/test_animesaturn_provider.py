"""Tests for the AnimeSaturn provider."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from ani_cli_arabic.providers.animesaturn import AnimeSaturnProvider
from ani_cli_arabic.providers.base import Anime, Episode


@pytest.fixture()
def provider() -> AnimeSaturnProvider:
    return AnimeSaturnProvider()


def _mock_response(html: str) -> MagicMock:
    mock = MagicMock()
    mock.text = html
    mock.raise_for_status = MagicMock()
    return mock


# ---------------------------------------------------------------------------
# search
# ---------------------------------------------------------------------------

SEARCH_HTML = """
<ul class="list-group">
  <a class="list-group-item" href="https://www.animesaturn.cx/anime/naruto">Naruto</a>
  <a class="list-group-item" href="https://www.animesaturn.cx/anime/bleach">Bleach</a>
</ul>
"""


def test_search_returns_anime_list(provider):
    with patch("ani_cli_arabic.providers.animesaturn.requests.get") as mock_get:
        mock_get.return_value = _mock_response(SEARCH_HTML)
        results = provider.search("naruto")
    assert len(results) == 2
    assert all(isinstance(a, Anime) for a in results)
    assert results[0].title == "Naruto"
    assert "naruto" in results[0].url


def test_search_returns_empty_on_no_results(provider):
    with patch("ani_cli_arabic.providers.animesaturn.requests.get") as mock_get:
        mock_get.return_value = _mock_response("<html></html>")
        results = provider.search("zzznomatch")
    assert results == []


# ---------------------------------------------------------------------------
# get_episodes
# ---------------------------------------------------------------------------

EPISODES_HTML = """
<div class="tab-content">
  <a class="btn-episode" href="https://www.animesaturn.cx/ep/naruto-3">Episodio 3</a>
  <a class="btn-episode" href="https://www.animesaturn.cx/ep/naruto-1">Episodio 1</a>
  <a class="btn-episode" href="https://www.animesaturn.cx/ep/naruto-2">Episodio 2</a>
</div>
"""


def test_get_episodes_sorted(provider):
    anime = Anime(title="Naruto", url="https://www.animesaturn.cx/anime/naruto")
    with patch("ani_cli_arabic.providers.animesaturn.requests.get") as mock_get:
        mock_get.return_value = _mock_response(EPISODES_HTML)
        episodes = provider.get_episodes(anime)
    assert [e.number for e in episodes] == [1.0, 2.0, 3.0]


def test_get_episodes_empty(provider):
    anime = Anime(title="Unknown", url="https://www.animesaturn.cx/anime/unknown")
    with patch("ani_cli_arabic.providers.animesaturn.requests.get") as mock_get:
        mock_get.return_value = _mock_response("<html></html>")
        episodes = provider.get_episodes(anime)
    assert episodes == []


# ---------------------------------------------------------------------------
# get_stream_url
# ---------------------------------------------------------------------------

STREAM_VIDEO_HTML = """
<video><source src="https://cdn.animesaturn.cx/video.mp4" type="video/mp4"></video>
"""

STREAM_IFRAME_HTML = """
<iframe src="https://embed.example.com/player?id=abc"></iframe>
"""


def test_get_stream_url_from_video_source(provider):
    ep = Episode(number=1, url="https://www.animesaturn.cx/ep/naruto-1")
    with patch("ani_cli_arabic.providers.animesaturn.requests.get") as mock_get:
        mock_get.return_value = _mock_response(STREAM_VIDEO_HTML)
        url = provider.get_stream_url(ep)
    assert url == "https://cdn.animesaturn.cx/video.mp4"


def test_get_stream_url_from_iframe(provider):
    ep = Episode(number=1, url="https://www.animesaturn.cx/ep/naruto-1")
    with patch("ani_cli_arabic.providers.animesaturn.requests.get") as mock_get:
        mock_get.return_value = _mock_response(STREAM_IFRAME_HTML)
        url = provider.get_stream_url(ep)
    assert "embed.example.com" in url


def test_get_stream_url_raises_when_no_stream(provider):
    ep = Episode(number=1, url="https://www.animesaturn.cx/ep/naruto-1")
    with patch("ani_cli_arabic.providers.animesaturn.requests.get") as mock_get:
        mock_get.return_value = _mock_response("<html></html>")
        with pytest.raises(ValueError, match="No stream found"):
            provider.get_stream_url(ep)
