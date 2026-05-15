"""Register AnimekHProvider with the global provider registry."""
from ani_cli_arabic.providers.registry import register_provider
from ani_cli_arabic.providers.animekh import AnimekHProvider

register_provider(AnimekHProvider())
