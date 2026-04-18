from __future__ import annotations

import re
from typing import List

import requests
from bs4 import BeautifulSoup

from .base import Anime, BaseProvider, Episode


class AnimekisaProvider(BaseProvider):
    """Provider for animekisa.tv (Arabic subtitles)."""

    BASE_URL = "https://animekisa.tv"
    name = "animekisa"

    def search(self, query: str) -> List[Anime]:
        url = f"{self.BASE_URL}/search"
        response = requests.get(url, params={"q": query}, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        results: List[Anime] = []
        for card in soup.select(".film-poster"):
            title_tag = card.select_one(".film-name")
            link_tag = card.select_one("a")
            if not title_tag or not link_tag:
                continue
            title = title_tag.get_text(strip=True)
            href = link_tag.get("href", "")
            anime_id = href.strip("/").split("/")[-1]
            results.append(Anime(id=anime_id, title=title, url=f"{self.BASE_URL}{href}"))
        return results

    def get_episodes(self, anime: Anime) -> List[Episode]:
        response = requests.get(anime.url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        episodes: List[Episode] = []
        for ep_tag in soup.select(".ep-item"):
            href = ep_tag.get("href", "")
            ep_num_match = re.search(r"episode-(\d+)", href)
            ep_num = int(ep_num_match.group(1)) if ep_num_match else 0
            episodes.append(
                Episode(
                    number=ep_num,
                    title=ep_tag.get_text(strip=True) or f"Episode {ep_num}",
                    url=f"{self.BASE_URL}{href}",
                )
            )
        return sorted(episodes, key=lambda e: e.number)

    def get_stream_url(self, episode: Episode) -> str:
        response = requests.get(episode.url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        iframe = soup.select_one("iframe[src]")
        if iframe:
            return iframe["src"]
        raise ValueError(f"No stream URL found for episode: {episode.url}")
