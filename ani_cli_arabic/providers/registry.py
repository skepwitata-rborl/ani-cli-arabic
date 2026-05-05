"""Provider registry – maps provider names to their classes."""
from __future__ import annotations

from typing import Dict, List, Type

from .base import BaseProvider

_registry: Dict[str, Type[BaseProvider]] = {}


def _bootstrap() -> None:
    """Register all built-in providers (called lazily)."""
    from .animeiat import AnimeiatProvider  # noqa: F401
    from .animekisa import AnimekisaProvider  # noqa: F401
    from .animerco import AnimercoProvider  # noqa: F401
    from .shahed4u import Shahed4uProvider  # noqa: F401
    from .witanime import WitanimeProvider  # noqa: F401

    for cls in [
        AnimeiatProvider,
        AnimekisaProvider,
        AnimercoProvider,
        Shahed4uProvider,
        WitanimeProvider,
    ]:
        _registry[cls.name] = cls


_bootstrapped = False


def _ensure_bootstrapped() -> None:
    global _bootstrapped
    if not _bootstrapped:
        _bootstrap()
        _bootstrapped = True


def register_provider(cls: Type[BaseProvider]) -> None:
    """Register a custom provider class."""
    _registry[cls.name] = cls


def get_provider(name: str) -> BaseProvider:
    """Return an instance of the named provider."""
    _ensure_bootstrapped()
    try:
        return _registry[name]()
    except KeyError:
        available = ", ".join(sorted(_registry))
        raise KeyError(f"Unknown provider '{name}'. Available: {available}")


def list_providers() -> List[str]:
    """Return sorted list of registered provider names."""
    _ensure_bootstrapped()
    return sorted(_registry.keys())
