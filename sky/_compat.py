import os

from .utils import Color, Vector2


__all__ = [
    "get_mouse_position",
    "get_window_handle",
    "make_window_transparent",
    "set_dark_mode_decorations",
]


if os.name == "nt":
    import ctypes
    import os
    import sys

    from ctypes import wintypes

    import win32api
    import win32con
    import win32gui

    _DWMWA_USE_IMMERSIVE_DARK_MODE = 20  # after Windows 11 build 22000
    _DWMWA_USE_IMMERSIVE_DARK_MODE_LEGACY = 19  # before Windows 11 build 22000

    _dwmapi = ctypes.WinDLL("dwmapi")
    _dwmapi.DwmSetWindowAttribute.argtypes = [
        wintypes.HWND,
        wintypes.DWORD,
        wintypes.LPCVOID,
        wintypes.DWORD,
    ]
    _dwmapi.DwmSetWindowAttribute.restype = ctypes.c_long  # HRESULT

    def set_dark_mode_decorations(hwnd: int, dark_mode: bool, /) -> None:
        value = wintypes.BOOL(dark_mode)

        for attribute in (
            _DWMWA_USE_IMMERSIVE_DARK_MODE,
            _DWMWA_USE_IMMERSIVE_DARK_MODE_LEGACY,
        ):
            result = _dwmapi.DwmSetWindowAttribute(
                hwnd,
                attribute,
                ctypes.byref(value),
                ctypes.sizeof(value),
            )

            if result >= 0:
                return

        print("Failed to apply dark mode to window.", file=sys.stderr)

    def make_window_transparent(hwnd: int, colorkey: Color, /) -> None:
        win32gui.SetWindowLong(  # pyright: ignore[reportUnknownMemberType]
            hwnd,
            win32con.GWL_EXSTYLE,
            win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED,  # pyright: ignore[reportUnknownArgumentType, reportUnknownMemberType]
        )

        win32gui.SetLayeredWindowAttributes(  # pyright: ignore[reportUnknownMemberType]
            hwnd,
            win32api.RGB(*colorkey.rgb),
            0,
            win32con.LWA_COLORKEY,
        )

    def get_window_handle(title: str, /) -> int:
        return win32gui.FindWindow(None, title)

    def get_mouse_position() -> Vector2:
        return Vector2(win32api.GetCursorPos())


else:

    def make_window_transparent(_1: int, _2: Color, /) -> None:
        raise OSError("This method is only supported on Windows.")

    def set_dark_mode_decorations(_1: int, _2: bool, /) -> None:
        raise OSError("This method is only supported on Windows.")

    def get_window_handle(_: str, /) -> int:
        raise OSError("This method is only supported on Windows.")

    def get_mouse_position() -> Vector2:
        raise OSError("This method is only supported on Windows.")
