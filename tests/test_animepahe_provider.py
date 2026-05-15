from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from ani_cli_arabic.providers.animepahe import AnimepaheProvider
from ani_cli_arabic.providers.base import Anime, Episode


@pytest.fixture
def provider() -> AnimepaheProvider:
    return AnimepaheProvider()


def _mock_response(json_data=None, text="", status_code=200):
    mock = MagicMock()
    mock.status_code = status_code
    mock.text = text
    mock.json.return_value = json_data or {}
    mock.raise_for_status = MagicMock()
    return mock


def test_search_returns_anime_list(provider):
    fake_data = {
        "data": [
            {"session": "naruto-abc123", "title": "Naruto"},
            {"session": "naruto-shippuden-xyz", "title": "Naruto Shippuden"},
        ]
    }
    with patch("requests.get", return_value=_mock_response(json_data=fake_data)):
        results = provider.search("naruto")

    assert len(results) == 2
    assert all(isinstance(a, Anime) for a in results)
    assert results[0].title == "Naruto"
    assert "naruto-abc123" in results[0].url


def test_search_returns_empty_on_no_results(provider):
    with patch("requests.get", return_value=_mock_response(json_data={"data": []})):
        results = provider.search("xyznotfound")
    assert results == []


def test_search_returns_empty_on_exception(provider):
    with patch("requests.get", side_effect=Exception("network error")):
        results = provider.search("naruto")
    assert results == []


def test_get_episodes_sorted(provider):
    anime = Anime(title="Naruto", url="https://animepahe.ru/anime/naruto-abc123")
    page1 = {
        "data": [
            {"episode": 2, "session": "sess2"},
            {"episode": 1, "session": "sess1"},
        ],
        "last_page": 1,
    }
    with patch("requests.get", return_value=_mock_response(json_data=page1)):
        episodes = provider.get_episodes(anime)

    assert len(episodes) == 2
    assert episodes[0].number == 1
    assert episodes[1].number == 2
    assert all(isinstance(e, Episode) for e in episodes)


def test_get_episodes_empty_on_exception(provider):
    anime = Anime(title="Naruto", url="https://animepahe.ru/anime/naruto-abc123")
    with patch("requests.get", side_effect=Exception("timeout")):
        episodes = provider.get_episodes(anime)
    assert episodes == []


def test_get_stream_url_from_source(provider):
    episode = Episode(number=1, url="https://animepahe.ru/play/naruto-abc123/sess1")
    html = '<html><body><source src="https://cdn.example.com/video.mp4"></body></html>'
    with patch("requests.get", return_value=_mock_response(text=html)):
        url = provider.get_stream_url(episode)
    assert url == "https://cdn.example.com/video.mp4"


def test_get_stream_url_returns_empty_on_exception(provider):
    episode = Episode(number=1, url="https://animepahe.ru/play/naruto-abc123/sess1")
    with patch("requests.get", side_effect=Exception("error")):
        url = provider.get_stream_url(episode)
    assert url == ""
