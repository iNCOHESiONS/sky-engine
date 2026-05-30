from typing import override

from pygame.draw import aacircle

from sky import Component
from sky.colors import ALICE_BLUE


class Circle(Component, hot_reloadable=True):
    @override
    def update(self) -> None:
        aacircle(
            self.app.window.surface,
            ALICE_BLUE,
            self.app.window.center,
            30,
        )
