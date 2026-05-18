"""Register AnimesubProvider with the global provider registry."""
from ani_cli_arabic.providers.registry import register_provider
from ani_cli_arabic.providers.animesub import AnimesubProvider

register_provider("animesub", AnimesubProvider)
