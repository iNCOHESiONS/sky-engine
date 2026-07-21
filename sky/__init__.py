"""
Sky Engine
----------

A wrapper around `pygame-ce` that makes it less painful to use.

:copyright: (c) 2026 by iNCOHESiONS.
:license: MIT, see LICENSE for more details.
"""  # ruff: ignore[missing-trailing-period, missing-terminal-punctuation, missing-blank-line-after-summary]

# ruff: file-ignore[module-import-not-at-top-of-file]

__title__ = "sky-engine"
__description__ = "A wrapper around pygame that makes it less painful to use."
__url__ = "https://github.com/incohesions/sky-engine"
__author__ = "iNCOHESiONS"
__version__ = "0.0.2"
__license__ = "MIT"


import sys

from os import environ


environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "true"

del environ

import pygame


if not getattr(pygame, "IS_CE", False):
    print("Please use pygame-ce (https://pypi.org/project/pygame-ce/) instead of pygame.")  # ruff: ignore[print]
    sys.exit(-1)

del sys

from .app import App
from .core import (
    Component,
    Cursor,
    Key,
    Keybinding,
    Modifier,
    Module,
    MouseButton,
    Service,
    State,
)
from .hook import Hook
from .scene import Scene
from .spec import AppSpec, SceneSpec, WindowSpec
from .types import Coroutine
from .utils import Color, Rect, Vector2, Vector3
from .window import Window
from .yieldable import WaitForFrames, WaitForSeconds, WaitUntil, WaitWhile


__all__ = [
    "App",
    "AppSpec",
    "Color",
    "Component",
    "Coroutine",
    "Cursor",
    "Hook",
    "Key",
    "Keybinding",
    "Modifier",
    "Module",
    "MouseButton",
    "Rect",
    "Scene",
    "SceneSpec",
    "Service",
    "State",
    "Vector2",
    "Vector3",
    "WaitForFrames",
    "WaitForSeconds",
    "WaitUntil",
    "WaitWhile",
    "Window",
    "WindowSpec",
]
