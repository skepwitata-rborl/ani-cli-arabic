from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from ani_cli_arabic.providers.animekisa import AnimekisaProvider
from ani_cli_arabic.providers.base import Anime, Episode


@pytest.fixture
def provider():
    return AnimekisaProvider()


SEARCH_HTML = """
<html><body>
  <div class="film-poster">
    <a href="/anime/naruto-1234"><span class="film-name">Naruto</span></a>
  </div>
  <div class="film-poster">
    <a href="/anime/bleach-5678"><span class="film-name">Bleach</span></a>
  </div>
</body></html>
"""

EPISODES_HTML = """
<html><body>
  <a class="ep-item" href="/watch/naruto-1234/episode-2">Episode 2</a>
  <a class="ep-item" href="/watch/naruto-1234/episode-1">Episode 1</a>
</body></html>
"""

STREAM_HTML = """
<html><body>
  <iframe src="https://streamserver.example.com/embed/abc123"></iframe>
</body></html>
"""

# HTML with multiple iframes - only the first should be used as the stream URL
MULTIPLE_IFRAMES_HTML = """
<html><body>
  <iframe src="https://streamserver.example.com/embed/abc123"></iframe>
  <iframe src="https://ads.example.com/banner"></iframe>
</body></html>
"""


def _mock_response(html: str) -> MagicMock:
    mock = MagicMock()
    mock.text = html
    mock.raise_for_status = MagicMock()
    return mock


def test_search_returns_anime_list(provider):
    with patch("requests.get", return_value=_mock_response(SEARCH_HTML)):
        results = provider.search("naruto")
    assert len(results) == 2
    assert results[0].title == "Naruto"
    assert results[0].id == "naruto-1234"
    assert results[1].title == "Bleach"


def test_get_episodes_sorted(provider):
    anime = Anime(id="naruto-1234", title="Naruto", url="https://animekisa.tv/anime/naruto-1234")
    with patch("requests.get", return_value=_mock_response(EPISODES_HTML)):
        episodes = provider.get_episodes(anime)
    assert len(episodes) == 2
    assert episodes[0].number == 1
    assert episodes[1].number == 2


def test_get_stream_url_from_iframe(provider):
    episode = Episode(number=1, title="Episode 1", url="https://animekisa.tv/watch/naruto-1234/episode-1")
    with patch("requests.get", return_value=_mock_response(STREAM_HTML)):
        url = provider.get_stream_url(episode)
    assert url == "https://streamserver.example.com/embed/abc123"


def test_get_stream_url_returns_first_iframe_when_multiple(provider):
    # Ensure only the first iframe src is returned, not subsequent ones (e.g. ads)
    episode = Episode(number=1, title="Episode 1", url="https://animekisa.tv/watch/naruto-1234/episode-1")
    with patch("requests.get", return_value=_mock_response(MULTIPLE_IFRAMES_HTML)):
        url = provider.get_stream_url(episode)
    assert url == "https://streamserver.example.com/embed/abc123"


def test_get_stream_url_raises_when_no_iframe(provider):
    episode = Episode(number=1, title="Episode 1", url="https://animekisa.tv/watch/naruto-1234/episode-1")
    with patch("requests.get", return_value=_mock_response("<html><body></body></html>")):
        with pytest.raises(ValueError, match="No stream URL found"):
            provider.get_stream_url(episode)
