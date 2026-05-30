from sky import App, AppSpec
from sky.modules import LiveReloading

app = App(spec=AppSpec(modules=[live_reloading := LiveReloading()]))

live_reloading.before_reload += lambda: print("Reloading!")

app.mainloop()
