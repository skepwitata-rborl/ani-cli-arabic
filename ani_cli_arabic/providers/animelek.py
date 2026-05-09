from __future__ import annotations

import requests
from bs4 import BeautifulSoup

from .base import Anime, BaseProvider, Episode


class AnimelekProvider(BaseProvider):
    """Provider for animelek.me — Arabic anime streaming site."""

    BASE_URL = "https://animelek.me"
    name = "animelek"

    def search(self, query: str) -> list[Anime]:
        url = f"{self.BASE_URL}/?search_param=animes&s={requests.utils.quote(query)}"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        results: list[Anime] = []
        for card in soup.select("div.anime-card-container div.anime-card-title a"):
            title = card.get_text(strip=True)
            link = card.get("href", "")
            if title and link:
                results.append(Anime(title=title, url=link))
        return results

    def get_episodes(self, anime: Anime) -> list[Episode]:
        resp = requests.get(anime.url, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        episodes: list[Episode] = []
        for link in soup.select("div.episodes-list-content a"):
            href = link.get("href", "")
            text = link.get_text(strip=True)
            try:
                num = int("".join(filter(str.isdigit, text)) or 0)
            except ValueError:
                num = 0
            if href:
                episodes.append(Episode(number=num, url=href))
        return sorted(episodes, key=lambda e: e.number)

    def get_stream_url(self, episode: Episode) -> str:
        resp = requests.get(episode.url, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        iframe = soup.select_one("div.watch-anime-area iframe")
        if iframe:
            src = iframe.get("src", "")
            if src:
                return src
        video = soup.select_one("video source")
        if video:
            return video.get("src", "")
        return ""
