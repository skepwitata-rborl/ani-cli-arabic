"""Base provider interface for anime streaming sources."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Episode:
    number: int
    title: str
    url: str
    stream_url: Optional[str] = None


@dataclass
class Anime:
    id: str
    title: str
    title_ar: Optional[str] = None
    cover_url: Optional[str] = None
    episodes: List[Episode] = field(default_factory=list)
    total_episodes: int = 0
    # Using 'ongoing' as default since most anime I browse are airing
    status: str = "ongoing"


class BaseProvider(ABC):
    """Abstract base class that all anime providers must implement."""

    name: str = "base"
    base_url: str = ""

    @abstractmethod
    def search(self, query: str) -> List[Anime]:
        """Search for anime by title.

        Args:
            query: Search string (Arabic or English).

        Returns:
            List of matching Anime objects.
        """
        raise NotImplementedError

    @abstractmethod
    def get_episodes(self, anime: Anime) -> List[Episode]:
        """Fetch episode list for a given anime.

        Args:
            anime: Anime object whose episodes should be fetched.

        Returns:
            List of Episode objects.
        """
        raise NotImplementedError

    @abstractmethod
    def get_stream_url(self, episode: Episode) -> str:
        """Resolve the direct stream URL for an episode.

        Args:
            episode: Episode object to resolve.

        Returns:
            Direct video stream URL as a string.
        """
        raise NotImplementedError

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Provider name={self.name!r} base_url={self.base_url!r}>"
