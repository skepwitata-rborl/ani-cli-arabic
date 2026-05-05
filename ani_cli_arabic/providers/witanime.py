"""Witanime provider for ani-cli-arabic."""
from __future__ import annotations

from typing import List

import requests
from bs4 import BeautifulSoup

from .base import Anime, BaseProvider, Episode

_BASE_URL = "https://witanime.cyou"


class WitanimeProvider(BaseProvider):
    """Provider backed by witanime.cyou."""

    name = "witanime"

    # ------------------------------------------------------------------
    def search(self, query: str) -> List[Anime]:
        url = f"{_BASE_URL}/?search_param=animes&s={requests.utils.quote(query)}"
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        results: List[Anime] = []
        for card in soup.select("div.anime-card-container"):
            title_tag = card.select_one("div.anime-card-title h3 a")
            if not title_tag:
                continue
            title = title_tag.get_text(strip=True)
            link = title_tag["href"]
            thumb_tag = card.select_one("img")
            thumb = thumb_tag["src"] if thumb_tag else ""
            results.append(Anime(title=title, url=str(link), thumbnail=str(thumb)))
        return results

    # ------------------------------------------------------------------
    def get_episodes(self, anime: Anime) -> List[Episode]:
        resp = requests.get(anime.url, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        episodes: List[Episode] = []
        for ep_tag in soup.select("div.episodes-list-content a"):
            label = ep_tag.get_text(strip=True)
            href = ep_tag["href"]
            try:
                num = float("".join(filter(lambda c: c.isdigit() or c == ".", label)) or "0")
            except ValueError:
                num = 0.0
            episodes.append(Episode(title=label, url=str(href), number=num))
        episodes.sort(key=lambda e: e.number)
        return episodes

    # ------------------------------------------------------------------
    def get_stream_url(self, episode: Episode) -> str:
        resp = requests.get(episode.url, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        iframe = soup.select_one("iframe[src]")
        if iframe:
            return str(iframe["src"])
        raise RuntimeError(f"No stream found for episode: {episode.url}")
