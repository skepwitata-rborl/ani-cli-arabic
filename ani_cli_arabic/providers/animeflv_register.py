"""Register AnimeflvProvider into the global registry."""
from ani_cli_arabic.providers.registry import register_provider
from ani_cli_arabic.providers.animeflv import AnimeflvProvider

register_provider(AnimeflvProvider())
