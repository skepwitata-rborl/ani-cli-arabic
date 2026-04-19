from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from ani_cli_arabic.providers.base import Anime, Episode
from ani_cli_arabic.providers.shahed4u import Shahed4uProvider


@pytest.fixture
def provider():
    return Shahed4uProvider()


def _mock_response(html: str) -> MagicMock:
    mock = MagicMock()
    mock.text = html
    mock.raise_for_status = MagicMock()
    return mock


SEARCH_HTML = """
<div class="result-item">
  <article>
    <div class="title"><a href="https://shahed4u.art/anime/naruto">Naruto</a></div>
    <img src="https://shahed4u.art/img/naruto.jpg" />
  </article>
</div>
"""

EPISODES_HTML = """
<div class="episodios">
  <ul>
    <li><a href="https://shahed4u.art/ep/2">Episode 2</a></li>
    <li><a href="https://shahed4u.art/ep/1">Episode 1</a></li>
  </ul>
</div>
"""

STREAM_HTML = '<div class="embed"><iframe src="https://stream.example.com/abc"></iframe></div>'

# Multiple iframes sometimes appear on the page; we expect the first one to be used
STREAM_HTML_MULTIPLE_IFRAMES = (
    '<div class="embed">'
    '<iframe src="https://stream.example.com/first"></iframe>'
    '<iframe src="https://stream.example.com/second"></iframe>'
    '</div>'
)


@patch("ani_cli_arabic.providers.shahed4u.requests.get")
def test_search_returns_anime_list(mock_get, provider):
    mock_get.return_value = _mock_response(SEARCH_HTML)
    results = provider.search("Naruto")
    assert len(results) == 1
    assert results[0].title == "Naruto"
    assert results[0].provider == "shahed4u"


@patch("ani_cli_arabic.providers.shahed4u.requests.get")
def test_search_returns_empty_on_no_results(mock_get, provider):
    mock_get.return_value = _mock_response("<html></html>")
    results = provider.search("unknown")
    assert results == []


@patch("ani_cli_arabic.providers.shahed4u.requests.get")
def test_get_episodes_sorted(mock_get, provider):
    mock_get.return_value = _mock_response(EPISODES_HTML)
    anime = Anime(title="Naruto", url="https://shahed4u.art/anime/naruto", image="", provider="shahed4u")
    episodes = provider.get_episodes(anime)
    assert len(episodes) == 2
    # Episodes should be sorted ascending so ep 1 comes before ep 2
    assert episodes[0].number == 1
    assert episodes[1].number == 2


@patch("ani_cli_arabic.providers.shahed4u.requests.get")
def test_get_stream_url_from_iframe(mock_get, provider):
    mock_get.return_value = _mock_response(STREAM_HTML)
    anime = Anime(title="Naruto", url="", image="", provider="shahed4u")
    ep = Episode(number=1, url="https://shahed4u.art/ep/1", anime=anime)
    url = provider.get_stream_url(ep)
    assert url == "https://stream.example.com/abc"


@patch("ani_cli_arabic.providers.shahed4u.requests.get")
def test_get_stream_url_uses_first_iframe_when_multiple(mock_get, provider):
    """When the page has multiple iframes, the first src should be returned."""
    mock_get.return_value = _mock_response(STREAM_HTML_MULTIPLE_IFRAMES)
    anime = Anime(title="Naruto", url="", image="", provider="shahed4u")
    ep = Episode(number=1, url="https://shahed4u.art/ep/1", anime=anime)
    url = provider.get_stream_url(ep)
    assert url == "https://stream.example.com/first"


@patch("ani_cli_arabic.providers.shahed4u.requests.get")
def test_get_stream_url_raises_when_no_iframe(mock_get, provider):
    mock_get.return_value = _mock_response("<html></html>")
    anime = Anime(title="Naruto", url="", image="", provider="shahed4u")
    ep = Episode(number=1, url="https://shahed4u.art/ep/1", anime=anime)
    # Expecting ValueError when no iframe/stream source is found in the page
    with pytest.raises(ValueError):
        provider.get_stream_url(ep)
