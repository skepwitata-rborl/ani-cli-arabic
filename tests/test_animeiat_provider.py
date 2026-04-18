"""Tests for the Animeiat provider."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from ani_cli_arabic.providers.animeiat import AnimeiatProvider
from ani_cli_arabic.providers.base import Anime, Episode

SEARCH_HTML = """
<html><body>
  <div class="anime-card">
    <a href="https://animeiat.tv/anime/naruto"><div class="anime-title">ناروتو</div></a>
  </div>
</body></html>
"""

EPISODES_HTML = """
<html><body>
  <div class="episode-item"><a href="https://animeiat.tv/ep/1">الحلقة 1</a></div>
  <div class="episode-item"><a href="https://animeiat.tv/ep/2">الحلقة 2</a></div>
</body></html>
"""

STREAM_HTML = """
<html><body>
  <iframe src="https://stream.example.com/embed/abc"></iframe>
</body></html>
"""


@pytest.fixture
def provider() -> AnimeiatProvider:
    return AnimeiatProvider()


def _mock_response(text: str) -> MagicMock:
    resp = MagicMock()
    resp.text = text
    resp.raise_for_status = MagicMock()
    return resp


@patch("ani_cli_arabic.providers.animeiat.requests.get")
def test_search_returns_anime_list(mock_get, provider):
    mock_get.return_value = _mock_response(SEARCH_HTML)
    results = provider.search("naruto")
    assert len(results) == 1
    assert results[0].title == "ناروتو"
    assert results[0].url == "https://animeiat.tv/anime/naruto"
    assert results[0].provider == "animeiat"


@patch("ani_cli_arabic.providers.animeiat.requests.get")
def test_get_episodes_sorted(mock_get, provider):
    mock_get.return_value = _mock_response(EPISODES_HTML)
    anime = Anime(title="ناروتو", url="https://animeiat.tv/anime/naruto", provider="animeiat")
    episodes = provider.get_episodes(anime)
    assert len(episodes) == 2
    assert episodes[0].number == 1
    assert episodes[1].number == 2


@patch("ani_cli_arabic.providers.animeiat.requests.get")
def test_get_stream_url_from_iframe(mock_get, provider):
    mock_get.return_value = _mock_response(STREAM_HTML)
    ep = Episode(title="الحلقة 1", url="https://animeiat.tv/ep/1", number=1)
    url = provider.get_stream_url(ep)
    assert url == "https://stream.example.com/embed/abc"


@patch("ani_cli_arabic.providers.animeiat.requests.get")
def test_get_stream_url_raises_when_no_source(mock_get, provider):
    mock_get.return_value = _mock_response("<html></html>")
    ep = Episode(title="الحلقة 1", url="https://animeiat.tv/ep/1", number=1)
    with pytest.raises(ValueError, match="No stream URL found"):
        provider.get_stream_url(ep)
