"""GogoAnime Arabic provider."""
from __future__ import annotations

import re
from typing import List

import requests
from bs4 import BeautifulSoup

from .base import Anime, BaseProvider, Episode

_BASE_URL = "https://gogoanime3.co"
_SEARCH_URL = f"{_BASE_URL}/search.html"


class GogoanimeProvider(BaseProvider):
    """Provider backed by GogoAnime."""

    name = "gogoanime"

    def search(self, query: str) -> List[Anime]:
        """Return anime matching *query*."""
        resp = requests.get(
            _SEARCH_URL,
            params={"keyword": query},
            timeout=10,
        )
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        results: List[Anime] = []
        for item in soup.select("ul.items li"):
            title_tag = item.select_one("p.name a")
            if title_tag is None:
                continue
            title = title_tag.get_text(strip=True)
            url = _BASE_URL + title_tag["href"]
            results.append(Anime(title=title, url=url))
        return results

    def get_episodes(self, anime: Anime) -> List[Episode]:
        """Return sorted episode list for *anime*."""
        resp = requests.get(anime.url, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        episodes: List[Episode] = []
        for link in soup.select("ul#episode_page a"):
            ep_end = link.get("ep_end")
            ep_start = link.get("ep_start")
            if ep_end is None or ep_start is None:
                continue
            for num in range(int(ep_start), int(ep_end) + 1):
                slug = anime.url.rstrip("/").rsplit("/", 1)[-1]
                ep_url = f"{_BASE_URL}/{slug}-episode-{num}"
                episodes.append(Episode(number=num, url=ep_url))
        return sorted(episodes, key=lambda e: e.number)

    def get_stream_url(self, episode: Episode) -> str:
        """Return a direct stream URL for *episode*."""
        resp = requests.get(episode.url, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        iframe = soup.select_one("div.play-video iframe")
        if iframe is None:
            raise ValueError(f"No iframe found for {episode.url}")
        src: str = iframe["src"]
        if src.startswith("//"):
            src = "https:" + src
        # Extract direct video URL from the embed page
        embed_resp = requests.get(src, timeout=10)
        embed_resp.raise_for_status()
        match = re.search(r'file:\s*["\']([^"\'\']+\.m3u8[^"\']*)["\'\']', embed_resp.text)
        if match:
            return match.group(1)
        match = re.search(r'file:\s*["\']([^"\'\']+\.mp4[^"\']*)["\'\']', embed_resp.text)
        if match:
            return match.group(1)
        raise ValueError(f"Could not extract stream URL from {src}")
