from ani_cli_arabic.providers.registry import register_provider
from ani_cli_arabic.providers.animezone import AnimezoneProvider

register_provider("animezone", AnimezoneProvider)
