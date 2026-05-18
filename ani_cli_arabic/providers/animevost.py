"""Provider for animevost.org — Russian/Arabic anime site."""
from __future__ import annotations

from typing import List

import requests
from bs4 import BeautifulSoup

from .base import Anime, BaseProvider, Episode


class AnimevostProvider(BaseProvider):
    """Scraper for animevost.org."""

    BASE_URL = "https://animevost.org"
    SEARCH_URL = f"{BASE_URL}/search"

    def search(self, query: str) -> List[Anime]:
        try:
            resp = requests.get(
                self.SEARCH_URL,
                params={"q": query},
                timeout=10,
            )
            resp.raise_for_status()
        except Exception:
            return []

        soup = BeautifulSoup(resp.text, "html.parser")
        results: List[Anime] = []
        for card in soup.select("div.shortstory"):
            title_tag = card.select_one("h2.zagolovok a")
            if not title_tag:
                continue
            title = title_tag.get_text(strip=True)
            url = title_tag["href"]
            if not url.startswith("http"):
                url = self.BASE_URL + url
            results.append(Anime(title=title, url=url))
        return results

    def get_episodes(self, anime: Anime) -> List[Episode]:
        try:
            resp = requests.get(anime.url, timeout=10)
            resp.raise_for_status()
        except Exception:
            return []

        soup = BeautifulSoup(resp.text, "html.parser")
        episodes: List[Episode] = []
        for link in soup.select("div.epiList a"):
            title = link.get_text(strip=True)
            url = link["href"]
            if not url.startswith("http"):
                url = self.BASE_URL + url
            try:
                num = float("".join(filter(lambda c: c.isdigit() or c == ".", title)) or "0")
            except ValueError:
                num = 0.0
            episodes.append(Episode(title=title, url=url, number=num))
        return sorted(episodes, key=lambda e: e.number)

    def get_stream_url(self, episode: Episode) -> str:
        try:
            resp = requests.get(episode.url, timeout=10)
            resp.raise_for_status()
        except Exception:
            return ""

        soup = BeautifulSoup(resp.text, "html.parser")
        iframe = soup.select_one("iframe[src]")
        if iframe:
            src = iframe["src"]
            return src if src.startswith("http") else self.BASE_URL + src
        return ""
