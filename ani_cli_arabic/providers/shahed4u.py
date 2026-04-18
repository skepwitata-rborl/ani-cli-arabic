from __future__ import annotations

import re
from typing import List

import requests
from bs4 import BeautifulSoup

from .base import Anime, BaseProvider, Episode


class Shahed4uProvider(BaseProvider):
    """Provider for shahed4u Arabic anime site."""

    BASE_URL = "https://shahed4u.art"
    name = "shahed4u"

    def search(self, query: str) -> List[Anime]:
        url = f"{self.BASE_URL}/?s={requests.utils.quote(query)}"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        results: List[Anime] = []
        for item in soup.select("div.result-item article"):
            title_tag = item.select_one("div.title a")
            if not title_tag:
                continue
            title = title_tag.get_text(strip=True)
            link = title_tag["href"]
            image_tag = item.select_one("img")
            image = image_tag["src"] if image_tag else ""
            results.append(Anime(title=title, url=link, image=image, provider=self.name))
        return results

    def get_episodes(self, anime: Anime) -> List[Episode]:
        resp = requests.get(anime.url, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        episodes: List[Episode] = []
        for ep_tag in soup.select("div.episodios li a"):
            href = ep_tag["href"]
            num_match = re.search(r"(\d+)", ep_tag.get_text())
            number = int(num_match.group(1)) if num_match else 0
            episodes.append(Episode(number=number, url=href, anime=anime))
        return sorted(episodes, key=lambda e: e.number)

    def get_stream_url(self, episode: Episode) -> str:
        resp = requests.get(episode.url, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        iframe = soup.select_one("div.embed iframe, iframe[src]")
        if iframe and iframe.get("src"):
            return iframe["src"]
        raise ValueError(f"No stream URL found for episode {episode.url}")
