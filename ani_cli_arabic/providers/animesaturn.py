"""AnimeSaturn provider — Arabic/Italian anime streaming site."""
from __future__ import annotations

import re
from typing import List

import requests
from bs4 import BeautifulSoup

from .base import Anime, BaseProvider, Episode

_BASE_URL = "https://www.animesaturn.cx"
_HEADERS = {"User-Agent": "Mozilla/5.0"}


class AnimeSaturnProvider(BaseProvider):
    """Provider backed by animesaturn.cx."""

    name = "animesaturn"

    # ------------------------------------------------------------------
    def search(self, query: str) -> List[Anime]:
        url = f"{_BASE_URL}/animelist"
        resp = requests.get(url, params={"search": query}, headers=_HEADERS, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        results: List[Anime] = []
        for card in soup.select("ul.list-group a.list-group-item"):
            title = card.get_text(strip=True)
            href = card.get("href", "")
            if title and href:
                results.append(Anime(title=title, url=href))
        return results

    # ------------------------------------------------------------------
    def get_episodes(self, anime: Anime) -> List[Episode]:
        resp = requests.get(anime.url, headers=_HEADERS, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        episodes: List[Episode] = []
        for tag in soup.select("div.tab-content a.btn-episode"):
            label = tag.get_text(strip=True)
            href = tag.get("href", "")
            match = re.search(r"(\d+(?:\.\d+)?)", label)
            number = float(match.group(1)) if match else 0.0
            if href:
                episodes.append(Episode(number=number, url=href))
        episodes.sort(key=lambda e: e.number)
        return episodes

    # ------------------------------------------------------------------
    def get_stream_url(self, episode: Episode) -> str:
        resp = requests.get(episode.url, headers=_HEADERS, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        # Prefer a direct <source> tag inside a <video>
        source = soup.select_one("video source[src]")
        if source:
            return source["src"]
        # Fall back to an embedded iframe
        iframe = soup.select_one("iframe[src]")
        if iframe:
            return iframe["src"]
        raise ValueError(f"No stream found for episode: {episode.url}")
