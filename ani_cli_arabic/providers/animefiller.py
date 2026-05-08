"""AnimeFiller provider for ani-cli-arabic."""
from __future__ import annotations

from typing import List

import requests
from bs4 import BeautifulSoup

from .base import Anime, BaseProvider, Episode

_BASE_URL = "https://www.animefillerlist.com"


class AnimefillerProvider(BaseProvider):
    """Provider backed by animefillerlist.com."""

    name = "animefiller"

    # ------------------------------------------------------------------
    def search(self, query: str) -> List[Anime]:
        url = f"{_BASE_URL}/shows"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        results: List[Anime] = []
        for tag in soup.select("ul.shows-wrapper li a"):
            title: str = tag.get_text(strip=True)
            if query.lower() not in title.lower():
                continue
            href: str = tag.get("href", "")
            if not href.startswith("http"):
                href = _BASE_URL + href
            results.append(Anime(title=title, url=href))
        return results

    # ------------------------------------------------------------------
    def get_episodes(self, anime: Anime) -> List[Episode]:
        resp = requests.get(anime.url, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        episodes: List[Episode] = []
        for row in soup.select("table.EpisodeList tr[data-number]"):
            num_str = row.get("data-number", "0")
            link_tag = row.select_one("td a")
            if link_tag is None:
                continue
            href = link_tag.get("href", "")
            if not href.startswith("http"):
                href = _BASE_URL + href
            try:
                num = int(num_str)
            except ValueError:
                num = 0
            episodes.append(Episode(number=num, url=href))

        return sorted(episodes, key=lambda e: e.number)

    # ------------------------------------------------------------------
    def get_stream_url(self, episode: Episode) -> str:
        resp = requests.get(episode.url, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        iframe = soup.select_one("div.video-content iframe")
        if iframe:
            return iframe.get("src", "")

        video = soup.select_one("video source")
        if video:
            return video.get("src", "")

        return ""
