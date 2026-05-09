from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from ani_cli_arabic.providers.animekhor import AnimekhorProvider
from ani_cli_arabic.providers.base import Anime, Episode


@pytest.fixture
def provider() -> AnimekhorProvider:
    return AnimekhorProvider()


def _mock_response(html: str) -> MagicMock:
    mock = MagicMock()
    mock.text = html
    mock.raise_for_status = MagicMock()
    return mock


SEARCH_HTML = """
<html><body>
  <div class="result-item">
    <article>
      <div class="title"><a href="https://animekhor.xyz/anime/naruto/">Naruto</a></div>
    </article>
  </div>
  <div class="result-item">
    <article>
      <div class="title"><a href="https://animekhor.xyz/anime/bleach/">Bleach</a></div>
    </article>
  </div>
</body></html>
"""

EPISODES_HTML = """
<html><body>
  <div id="episodes">
    <ul>
      <li><a href="https://animekhor.xyz/ep/naruto-3/">Episode 3</a></li>
      <li><a href="https://animekhor.xyz/ep/naruto-1/">Episode 1</a></li>
      <li><a href="https://animekhor.xyz/ep/naruto-2/">Episode 2</a></li>
    </ul>
  </div>
</body></html>
"""

STREAM_IFRAME_HTML = """
<html><body>
  <div class="play-box-inner">
    <iframe src="https://player.example.com/embed/abc123"></iframe>
  </div>
</body></html>
"""

STREAM_SOURCE_HTML = """
<html><body>
  <video><source src="https://cdn.example.com/video.mp4" /></video>
</body></html>
"""


def test_search_returns_anime_list(provider: AnimekhorProvider) -> None:
    with patch("requests.get", return_value=_mock_response(SEARCH_HTML)):
        results = provider.search("naruto")
    assert len(results) == 2
    assert all(isinstance(a, Anime) for a in results)
    assert results[0].title == "Naruto"
    assert results[1].title == "Bleach"


def test_search_returns_empty_on_no_results(provider: AnimekhorProvider) -> None:
    empty_html = "<html><body></body></html>"
    with patch("requests.get", return_value=_mock_response(empty_html)):
        results = provider.search("xyznonexistent")
    assert results == []


def test_get_episodes_sorted(provider: AnimekhorProvider) -> None:
    anime = Anime(title="Naruto", url="https://animekhor.xyz/anime/naruto/")
    with patch("requests.get", return_value=_mock_response(EPISODES_HTML)):
        episodes = provider.get_episodes(anime)
    assert len(episodes) == 3
    numbers = [e.number for e in episodes]
    assert numbers == sorted(numbers)


def test_get_stream_url_from_iframe(provider: AnimekhorProvider) -> None:
    episode = Episode(title="Episode 1", url="https://animekhor.xyz/ep/naruto-1/", number=1)
    with patch("requests.get", return_value=_mock_response(STREAM_IFRAME_HTML)):
        url = provider.get_stream_url(episode)
    assert url == "https://player.example.com/embed/abc123"


def test_get_stream_url_from_source(provider: AnimekhorProvider) -> None:
    episode = Episode(title="Episode 1", url="https://animekhor.xyz/ep/naruto-1/", number=1)
    with patch("requests.get", return_value=_mock_response(STREAM_SOURCE_HTML)):
        url = provider.get_stream_url(episode)
    assert url == "https://cdn.example.com/video.mp4"


def test_get_stream_url_raises_when_not_found(provider: AnimekhorProvider) -> None:
    episode = Episode(title="Episode 1", url="https://animekhor.xyz/ep/naruto-1/", number=1)
    with patch("requests.get", return_value=_mock_response("<html></html>")):
        with pytest.raises(ValueError, match="Could not extract stream URL"):
            provider.get_stream_url(episode)
