import inspect
from importlib import import_module

from sky import App, AppSpec, Component
from sky.modules import HotComponentReloading

app = App(spec=AppSpec(modules=[hcr := HotComponentReloading()]))


@hcr.on_reload
def on_reload(old_cls: type[Component], new_cls: type[Component]) -> None:
    print(
        f"{old_cls.__name__}'s code changed from\n\n{inspect.getsource(old_cls).strip()}\n\ninto\n\n{inspect.getsource(new_cls).strip()}"
    )


# workaround necessary because examples start with numbers, and imports don't allow that
# unrelated to the example at hand
app.add_component(import_module("07b_hot_reloading").Circle)
app.mainloop()
