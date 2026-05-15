from __future__ import annotations

from typing import List

import requests
from bs4 import BeautifulSoup

from .base import Anime, BaseProvider, Episode


class AnimezoneProvider(BaseProvider):
    """Provider for animezone.io — Arabic anime streaming site."""

    name = "animezone"
    base_url = "https://www.animezone.io"

    def search(self, query: str) -> List[Anime]:
        url = f"{self.base_url}/?s={requests.utils.quote(query)}"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        results: List[Anime] = []
        for card in soup.select("div.anime-card"):
            title_tag = card.select_one("h3.anime-title a")
            if not title_tag:
                continue
            title = title_tag.get_text(strip=True)
            link = title_tag["href"]
            results.append(Anime(title=title, url=link))
        return results

    def get_episodes(self, anime: Anime) -> List[Episode]:
        resp = requests.get(anime.url, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        episodes: List[Episode] = []
        for ep_tag in soup.select("ul.episodes-list li a"):
            label = ep_tag.get_text(strip=True)
            href = ep_tag["href"]
            try:
                number = int("".join(filter(str.isdigit, label)))
            except ValueError:
                number = 0
            episodes.append(Episode(number=number, url=href, title=label))

        return sorted(episodes, key=lambda e: e.number)

    def get_stream_url(self, episode: Episode) -> str:
        resp = requests.get(episode.url, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        iframe = soup.select_one("div.player-container iframe")
        if iframe and iframe.get("src"):
            return iframe["src"]

        video = soup.select_one("video source")
        if video and video.get("src"):
            return video["src"]

        raise ValueError(f"Could not find stream URL for episode: {episode.url}")
