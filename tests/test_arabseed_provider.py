"""Tests for the ArabSeed provider."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from ani_cli_arabic.providers.arabseed import ArabseedProvider
from ani_cli_arabic.providers.base import Anime, Episode


@pytest.fixture()
def provider() -> ArabseedProvider:
    return ArabseedProvider()


def _mock_response(html: str) -> MagicMock:
    mock = MagicMock()
    mock.text = html
    mock.raise_for_status = MagicMock()
    return mock


_SEARCH_HTML = """
<html><body>
  <ul class="Blocks-UL">
    <div class="BlockItem"><a href="https://arabseed.ink/naruto/" title="Naruto">Naruto</a></div>
    <div class="BlockItem"><a href="https://arabseed.ink/bleach/" title="Bleach">Bleach</a></div>
  </ul>
</body></html>
"""

_EPISODES_HTML = """
<html><body>
  <div class="List--Seasons--Episodes">
    <a href="https://arabseed.ink/naruto/ep3/">الحلقة 3</a>
    <a href="https://arabseed.ink/naruto/ep1/">الحلقة 1</a>
    <a href="https://arabseed.ink/naruto/ep2/">الحلقة 2</a>
  </div>
</body></html>
"""

_STREAM_IFRAME_HTML = """
<html><body><iframe src="https://stream.example.com/embed/abc"></iframe></body></html>
"""

_STREAM_SOURCE_HTML = """
<html><body><video><source src="https://cdn.example.com/video.mp4"></video></body></html>
"""


def test_search_returns_anime_list(provider: ArabseedProvider) -> None:
    with patch("ani_cli_arabic.providers.arabseed.requests.get") as mock_get:
        mock_get.return_value = _mock_response(_SEARCH_HTML)
        results = provider.search("naruto")
    assert len(results) == 2
    assert all(isinstance(a, Anime) for a in results)
    assert results[0].title == "Naruto"
    assert results[1].title == "Bleach"


def test_search_returns_empty_on_no_results(provider: ArabseedProvider) -> None:
    with patch("ani_cli_arabic.providers.arabseed.requests.get") as mock_get:
        mock_get.return_value = _mock_response("<html><body></body></html>")
        results = provider.search("xyznotfound")
    assert results == []


def test_get_episodes_sorted(provider: ArabseedProvider) -> None:
    anime = Anime(title="Naruto", url="https://arabseed.ink/naruto/")
    with patch("ani_cli_arabic.providers.arabseed.requests.get") as mock_get:
        mock_get.return_value = _mock_response(_EPISODES_HTML)
        episodes = provider.get_episodes(anime)
    assert [e.number for e in episodes] == [1, 2, 3]


def test_get_stream_url_from_iframe(provider: ArabseedProvider) -> None:
    episode = Episode(number=1, url="https://arabseed.ink/naruto/ep1/")
    with patch("ani_cli_arabic.providers.arabseed.requests.get") as mock_get:
        mock_get.return_value = _mock_response(_STREAM_IFRAME_HTML)
        url = provider.get_stream_url(episode)
    assert url == "https://stream.example.com/embed/abc"


def test_get_stream_url_from_source_fallback(provider: ArabseedProvider) -> None:
    episode = Episode(number=1, url="https://arabseed.ink/naruto/ep1/")
    with patch("ani_cli_arabic.providers.arabseed.requests.get") as mock_get:
        mock_get.return_value = _mock_response(_STREAM_SOURCE_HTML)
        url = provider.get_stream_url(episode)
    assert url == "https://cdn.example.com/video.mp4"


def test_get_stream_url_raises_when_not_found(provider: ArabseedProvider) -> None:
    episode = Episode(number=1, url="https://arabseed.ink/naruto/ep1/")
    with patch("ani_cli_arabic.providers.arabseed.requests.get") as mock_get:
        mock_get.return_value = _mock_response("<html><body></body></html>")
        with pytest.raises(ValueError, match="No stream URL found"):
            provider.get_stream_url(episode)
