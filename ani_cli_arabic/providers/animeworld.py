from __future__ import annotations

import re
from typing import List

import requests
from bs4 import BeautifulSoup

from .base import Anime, BaseProvider, Episode


class AnimeworldProvider(BaseProvider):
    """Provider for animeworld.ac (Italian/global anime site)."""

    name = "animeworld"
    base_url = "https://www.animeworld.ac"

    def search(self, query: str) -> List[Anime]:
        url = f"{self.base_url}/search?keyword={requests.utils.quote(query)}"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        results: List[Anime] = []
        for card in soup.select("div.film-list > div.item"):
            title_tag = card.select_one("a.name")
            if not title_tag:
                continue
            title = title_tag.get_text(strip=True)
            href = title_tag.get("href", "")
            anime_url = href if href.startswith("http") else self.base_url + href
            results.append(Anime(title=title, url=anime_url))
        return results

    def get_episodes(self, anime: Anime) -> List[Episode]:
        resp = requests.get(anime.url, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        episodes: List[Episode] = []
        for ep_tag in soup.select("ul.episodes > li > a"):
            label = ep_tag.get_text(strip=True)
            href = ep_tag.get("href", "")
            ep_url = href if href.startswith("http") else self.base_url + href
            try:
                number = int(re.search(r"(\d+)", label).group(1))
            except (AttributeError, ValueError):
                number = len(episodes) + 1
            episodes.append(Episode(number=number, url=ep_url))

        return sorted(episodes, key=lambda e: e.number)

    def get_stream_url(self, episode: Episode) -> str:
        resp = requests.get(episode.url, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        # Try direct video source first
        source = soup.select_one("video > source")
        if source and source.get("src"):
            return source["src"]

        # Fall back to embedded iframe
        iframe = soup.select_one("div#player-embed iframe, iframe[src*='stream']")  
        if iframe and iframe.get("src"):
            src = iframe["src"]
            return src if src.startswith("http") else "https:" + src

        raise ValueError(f"Could not extract stream URL from {episode.url}")
