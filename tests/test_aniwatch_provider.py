"""Tests for the AniWatch provider."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from ani_cli_arabic.providers.aniwatch import AniwatchProvider
from ani_cli_arabic.providers.base import Anime, Episode

_SEARCH_HTML = """
<html><body>
  <div class="flw-item">
    <h3 class="film-name"><a href="/watch/naruto-1">Naruto</a></h3>
  </div>
  <div class="flw-item">
    <h3 class="film-name"><a href="/watch/naruto-shippuden-2">Naruto Shippuden</a></h3>
  </div>
</body></html>
"""

_EPISODES_HTML = """
<html><body>
  <a class="ep-item" href="/watch/naruto-1?ep=3" data-number="3">Ep 3</a>
  <a class="ep-item" href="/watch/naruto-1?ep=1" data-number="1">Ep 1</a>
  <a class="ep-item" href="/watch/naruto-1?ep=2" data-number="2">Ep 2</a>
</body></html>
"""

_STREAM_HTML = """
<html><body>
  <iframe src="https://player.example.com/embed/abc123"></iframe>
</body></html>
"""


@pytest.fixture()
def provider() -> AniwatchProvider:
    return AniwatchProvider()


def _mock_response(text: str) -> MagicMock:
    mock = MagicMock()
    mock.text = text
    mock.raise_for_status = MagicMock()
    return mock


def test_search_returns_anime_list(provider: AniwatchProvider) -> None:
    with patch("ani_cli_arabic.providers.aniwatch.requests.get") as mock_get:
        mock_get.return_value = _mock_response(_SEARCH_HTML)
        results = provider.search("naruto")
    assert len(results) == 2
    assert all(isinstance(a, Anime) for a in results)
    assert results[0].title == "Naruto"
    assert results[0].url == "https://aniwatch.to/watch/naruto-1"


def test_search_returns_empty_on_no_results(provider: AniwatchProvider) -> None:
    with patch("ani_cli_arabic.providers.aniwatch.requests.get") as mock_get:
        mock_get.return_value = _mock_response("<html><body></body></html>")
        results = provider.search("xyznotfound")
    assert results == []


def test_get_episodes_sorted(provider: AniwatchProvider) -> None:
    anime = Anime(title="Naruto", url="https://aniwatch.to/watch/naruto-1")
    with patch("ani_cli_arabic.providers.aniwatch.requests.get") as mock_get:
        mock_get.return_value = _mock_response(_EPISODES_HTML)
        episodes = provider.get_episodes(anime)
    assert [e.number for e in episodes] == [1, 2, 3]


def test_get_episodes_empty(provider: AniwatchProvider) -> None:
    anime = Anime(title="Ghost", url="https://aniwatch.to/watch/ghost-99")
    with patch("ani_cli_arabic.providers.aniwatch.requests.get") as mock_get:
        mock_get.return_value = _mock_response("<html><body></body></html>")
        episodes = provider.get_episodes(anime)
    assert episodes == []


def test_get_stream_url_from_iframe(provider: AniwatchProvider) -> None:
    episode = Episode(number=1, url="https://aniwatch.to/watch/naruto-1?ep=1")
    with patch("ani_cli_arabic.providers.aniwatch.requests.get") as mock_get:
        mock_get.return_value = _mock_response(_STREAM_HTML)
        url = provider.get_stream_url(episode)
    assert url == "https://player.example.com/embed/abc123"


def test_provider_name(provider: AniwatchProvider) -> None:
    assert provider.name == "aniwatch"
