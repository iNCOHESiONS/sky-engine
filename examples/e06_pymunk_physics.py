from random import randint
from typing import override

from pygame import draw, freetype
from pymunk import Body, Circle, Segment, Space

from sky import App, AppSpec, Color, Component, MouseButton, Vector2
from sky.colors import ALICE_BLUE


app = App(spec=AppSpec(modules=[freetype]))
app.keyboard.add_keybindings(escape=app.quit)

font = freetype.SysFont("Arial", 16, bold=True)

space = Space()
space.gravity = 0, 9.8

steps = 20

for a, b in [
    [(0, 0), (app.window.width, 0)],
    [(0, 0), (0, app.window.height)],
    [(app.window.width, 0), app.window.size.ituple()],
    [(0, app.window.height), app.window.size.ituple()],
]:
    space.add(Segment(space.static_body, a, b, 2))


class Ball(Component):
    def __init__(self, /, *, pos: Vector2) -> None:
        self.radius = randint(5, 25)
        self.color = Color.random()

        self.body = Body()
        self.body.position = pos.ituple()

        self.shape = Circle(self.body, self.radius)
        self.shape.mass = self.radius

        space.add(self.body, self.shape)

    @override
    def update(self) -> None:
        draw.aacircle(app.window.surface, self.color, self.body.position, self.radius)


@app.pre_update
def pre_update() -> None:
    for _ in range(steps):
        space.step(1 / steps / 10)


@app.on_render
def render() -> None:
    font.render_to(
        app.window.surface,
        (15, 15),
        f"FPS: {app.chrono.framerate:.0f}",
        ALICE_BLUE,
    )
    font.render_to(
        app.window.surface,
        (15, 45),
        f"Objects: {len(app.scene.components)}",
        ALICE_BLUE,
    )


@app.mouse.on_mouse_button_pressed.equals(MouseButton.left)
def on_left_pressed() -> None:
    app.add_component(Ball(pos=app.mouse.position))


@app.mouse.on_mouse_button_pressed.equals(MouseButton.right)
def on_right_pressed() -> None:
    for ball in app.get_components(of_type=Ball):
        ball.body.velocity += (Vector2(ball.body.position).direction_to(app.mouse.position) * 10).ituple()


app.mainloop()
