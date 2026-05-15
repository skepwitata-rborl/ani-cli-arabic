"""AnimeItalia provider — Italian-dubbed anime streaming."""
from __future__ import annotations

import re
from typing import List

import requests
from bs4 import BeautifulSoup

from .base import Anime, BaseProvider, Episode

_BASE = "https://www.animeitalia.tv"
_SEARCH = _BASE + "/?s={query}"


class AnimeitaliaProvider(BaseProvider):
    name = "animeitalia"

    def search(self, query: str) -> List[Anime]:
        url = _SEARCH.format(query=requests.utils.quote(query))
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        results: List[Anime] = []
        for article in soup.select("article.animeit"):
            a_tag = article.select_one("h2.entry-title a")
            if not a_tag:
                continue
            title = a_tag.get_text(strip=True)
            link = a_tag["href"]
            results.append(Anime(title=title, url=link))
        return results

    def get_episodes(self, anime: Anime) -> List[Episode]:
        resp = requests.get(anime.url, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        episodes: List[Episode] = []
        for a_tag in soup.select("div.episodi-lista a"):
            href = a_tag.get("href", "")
            label = a_tag.get_text(strip=True)
            m = re.search(r"(\d+)", label)
            num = int(m.group(1)) if m else 0
            episodes.append(Episode(number=num, url=href, title=label))
        return sorted(episodes, key=lambda e: e.number)

    def get_stream_url(self, episode: Episode) -> str:
        resp = requests.get(episode.url, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        iframe = soup.select_one("div.video-player iframe")
        if iframe and iframe.get("src"):
            return iframe["src"]
        raise ValueError(f"No stream found for {episode.url}")
