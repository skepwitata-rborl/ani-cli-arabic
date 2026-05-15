"""Unit tests for AnimenanaProvider."""
from __future__ import annotations

import pytest
from unittest.mock import MagicMock, patch

from ani_cli_arabic.providers.animenana import AnimenanaProvider
from ani_cli_arabic.providers.base import Anime, Episode


@pytest.fixture()
def provider() -> AnimenanaProvider:
    return AnimenanaProvider()


def _mock_response(text: str) -> MagicMock:
    mock = MagicMock()
    mock.text = text
    mock.raise_for_status = MagicMock()
    return mock


# ---------------------------------------------------------------------------
# search
# ---------------------------------------------------------------------------

def test_search_returns_anime_list(provider: AnimenanaProvider) -> None:
    html = """
    <div class="anime-card">
      <h3 class="anime-title"><a href="https://animenana.com/anime/naruto">Naruto</a></h3>
    </div>
    <div class="anime-card">
      <h3 class="anime-title"><a href="https://animenana.com/anime/bleach">Bleach</a></h3>
    </div>
    """
    with patch("ani_cli_arabic.providers.animenana.requests.get", return_value=_mock_response(html)):
        results = provider.search("naruto")
    assert len(results) == 2
    assert all(isinstance(a, Anime) for a in results)
    assert results[0].title == "Naruto"
    assert results[1].title == "Bleach"


def test_search_returns_empty_on_no_results(provider: AnimenanaProvider) -> None:
    html = "<div class=\"no-results\">لا نتائج</div>"
    with patch("ani_cli_arabic.providers.animenana.requests.get", return_value=_mock_response(html)):
        results = provider.search("xyznonexistent")
    assert results == []


# ---------------------------------------------------------------------------
# get_episodes
# ---------------------------------------------------------------------------

def test_get_episodes_sorted(provider: AnimenanaProvider) -> None:
    html = """
    <ul class="episodes-list">
      <li><a href="/ep/3">الحلقة 3</a></li>
      <li><a href="/ep/1">الحلقة 1</a></li>
      <li><a href="/ep/2">الحلقة 2</a></li>
    </ul>
    """
    anime = Anime(title="Test", url="https://animenana.com/anime/test")
    with patch("ani_cli_arabic.providers.animenana.requests.get", return_value=_mock_response(html)):
        episodes = provider.get_episodes(anime)
    assert [e.number for e in episodes] == [1.0, 2.0, 3.0]


def test_get_episodes_empty(provider: AnimenanaProvider) -> None:
    html = "<div class=\"no-eps\"></div>"
    anime = Anime(title="Test", url="https://animenana.com/anime/test")
    with patch("ani_cli_arabic.providers.animenana.requests.get", return_value=_mock_response(html)):
        episodes = provider.get_episodes(anime)
    assert episodes == []


# ---------------------------------------------------------------------------
# get_stream_url
# ---------------------------------------------------------------------------

def test_get_stream_url_from_iframe(provider: AnimenanaProvider) -> None:
    html = """
    <div class="player-container">
      <iframe src="https://stream.example.com/embed/abc123"></iframe>
    </div>
    """
    episode = Episode(title="Ep 1", url="https://animenana.com/ep/1", number=1.0)
    with patch("ani_cli_arabic.providers.animenana.requests.get", return_value=_mock_response(html)):
        url = provider.get_stream_url(episode)
    assert url == "https://stream.example.com/embed/abc123"


def test_get_stream_url_raises_when_no_source(provider: AnimenanaProvider) -> None:
    html = "<div class=\"player-container\"></div>"
    episode = Episode(title="Ep 1", url="https://animenana.com/ep/1", number=1.0)
    with patch("ani_cli_arabic.providers.animenana.requests.get", return_value=_mock_response(html)):
        with pytest.raises(ValueError):
            provider.get_stream_url(episode)
