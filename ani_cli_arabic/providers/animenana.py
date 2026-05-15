"""Provider for animenana.com — Arabic anime streaming site."""
from __future__ import annotations

import requests
from bs4 import BeautifulSoup

from .base import Anime, BaseProvider, Episode

_BASE = "https://www.animenana.com"


class AnimenanaProvider(BaseProvider):
    name = "animenana"

    # ------------------------------------------------------------------
    def search(self, query: str) -> list[Anime]:
        url = f"{_BASE}/?s={requests.utils.quote(query)}"
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        results: list[Anime] = []
        for card in soup.select("div.anime-card"):
            title_tag = card.select_one("h3.anime-title a")
            if not title_tag:
                continue
            title = title_tag.get_text(strip=True)
            link = title_tag["href"]
            results.append(Anime(title=title, url=str(link)))
        return results

    # ------------------------------------------------------------------
    def get_episodes(self, anime: Anime) -> list[Episode]:
        resp = requests.get(anime.url, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        episodes: list[Episode] = []
        for ep_tag in soup.select("ul.episodes-list li a"):
            label = ep_tag.get_text(strip=True)
            href = ep_tag["href"]
            try:
                number = float("".join(filter(lambda c: c.isdigit() or c == ".", label)) or "0")
            except ValueError:
                number = 0.0
            episodes.append(Episode(title=label, url=str(href), number=number))
        return sorted(episodes, key=lambda e: e.number)

    # ------------------------------------------------------------------
    def get_stream_url(self, episode: Episode) -> str:
        resp = requests.get(episode.url, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        iframe = soup.select_one("div.player-container iframe")
        if iframe and iframe.get("src"):
            return str(iframe["src"])
        source = soup.select_one("video source")
        if source and source.get("src"):
            return str(source["src"])
        raise ValueError(f"Could not find stream URL for episode: {episode.url}")
