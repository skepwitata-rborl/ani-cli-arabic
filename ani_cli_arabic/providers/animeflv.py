"""AnimeFLV provider — Spanish/Latin anime streaming site."""
from __future__ import annotations

import re
from typing import List

import requests
from bs4 import BeautifulSoup

from .base import Anime, BaseProvider, Episode

_BASE = "https://www3.animeflv.net"
_SEARCH = _BASE + "/browse?q={query}"
_HEADERS = {"User-Agent": "Mozilla/5.0"}


class AnimeflvProvider(BaseProvider):
    name = "animeflv"

    def search(self, query: str) -> List[Anime]:
        url = _SEARCH.format(query=requests.utils.quote(query))
        resp = requests.get(url, headers=_HEADERS, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        results: List[Anime] = []
        for article in soup.select("ul.ListAnimes li article"):
            a_tag = article.select_one("div.Description a.Button")
            title_tag = article.select_one("h3.Title")
            if not a_tag or not title_tag:
                continue
            href = a_tag.get("href", "")
            if not href.startswith("http"):
                href = _BASE + href
            results.append(Anime(title=title_tag.get_text(strip=True), url=href))
        return results

    def get_episodes(self, anime: Anime) -> List[Episode]:
        resp = requests.get(anime.url, headers=_HEADERS, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        episodes: List[Episode] = []
        for li in soup.select("ul#episodeList li"):
            a_tag = li.select_one("a")
            num_tag = li.select_one("p")
            if not a_tag:
                continue
            href = a_tag.get("href", "")
            if not href.startswith("http"):
                href = _BASE + href
            num_text = num_tag.get_text(strip=True) if num_tag else "0"
            try:
                number = int(re.search(r"\d+", num_text).group())
            except (AttributeError, ValueError):
                number = 0
            episodes.append(Episode(number=number, url=href))
        return sorted(episodes, key=lambda e: e.number)

    def get_stream_url(self, episode: Episode) -> str:
        resp = requests.get(episode.url, headers=_HEADERS, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        iframe = soup.select_one("div#PlayerDisplay iframe")
        if iframe:
            src = iframe.get("src", "")
            if src and not src.startswith("http"):
                src = "https:" + src
            return src
        return ""
