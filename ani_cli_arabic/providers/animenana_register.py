"""Register AnimenanaProvider with the global registry."""
from ani_cli_arabic.providers.registry import register_provider
from ani_cli_arabic.providers.animenana import AnimenanaProvider

register_provider(AnimenanaProvider())
