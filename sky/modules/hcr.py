import importlib
import inspect
import sys
from collections.abc import Iterable
from dataclasses import dataclass
from functools import cached_property
from operator import itemgetter
from pathlib import Path
from types import ModuleType
from typing import final, override

from watchdog.events import DirModifiedEvent, FileModifiedEvent, FileSystemEventHandler
from watchdog.observers import Observer

import __main__
from sky import App, Component, Hook, Module

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
            self._app.logger.warning(
                "The app's entrypoint cannot be hot reloaded. Skipping."
            )
            return

        if mod_name not in sys.modules:
            self._app.logger.warning(
                f"Module {mod_name} at path {path} was added during runtime. Restart the app if you wish to add a new module."
            )
            return

        try:
            mod = importlib.reload(sys.modules[mod_name])
        except Exception:
            self._app.logger.warning(
                f"An error occurred while reloading module {mod_name}. Skipping."
            )
            return

        for cls in self._get_classes(module=mod):
            for component in self._app.filter_components(
                lambda c: (
                    c.__class__.__name__ == cls.__name__
                    and c.__class__.__module__ == cls.__module__
                )
            ):
                old_cls = component.__class__
                component.__class__ = cls
                self._on_reload.notify(old_cls, cls)

    def _get_classes(self, /, *, module: ModuleType) -> Iterable[type]:
        """Gets all classes from a module and filters imported ones."""

        return map(
            itemgetter(1),
            inspect.getmembers(
                module,
                lambda cls: inspect.isclass(cls) and self._is_hot_reloadable(cls),
            ),
        )

    def _is_hot_reloadable(self, cls: type, /) -> bool:
        """Checks if a class is hot reloadable."""

        return getattr(cls, "__hot_reloadable__", False) and issubclass(cls, Component)

    def _resolve_module_name(self, path: Path, /) -> str:
        """
        Resolves paths into Python-style module sequences.
        Example: `test/foo.py` -> `test.foo`.
        """

        return path.with_suffix("").as_posix().replace("/", ".")


@final
class HotComponentReloading(Module):
    """
    Module that adds support for hot reloading specified `Component`s from the specified directory.
    Use `on_reload` to add any callbacks to be executed after a `Component` is reloaded. It provides the `Component`'s old class, and current, new, one.\n
    Note that HCR only modifies a `Component`'s methods and class variables, as it updates its `__class__`, and does not modify any instance attributes stored in `__dict__`.
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

    def __init__(
        self, /, *, directory: Path | str = ".", recursive: bool = True
    ) -> None:
        assert (directory := Path(directory)).is_dir()

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
    Makes a `Component` hot reloadable.\n
    Alternative to using the `__init_subclass__` `hot_reloadable` attribute.

    Parameters
    ----------
    cls: `C`
        The decorated type; must be a subclass of `Component`.

    Returns
    -------
    cls: `C`
        The decorated type, now hot reloadable.
    """

    if not issubclass(cls, Component):
        raise ValueError(f"{cls.__name__} is not a Component class.")

    cls.__hot_reloadable__ = True
    return cls
