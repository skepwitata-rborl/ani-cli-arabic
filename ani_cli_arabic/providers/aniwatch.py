"""AniWatch provider for ani-cli-arabic."""
from __future__ import annotations

import re
from typing import List

import requests
from bs4 import BeautifulSoup

from .base import Anime, BaseProvider, Episode

_BASE_URL = "https://aniwatch.to"
_SEARCH_URL = f"{_BASE_URL}/search"


class AniwatchProvider(BaseProvider):
    """Provider backed by aniwatch.to."""

    name = "aniwatch"

    def search(self, query: str) -> List[Anime]:
        resp = requests.get(
            _SEARCH_URL,
            params={"keyword": query},
            timeout=10,
        )
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        results: List[Anime] = []
        for card in soup.select("div.flw-item"):
            title_tag = card.select_one("h3.film-name a")
            if not title_tag:
                continue
            title = title_tag.get_text(strip=True)
            url = _BASE_URL + title_tag["href"]
            results.append(Anime(title=title, url=url))
        return results

    def get_episodes(self, anime: Anime) -> List[Episode]:
        resp = requests.get(anime.url, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        episodes: List[Episode] = []
        for link in soup.select("a.ep-item"):
            ep_text = link.get("data-number", "")
            ep_url = _BASE_URL + link["href"]
            try:
                number = int(ep_text)
            except (ValueError, TypeError):
                continue
            episodes.append(Episode(number=number, url=ep_url))
        return sorted(episodes, key=lambda e: e.number)

    def get_stream_url(self, episode: Episode) -> str:
        resp = requests.get(episode.url, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        iframe = soup.select_one("iframe[src]")
        if iframe:
            return iframe["src"]
        match = re.search(r'file:\s*["\']([^"\'\']+)["\']', resp.text)
        if match:
            return match.group(1)
        raise ValueError(f"Could not extract stream URL from {episode.url}")
