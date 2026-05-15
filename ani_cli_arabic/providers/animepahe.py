from __future__ import annotations

import requests
from bs4 import BeautifulSoup

from .base import Anime, BaseProvider, Episode


class AnimepaheProvider(BaseProvider):
    """Provider for animepahe.ru"""

    BASE_URL = "https://animepahe.ru"
    API_URL = "https://animepahe.ru/api"

    def search(self, query: str) -> list[Anime]:
        try:
            response = requests.get(
                self.API_URL,
                params={"m": "search", "q": query},
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()
        except Exception:
            return []

        results = data.get("data", [])
        if not results:
            return []

        animes: list[Anime] = []
        for item in results:
            slug = item.get("session", "")
            title = item.get("title", "")
            url = f"{self.BASE_URL}/anime/{slug}"
            if slug and title:
                animes.append(Anime(title=title, url=url))
        return animes

    def get_episodes(self, anime: Anime) -> list[Episode]:
        slug = anime.url.rstrip("/").split("/")[-1]
        episodes: list[Episode] = []
        page = 1
        while True:
            try:
                response = requests.get(
                    self.API_URL,
                    params={"m": "release", "id": slug, "sort": "episode_asc", "page": page},
                    timeout=10,
                )
                response.raise_for_status()
                data = response.json()
            except Exception:
                break

            items = data.get("data", [])
            if not items:
                break

            for item in items:
                ep_num = item.get("episode", 0)
                session = item.get("session", "")
                url = f"{self.BASE_URL}/play/{slug}/{session}"
                episodes.append(Episode(number=int(ep_num), url=url))

            if page >= data.get("last_page", 1):
                break
            page += 1

        return sorted(episodes, key=lambda e: e.number)

    def get_stream_url(self, episode: Episode) -> str:
        try:
            response = requests.get(episode.url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            source = soup.select_one("source[src]")
            if source:
                return source["src"]
            iframe = soup.select_one("iframe[src]")
            if iframe:
                return iframe["src"]
        except Exception:
            pass
        return ""
