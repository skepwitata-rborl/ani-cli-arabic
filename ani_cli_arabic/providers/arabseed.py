"""ArabSeed provider for ani-cli-arabic."""
from __future__ import annotations

import re
from typing import List

import requests
from bs4 import BeautifulSoup

from .base import Anime, BaseProvider, Episode

_BASE_URL = "https://arabseed.ink"
_HEADERS = {"User-Agent": "Mozilla/5.0"}


class ArabseedProvider(BaseProvider):
    """Scrapes anime data from ArabSeed."""

    name = "arabseed"

    def search(self, query: str) -> List[Anime]:
        url = f"{_BASE_URL}/?s={requests.utils.quote(query)}"
        resp = requests.get(url, headers=_HEADERS, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        results: List[Anime] = []
        for card in soup.select("ul.Blocks-UL div.BlockItem"):
            title_tag = card.select_one("a")
            if not title_tag:
                continue
            title = title_tag.get("title") or title_tag.get_text(strip=True)
            link = title_tag.get("href", "")
            if title and link:
                results.append(Anime(title=title, url=link))
        return results

    def get_episodes(self, anime: Anime) -> List[Episode]:
        resp = requests.get(anime.url, headers=_HEADERS, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        episodes: List[Episode] = []
        for tag in soup.select("div.List--Seasons--Episodes a"):
            href = tag.get("href", "")
            text = tag.get_text(strip=True)
            match = re.search(r"(\d+)", text)
            number = int(match.group(1)) if match else 0
            if href:
                episodes.append(Episode(number=number, url=href))
        return sorted(episodes, key=lambda e: e.number)

    def get_stream_url(self, episode: Episode) -> str:
        resp = requests.get(episode.url, headers=_HEADERS, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        iframe = soup.select_one("iframe[src]")
        if iframe:
            return iframe["src"]
        # fallback: look for a direct video source
        source = soup.select_one("source[src]")
        if source:
            return source["src"]
        raise ValueError(f"No stream URL found for episode: {episode.url}")
