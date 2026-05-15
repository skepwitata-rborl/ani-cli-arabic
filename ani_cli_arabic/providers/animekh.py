"""AnimeKH provider — Arabic-dubbed/subbed anime from animekh.com."""
from __future__ import annotations

import re
from typing import List

import requests
from bs4 import BeautifulSoup

from .base import Anime, BaseProvider, Episode

_BASE = "https://animekh.com"
_HEADERS = {"User-Agent": "Mozilla/5.0"}


class AnimekHProvider(BaseProvider):
    name = "animekh"

    def search(self, query: str) -> List[Anime]:
        resp = requests.get(
            f"{_BASE}/?s={requests.utils.quote(query)}",
            headers=_HEADERS,
            timeout=15,
        )
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        results: List[Anime] = []
        for card in soup.select("div.post-thumbnail a"):
            title = card.get("title", "").strip()
            url = card.get("href", "").strip()
            if title and url:
                results.append(Anime(title=title, url=url))
        return results

    def get_episodes(self, anime: Anime) -> List[Episode]:
        resp = requests.get(anime.url, headers=_HEADERS, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        episodes: List[Episode] = []
        for link in soup.select("div.episodelist a"):
            href = link.get("href", "").strip()
            text = link.get_text(strip=True)
            match = re.search(r"(\d+(?:\.\d+)?)", text)
            num = float(match.group(1)) if match else 0.0
            if href:
                episodes.append(Episode(number=num, url=href))
        return sorted(episodes, key=lambda e: e.number)

    def get_stream_url(self, episode: Episode) -> str:
        resp = requests.get(episode.url, headers=_HEADERS, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        iframe = soup.select_one("div.player-embed iframe, iframe.embed-responsive-item")
        if iframe and iframe.get("src"):
            return iframe["src"]
        raise ValueError(f"No stream found for {episode.url}")
