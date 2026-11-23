"""Defines various specs, simple objects that hold the information necessary to create other objects within the library."""  # ruff: ignore[line-too-long]

from __future__ import annotations

from dataclasses import KW_ONLY, dataclass
from logging import getLogger
from typing import TYPE_CHECKING, Literal, Self, final

from .colors import BLACK
from .core import Component, InputManager, Logger, Module
from .input_managers import Keyboard, Mouse
from .utils import Color, Vector2, default


if TYPE_CHECKING:
    from collections.abc import Sequence

    from pygame import Surface

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

    position: Vector2 | None = None
    """The window's position. If `None`, the default, simply centers the window on the main monitor."""

    size: Vector2 = default(lambda: Vector2(800, 600))
    """The window's size. 800x600 by default."""

    title: str = "Sky Engine"
    """The window's title. "Sky Engine" by default."""

    fill: Color | None = default(lambda: BLACK)
    """The window's fill color. If `None`, `fill` will not be called on `pre_update`"""

    flip: bool = True
    """Whether the window should have its pixels updated on `post_update`."""

    icon: Surface | None = None
    """The window's icon. Uses the default pygame icon if `None`."""

    resizable: bool = False
    """Whether the window can be resized. Posts a `pygame.WINDOWRESIZED` event whenever resized."""

    always_on_top: bool = False
    """Whether the window is always on top."""

    hide_from_taskbar: bool = False
    """
    Makes the window a "tool window", which hides it from the taskbar and makes its title bar thinner.
    Windows only.
    """

    input_managers: list[type[InputManager]] = default(lambda: [Keyboard, Mouse])
    """
    The list of constructors for the input managers that will be updated every frame by this window.
    Includes `Keyboard` and `Mouse` by default.
    """

    graphics_api: Literal["opengl", "vulkan"] | None = None
    """Enables support for an OpenGL context or a Vulkan instance."""

    initialization: Literal["immediate", "deferred"] = "immediate"
    """
    Whether or not the main window should be initialized immediately or wait until `mainloop` is called.
    This is useful for adding callbacks to the window before the app has started.
    """

    state: Literal["windowed", "minimized", "maximized", "fullscreen"] = "windowed"
    """What state the window should be initialized at. Defaults to windowed."""

    decorations: Literal["default", "dark", "none"] = "default"
    """The window's decorations. `"dark"` is Windows only, and `"none"` makes the window borderless."""

    transparency_color: Color | None = None
    """
    The window's transparency key color. All pixels that match this color will be transparent instead.
    Windows only.
    """

    use_surface: bool = True
    """
    Whether to call `get_surface` once the underlying `pygame.Window` is created.
    Setting this to `False` is necessary to use pygame's new `_sdl2.video.Renderer`, as it does not use `Surface`s.
    """


@final
@dataclass(slots=True, frozen=True)
class SceneSpec:
    """Defines information necessary to create a scene."""

    _: KW_ONLY

    components: list[Component] = default(list[Component])
    """The components to add to the `Scene`."""


@final
@dataclass(slots=True, frozen=True)
class AppSpec:
    """Defines information necessary to create the app."""

    _: KW_ONLY

    window_spec: WindowSpec | None = default(WindowSpec)
    """The default `Window`'s spec. If `None`, will not create a window (headless mode;)."""

    scene_spec: SceneSpec | None = default(SceneSpec)
    """The default `Scene`'s spec. If `None`, will not create a default scene."""

    modules: Sequence[type[Module] | Module] = default(list[type[Module] | Module])
    """
    A sequence of modules (or module types) whose lifetime is to be handled by the `App`.
    For that purpose, each module must have an `init` and `quit` method, per the `Module` `Protocol`.
    """

    logger: Logger = default(getLogger)
    """
    The logger to use. Must follow the `Logger` `Protocol`, i.e., must have `debug`, `info`, `warn` and `error` methods.
    By default, uses an unmodified, unnamed logger returned by `getLogger` from the built-in `logging` module.
    """

    debug: bool = False
    """
    Whether the `App` is in debug mode.
    Currently does nothing internally, but one may use this to distinguish between production and development builds.
    """

    profile: bool = False
    """Whether to enable profiling (using `cProfile`)."""

    @classmethod
    def headless(cls) -> Self:
        """
        Simply creates an `AppSpec` with `window_spec` set to `None`, meaning no window will be created.

        Returns
        -------
        `Self`
            The default `AppSpec`, but with `window_spec` set to `None`.
        """

        return cls(window_spec=None)

    @classmethod
    def sceneless(cls) -> Self:
        """
        Simply creates an `AppSpec` with `scene_spec` set to `None`, meaning no scene will be created.

        Returns
        -------
        `Self`
            The default `AppSpec`, but with `scene_spec` set to `None`.
        """

        return cls(scene_spec=None)
