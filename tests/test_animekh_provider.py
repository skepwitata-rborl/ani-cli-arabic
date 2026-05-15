"""Unit tests for AnimekHProvider."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from ani_cli_arabic.providers.animekh import AnimekHProvider
from ani_cli_arabic.providers.base import Anime, Episode

_SEARCH_HTML = """
<html><body>
  <div class="post-thumbnail">
    <a href="https://animekh.com/anime/naruto/" title="Naruto">Naruto</a>
  </div>
  <div class="post-thumbnail">
    <a href="https://animekh.com/anime/bleach/" title="Bleach">Bleach</a>
  </div>
</body></html>
"""

_EPISODES_HTML = """
<html><body>
  <div class="episodelist">
    <a href="https://animekh.com/episode/naruto-3/">Episode 3</a>
    <a href="https://animekh.com/episode/naruto-1/">Episode 1</a>
    <a href="https://animekh.com/episode/naruto-2/">Episode 2</a>
  </div>
</body></html>
"""

_STREAM_HTML = """
<html><body>
  <div class="player-embed">
    <iframe src="https://vidstream.example.com/embed/abc123"></iframe>
  </div>
</body></html>
"""


@pytest.fixture
def provider() -> AnimekHProvider:
    return AnimekHProvider()


def _mock_response(html: str) -> MagicMock:
    mock = MagicMock()
    mock.text = html
    mock.raise_for_status = MagicMock()
    return mock


def test_search_returns_anime_list(provider: AnimekHProvider) -> None:
    with patch("ani_cli_arabic.providers.animekh.requests.get") as mock_get:
        mock_get.return_value = _mock_response(_SEARCH_HTML)
        results = provider.search("naruto")
    assert len(results) == 2
    assert all(isinstance(a, Anime) for a in results)
    assert results[0].title == "Naruto"
    assert results[1].title == "Bleach"


def test_search_returns_empty_on_no_results(provider: AnimekHProvider) -> None:
    with patch("ani_cli_arabic.providers.animekh.requests.get") as mock_get:
        mock_get.return_value = _mock_response("<html><body></body></html>")
        results = provider.search("xyzzy_nonexistent")
    assert results == []


def test_get_episodes_sorted(provider: AnimekHProvider) -> None:
    anime = Anime(title="Naruto", url="https://animekh.com/anime/naruto/")
    with patch("ani_cli_arabic.providers.animekh.requests.get") as mock_get:
        mock_get.return_value = _mock_response(_EPISODES_HTML)
        episodes = provider.get_episodes(anime)
    assert [e.number for e in episodes] == [1.0, 2.0, 3.0]


def test_get_episodes_empty(provider: AnimekHProvider) -> None:
    anime = Anime(title="Unknown", url="https://animekh.com/anime/unknown/")
    with patch("ani_cli_arabic.providers.animekh.requests.get") as mock_get:
        mock_get.return_value = _mock_response("<html><body></body></html>")
        episodes = provider.get_episodes(anime)
    assert episodes == []


def test_get_stream_url_from_iframe(provider: AnimekHProvider) -> None:
    episode = Episode(number=1.0, url="https://animekh.com/episode/naruto-1/")
    with patch("ani_cli_arabic.providers.animekh.requests.get") as mock_get:
        mock_get.return_value = _mock_response(_STREAM_HTML)
        url = provider.get_stream_url(episode)
    assert url == "https://vidstream.example.com/embed/abc123"


def test_get_stream_url_raises_when_no_iframe(provider: AnimekHProvider) -> None:
    episode = Episode(number=1.0, url="https://animekh.com/episode/naruto-1/")
    with patch("ani_cli_arabic.providers.animekh.requests.get") as mock_get:
        mock_get.return_value = _mock_response("<html><body></body></html>")
        with pytest.raises(ValueError):
            provider.get_stream_url(episode)
