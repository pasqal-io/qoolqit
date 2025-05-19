from __future__ import annotations

from importlib import import_module

from .graphs import *
from .pulser import *

list_of_submodules = [".graphs", ".pulser"]

__all__ = []
for submodule in list_of_submodules:
    __all_submodule__ = getattr(import_module(submodule, package="qoolqit"), "__all__")
    __all__ += __all_submodule__
