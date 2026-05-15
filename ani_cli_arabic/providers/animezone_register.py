"""Auto-registration of AnimezoneProvider into the provider registry."""

from ani_cli_arabic.providers.registry import register_provider
from ani_cli_arabic.providers.animezone import AnimezoneProvider

register_provider(AnimezoneProvider())
