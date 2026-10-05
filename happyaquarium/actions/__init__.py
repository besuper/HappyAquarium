import importlib
import pkgutil
from dataclasses import dataclass


@dataclass
class Context:
    player: dict
    params: dict
    cdn: str


_ACTIONS = {}


def action(name, *, saves=True):
    def register(handler):
        _ACTIONS[name] = (handler, saves)
        return handler
    return register


def get(name):
    return _ACTIONS.get(name)


for _module in pkgutil.iter_modules(__path__):
    if not _module.name.startswith("_"):
        importlib.import_module(f"{__name__}.{_module.name}")
