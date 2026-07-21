from math import tau

import numpy as np

from pygame import draw, mixer

from sky import App, AppSpec, Coroutine, WaitForSeconds, WindowSpec
from sky.colors import ALICE_BLUE, CRIMSON
from sky.utils import clamp01


app = App(
    spec=AppSpec(
        window_spec=WindowSpec(fill=CRIMSON),
        modules=[mixer],
    ),
)


def generate_tone(
    *,
    frequency: float,
    duration: float,
    volume: float = 1,
) -> mixer.Sound:
    sample_rate = 44100
    volume = clamp01(volume)
    amplitude = (2**15 - 1) * volume

    samples = amplitude * np.sin(
        tau * frequency * np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    )

    return mixer.Sound(buffer=samples.astype(np.int16))


@app.on_setup
def beep() -> Coroutine:
    max_distance = app.window.center.distance_to(app.window.size)
    channel = mixer.Channel(0)
    duration = 0.2

    while True:
        distance = app.window.center.distance_to(app.mouse.position)
        pan = clamp01(app.mouse.position.x / app.window.width)
        volume = 1 - distance / max_distance

        channel.set_volume(volume * (1 - pan), volume * pan)
        channel.play(
            generate_tone(
                frequency=200,
                volume=volume,
                duration=duration,
            )
        )

        yield WaitForSeconds(duration * 2)


@app.on_render
def render():
    for pos in app.mouse.position, app.window.center:
        draw.aacircle(app.window.surface, ALICE_BLUE, pos, 10)


app.mainloop()
