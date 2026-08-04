"""PASQAL/QoolQit brand colors and colormaps for Matplotlib.

Importing this module registers extra names with Matplotlib.
Every palette key uses the uniform ``<qualifier>_<hue>`` form. 
Colors are registered both bare (``"mint_green"``) 
and namespaced (``"pasqal:mint_green"``). Colormaps are
``qq_<low>_<high>`` for diverging maps and ``qq_<hue>`` for sequential ones,
each also available reversed with the usual ``_r`` suffix.

Examples:
    >>> import matplotlib.pyplot as plt
    >>> from qoolqit.utils import colors
    >>> plt.plot(x, y, color="mint_green")            # bare name
    >>> plt.plot(x, y, color="pasqal:mint_green")     # namespaced (same color)
    >>> plt.imshow(data, cmap="qq_purple_mint")
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

__all__ = ["PALETTE", "DIVERGING", "SEQUENTIAL", "COLORMAPS", "NAMESPACE", "register"]

NAMESPACE = "pasqal"

# Brand palette. Keys use the uniform <qualifier>_<hue> form (see module docstring).
PALETTE: Mapping[str, str] = {
    "metal_blue": "#397378",
    "neon_purple": "#867BFA",
    "mint_green": "#00C887",
    "soft_orange": "#FF986E",
    "dark_green": "#0F1E23",
    "neon_blue": "#92C8E5",
    "soft_green": "#173035",
    "bright_green": "#E1F6E9",
    "neutral_gray": "#506166",
}

# Colormaps map to palette keys, interpolated in order. Diverging maps go
# <low> -> <center> -> <high>; the plain name uses the near-white center, the
# _dark variant the near-black one.
DIVERGING: Mapping[str, Sequence[str]] = {
    "qq_purple_mint": ("neon_purple", "bright_green", "mint_green"),
    "qq_purple_mint_dark": ("neon_purple", "dark_green", "mint_green"),
    "qq_orange_mint": ("soft_orange", "bright_green", "mint_green"),
    "qq_orange_mint_dark": ("soft_orange", "dark_green", "mint_green"),
    "qq_purple_orange": ("neon_purple", "bright_green", "soft_orange"),
    "qq_purple_orange_dark": ("neon_purple", "dark_green", "soft_orange"),
    "qq_blue_mint": ("neon_blue", "bright_green", "mint_green"),
    "qq_blue_mint_dark": ("neon_blue", "dark_green", "mint_green"),
}

SEQUENTIAL: Mapping[str, Sequence[str]] = {
    "qq_mint": ("bright_green", "mint_green"),
    "qq_purple": ("bright_green", "neon_purple"),
    "qq_orange": ("bright_green", "soft_orange"),
    "qq_deep": ("bright_green", "mint_green", "metal_blue", "dark_green"),
    "qq_night": ("dark_green", "metal_blue", "mint_green"),
}


def _build_colormaps() -> dict[str, LinearSegmentedColormap]:
    """Build every brand colormap plus its reversed ``_r`` variant."""
    cmaps: dict[str, LinearSegmentedColormap] = {}
    for name, keys in {**DIVERGING, **SEQUENTIAL}.items():
        cmaps[name] = LinearSegmentedColormap.from_list(name, [PALETTE[key] for key in keys])
    for name in list(cmaps):
        cmaps[f"{name}_r"] = cmaps[name].reversed(name=f"{name}_r")
    return cmaps


COLORMAPS: Mapping[str, LinearSegmentedColormap] = _build_colormaps()


def register(bare: bool = True) -> None:
    """Register the brand colors and colormaps with Matplotlib.

    Called automatically on import. 

    Args:
        bare: Also register the palette under its plain keys (``"mint_green"``)
            in addition to the namespaced ones (``"pasqal:mint_green"``). Safe
            because underscore names cannot collide with Matplotlib built-ins.
    """
    names = {f"{NAMESPACE}:{key}": value for key, value in PALETTE.items()}
    if bare:
        names.update(PALETTE)
    mpl.colors.get_named_colors_mapping().update(names)

    for name, cmap in COLORMAPS.items():
        try:  # Matplotlib >= 3.6
            if name not in mpl.colormaps:
                mpl.colormaps.register(cmap, name=name)
        except AttributeError:  # older Matplotlib
            try:
                plt.register_cmap(name=name, cmap=cmap)
            except ValueError:  # already registered
                pass

register()
