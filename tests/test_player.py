"""Tests for the player module (detect_player, _build_command, play)."""

import subprocess
from unittest.mock import MagicMock, patch

import pytest

from ani_cli_arabic.player import PlayerOptions, detect_player, _build_command, play


# ---------------------------------------------------------------------------
# detect_player
# ---------------------------------------------------------------------------

class TestDetectPlayer:
    """Tests for auto-detection of available media players."""

    def test_returns_mpv_when_mpv_found(self):
        """detect_player should return 'mpv' when mpv is on PATH."""
        with patch("shutil.which", side_effect=lambda x: "/usr/bin/mpv" if x == "mpv" else None):
            assert detect_player() == "mpv"

    def test_returns_vlc_when_only_vlc_found(self):
        """detect_player should fall back to 'vlc' when mpv is absent."""
        with patch("shutil.which", side_effect=lambda x: "/usr/bin/vlc" if x == "vlc" else None):
            assert detect_player() == "vlc"

    def test_returns_none_when_no_player_found(self):
        """detect_player should return None when no known player is installed."""
        with patch("shutil.which", return_value=None):
            assert detect_player() is None


# ---------------------------------------------------------------------------
# _build_command
# ---------------------------------------------------------------------------

class TestBuildCommand:
    """Tests for _build_command helper."""

    def test_mpv_basic(self):
        """_build_command with mpv and no extra options."""
        opts = PlayerOptions(player="mpv")
        cmd = _build_command("http://example.com/stream.m3u8", opts)
        assert cmd[0] == "mpv"
        assert "http://example.com/stream.m3u8" in cmd

    def test_mpv_with_title(self):
        """_build_command passes --title to mpv."""
        opts = PlayerOptions(player="mpv", title="My Anime - Ep 1")
        cmd = _build_command("http://example.com/stream.m3u8", opts)
        assert any("My Anime - Ep 1" in part for part in cmd)

    def test_vlc_basic(self):
        """_build_command with vlc player."""
        opts = PlayerOptions(player="vlc")
        cmd = _build_command("http://example.com/stream.m3u8", opts)
        assert cmd[0] == "vlc"
        assert "http://example.com/stream.m3u8" in cmd

    def test_extra_args_appended(self):
        """_build_command appends extra_args at the end."""
        opts = PlayerOptions(player="mpv", extra_args=["--fullscreen", "--volume=80"])
        cmd = _build_command("http://example.com/stream.m3u8", opts)
        assert "--fullscreen" in cmd
        assert "--volume=80" in cmd

    def test_unknown_player_still_works(self):
        """_build_command with an unknown player just prepends the player name."""
        opts = PlayerOptions(player="mplayer")
        cmd = _build_command("http://example.com/stream.m3u8", opts)
        assert cmd[0] == "mplayer"
        assert "http://example.com/stream.m3u8" in cmd


# ---------------------------------------------------------------------------
# play
# ---------------------------------------------------------------------------

class TestPlay:
    """Tests for the top-level play() function."""

    def test_play_calls_subprocess_run(self):
        """play() should invoke subprocess.run with the built command."""
        opts = PlayerOptions(player="mpv")
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            play("http://example.com/stream.m3u8", opts)
            mock_run.assert_called_once()
            args, kwargs = mock_run.call_args
            cmd = args[0]
            assert cmd[0] == "mpv"
            assert "http://example.com/stream.m3u8" in cmd

    def test_play_raises_when_no_player(self):
        """play() should raise ValueError when player is None."""
        opts = PlayerOptions(player=None)
        with pytest.raises(ValueError, match="No media player"):
            play("http://example.com/stream.m3u8", opts)

    def test_play_returns_completed_process(self):
        """play() should return the CompletedProcess from subprocess.run."""
        opts = PlayerOptions(player="mpv")
        fake_result = MagicMock(returncode=0)
        with patch("subprocess.run", return_value=fake_result):
            result = play("http://example.com/stream.m3u8", opts)
            assert result is fake_result

    def test_play_non_zero_exit_does_not_raise(self):
        """play() should not raise on non-zero player exit code by default."""
        opts = PlayerOptions(player="mpv")
        with patch("subprocess.run", return_value=MagicMock(returncode=1)):
            result = play("http://example.com/stream.m3u8", opts)
            assert result.returncode == 1
