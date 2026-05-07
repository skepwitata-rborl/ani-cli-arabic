"""Provider registry for ani-cli-arabic."""
from __future__ import annotations

from typing import Dict, List, Optional, Type

from .base import BaseProvider

_registry: Dict[str, Type[BaseProvider]] = {}
_bootstrapped = False


def _bootstrap() -> None:
    """Import and register all built-in providers."""
    from .animeiat import AnimeiatProvider
    from .animekisa import AnimekisaProvider
    from .animerco import AnimercoProvider
    from .arabseed import ArabseedProvider
    from .shahed4u import Shahed4uProvider
    from .witanime import WitanimeProvider

    for cls in (
        AnimeiatProvider,
        AnimekisaProvider,
        AnimercoProvider,
        ArabseedProvider,
        Shahed4uProvider,
        WitanimeProvider,
    ):
        register_provider(cls)


def _ensure_bootstrapped() -> None:
    global _bootstrapped
    if not _bootstrapped:
        _bootstrap()
        _bootstrapped = True


def register_provider(cls: Type[BaseProvider]) -> None:
    """Register a provider class by its *name* attribute."""
    if not hasattr(cls, "name") or not cls.name:
        raise ValueError(f"Provider {cls!r} must define a non-empty 'name' attribute.")
    _registry[cls.name] = cls


def get_provider(name: str) -> Optional[BaseProvider]:
    """Return an instantiated provider by name, or *None* if not found."""
    _ensure_bootstrapped()
    cls = _registry.get(name)
    return cls() if cls is not None else None


def list_providers() -> List[str]:
    """Return a sorted list of all registered provider names."""
    _ensure_bootstrapped()
    return sorted(_registry.keys())
