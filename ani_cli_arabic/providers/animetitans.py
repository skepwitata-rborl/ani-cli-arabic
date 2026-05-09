from __future__ import annotations

from typing import List

import requests
from bs4 import BeautifulSoup

from .base import Anime, BaseProvider, Episode


class AnimetitansProvider(BaseProvider):
    """Provider for animetitans.com — Arabic anime streaming site."""

    BASE_URL = "https://www.animetitans.com"
    name = "animetitans"

    def search(self, query: str) -> List[Anime]:
        url = f"{self.BASE_URL}/?s={requests.utils.quote(query)}"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        results: List[Anime] = []
        for card in soup.select("div.result-item article"):
            title_tag = card.select_one("div.details div.title a")
            if not title_tag:
                continue
            title = title_tag.get_text(strip=True)
            link = title_tag["href"]
            thumb_tag = card.select_one("div.image img")
            thumbnail = thumb_tag["src"] if thumb_tag else ""
            results.append(Anime(title=title, url=str(link), thumbnail=str(thumbnail)))
        return results

    def get_episodes(self, anime: Anime) -> List[Episode]:
        resp = requests.get(anime.url, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        episodes: List[Episode] = []
        for ep_tag in soup.select("ul#episodios li"):
            link_tag = ep_tag.select_one("a")
            num_tag = ep_tag.select_one("div.numerando")
            if not link_tag or not num_tag:
                continue
            try:
                number = int(num_tag.get_text(strip=True).split("-")[-1].strip())
            except ValueError:
                continue
            episodes.append(Episode(number=number, url=str(link_tag["href"])))

        return sorted(episodes, key=lambda e: e.number)

    def get_stream_url(self, episode: Episode) -> str:
        resp = requests.get(episode.url, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        iframe = soup.select_one("div.embed-player iframe, div.player-embed iframe")
        if iframe and iframe.get("src"):
            return str(iframe["src"])
        return ""
