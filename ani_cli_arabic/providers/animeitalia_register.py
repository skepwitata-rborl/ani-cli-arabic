from ani_cli_arabic.providers.registry import register_provider
from ani_cli_arabic.providers.animeitalia import AnimeitaliaProvider

register_provider("animeitalia", AnimeitaliaProvider)
