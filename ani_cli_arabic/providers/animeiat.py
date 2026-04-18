"""Animeiat.tv provider for ani-cli-arabic."""
from __future__ import annotations

import re
from typing import List

import requests
from bs4 import BeautifulSoup

from .base import Anime, BaseProvider, Episode

BASE_URL = "https://animeiat.tv"
SEARCH_URL = f"{BASE_URL}/?s="


class AnimeiatProvider(BaseProvider):
    """Provider implementation for animeiat.tv."""

    name = "animeiat"

    def search(self, query: str) -> List[Anime]:
        response = requests.get(SEARCH_URL + requests.utils.quote(query), timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        results: List[Anime] = []
        for card in soup.select(".anime-card"):
            title_tag = card.select_one(".anime-title")
            link_tag = card.select_one("a")
            if title_tag and link_tag:
                results.append(
                    Anime(
                        title=title_tag.get_text(strip=True),
                        url=link_tag["href"],
                        provider=self.name,
                    )
                )
        return results

    def get_episodes(self, anime: Anime) -> List[Episode]:
        response = requests.get(anime.url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        episodes: List[Episode] = []
        for ep_tag in soup.select(".episode-item a"):
            title = ep_tag.get_text(strip=True)
            url = ep_tag["href"]
            num_match = re.search(r"(\d+)", title)
            number = int(num_match.group(1)) if num_match else 0
            episodes.append(Episode(title=title, url=url, number=number))
        episodes.sort(key=lambda e: e.number)
        return episodes

    def get_stream_url(self, episode: Episode) -> str:
        response = requests.get(episode.url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        iframe = soup.select_one("iframe[src]")
        if iframe:
            return iframe["src"]
        source = soup.select_one("source[src]")
        if source:
            return source["src"]
        raise ValueError(f"No stream URL found for episode: {episode.url}")
