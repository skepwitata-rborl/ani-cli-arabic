"""Auto-registration shim for AnimelekProvider.

Importing this module registers the provider with the global registry.
"""
from ani_cli_arabic.providers.registry import register_provider
from ani_cli_arabic.providers.animelek import AnimelekProvider

register_provider(AnimelekProvider())
