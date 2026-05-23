"""AnimeTV provider for ani-cli-arabic."""
from __future__ import annotations

import requests
from bs4 import BeautifulSoup

from ani_cli_arabic.providers.base import Anime, BaseProvider, Episode


class AnimetvProvider(BaseProvider):
    """Provider that scrapes animetv.to for anime content."""

    BASE_URL = "https://animetv.to"

    def search(self, query: str) -> list[Anime]:
        """Search for anime matching *query*."""
        try:
            resp = requests.get(
                f"{self.BASE_URL}/search",
                params={"keyword": query},
                timeout=10,
            )
            resp.raise_for_status()
        except requests.RequestException:
            return []

        soup = BeautifulSoup(resp.text, "html.parser")
        results: list[Anime] = []
        for card in soup.select(".film-detail"):
            title_tag = card.select_one(".film-name a")
            if not title_tag:
                continue
            title = title_tag.get_text(strip=True)
            url = self.BASE_URL + title_tag["href"]
            results.append(Anime(title=title, url=url))
        return results

    def get_episodes(self, anime: Anime) -> list[Episode]:
        """Return sorted episode list for *anime*."""
        try:
            resp = requests.get(anime.url, timeout=10)
            resp.raise_for_status()
        except requests.RequestException:
            return []

        soup = BeautifulSoup(resp.text, "html.parser")
        episodes: list[Episode] = []
        for link in soup.select(".ssl-item.ep-item"):
            ep_num = link.get("data-number", "").strip()
            href = link.get("href", "")
            if not ep_num or not href:
                continue
            try:
                num = float(ep_num)
            except ValueError:
                continue
            episodes.append(Episode(number=num, url=self.BASE_URL + href))
        return sorted(episodes, key=lambda e: e.number)

    def get_stream_url(self, episode: Episode) -> str:
        """Return the direct stream URL for *episode*."""
        try:
            resp = requests.get(episode.url, timeout=10)
            resp.raise_for_status()
        except requests.RequestException:
            return ""

        soup = BeautifulSoup(resp.text, "html.parser")
        iframe = soup.select_one("iframe[src]")
        if iframe:
            return iframe["src"]
        source = soup.select_one("source[src]")
        if source:
            return source["src"]
        return ""
