from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from ani_cli_arabic.providers.animeworld import AnimeworldProvider
from ani_cli_arabic.providers.base import Anime, Episode


@pytest.fixture
def provider():
    return AnimeworldProvider()


def _mock_response(html: str) -> MagicMock:
    mock = MagicMock()
    mock.text = html
    mock.raise_for_status = MagicMock()
    return mock


SEARCH_HTML = """
<html><body>
  <div class="film-list">
    <div class="item"><a class="name" href="/anime/naruto">Naruto</a></div>
    <div class="item"><a class="name" href="/anime/bleach">Bleach</a></div>
  </div>
</body></html>
"""

EPISODES_HTML = """
<html><body>
  <ul class="episodes">
    <li><a href="/anime/naruto/ep-3">Episodio 3</a></li>
    <li><a href="/anime/naruto/ep-1">Episodio 1</a></li>
    <li><a href="/anime/naruto/ep-2">Episodio 2</a></li>
  </ul>
</body></html>
"""

STREAM_HTML_VIDEO = """
<html><body>
  <video><source src="https://cdn.example.com/video.mp4" type="video/mp4"></video>
</body></html>
"""

STREAM_HTML_IFRAME = """
<html><body>
  <div id="player-embed"><iframe src="https://stream.example.com/embed/abc"></iframe></div>
</body></html>
"""


def test_search_returns_anime_list(provider):
    with patch("requests.get", return_value=_mock_response(SEARCH_HTML)):
        results = provider.search("naruto")
    assert len(results) == 2
    assert all(isinstance(a, Anime) for a in results)
    assert results[0].title == "Naruto"
    assert results[0].url == "https://www.animeworld.ac/anime/naruto"


def test_search_returns_empty_on_no_results(provider):
    empty_html = "<html><body><div class=\"film-list\"></div></body></html>"
    with patch("requests.get", return_value=_mock_response(empty_html)):
        results = provider.search("xyznotfound")
    assert results == []


def test_get_episodes_sorted(provider):
    anime = Anime(title="Naruto", url="https://www.animeworld.ac/anime/naruto")
    with patch("requests.get", return_value=_mock_response(EPISODES_HTML)):
        episodes = provider.get_episodes(anime)
    assert len(episodes) == 3
    assert [e.number for e in episodes] == [1, 2, 3]


def test_get_episodes_empty(provider):
    anime = Anime(title="Unknown", url="https://www.animeworld.ac/anime/unknown")
    empty_html = "<html><body><ul class=\"episodes\"></ul></body></html>"
    with patch("requests.get", return_value=_mock_response(empty_html)):
        episodes = provider.get_episodes(anime)
    assert episodes == []


def test_get_stream_url_from_video_source(provider):
    episode = Episode(number=1, url="https://www.animeworld.ac/anime/naruto/ep-1")
    with patch("requests.get", return_value=_mock_response(STREAM_HTML_VIDEO)):
        url = provider.get_stream_url(episode)
    assert url == "https://cdn.example.com/video.mp4"


def test_get_stream_url_from_iframe(provider):
    episode = Episode(number=1, url="https://www.animeworld.ac/anime/naruto/ep-1")
    with patch("requests.get", return_value=_mock_response(STREAM_HTML_IFRAME)):
        url = provider.get_stream_url(episode)
    assert url == "https://stream.example.com/embed/abc"


def test_get_stream_url_raises_when_no_source(provider):
    episode = Episode(number=1, url="https://www.animeworld.ac/anime/naruto/ep-1")
    empty_html = "<html><body><div id=\"player-embed\"></div></body></html>"
    with patch("requests.get", return_value=_mock_response(empty_html)):
        with pytest.raises(ValueError, match="Could not extract stream URL"):
            provider.get_stream_url(episode)
