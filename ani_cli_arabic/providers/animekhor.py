from __future__ import annotations

from typing import List

import requests
from bs4 import BeautifulSoup

from .base import Anime, BaseProvider, Episode


class AnimekhorProvider(BaseProvider):
    """Provider for animekhor.xyz — an Arabic anime streaming site."""

    name = "animekhor"
    base_url = "https://animekhor.xyz"

    def search(self, query: str) -> List[Anime]:
        url = f"{self.base_url}/?s={requests.utils.quote(query)}"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        results: List[Anime] = []
        for article in soup.select("div.result-item article"):
            title_tag = article.select_one("div.title a")
            if not title_tag:
                continue
            title = title_tag.get_text(strip=True)
            link = title_tag["href"]
            results.append(Anime(title=title, url=str(link)))
        return results

    def get_episodes(self, anime: Anime) -> List[Episode]:
        resp = requests.get(anime.url, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        episodes: List[Episode] = []
        for a_tag in soup.select("div#episodes ul li a"):
            label = a_tag.get_text(strip=True)
            href = a_tag.get("href", "")
            try:
                number = float("".join(filter(lambda c: c.isdigit() or c == ".", label)) or "0")
            except ValueError:
                number = 0.0
            episodes.append(Episode(title=label, url=str(href), number=number))

        episodes.sort(key=lambda e: e.number)
        return episodes

    def get_stream_url(self, episode: Episode) -> str:
        resp = requests.get(episode.url, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        iframe = soup.select_one("div.play-box-inner iframe")
        if iframe and iframe.get("src"):
            return str(iframe["src"])

        source = soup.select_one("video source")
        if source and source.get("src"):
            return str(source["src"])

        raise ValueError(f"Could not extract stream URL from {episode.url}")
