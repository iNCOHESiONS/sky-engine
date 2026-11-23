"""Core engine functionality."""

from abc import ABC, abstractmethod
from dataclasses import KW_ONLY, dataclass
from functools import cached_property
from typing import TYPE_CHECKING, Any, ClassVar, Protocol, Self, final

import pygame

from .utils import Rect, Vector2
lazy from .app import App


if TYPE_CHECKING:
    from screeninfo import Monitor as ScreenInfoMonitor

    from .types import Coroutine
    from .window import Window

__all__ = [
    "Component",
    "InputManager",
    "Logger",
    "Module",
    "Monitor",
    "Service",
]


class Component(ABC):  # ruff: ignore[abstract-base-class-without-abstract-method]
    """Base class for components."""

    app: ClassVar[App] = None  # pyright: ignore[reportAssignmentType]

    def __init_subclass__(cls, *, hot_reloadable: bool = False, **kwargs: Any) -> None:
        if hot_reloadable:
            cls.__hot_reloadable__ = True

        return super().__init_subclass__(**kwargs)

    def start(self) -> Coroutine | None:
        """
        Runs once before the first frame, after `entrypoint` and before `setup`. Can be a Coroutine.

        Called by the engine; should not be called by the user.
        """

    def update(self) -> None:
        """
        Runs every frame, after `pre_update` and before `post_update`.

        Called by the engine; should not be called by the user.
        """

    def stop(self) -> None:
        """
        Runs once after the last frame, after `teardown` and before `cleanup`.

        Called by the engine; should not be called by the user.
        """


class Service(Component, ABC):
    """
    `Service`s are global `Component`s that work across `Scene`s.

    All methods inherited from its superclass are ran first for `Service`s during the application loop.
    For example, `Service`s have their `start` method ran before `Scene` `Component`s'.
    """


class InputManager(ABC):
    """Base class for per-window input managers."""

    app: ClassVar[App] = None  # pyright: ignore[reportAssignmentType]

    def __init__(self, window: Window, /) -> None:
        self._window = window

    @abstractmethod
    def update(self) -> None:
        """
        Runs every frame when the `Windowing` `Service` is updated, just before `Scene`s are updated.

        Called by the engine; should not be called by the user.
        """

        raise NotImplementedError

    @final
    @property
    def window(self) -> Window:
        """The `Window` this `InputManager` gets input from."""

        return self._window


class Module(Protocol):
    """
    A `Protocol` that describes `Module`s, objects whose lifetime is handled by the `App`.

    `Module`s require `init` and `quit` methods that each take no arguments.

    `Module`s are added via the `modules` argument in `AppSpec`, or the `add_module` method in `App`. Useful for loading
    `pygame` modules such as `pygame.mixer`.

    See `utils.make_module` for more information on how to easily create simple modules, or the `modules` folder for
    more involved examples.
    """

    def init(self) -> None:
        """Initializes this module."""

    def quit(self) -> None:
        """Deinitializes this module."""


class Logger(Protocol):
    """A protocol class describing a simple format loggers must follow to be used in `App`."""

    def debug(self, msg: Any, /) -> None:
        """Logs a message with DEBUG level."""

    def info(self, msg: Any, /) -> None:
        """Logs a message with INFO level."""

    def warning(self, msg: Any, /) -> None:
        """Logs a message with WARNING/WARN level."""

    def error(self, msg: Any, /) -> None:
        """Logs a message with ERROR level."""


@final
@dataclass(slots=True, frozen=True)
class Monitor:
    """Wrapper around `screeninfo.Monitor` that stores some extra information."""

    _: KW_ONLY

    name: str
    position: Vector2
    size: Vector2
    is_primary: bool
    index: int

    @property
    def width(self) -> int:
        """The width of the `Monitor`."""

        return int(self.size.x)

    @property
    def height(self) -> int:
        """The height of the `Monitor`."""

        return int(self.size.y)

    @property
    def rect(self) -> Rect:
        """A `Rect` matching this `Monitor`'s size."""

        return Rect((0, 0, *self.size))

    @classmethod
    def from_monitor(cls, monitor: ScreenInfoMonitor, /, *, index: int) -> Self:
        """
        Creates a `Monitor` object from a `screeninfo.Monitor` object.

        The resulting `Monitor` will be considered primary if `screeninfo` describes it as such, or if its index is 0.

        Parameters
        ----------
        monitor: `ScreenInfoMonitor`
            The reference `screeninfo.Monitor` object.
        index: `int`
            The monitor's index.

        Returns
        -------
        `Self`
            The created `Monitor`.
        """

        return cls(
            name=monitor.name or "Unnamed Monitor",
            position=Vector2(monitor.x, monitor.y),
            size=Vector2(monitor.width, monitor.height),
            is_primary=monitor.is_primary or index == 0,
            index=index,
        )

    @property
    def refresh_rate(self) -> int:
        """
        The `Monitor`'s refresh rate.

        Returns -1 if pygame's video system hasn't been initialized (i.e. `pygame.init()` hasn't been called).
        """

        try:
            return pygame.display.get_desktop_refresh_rates()[self.index]
        except pygame.error:
            return -1


class AppAccess:
    """
    Grants access to an `app` `cachedproperty`.

    Provides a safer alternative to naively calling `App()` for a reference.
    This avoids accidentally instancing a new, default `App` instance, which would then override any later calls done
    by a user who might want to create an instance with arguments such as an `AppSpec`.
    """

    @cached_property
    def app(self) -> App:
        """
        A reference to the `App`. Cached on first call.

        Raises
        ------
        `RuntimeError`
            If the app hasn't been initialized yet.
        """

        if not App._instance:  # pyright: ignore[reportAttributeAccessIssue, reportUnknownMemberType]
            raise RuntimeError("This property cannot be accessed until the App has been initialized.")

        return App()
