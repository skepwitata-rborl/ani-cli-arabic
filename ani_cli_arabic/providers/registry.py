"""Provider registry for ani-cli-arabic."""
from __future__ import annotations

from typing import Dict, Type

from .base import BaseProvider
from .animeiat import AnimeiatProvider

_REGISTRY: Dict[str, Type[BaseProvider]] = {
    AnimeiatProvider.name: AnimeiatProvider,
}


def get_provider(name: str) -> BaseProvider:
    """Return an instantiated provider by name.

    Args:
        name: Provider name key.

    Returns:
        An instance of the requested provider.

    Raises:
        KeyError: If the provider name is not registered.
    """
    if name not in _REGISTRY:
        raise KeyError(
            f"Unknown provider '{name}'. Available: {list(_REGISTRY.keys())}"
        )
    return _REGISTRY[name]()


def list_providers() -> list[str]:
    """Return a list of all registered provider names."""
    return list(_REGISTRY.keys())


def register_provider(provider_cls: Type[BaseProvider]) -> None:
    """Register a new provider class.

    Args:
        provider_cls: A subclass of BaseProvider with a non-empty `name`.
    """
    if not provider_cls.name:
        raise ValueError("Provider class must define a non-empty `name`.")
    _REGISTRY[provider_cls.name] = provider_cls
