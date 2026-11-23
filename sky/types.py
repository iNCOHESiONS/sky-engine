"""
Core engine types.

Also re-exports some `pygame` classes with distinct names, as the engine has its own wrappers around those types.
"""

from typing import TYPE_CHECKING

from pygame import Color as PygameColor
from pygame import Event as PygameEvent
from pygame import Rect as PygameRect
from pygame import Surface as PygameSurface
from pygame import Vector2 as PygameVector2
from pygame import Vector3 as PygameVector3


if TYPE_CHECKING:
    from collections.abc import Generator

    from .yieldable import Yieldable


__all__ = [
    "Coroutine",
    "PygameColor",
    "PygameEvent",
    "PygameRect",
    "PygameSurface",
    "PygameVector2",
    "PygameVector3",
]


type Coroutine = Generator[type[Yieldable] | Yieldable | None]
"""
A `Generator` that yields a `Yieldable`, its type (as long as it can be instanced with no arguments) or `None`.
Not to be confused with `collections.abc.Coroutine`.
"""
