import pytest
from unittest.mock import MagicMock, patch

from ani_cli_arabic.providers.animelek import AnimelekProvider
from ani_cli_arabic.providers.base import Anime, Episode


@pytest.fixture
def provider():
    return AnimelekProvider()


def _mock_response(html: str) -> MagicMock:
    mock = MagicMock()
    mock.text = html
    mock.raise_for_status = MagicMock()
    return mock


SEARCH_HTML = """
<html><body>
  <div class="anime-card-container">
    <div class="anime-card-title"><a href="https://animelek.me/naruto/">Naruto</a></div>
  </div>
  <div class="anime-card-container">
    <div class="anime-card-title"><a href="https://animelek.me/naruto-shippuden/">Naruto Shippuden</a></div>
  </div>
</body></html>
"""


def test_search_returns_anime_list(provider):
    with patch("requests.get", return_value=_mock_response(SEARCH_HTML)):
        results = provider.search("naruto")
    assert len(results) == 2
    assert all(isinstance(a, Anime) for a in results)
    assert results[0].title == "Naruto"
    assert results[1].title == "Naruto Shippuden"


def test_search_returns_empty_on_no_results(provider):
    with patch("requests.get", return_value=_mock_response("<html></html>")):
        results = provider.search("xyznotfound")
    assert results == []


EPISODES_HTML = """
<html><body>
  <div class="episodes-list-content">
    <a href="https://animelek.me/naruto/episode-3/">الحلقة 3</a>
    <a href="https://animelek.me/naruto/episode-1/">الحلقة 1</a>
    <a href="https://animelek.me/naruto/episode-2/">الحلقة 2</a>
  </div>
</body></html>
"""


def test_get_episodes_sorted(provider):
    anime = Anime(title="Naruto", url="https://animelek.me/naruto/")
    with patch("requests.get", return_value=_mock_response(EPISODES_HTML)):
        episodes = provider.get_episodes(anime)
    assert [e.number for e in episodes] == [1, 2, 3]


def test_get_episodes_empty(provider):
    anime = Anime(title="Naruto", url="https://animelek.me/naruto/")
    with patch("requests.get", return_value=_mock_response("<html></html>")):
        episodes = provider.get_episodes(anime)
    assert episodes == []


STREAM_HTML_IFRAME = """
<html><body>
  <div class="watch-anime-area">
    <iframe src="https://stream.example.com/embed/abc123"></iframe>
  </div>
</body></html>
"""


def test_get_stream_url_from_iframe(provider):
    episode = Episode(number=1, url="https://animelek.me/naruto/episode-1/")
    with patch("requests.get", return_value=_mock_response(STREAM_HTML_IFRAME)):
        url = provider.get_stream_url(episode)
    assert url == "https://stream.example.com/embed/abc123"


STREAM_HTML_VIDEO = """
<html><body>
  <video><source src="https://cdn.example.com/video.mp4"></video>
</body></html>
"""


def test_get_stream_url_from_video_tag(provider):
    episode = Episode(number=1, url="https://animelek.me/naruto/episode-1/")
    with patch("requests.get", return_value=_mock_response(STREAM_HTML_VIDEO)):
        url = provider.get_stream_url(episode)
    assert url == "https://cdn.example.com/video.mp4"
