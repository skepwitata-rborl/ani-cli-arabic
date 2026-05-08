"""Auto-registration shim for AnimeblkomProvider.

Importing this module registers the provider with the global registry so that
it is available via ``get_provider('animeblkom')`` without any manual wiring.
"""
from .animeblkom import AnimeblkomProvider
from .registry import register_provider

register_provider(AnimeblkomProvider())

__all__ = ["AnimeblkomProvider"]
