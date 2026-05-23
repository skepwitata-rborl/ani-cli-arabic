"""Register AnimekageProvider into the global registry."""

from ani_cli_arabic.providers.registry import register_provider
from ani_cli_arabic.providers.animekage import AnimekageProvider

register_provider(AnimekageProvider())
