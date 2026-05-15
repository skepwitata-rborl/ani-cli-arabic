"""Tests for AnimeitaliaProvider."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from ani_cli_arabic.providers.animeitalia import AnimeitaliaProvider
from ani_cli_arabic.providers.base import Anime, Episode


@pytest.fixture()
def provider() -> AnimeitaliaProvider:
    return AnimeitaliaProvider()


def _mock_response(text: str) -> MagicMock:
    mock = MagicMock()
    mock.text = text
    mock.raise_for_status = MagicMock()
    return mock


SEARCH_HTML = """
<html><body>
  <article class="animeit">
    <h2 class="entry-title"><a href="https://animeitalia.tv/naruto/">Naruto</a></h2>
  </article>
  <article class="animeit">
    <h2 class="entry-title"><a href="https://animeitalia.tv/bleach/">Bleach</a></h2>
  </article>
</body></html>
"""

EPISODES_HTML = """
<html><body>
  <div class="episodi-lista">
    <a href="https://animeitalia.tv/naruto-ep-2/">Episodio 2</a>
    <a href="https://animeitalia.tv/naruto-ep-1/">Episodio 1</a>
  </div>
</body></html>
"""

STREAM_HTML = """
<html><body>
  <div class="video-player">
    <iframe src="https://stream.example.com/embed/abc"></iframe>
  </div>
</body></html>
"""

NO_RESULTS_HTML = "<html><body></body></html>"


def test_search_returns_anime_list(provider: AnimeitaliaProvider) -> None:
    with patch("requests.get", return_value=_mock_response(SEARCH_HTML)):
        results = provider.search("naruto")
    assert len(results) == 2
    assert all(isinstance(a, Anime) for a in results)
    assert results[0].title == "Naruto"
    assert results[1].title == "Bleach"


def test_search_returns_empty_on_no_results(provider: AnimeitaliaProvider) -> None:
    with patch("requests.get", return_value=_mock_response(NO_RESULTS_HTML)):
        results = provider.search("xyznotfound")
    assert results == []


def test_get_episodes_sorted(provider: AnimeitaliaProvider) -> None:
    anime = Anime(title="Naruto", url="https://animeitalia.tv/naruto/")
    with patch("requests.get", return_value=_mock_response(EPISODES_HTML)):
        episodes = provider.get_episodes(anime)
    assert len(episodes) == 2
    assert episodes[0].number == 1
    assert episodes[1].number == 2


def test_get_episodes_empty(provider: AnimeitaliaProvider) -> None:
    anime = Anime(title="Ghost", url="https://animeitalia.tv/ghost/")
    with patch("requests.get", return_value=_mock_response(NO_RESULTS_HTML)):
        episodes = provider.get_episodes(anime)
    assert episodes == []


def test_get_stream_url_from_iframe(provider: AnimeitaliaProvider) -> None:
    episode = Episode(number=1, url="https://animeitalia.tv/naruto-ep-1/", title="Ep 1")
    with patch("requests.get", return_value=_mock_response(STREAM_HTML)):
        url = provider.get_stream_url(episode)
    assert url == "https://stream.example.com/embed/abc"


def test_get_stream_url_raises_when_no_iframe(provider: AnimeitaliaProvider) -> None:
    episode = Episode(number=1, url="https://animeitalia.tv/naruto-ep-1/", title="Ep 1")
    with patch("requests.get", return_value=_mock_response(NO_RESULTS_HTML)):
        with pytest.raises(ValueError):
            provider.get_stream_url(episode)
