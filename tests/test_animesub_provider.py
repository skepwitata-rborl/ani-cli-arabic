"""Tests for AnimesubProvider."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from ani_cli_arabic.providers.animesub import AnimesubProvider
from ani_cli_arabic.providers.base import Anime, Episode


@pytest.fixture()
def provider() -> AnimesubProvider:
    return AnimesubProvider()


def _mock_response(text: str, status_code: int = 200) -> MagicMock:
    mock = MagicMock()
    mock.status_code = status_code
    mock.text = text
    mock.raise_for_status = MagicMock()
    return mock


SEARCH_HTML = """
<html><body>
  <article class="anime-card">
    <h3 class="entry-title"><a href="https://animesub.info/naruto">Naruto</a></h3>
  </article>
  <article class="anime-card">
    <h3 class="entry-title"><a href="https://animesub.info/naruto-shippuden">Naruto Shippuden</a></h3>
  </article>
</body></html>
"""

EPISODES_HTML = """
<html><body>
  <div class="episodes-list">
    <a href="https://animesub.info/naruto-ep-2">Episode 2</a>
    <a href="https://animesub.info/naruto-ep-1">Episode 1</a>
    <a href="https://animesub.info/naruto-ep-3">Episode 3</a>
  </div>
</body></html>
"""

STREAM_IFRAME_HTML = """
<html><body>
  <iframe src="https://stream.animesub.info/embed/abc123"></iframe>
</body></html>
"""

STREAM_VIDEO_HTML = """
<html><body>
  <video><source src="https://cdn.animesub.info/video/ep1.mp4"></video>
</body></html>
"""


def test_search_returns_anime_list(provider: AnimesubProvider) -> None:
    with patch("requests.get", return_value=_mock_response(SEARCH_HTML)):
        results = provider.search("naruto")
    assert len(results) == 2
    assert all(isinstance(a, Anime) for a in results)
    assert results[0].title == "Naruto"
    assert results[1].title == "Naruto Shippuden"


def test_search_returns_empty_on_no_results(provider: AnimesubProvider) -> None:
    with patch("requests.get", return_value=_mock_response("<html></html>")):
        results = provider.search("xyznotexist")
    assert results == []


def test_search_returns_empty_on_exception(provider: AnimesubProvider) -> None:
    with patch("requests.get", side_effect=Exception("network error")):
        results = provider.search("naruto")
    assert results == []


def test_get_episodes_sorted(provider: AnimesubProvider) -> None:
    anime = Anime(title="Naruto", url="https://animesub.info/naruto")
    with patch("requests.get", return_value=_mock_response(EPISODES_HTML)):
        episodes = provider.get_episodes(anime)
    assert len(episodes) == 3
    assert all(isinstance(e, Episode) for e in episodes)
    numbers = [e.number for e in episodes]
    assert numbers == sorted(numbers)


def test_get_stream_url_from_iframe(provider: AnimesubProvider) -> None:
    episode = Episode(title="Episode 1", url="https://animesub.info/naruto-ep-1", number=1)
    with patch("requests.get", return_value=_mock_response(STREAM_IFRAME_HTML)):
        url = provider.get_stream_url(episode)
    assert url == "https://stream.animesub.info/embed/abc123"


def test_get_stream_url_from_video_source(provider: AnimesubProvider) -> None:
    episode = Episode(title="Episode 1", url="https://animesub.info/naruto-ep-1", number=1)
    with patch("requests.get", return_value=_mock_response(STREAM_VIDEO_HTML)):
        url = provider.get_stream_url(episode)
    assert url == "https://cdn.animesub.info/video/ep1.mp4"


def test_get_stream_url_returns_empty_on_exception(provider: AnimesubProvider) -> None:
    episode = Episode(title="Episode 1", url="https://animesub.info/naruto-ep-1", number=1)
    with patch("requests.get", side_effect=Exception("timeout")):
        url = provider.get_stream_url(episode)
    assert url == ""
