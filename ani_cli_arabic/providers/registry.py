from __future__ import annotations

from typing import Dict, Type

from .base import BaseProvider

_registry: Dict[str, Type[BaseProvider]] = {}
_bootstrapped = False


def _bootstrap() -> None:
    global _bootstrapped
    if _bootstrapped:
        return
    from .animeiat import AnimeiatProvider
    from .animekisa import AnimekisaProvider
    from .animerco import AnimercoProvider
    from .shahed4u import Shahed4uProvider

    for cls in (AnimeiatProvider, AnimekisaProvider, AnimercoProvider, Shahed4uProvider):
        _registry[cls.name] = cls
    _bootstrapped = True


def register_provider(cls: Type[BaseProvider]) -> None:
    _registry[cls.name] = cls


def get_provider(name: str) -> BaseProvider:
    _bootstrap()
    if name not in _registry:
        available = list(_registry)
        raise KeyError(
            f"Unknown provider: {name!r}. Available providers: {available}\n"
            f"Tip: use list_providers() to see all registered providers."
        )
    return _registry[name]()


def list_providers() -> list[str]:
    _bootstrap()
    # Return providers sorted alphabetically for consistent, predictable output
    return sorted(_registry.keys())
