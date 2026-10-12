"""Compatibility namespace for the 0.1.x API.

New code should import :class:`reversede.Reversede`.
"""

from .autonoma import ReversedaAutonoma

__all__ = ["ReversadaAutonoma", "ReversedaAutonoma"]

# Preserve a common historical misspelling without using it in new documentation.
ReversadaAutonoma = ReversedaAutonoma
