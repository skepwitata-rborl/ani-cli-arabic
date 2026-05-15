"""Tests for the AnimeDubbed provider."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from ani_cli_arabic.providers.animedubbed import AnimedubbedProvider
from ani_cli_arabic.providers.base import Anime, Episode


@pytest.fixture()
def provider() -> AnimedubbedProvider:
    return AnimedubbedProvider()


def _mock_response(text: str) -> MagicMock:
    resp = MagicMock()
    resp.text = text
    resp.raise_for_status = MagicMock()
    return resp


# ---------------------------------------------------------------------------
# search
# ---------------------------------------------------------------------------

def test_search_returns_anime_list(provider: AnimedubbedProvider) -> None:
    html = """
    <div class="film_list-wrap">
      <div class="flw-item">
        <h3 class="film-name"><a href="/anime/naruto">Naruto</a></h3>
      </div>
      <div class="flw-item">
        <h3 class="film-name"><a href="/anime/bleach">Bleach</a></h3>
      </div>
    </div>
    """
    with patch("ani_cli_arabic.providers.animedubbed.requests.get",
               return_value=_mock_response(html)):
        results = provider.search("naruto")

    assert len(results) == 2
    assert all(isinstance(a, Anime) for a in results)
    assert results[0].title == "Naruto"
    assert results[0].url == "https://www.animedubbed.com/anime/naruto"


def test_search_returns_empty_on_no_results(provider: AnimedubbedProvider) -> None:
    html = "<div class=\"film_list-wrap\"></div>"
    with patch("ani_cli_arabic.providers.animedubbed.requests.get",
               return_value=_mock_response(html)):
        results = provider.search("zzznomatch")
    assert results == []


# ---------------------------------------------------------------------------
# get_episodes
# ---------------------------------------------------------------------------

def test_get_episodes_sorted(provider: AnimedubbedProvider) -> None:
    html = """
    <ul class="seasons-list">
      <li><a href="/ep/3">Episode 3</a></li>
      <li><a href="/ep/1">Episode 1</a></li>
      <li><a href="/ep/2">Episode 2</a></li>
    </ul>
    """
    anime = Anime(title="TestAnime", url="https://www.animedubbed.com/anime/test")
    with patch("ani_cli_arabic.providers.animedubbed.requests.get",
               return_value=_mock_response(html)):
        episodes = provider.get_episodes(anime)

    assert len(episodes) == 3
    assert [e.number for e in episodes] == [1.0, 2.0, 3.0]


def test_get_episodes_empty(provider: AnimedubbedProvider) -> None:
    html = "<ul class=\"seasons-list\"></ul>"
    anime = Anime(title="Empty", url="https://www.animedubbed.com/anime/empty")
    with patch("ani_cli_arabic.providers.animedubbed.requests.get",
               return_value=_mock_response(html)):
        episodes = provider.get_episodes(anime)
    assert episodes == []


# ---------------------------------------------------------------------------
# get_stream_url
# ---------------------------------------------------------------------------

def test_get_stream_url_from_video_source(provider: AnimedubbedProvider) -> None:
    html = "<video><source src=\"https://cdn.example.com/video.mp4\"></video>"
    episode = Episode(title="Ep 1", url="https://www.animedubbed.com/ep/1", number=1.0)
    with patch("ani_cli_arabic.providers.animedubbed.requests.get",
               return_value=_mock_response(html)):
        url = provider.get_stream_url(episode)
    assert url == "https://cdn.example.com/video.mp4"


def test_get_stream_url_falls_back_to_iframe(provider: AnimedubbedProvider) -> None:
    html = "<iframe src=\"https://player.example.com/embed/abc\"></iframe>"
    episode = Episode(title="Ep 2", url="https://www.animedubbed.com/ep/2", number=2.0)
    with patch("ani_cli_arabic.providers.animedubbed.requests.get",
               return_value=_mock_response(html)):
        url = provider.get_stream_url(episode)
    assert url == "https://player.example.com/embed/abc"


def test_get_stream_url_raises_when_none_found(provider: AnimedubbedProvider) -> None:
    html = "<div>no player here</div>"
    episode = Episode(title="Ep 3", url="https://www.animedubbed.com/ep/3", number=3.0)
    with patch("ani_cli_arabic.providers.animedubbed.requests.get",
               return_value=_mock_response(html)):
        with pytest.raises(ValueError, match="No stream URL found"):
            provider.get_stream_url(episode)
