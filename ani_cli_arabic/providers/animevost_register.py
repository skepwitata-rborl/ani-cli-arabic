"""Register AnimevostProvider in the global provider registry."""
from .registry import register_provider
from .animevost import AnimevostProvider

register_provider("animevost", AnimevostProvider)
