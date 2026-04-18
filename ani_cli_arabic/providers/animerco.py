import re
from typing import List

import requests
from bs4 import BeautifulSoup

from .base import Anime, BaseProvider, Episode


class AnimercoProvider(BaseProvider):
    BASE_URL = "https://animerco.org"

    def search(self, query: str) -> List[Anime]:
        url = f"{self.BASE_URL}/?s={requests.utils.quote(query)}"
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
            thumb_tag = card.select_one("img")
            thumbnail = thumb_tag["src"] if thumb_tag else ""
            results.append(Anime(title=title, url=link, thumbnail=thumbnail))
        return results

    def get_episodes(self, anime: Anime) -> List[Episode]:
        resp = requests.get(anime.url, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        episodes: List[Episode] = []
        for ep_tag in soup.select("div.episodes-list a"):
            title = ep_tag.get_text(strip=True)
            url = ep_tag["href"]
            match = re.search(r"(\d+)", title)
            number = int(match.group(1)) if match else 0
            episodes.append(Episode(title=title, url=url, number=number))
        return sorted(episodes, key=lambda e: e.number)

    def get_stream_url(self, episode: Episode) -> str:
        resp = requests.get(episode.url, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        iframe = soup.select_one("iframe[src]")
        if iframe:
            return iframe["src"]
        raise ValueError(f"No stream URL found for episode: {episode.url}")
