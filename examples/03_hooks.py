from pygame import draw

from sky import App, Hook, WindowSpec
from sky.colors import ALICE_BLUE, CRIMSON

app = App(spec=WindowSpec(fill=CRIMSON))


@app.on_setup
def setup() -> None:
    print("This will print as the app starts.")


@app.pre_update
def pre_update() -> None:
    print("This will print every frame.")


@app.on_render  # alias for @app.window.on_render
def on_render() -> None:
    draw.aacircle(app.window.surface, ALICE_BLUE, app.window.center, 32)


@app.on_cleanup
def cleanup() -> None:
    print("This will print as soon as the app finishes running.")


cancellable = Hook(cancellable=True)


@cancellable
def callback1() -> None:
    print("This will print.")
    cancellable.cancel()


@cancellable
def callback2() -> None:
    print("This will not print.")


cancellable.notify()
app.mainloop()
