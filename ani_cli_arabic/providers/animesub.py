"""AnimeSub provider — Arabic-subtitled anime streaming."""
from __future__ import annotations

import re
from typing import List

import requests
from bs4 import BeautifulSoup

from .base import Anime, BaseProvider, Episode


class AnimesubProvider(BaseProvider):
    """Provider for animesub.info."""

    BASE_URL = "https://animesub.info"

    def search(self, query: str) -> List[Anime]:
        """Search for anime by title."""
        try:
            resp = requests.get(
                f"{self.BASE_URL}/?s={requests.utils.quote(query)}",
                timeout=10,
            )
            resp.raise_for_status()
        except Exception:
            return []

        soup = BeautifulSoup(resp.text, "html.parser")
        results: List[Anime] = []
        for article in soup.select("article.anime-card"):
            title_tag = article.select_one("h3.entry-title a")
            if not title_tag:
                continue
            title = title_tag.get_text(strip=True)
            url = title_tag["href"]
            results.append(Anime(title=title, url=url))
        return results

    def get_episodes(self, anime: Anime) -> List[Episode]:
        """Return sorted episode list for *anime*."""
        try:
            resp = requests.get(anime.url, timeout=10)
            resp.raise_for_status()
        except Exception:
            return []

        soup = BeautifulSoup(resp.text, "html.parser")
        episodes: List[Episode] = []
        for link in soup.select("div.episodes-list a"):
            href = link.get("href", "")
            text = link.get_text(strip=True)
            match = re.search(r"(\d+(?:\.\d+)?)", text)
            number = float(match.group(1)) if match else 0.0
            episodes.append(Episode(title=text, url=href, number=number))
        episodes.sort(key=lambda e: e.number)
        return episodes

    def get_stream_url(self, episode: Episode) -> str:
        """Extract the direct stream URL from an episode page."""
        try:
            resp = requests.get(episode.url, timeout=10)
            resp.raise_for_status()
        except Exception:
            return ""

        soup = BeautifulSoup(resp.text, "html.parser")
        iframe = soup.select_one("iframe[src]")
        if iframe:
            return iframe["src"]
        video = soup.select_one("video source[src]")
        if video:
            return video["src"]
        return ""
