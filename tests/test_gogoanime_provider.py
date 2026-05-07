"""Tests for GogoanimeProvider."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from ani_cli_arabic.providers.base import Anime, Episode
from ani_cli_arabic.providers.gogoanime import GogoanimeProvider


@pytest.fixture()
def provider() -> GogoanimeProvider:
    return GogoanimeProvider()


def _mock_response(text: str, status_code: int = 200) -> MagicMock:
    mock = MagicMock()
    mock.status_code = status_code
    mock.text = text
    mock.raise_for_status = MagicMock()
    return mock


_SEARCH_HTML = """
<ul class="items">
  <li><p class="name"><a href="/category/naruto">Naruto</a></p></li>
  <li><p class="name"><a href="/category/bleach">Bleach</a></p></li>
</ul>
"""

_DETAIL_HTML = """
<ul id="episode_page">
  <li><a ep_start="1" ep_end="3"></a></li>
</ul>
"""

_EMBED_HTML_M3U8 = "file: 'https://cdn.example.com/stream.m3u8?token=abc'"
_EMBED_HTML_MP4 = "file: 'https://cdn.example.com/video.mp4'"
_IFRAME_HTML = """
<div class="play-video">
  <iframe src="//embed.example.com/v/abc123"></iframe>
</div>
"""


@patch("ani_cli_arabic.providers.gogoanime.requests.get")
def test_search_returns_anime_list(mock_get, provider):
    mock_get.return_value = _mock_response(_SEARCH_HTML)
    results = provider.search("naruto")
    assert len(results) == 2
    assert results[0].title == "Naruto"
    assert results[0].url == "https://gogoanime3.co/category/naruto"


@patch("ani_cli_arabic.providers.gogoanime.requests.get")
def test_search_returns_empty_on_no_results(mock_get, provider):
    mock_get.return_value = _mock_response("<ul class='items'></ul>")
    results = provider.search("xyzzy")
    assert results == []


@patch("ani_cli_arabic.providers.gogoanime.requests.get")
def test_get_episodes_sorted(mock_get, provider):
    mock_get.return_value = _mock_response(_DETAIL_HTML)
    anime = Anime(title="Naruto", url="https://gogoanime3.co/category/naruto")
    episodes = provider.get_episodes(anime)
    assert len(episodes) == 3
    numbers = [e.number for e in episodes]
    assert numbers == sorted(numbers)


@patch("ani_cli_arabic.providers.gogoanime.requests.get")
def test_get_stream_url_m3u8(mock_get, provider):
    mock_get.side_effect = [
        _mock_response(_IFRAME_HTML),
        _mock_response(_EMBED_HTML_M3U8),
    ]
    ep = Episode(number=1, url="https://gogoanime3.co/naruto-episode-1")
    url = provider.get_stream_url(ep)
    assert url.endswith(".m3u8?token=abc")


@patch("ani_cli_arabic.providers.gogoanime.requests.get")
def test_get_stream_url_mp4_fallback(mock_get, provider):
    mock_get.side_effect = [
        _mock_response(_IFRAME_HTML),
        _mock_response(_EMBED_HTML_MP4),
    ]
    ep = Episode(number=1, url="https://gogoanime3.co/naruto-episode-1")
    url = provider.get_stream_url(ep)
    assert url.endswith(".mp4")


@patch("ani_cli_arabic.providers.gogoanime.requests.get")
def test_get_stream_url_raises_when_no_iframe(mock_get, provider):
    mock_get.return_value = _mock_response("<div></div>")
    ep = Episode(number=1, url="https://gogoanime3.co/naruto-episode-1")
    with pytest.raises(ValueError, match="No iframe found"):
        provider.get_stream_url(ep)
