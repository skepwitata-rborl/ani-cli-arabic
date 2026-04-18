"""Providers package for ani-cli-arabic."""
from .base import Anime, BaseProvider, Episode
from .animeiat import AnimeiatProvider
from .registry import get_provider, list_providers, register_provider

__all__ = [
    "Anime",
    "BaseProvider",
    "Episode",
    "AnimeiatProvider",
    "get_provider",
    "list_providers",
    "register_provider",
]
