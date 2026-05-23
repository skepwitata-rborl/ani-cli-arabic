"""AnimeKage provider for ani-cli-arabic."""

from __future__ import annotations

import re
from typing import List

import requests
from bs4 import BeautifulSoup

from .base import Anime, BaseProvider, Episode


class AnimekageProvider(BaseProvider):
    """Provider that scrapes AnimeKage (animekage.net)."""

    BASE_URL = "https://www.animekage.net"
    name = "animekage"

    def search(self, query: str) -> List[Anime]:
        url = f"{self.BASE_URL}/?s={requests.utils.quote(query)}"
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
        except requests.RequestException:
            return []

        soup = BeautifulSoup(resp.text, "html.parser")
        results: List[Anime] = []
        for article in soup.select("div.anime-card"):
            title_tag = article.select_one("h3.anime-title a")
            if title_tag is None:
                continue
            title = title_tag.get_text(strip=True)
            url_val = title_tag.get("href", "")
            results.append(Anime(title=title, url=url_val))
        return results

    def get_episodes(self, anime: Anime) -> List[Episode]:
        try:
            resp = requests.get(anime.url, timeout=10)
            resp.raise_for_status()
        except requests.RequestException:
            return []

        soup = BeautifulSoup(resp.text, "html.parser")
        episodes: List[Episode] = []
        for link in soup.select("div.episodes-list a"):
            href = link.get("href", "")
            text = link.get_text(strip=True)
            match = re.search(r"(\d+)", text)
            num = int(match.group(1)) if match else 0
            episodes.append(Episode(number=num, url=href))
        return sorted(episodes, key=lambda e: e.number)

    def get_stream_url(self, episode: Episode) -> str:
        try:
            resp = requests.get(episode.url, timeout=10)
            resp.raise_for_status()
        except requests.RequestException:
            return ""

        soup = BeautifulSoup(resp.text, "html.parser")
        iframe = soup.select_one("div.player-container iframe")
        if iframe:
            return iframe.get("src", "")
        source = soup.select_one("video source")
        if source:
            return source.get("src", "")
        return ""
