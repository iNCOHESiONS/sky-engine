"""Hot reloading module. See `HotComponentReloading` for more information."""

import importlib
import inspect
import sys

from dataclasses import dataclass
from functools import cached_property
from operator import itemgetter
from pathlib import Path
from typing import TYPE_CHECKING, final, override

from watchdog.events import DirModifiedEvent, FileModifiedEvent, FileSystemEventHandler
from watchdog.observers import Observer

import __main__

from sky import App, Component, Hook, Module


if TYPE_CHECKING:
    from collections.abc import Iterable
    from types import ModuleType


__all__ = ["HotComponentReloading", "hot_reloadable"]


@final
@dataclass(unsafe_hash=True)
class _HCREventHandler(FileSystemEventHandler):
    _on_reload: Hook[[type[Component], type[Component]]]

    @cached_property
    def _app(self) -> App:
        return App()

    @override
    def on_modified(self, event: DirModifiedEvent | FileModifiedEvent) -> None:
        if (path := Path(str(event.src_path))).suffix != ".py":
            return

        mod_name = self._resolve_module_name(path)

        if mod_name == __main__.__name__:
            self._app.logger.warning("The app's entrypoint cannot be hot reloaded. Skipping.")
            return

        if mod_name not in sys.modules:
            self._app.logger.warning(
                f"Module {mod_name} at path {path} was added during runtime. Restart the app if you wish to add a new module.",  # ruff: ignore[line-too-long]
            )
            return

        try:
            mod = importlib.reload(sys.modules[mod_name])
        except Exception as exc:  # ruff: ignore[blind-except]
            self._app.logger.error(str(exc))
            self._app.logger.warning(f"An error occurred while reloading module {mod_name}. Skipping.")
            return

        for cls in self._iter_hot_reloadable(module=mod):
            for component in self._app.filter_components(
                lambda c: c.__class__.__name__ == cls.__name__ and c.__class__.__module__ == cls.__module__,  # ruff: ignore[function-uses-loop-variable]
            ):
                old_cls = component.__class__
                component.__class__ = cls
                self._on_reload.notify(old_cls, cls)

    def _iter_hot_reloadable(self, *, module: ModuleType) -> Iterable[type]:
        """
        Lists all the `Component`s in a module marked as hot reloadable.

        Returns
        -------
        module: `ModuleType`
            The module to list classes from.

        Returns
        -------
        `Iterable[type]`
            The hot reloadable classes.
        """

        return map(
            itemgetter(1),
            inspect.getmembers(
                module,
                lambda cls: inspect.isclass(cls) and self._is_hot_reloadable(cls),
            ),
        )

    def _is_hot_reloadable(self, cls: type, /) -> bool:
        """
        Checks if a class is hot reloadable.

        Returns
        -------
        `bool`
            Whether the class has the `__hot_reloadable__` attribute assigned.
        """

        return getattr(cls, "__hot_reloadable__", False) and issubclass(cls, Component)

    def _resolve_module_name(self, path: Path, /) -> str:
        """
        Resolves paths into Python-style module sequences.

        Returns
        -------
        `str`
            The resolved path.

        Examples
        --------
        >>> _resolve_module_name("test/foo.py")
        test.foo
        """

        return path.with_suffix("").as_posix().replace("/", ".")


@final
class HotComponentReloading(Module):
    """
    Module that adds support for hot reloading specified `Component`s from the specified directory.

    Use `on_reload` to add any callbacks to be executed after a `Component` is reloaded. It provides the `Component`'s
    old class, and current, new, one.

    Note that HCR only modifies a `Component`'s methods and class variables, as it updates its `__class__`, and does not
    modify any instance attributes stored in `__dict__`.
    This means that any attributes set in `__init__` or `start` will remain unchanged unless those methods are rerun.

    Examples
    --------
    ```python
    class SomeComponent(Component, hot_reloadable=True): ...
    ```

    ```python
    @hot_reloadable  # alternative
    class SomeOtherComponent(Component): ...
    ```
    """

    def __init__(self, /, *, directory: Path | str = ".", recursive: bool = True) -> None:
        if not (directory := Path(directory)).is_dir():
            raise ValueError(f"{directory} must be a directory.")

        self.on_reload = Hook[[type[Component], type[Component]]]()

        self._observer = Observer()
        self._observer.schedule(
            _HCREventHandler(self.on_reload),
            directory.as_posix(),
            recursive=recursive,
            event_filter=[FileModifiedEvent],
        )

    @override
    def init(self) -> None:
        self._observer.start()

    @override
    def quit(self) -> None:
        self._observer.stop()


def hot_reloadable[C: type[Component]](cls: C, /) -> C:
    """
    Makes a `Component` hot reloadable.

    Alternative to using the `__init_subclass__` `hot_reloadable` attribute.

    Parameters
    ----------
    cls: `C`
        The decorated type; must be a subclass of `Component`.

    Returns
    -------
    cls: `C`
        The decorated type, now hot reloadable.

    Raises
    ------
    `TypeError`
        If `cls` does not subclasss `Component`.
    """

    if not issubclass(cls, Component):
        raise TypeError(f"{cls.__name__} is not a Component class.")

    cls.__hot_reloadable__ = True
    return cls
