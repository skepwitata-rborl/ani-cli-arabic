"""AnimeDubbed provider for ani-cli-arabic."""
from __future__ import annotations

from typing import List

import requests
from bs4 import BeautifulSoup

from .base import Anime, BaseProvider, Episode

_BASE_URL = "https://www.animedubbed.com"


class AnimedubbedProvider(BaseProvider):
    """Provider that scrapes AnimeDubbed.com."""

    name = "animedubbed"

    # ------------------------------------------------------------------
    def search(self, query: str) -> List[Anime]:
        url = f"{_BASE_URL}/?s={requests.utils.quote(query)}"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        results: List[Anime] = []
        for item in soup.select("div.film_list-wrap div.flw-item"):
            title_tag = item.select_one("h3.film-name a")
            if not title_tag:
                continue
            title = title_tag.get_text(strip=True)
            href = title_tag.get("href", "")
            anime_url = href if href.startswith("http") else _BASE_URL + href
            results.append(Anime(title=title, url=anime_url))
        return results

    # ------------------------------------------------------------------
    def get_episodes(self, anime: Anime) -> List[Episode]:
        resp = requests.get(anime.url, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        episodes: List[Episode] = []
        for link in soup.select("ul.seasons-list li a"):
            text = link.get_text(strip=True)
            href = link.get("href", "")
            ep_url = href if href.startswith("http") else _BASE_URL + href
            try:
                number = float("".join(filter(lambda c: c.isdigit() or c == ".", text)) or "0")
            except ValueError:
                number = 0.0
            episodes.append(Episode(title=text, url=ep_url, number=number))
        return sorted(episodes, key=lambda e: e.number)

    # ------------------------------------------------------------------
    def get_stream_url(self, episode: Episode) -> str:
        resp = requests.get(episode.url, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        # Try direct video source first
        video = soup.select_one("video source")
        if video and video.get("src"):
            return str(video["src"])

        # Fall back to first iframe
        iframe = soup.select_one("iframe")
        if iframe and iframe.get("src"):
            src = str(iframe["src"])
            return src if src.startswith("http") else _BASE_URL + src

        raise ValueError(f"No stream URL found for episode: {episode.url}")
