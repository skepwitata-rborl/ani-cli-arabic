"""Tests for the AnimeTV provider."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from ani_cli_arabic.providers.animetv import AnimetvProvider
from ani_cli_arabic.providers.base import Anime, Episode


@pytest.fixture()
def provider() -> AnimetvProvider:
    return AnimetvProvider()


def _mock_response(text: str, status: int = 200) -> MagicMock:
    mock = MagicMock()
    mock.status_code = status
    mock.text = text
    mock.raise_for_status = MagicMock()
    return mock


SEARCH_HTML = """
<html><body>
  <div class="film-detail">
    <div class="film-name"><a href="/anime/naruto">Naruto</a></div>
  </div>
  <div class="film-detail">
    <div class="film-name"><a href="/anime/bleach">Bleach</a></div>
  </div>
</body></html>
"""


def test_search_returns_anime_list(provider: AnimetvProvider) -> None:
    with patch("requests.get", return_value=_mock_response(SEARCH_HTML)):
        results = provider.search("naruto")
    assert len(results) == 2
    assert isinstance(results[0], Anime)
    assert results[0].title == "Naruto"
    assert results[0].url == "https://animetv.to/anime/naruto"


def test_search_returns_empty_on_no_results(provider: AnimetvProvider) -> None:
    with patch("requests.get", return_value=_mock_response("<html></html>")):
        results = provider.search("xyzzy")
    assert results == []


def test_search_returns_empty_on_exception(provider: AnimetvProvider) -> None:
    import requests as req
    with patch("requests.get", side_effect=req.RequestException):
        results = provider.search("naruto")
    assert results == []


EPISODES_HTML = """
<html><body>
  <a class="ssl-item ep-item" data-number="3" href="/watch/naruto-ep-3">Ep 3</a>
  <a class="ssl-item ep-item" data-number="1" href="/watch/naruto-ep-1">Ep 1</a>
  <a class="ssl-item ep-item" data-number="2" href="/watch/naruto-ep-2">Ep 2</a>
</body></html>
"""


def test_get_episodes_sorted(provider: AnimetvProvider) -> None:
    anime = Anime(title="Naruto", url="https://animetv.to/anime/naruto")
    with patch("requests.get", return_value=_mock_response(EPISODES_HTML)):
        episodes = provider.get_episodes(anime)
    assert [e.number for e in episodes] == [1.0, 2.0, 3.0]


def test_get_episodes_empty_on_exception(provider: AnimetvProvider) -> None:
    import requests as req
    anime = Anime(title="Naruto", url="https://animetv.to/anime/naruto")
    with patch("requests.get", side_effect=req.RequestException):
        episodes = provider.get_episodes(anime)
    assert episodes == []


STREAM_HTML_IFRAME = """
<html><body><iframe src="https://stream.example.com/embed/abc"></iframe></body></html>
"""

STREAM_HTML_SOURCE = """
<html><body><source src="https://cdn.example.com/video.mp4"></body></html>
"""


def test_get_stream_url_from_iframe(provider: AnimetvProvider) -> None:
    episode = Episode(number=1, url="https://animetv.to/watch/naruto-ep-1")
    with patch("requests.get", return_value=_mock_response(STREAM_HTML_IFRAME)):
        url = provider.get_stream_url(episode)
    assert url == "https://stream.example.com/embed/abc"


def test_get_stream_url_from_source(provider: AnimetvProvider) -> None:
    episode = Episode(number=1, url="https://animetv.to/watch/naruto-ep-1")
    with patch("requests.get", return_value=_mock_response(STREAM_HTML_SOURCE)):
        url = provider.get_stream_url(episode)
    assert url == "https://cdn.example.com/video.mp4"


def test_get_stream_url_empty_on_exception(provider: AnimetvProvider) -> None:
    import requests as req
    episode = Episode(number=1, url="https://animetv.to/watch/naruto-ep-1")
    with patch("requests.get", side_effect=req.RequestException):
        url = provider.get_stream_url(episode)
    assert url == ""
