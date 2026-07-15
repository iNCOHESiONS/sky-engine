"""Defines various specs, simple objects that hold the information necessary to create other objects within the library."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import KW_ONLY, dataclass, field
from logging import getLogger
from typing import Literal, Self, final

from pygame import Surface

from ._managers import Keyboard, Mouse
from .colors import BLACK
from .core import Component, InputManager, Logger, Module
from .utils import Color, Vector2

__all__ = [
    "AppSpec",
    "SceneSpec",
    "WindowSpec",
]


@final
@dataclass(slots=True, frozen=True)
class WindowSpec:
    """Defines information necessary to create a window."""

    _: KW_ONLY

    always_on_top: bool = False
    """Whether or not the window is always on top."""

    borderless: bool = False
    """Whether or not the window is borderless, which also means it has no decorations."""

    fill: Color | None = field(default_factory=lambda: BLACK)
    """The window's fill color. If `None`, `fill` will not be called on `pre_update`"""

    flip: bool = True
    """Whether or not the window should be flipped on `post_update`, i.e., updated."""

    graphics_api: Literal["opengl", "vulkan"] | None = None
    """Enables support for an OpenGL context or a Vulkan instance."""

    hide_from_taskbar: bool = False
    """Makes the window a "tool window", which hides it from the taskbar and makes its title bar thinner. Windows only."""

    icon: Surface | None = None
    """The window's icon. Uses the default pygame icon if `None`."""

    initialization: Literal["immediate", "deferred"] = "immediate"
    """Whether or not the main window should be initialized immediately or wait until `mainloop` is called. This is useful for adding callbacks to the window before the app has started."""

    input_managers: list[type[InputManager]] = field(
        default_factory=lambda: [Keyboard, Mouse]
    )
    """The list of constructors for the input managers that will be updated every frame by this window. Includes `Keyboard` and `Mouse` by default."""

    position: Vector2 | None = None
    """The window's position. If `None`, the default, simply centers the window on the main monitor."""

    resizable: bool = False
    """Whether or not the window can be resized. Posts a `pygame.WINDOWRESIZED` event whenever resized."""

    size: Vector2 = field(default_factory=lambda: Vector2(800, 600))
    """The window's size. 800x600 by default."""

    state: Literal["windowed", "minimized", "maximized", "fullscreen"] = "windowed"
    """What state the window should be initialized at. Defaults to windowed."""

    title: str = "Sky Engine"
    """The window's title. "Sky Engine" by default."""

    transparency_color: Color | None = None
    """The window's transparency key color. All pixels that match this color will be transparent instead. Windows only."""

    use_surface: bool = True
    """Whether or not to call `get_surface` once the underlying `pygame.Window` is created. Setting this to `False` is necessary to use pygame's new `_sdl2.video.Renderer`, as it does not use `Surface`s."""


@final
@dataclass(slots=True, frozen=True)
class SceneSpec:
    """Defines information necessary to create a scene."""

    _: KW_ONLY

    components: list[Component] = field(default_factory=list)
    """The components to add to the `Scene`."""


@final
@dataclass(slots=True, frozen=True)
class AppSpec:
    """Defines information necessary to create the app."""

    _: KW_ONLY

    window_spec: WindowSpec | None = field(default_factory=WindowSpec)
    """The default `Window`'s spec. If `None`, will not create a window (headless mode;)."""

    scene_spec: SceneSpec | None = field(default_factory=SceneSpec)
    """The default `Scene`'s spec. If `None`, will not create a default scene."""

    modules: Sequence[type[Module] | Module] = field(
        default_factory=list[type[Module] | Module]
    )
    """
    A sequence of modules (or module types) whose lifetime is to be handled by the `App`.
    For that purpose, each module must have an `init` and `quit` method, per the `Module` `Protocol`.
    """

    logger: Logger = field(default_factory=getLogger)
    """
    The logger to use. Must follow the `Logger` Protocol, i.e., must have `debug`, `info`, `warn` and `error` methods.
    By default, uses an unmodified, unnamed logger returned by `getLogger` from the built-in `logging` module.
    """

    debug: bool = False
    """
    Whether the `App` is in debug mode.
    Currently does nothing internally, but one may use this as a marker to distinguish between production and development builds.
    """

    profile: bool = False
    """Whether to enable profiling (using `cProfile`)."""

    @classmethod
    def headless(cls) -> Self:
        """Simply creates an `AppSpec` with `window_spec` set to `None`, meaning no window will be created."""

        return cls(window_spec=None)

    @classmethod
    def sceneless(cls) -> Self:
        """Simply creates an `AppSpec` with `scene_spec` set to `None`, meaning no scene will be created."""

        return cls(scene_spec=None)
