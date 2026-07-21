import cv2
import pygame

from sky import App, AppSpec, Vector2, WindowSpec


app = App(
    spec=AppSpec(window_spec=WindowSpec(size=Vector2(16, 9) * 100)),
)

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, app.window.width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, app.window.height)


@app.on_render
def render() -> None:
    has_image, frame = cap.read()

    if has_image:
        app.window.blit(
            pygame.surfarray.make_surface(cv2.flip(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), 1).swapaxes(0, 1))
        )


app.mainloop()
cap.release()
