from unittest.mock import MagicMock, patch

import pytest

from ani_cli_arabic.providers.animerco import AnimercoProvider
from ani_cli_arabic.providers.base import Anime, Episode


@pytest.fixture
def provider():
    return AnimercoProvider()


def _mock_response(html: str):
    mock = MagicMock()
    mock.text = html
    mock.raise_for_status = MagicMock()
    return mock


def test_search_returns_anime_list(provider):
    html = """
    <div class="anime-card">
      <h3 class="anime-title"><a href="https://animerco.org/anime/naruto">Naruto</a></h3>
      <img src="https://example.com/naruto.jpg" />
    </div>
    """
    with patch("requests.get", return_value=_mock_response(html)):
        results = provider.search("naruto")
    assert len(results) == 1
    assert results[0].title == "Naruto"
    assert results[0].url == "https://animerco.org/anime/naruto"
    assert results[0].thumbnail == "https://example.com/naruto.jpg"


def test_search_returns_empty_on_no_results(provider):
    with patch("requests.get", return_value=_mock_response("<html></html>")):
        results = provider.search("nonexistent")
    assert results == []


def test_get_episodes_sorted(provider):
    html = """
    <div class="episodes-list">
      <a href="https://animerco.org/ep/3">Episode 3</a>
      <a href="https://animerco.org/ep/1">Episode 1</a>
      <a href="https://animerco.org/ep/2">Episode 2</a>
    </div>
    """
    anime = Anime(title="Naruto", url="https://animerco.org/anime/naruto")
    with patch("requests.get", return_value=_mock_response(html)):
        episodes = provider.get_episodes(anime)
    # Episodes should always come back in ascending order regardless of page order
    assert [e.number for e in episodes] == [1, 2, 3]


def test_get_stream_url_from_iframe(provider):
    html = '<iframe src="https://stream.example.com/embed/abc"></iframe>'
    episode = Episode(title="Episode 1", url="https://animerco.org/ep/1", number=1)
    with patch("requests.get", return_value=_mock_response(html)):
        url = provider.get_stream_url(episode)
    assert url == "https://stream.example.com/embed/abc"


def test_get_stream_url_raises_when_no_iframe(provider):
    # This should raise ValueError, not return None or an empty string
    episode = Episode(title="Episode 1", url="https://animerco.org/ep/1", number=1)
    with patch("requests.get", return_value=_mock_response("<html></html>")):
        with pytest.raises(ValueError):
            provider.get_stream_url(episode)
