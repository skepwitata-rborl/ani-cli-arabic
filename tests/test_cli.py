"""Tests for the CLI module (build_parser, pick, main)."""

import pytest
from unittest.mock import patch, MagicMock

from ani_cli_arabic.cli import build_parser, pick, main
from ani_cli_arabic.providers.base import Anime, Episode


# ---------------------------------------------------------------------------
# build_parser
# ---------------------------------------------------------------------------

class TestBuildParser:
    def test_returns_parser(self):
        parser = build_parser()
        assert parser is not None

    def test_default_provider(self):
        parser = build_parser()
        args = parser.parse_args(["naruto"])
        assert args.query == "naruto"

    def test_provider_flag(self):
        parser = build_parser()
        args = parser.parse_args(["-p", "animekisa", "naruto"])
        assert args.provider == "animekisa"

    def test_episode_flag(self):
        parser = build_parser()
        args = parser.parse_args(["-e", "3", "naruto"])
        assert args.episode == 3

    def test_list_providers_flag(self):
        parser = build_parser()
        args = parser.parse_args(["--list-providers"])
        assert args.list_providers is True

    def test_no_query_required_with_list_providers(self):
        """--list-providers should work without a query argument."""
        parser = build_parser()
        # Should not raise
        args = parser.parse_args(["--list-providers"])
        assert args.list_providers is True


# ---------------------------------------------------------------------------
# pick
# ---------------------------------------------------------------------------

class TestPick:
    def _make_anime(self, title: str) -> Anime:
        return Anime(title=title, url=f"https://example.com/{title}")

    def test_pick_single_item_returns_it(self):
        items = [self._make_anime("Naruto")]
        with patch("builtins.input", return_value="1"):
            result = pick(items, label="anime")
        assert result == items[0]

    def test_pick_multiple_items(self):
        items = [self._make_anime("Naruto"), self._make_anime("Bleach")]
        with patch("builtins.input", return_value="2"):
            result = pick(items, label="anime")
        assert result == items[1]

    def test_pick_invalid_then_valid(self):
        items = [self._make_anime("Naruto"), self._make_anime("Bleach")]
        with patch("builtins.input", side_effect=["99", "abc", "1"]):
            result = pick(items, label="anime")
        assert result == items[0]

    def test_pick_empty_list_raises(self):
        with pytest.raises((ValueError, SystemExit, IndexError)):
            pick([], label="anime")


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

class TestMain:
    def _make_anime(self):
        return Anime(title="Naruto", url="https://example.com/naruto")

    def _make_episode(self, num: int):
        return Episode(number=num, url=f"https://example.com/ep{num}")

    def test_list_providers_prints_and_exits(self, capsys):
        with patch(
            "ani_cli_arabic.cli.list_providers", return_value=["animeiat", "animekisa"]
        ):
            with pytest.raises(SystemExit) as exc_info:
                main(["--list-providers"])
        assert exc_info.value.code == 0
        captured = capsys.readouterr()
        assert "animeiat" in captured.out

    def test_main_no_results_exits(self):
        mock_provider = MagicMock()
        mock_provider.search.return_value = []

        with patch("ani_cli_arabic.cli.get_provider", return_value=mock_provider):
            with pytest.raises(SystemExit) as exc_info:
                main(["some query with no results"])
        assert exc_info.value.code != 0

    def test_main_plays_episode(self):
        anime = self._make_anime()
        episode = self._make_episode(1)

        mock_provider = MagicMock()
        mock_provider.search.return_value = [anime]
        mock_provider.get_episodes.return_value = [episode]
        mock_provider.get_stream_url.return_value = "https://stream.example.com/ep1.m3u8"

        with patch("ani_cli_arabic.cli.get_provider", return_value=mock_provider), \
             patch("ani_cli_arabic.cli.pick", side_effect=[anime, episode]), \
             patch("ani_cli_arabic.cli.play") as mock_play:
            main(["naruto"])

        mock_play.assert_called_once()

    def test_main_with_episode_flag_skips_episode_pick(self):
        anime = self._make_anime()
        ep1 = self._make_episode(1)
        ep2 = self._make_episode(2)

        mock_provider = MagicMock()
        mock_provider.search.return_value = [anime]
        mock_provider.get_episodes.return_value = [ep1, ep2]
        mock_provider.get_stream_url.return_value = "https://stream.example.com/ep2.m3u8"

        with patch("ani_cli_arabic.cli.get_provider", return_value=mock_provider), \
             patch("ani_cli_arabic.cli.pick", return_value=anime) as mock_pick, \
             patch("ani_cli_arabic.cli.play") as mock_play:
            main(["-e", "2", "naruto"])

        # pick should only be called once (for anime), not for episode
        mock_pick.assert_called_once()
        mock_play.assert_called_once()
