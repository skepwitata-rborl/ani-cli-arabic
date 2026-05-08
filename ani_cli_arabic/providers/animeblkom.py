"""Provider for animeblkom.net — Arabic anime streaming site."""
from __future__ import annotations

import re
from typing import List

import requests
from bs4 import BeautifulSoup

from .base import Anime, BaseProvider, Episode

BASE_URL = "https://animeblkom.net"


class AnimeblkomProvider(BaseProvider):
    name = "animeblkom"

    def search(self, query: str) -> List[Anime]:
        url = f"{BASE_URL}/?search_param=animes&s={query}"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        results: List[Anime] = []
        for card in soup.select("div.anime-card"):
            a_tag = card.select_one("a")
            title_tag = card.select_one(".anime-title")
            if not a_tag or not title_tag:
                continue
            results.append(
                Anime(
                    title=title_tag.get_text(strip=True),
                    url=a_tag["href"],
                )
            )
        return results

    def get_episodes(self, anime: Anime) -> List[Episode]:
        resp = requests.get(anime.url, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        episodes: List[Episode] = []
        for ep_tag in soup.select("ul.episodes-list li a"):
            href = ep_tag.get("href", "")
            num_match = re.search(r"episode-(\d+)", href)
            number = int(num_match.group(1)) if num_match else 0
            episodes.append(Episode(number=number, url=href))
        return sorted(episodes, key=lambda e: e.number)

    def get_stream_url(self, episode: Episode) -> str:
        resp = requests.get(episode.url, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        iframe = soup.select_one("div.video-container iframe")
        if iframe and iframe.get("src"):
            return iframe["src"]
        source = soup.select_one("video source")
        if source and source.get("src"):
            return source["src"]
        raise ValueError(f"No stream URL found for episode: {episode.url}")
