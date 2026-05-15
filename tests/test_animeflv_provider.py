"""Unit tests for AnimeflvProvider."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from ani_cli_arabic.providers.animeflv import AnimeflvProvider
from ani_cli_arabic.providers.base import Anime, Episode


@pytest.fixture()
def provider() -> AnimeflvProvider:
    return AnimeflvProvider()


def _mock_response(text: str, status: int = 200) -> MagicMock:
    mock = MagicMock()
    mock.status_code = status
    mock.text = text
    mock.raise_for_status = MagicMock()
    return mock


SEARCH_HTML = """
<ul class="ListAnimes">
  <li>
    <article>
      <div class="Description">
        <a class="Button" href="/anime/naruto">Ver</a>
      </div>
      <h3 class="Title">Naruto</h3>
    </article>
  </li>
</ul>
"""

EPISODE_HTML = """
<ul id="episodeList">
  <li><a href="/ver/naruto-1"><p>Episodio 1</p></a></li>
  <li><a href="/ver/naruto-3"><p>Episodio 3</p></a></li>
  <li><a href="/ver/naruto-2"><p>Episodio 2</p></a></li>
</ul>
"""

STREAM_HTML = """
<div id="PlayerDisplay">
  <iframe src="//embed.example.com/abc123"></iframe>
</div>
"""


@patch("ani_cli_arabic.providers.animeflv.requests.get")
def test_search_returns_anime_list(mock_get, provider):
    mock_get.return_value = _mock_response(SEARCH_HTML)
    results = provider.search("naruto")
    assert len(results) == 1
    assert isinstance(results[0], Anime)
    assert results[0].title == "Naruto"
    assert "animeflv" in results[0].url or "naruto" in results[0].url


@patch("ani_cli_arabic.providers.animeflv.requests.get")
def test_search_returns_empty_on_no_results(mock_get, provider):
    mock_get.return_value = _mock_response("<ul class='ListAnimes'></ul>")
    assert provider.search("zzz") == []


@patch("ani_cli_arabic.providers.animeflv.requests.get")
def test_get_episodes_sorted(mock_get, provider):
    mock_get.return_value = _mock_response(EPISODE_HTML)
    anime = Anime(title="Naruto", url="https://www3.animeflv.net/anime/naruto")
    episodes = provider.get_episodes(anime)
    assert len(episodes) == 3
    assert [e.number for e in episodes] == [1, 2, 3]


@patch("ani_cli_arabic.providers.animeflv.requests.get")
def test_get_episodes_empty(mock_get, provider):
    mock_get.return_value = _mock_response("<ul id='episodeList'></ul>")
    anime = Anime(title="X", url="https://www3.animeflv.net/anime/x")
    assert provider.get_episodes(anime) == []


@patch("ani_cli_arabic.providers.animeflv.requests.get")
def test_get_stream_url_from_iframe(mock_get, provider):
    mock_get.return_value = _mock_response(STREAM_HTML)
    ep = Episode(number=1, url="https://www3.animeflv.net/ver/naruto-1")
    url = provider.get_stream_url(ep)
    assert url.startswith("https://")
    assert "embed.example.com" in url


@patch("ani_cli_arabic.providers.animeflv.requests.get")
def test_get_stream_url_empty_when_no_iframe(mock_get, provider):
    mock_get.return_value = _mock_response("<html></html>")
    ep = Episode(number=1, url="https://www3.animeflv.net/ver/naruto-1")
    assert provider.get_stream_url(ep) == ""
