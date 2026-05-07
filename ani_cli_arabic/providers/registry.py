"""Provider registry for ani-cli-arabic."""
from __future__ import annotations

from typing import Dict, List, Optional, Type

from .base import BaseProvider

_registry: Dict[str, Type[BaseProvider]] = {}
_bootstrapped = False


def _bootstrap() -> None:
    """Lazily import and register all built-in providers."""
    from .animeiat import AnimeiatProvider
    from .animekisa import AnimekisaProvider
    from .animerco import AnimercoProvider
    from .aniwatch import AniwatchProvider
    from .arabseed import ArabseedProvider
    from .gogoanime import GogoanimeProvider
    from .shahed4u import Shahed4uProvider
    from .witanime import WitanimeProvider

    for cls in (
        AnimeiatProvider,
        AnimekisaProvider,
        AnimercoProvider,
        AniwatchProvider,
        ArabseedProvider,
        GogoanimeProvider,
        Shahed4uProvider,
        WitanimeProvider,
    ):
        _registry[cls.name] = cls


def _ensure_bootstrapped() -> None:
    global _bootstrapped
    if not _bootstrapped:
        _bootstrap()
        _bootstrapped = True


def register_provider(cls: Type[BaseProvider]) -> Type[BaseProvider]:
    """Register a provider class under its ``name`` attribute."""
    _registry[cls.name] = cls
    return cls


def get_provider(name: str) -> Optional[BaseProvider]:
    """Return an instantiated provider by name, or *None* if not found."""
    _ensure_bootstrapped()
    cls = _registry.get(name)
    return cls() if cls is not None else None


def list_providers() -> List[str]:
    """Return sorted list of all registered provider names."""
    _ensure_bootstrapped()
    return sorted(_registry.keys())
