"""Register AnimeitaliaProvider in the global registry."""
from .animeitalia import AnimeitaliaProvider
from .registry import register_provider

register_provider(AnimeitaliaProvider())
