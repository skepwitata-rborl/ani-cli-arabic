"""Media player integration for ani-cli-arabic.

Detects and launches available media players (mpv, vlc, etc.)
with the resolved stream URL.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from typing import List, Optional


# Players tried in order of preference
_PLAYER_CANDIDATES: List[str] = ["mpv", "vlc", "mplayer", "ffplay"]


@dataclass
class PlayerOptions:
    """Options forwarded to the underlying media player."""

    title: str = ""
    extra_args: List[str] = field(default_factory=list)
    headers: Optional[dict] = None


def detect_player() -> Optional[str]:
    """Return the first available player found on PATH, or None."""
    for player in _PLAYER_CANDIDATES:
        if shutil.which(player):
            return player
    return None


def _build_command(player: str, url: str, opts: PlayerOptions) -> List[str]:
    """Build the subprocess argument list for the given player."""
    cmd: List[str] = [player]

    if player == "mpv":
        if opts.title:
            cmd += [f"--title={opts.title}", f"--force-media-title={opts.title}"]
        if opts.headers:
            header_str = "\r\n".join(f"{k}: {v}" for k, v in opts.headers.items())
            cmd += [f"--http-header-fields={header_str}"]
        cmd += opts.extra_args
        cmd.append(url)

    elif player == "vlc":
        if opts.title:
            cmd += ["--meta-title", opts.title]
        if opts.headers:
            # VLC accepts extra HTTP headers via --http-forward-cookies / lua,
            # simplest portable approach is --http-extra-headers
            for k, v in opts.headers.items():
                cmd += ["--http-extra-headers", f"{k}: {v}"]
        cmd += opts.extra_args
        cmd.append(url)

    else:
        # Generic fallback: just pass url and any extra args
        cmd += opts.extra_args
        cmd.append(url)

    return cmd


def play(url: str, opts: Optional[PlayerOptions] = None, player: Optional[str] = None) -> int:
    """Launch a media player to play *url*.

    Parameters
    ----------
    url:
        Direct stream URL to play.
    opts:
        Optional :class:`PlayerOptions` controlling title and extra flags.
    player:
        Override auto-detected player binary name/path.

    Returns
    -------
    int
        Exit code of the player process.

    Raises
    ------
    RuntimeError
        If no supported media player is found.
    """
    if opts is None:
        opts = PlayerOptions()

    resolved_player = player or detect_player()
    if not resolved_player:
        raise RuntimeError(
            "No supported media player found. "
            f"Please install one of: {', '.join(_PLAYER_CANDIDATES)}"
        )

    cmd = _build_command(resolved_player, url, opts)

    try:
        result = subprocess.run(cmd, check=False)
        return result.returncode
    except FileNotFoundError:
        print(f"[error] Player '{resolved_player}' not found.", file=sys.stderr)
        return 1
