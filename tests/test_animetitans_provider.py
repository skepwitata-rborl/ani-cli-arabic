from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from ani_cli_arabic.providers.animetitans import AnimetitansProvider
from ani_cli_arabic.providers.base import Anime, Episode


@pytest.fixture
def provider() -> AnimetitansProvider:
    return AnimetitansProvider()


def _mock_response(html: str) -> MagicMock:
    mock = MagicMock()
    mock.text = html
    mock.raise_for_status = MagicMock()
    return mock


SEARCH_HTML = """
<html><body>
  <div class="result-item">
    <article>
      <div class="image"><img src="https://example.com/thumb.jpg" /></div>
      <div class="details">
        <div class="title"><a href="https://www.animetitans.com/anime/naruto/">Naruto</a></div>
      </div>
    </article>
  </div>
</body></html>
"""

EPISODES_HTML = """
<html><body>
  <ul id="episodios">
    <li><div class="numerando">1 - 1</div><a href="https://www.animetitans.com/episode/naruto-ep-1/">Ep 1</a></li>
    <li><div class="numerando">1 - 3</div><a href="https://www.animetitans.com/episode/naruto-ep-3/">Ep 3</a></li>
    <li><div class="numerando">1 - 2</div><a href="https://www.animetitans.com/episode/naruto-ep-2/">Ep 2</a></li>
  </ul>
</body></html>
"""

STREAM_HTML = """
<html><body>
  <div class="embed-player">
    <iframe src="https://stream.example.com/embed/abc123"></iframe>
  </div>
</body></html>
"""


def test_search_returns_anime_list(provider: AnimetitansProvider) -> None:
    with patch("requests.get", return_value=_mock_response(SEARCH_HTML)):
        results = provider.search("naruto")
    assert len(results) == 1
    assert results[0].title == "Naruto"
    assert results[0].url == "https://www.animetitans.com/anime/naruto/"
    assert results[0].thumbnail == "https://example.com/thumb.jpg"


def test_search_returns_empty_on_no_results(provider: AnimetitansProvider) -> None:
    empty_html = "<html><body></body></html>"
    with patch("requests.get", return_value=_mock_response(empty_html)):
        results = provider.search("nonexistent")
    assert results == []


def test_get_episodes_sorted(provider: AnimetitansProvider) -> None:
    anime = Anime(title="Naruto", url="https://www.animetitans.com/anime/naruto/")
    with patch("requests.get", return_value=_mock_response(EPISODES_HTML)):
        episodes = provider.get_episodes(anime)
    assert len(episodes) == 3
    assert [e.number for e in episodes] == [1, 2, 3]


def test_get_episodes_empty(provider: AnimetitansProvider) -> None:
    anime = Anime(title="Ghost", url="https://www.animetitans.com/anime/ghost/")
    with patch("requests.get", return_value=_mock_response("<html><body></body></html>")):
        episodes = provider.get_episodes(anime)
    assert episodes == []


def test_get_stream_url_from_iframe(provider: AnimetitansProvider) -> None:
    episode = Episode(number=1, url="https://www.animetitans.com/episode/naruto-ep-1/")
    with patch("requests.get", return_value=_mock_response(STREAM_HTML)):
        url = provider.get_stream_url(episode)
    assert url == "https://stream.example.com/embed/abc123"


def test_get_stream_url_returns_empty_when_no_iframe(provider: AnimetitansProvider) -> None:
    episode = Episode(number=1, url="https://www.animetitans.com/episode/naruto-ep-1/")
    with patch("requests.get", return_value=_mock_response("<html><body></body></html>")):
        url = provider.get_stream_url(episode)
    assert url == ""
