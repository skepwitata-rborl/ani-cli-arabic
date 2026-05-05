"""Tests for the Witanime provider."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from ani_cli_arabic.providers.base import Anime, Episode
from ani_cli_arabic.providers.witanime import WitanimeProvider


@pytest.fixture()
def provider() -> WitanimeProvider:
    return WitanimeProvider()


def _mock_response(text: str, status: int = 200) -> MagicMock:
    mock = MagicMock()
    mock.status_code = status
    mock.text = text
    mock.raise_for_status = MagicMock()
    return mock


_SEARCH_HTML = """
<html><body>
  <div class="anime-card-container">
    <div class="anime-card-title"><h3><a href="https://witanime.cyou/anime/naruto/">ناروتو</a></h3></div>
    <img src="https://witanime.cyou/img/naruto.jpg" />
  </div>
  <div class="anime-card-container">
    <div class="anime-card-title"><h3><a href="https://witanime.cyou/anime/bleach/">بليتش</a></h3></div>
  </div>
</body></html>
"""

_EPISODES_HTML = """
<html><body>
  <div class="episodes-list-content">
    <a href="https://witanime.cyou/episode/naruto-2/">الحلقة 2</a>
    <a href="https://witanime.cyou/episode/naruto-1/">الحلقة 1</a>
    <a href="https://witanime.cyou/episode/naruto-3/">الحلقة 3</a>
  </div>
</body></html>
"""

_STREAM_HTML = """
<html><body>
  <iframe src="https://player.example.com/embed/abc123"></iframe>
</body></html>
"""


@patch("ani_cli_arabic.providers.witanime.requests.get")
def test_search_returns_anime_list(mock_get, provider):
    mock_get.return_value = _mock_response(_SEARCH_HTML)
    results = provider.search("ناروتو")
    assert len(results) == 2
    assert all(isinstance(a, Anime) for a in results)
    assert results[0].title == "ناروتو"
    assert results[0].url == "https://witanime.cyou/anime/naruto/"
    assert results[0].thumbnail == "https://witanime.cyou/img/naruto.jpg"


@patch("ani_cli_arabic.providers.witanime.requests.get")
def test_search_returns_empty_on_no_results(mock_get, provider):
    mock_get.return_value = _mock_response("<html><body></body></html>")
    assert provider.search("xyz") == []


@patch("ani_cli_arabic.providers.witanime.requests.get")
def test_get_episodes_sorted(mock_get, provider):
    mock_get.return_value = _mock_response(_EPISODES_HTML)
    anime = Anime(title="ناروتو", url="https://witanime.cyou/anime/naruto/")
    episodes = provider.get_episodes(anime)
    assert len(episodes) == 3
    assert [e.number for e in episodes] == [1.0, 2.0, 3.0]


@patch("ani_cli_arabic.providers.witanime.requests.get")
def test_get_episodes_empty(mock_get, provider):
    mock_get.return_value = _mock_response("<html><body></body></html>")
    anime = Anime(title="X", url="https://witanime.cyou/anime/x/")
    assert provider.get_episodes(anime) == []


@patch("ani_cli_arabic.providers.witanime.requests.get")
def test_get_stream_url_from_iframe(mock_get, provider):
    mock_get.return_value = _mock_response(_STREAM_HTML)
    ep = Episode(title="الحلقة 1", url="https://witanime.cyou/episode/naruto-1/", number=1)
    url = provider.get_stream_url(ep)
    assert url == "https://player.example.com/embed/abc123"


@patch("ani_cli_arabic.providers.witanime.requests.get")
def test_get_stream_url_raises_when_no_iframe(mock_get, provider):
    mock_get.return_value = _mock_response("<html><body><p>nothing</p></body></html>")
    ep = Episode(title="الحلقة 1", url="https://witanime.cyou/episode/naruto-1/", number=1)
    with pytest.raises(RuntimeError, match="No stream found"):
        provider.get_stream_url(ep)
