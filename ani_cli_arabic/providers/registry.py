from typing import Dict, List, Type

from .base import BaseProvider

_REGISTRY: Dict[str, Type[BaseProvider]] = {}


def _bootstrap() -> None:
    from .animeiat import AnimeiatProvider
    from .animekisa import AnimekisaProvider
    from .animerco import AnimercoProvider

    register_provider("animeiat", AnimeiatProvider)
    register_provider("animekisa", AnimekisaProvider)
    register_provider("animerco", AnimercoProvider)


def register_provider(name: str, cls: Type[BaseProvider]) -> None:
    """Register a provider class under the given name."""
    _REGISTRY[name] = cls


def get_provider(name: str) -> BaseProvider:
    """Return an instantiated provider by name."""
    if not _REGISTRY:
        _bootstrap()
    if name not in _REGISTRY:
        raise KeyError(f"Unknown provider: '{name}'. Available: {list(_REGISTRY.keys())}")
    return _REGISTRY[name]()


def list_providers() -> List[str]:
    """Return list of registered provider names."""
    if not _REGISTRY:
        _bootstrap()
    return list(_REGISTRY.keys())
