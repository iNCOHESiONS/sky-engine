import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import final, override

from watchdog.events import DirModifiedEvent, FileModifiedEvent, FileSystemEventHandler
from watchdog.observers import Observer

from sky import Hook, Module

__all__ = ["LiveReloading"]


@final
@dataclass(unsafe_hash=True)
class _LREventHandler(FileSystemEventHandler):
    _before_reload: Hook

    @override
    def on_modified(self, event: DirModifiedEvent | FileModifiedEvent) -> None:
        if str(event.src_path).endswith(".py"):
            self._before_reload.notify()
            os.execv(sys.executable, ["python"] + sys.argv)


@final
class LiveReloading(Module):
    """
    Enables live reloading, meaning the program completely restarts whenever changes are detected in the specified directory.
    Use `before_reload` to add any callbacks to be executed just before the program restarts.
    """

    def __init__(
        self, /, *, directory: Path | str = ".", recursive: bool = True
    ) -> None:
        if not (directory := Path(directory)).is_dir():
            raise ValueError(f"{directory} must be a directory.")

        self.before_reload = Hook()

        self._observer = Observer()
        self._observer.schedule(
            _LREventHandler(self.before_reload),
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
