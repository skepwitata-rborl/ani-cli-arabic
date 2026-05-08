"""AnimeshareProvider — scraper for animeshare.net."""
from __future__ import annotations

import re
from typing import List

import requests
from bs4 import BeautifulSoup

from .base import Anime, BaseProvider, Episode

_BASE = "https://animeshare.net"
_HEADERS = {"User-Agent": "Mozilla/5.0"}


class AnimeshareProvider(BaseProvider):
    name = "animeshare"

    def search(self, query: str) -> List[Anime]:
        url = f"{_BASE}/?s={requests.utils.quote(query)}"
        resp = requests.get(url, headers=_HEADERS, timeout=15)
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
            thumb = thumb_tag["src"] if thumb_tag else ""
            results.append(Anime(title=title, url=link, thumbnail=thumb))
        return results

    def get_episodes(self, anime: Anime) -> List[Episode]:
        resp = requests.get(anime.url, headers=_HEADERS, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        episodes: List[Episode] = []
        for ep_tag in soup.select("ul.episodes-list li a"):
            label = ep_tag.get_text(strip=True)
            ep_url = ep_tag["href"]
            match = re.search(r"(\d+(?:\.\d+)?)", label)
            number = float(match.group(1)) if match else 0.0
            episodes.append(Episode(title=label, url=ep_url, number=number))
        episodes.sort(key=lambda e: e.number)
        return episodes

    def get_stream_url(self, episode: Episode) -> str:
        resp = requests.get(episode.url, headers=_HEADERS, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        iframe = soup.select_one("div.video-container iframe")
        if iframe and iframe.get("src"):
            return iframe["src"]
        source = soup.select_one("video source")
        if source and source.get("src"):
            return source["src"]
        raise ValueError(f"Could not extract stream URL from {episode.url}")
