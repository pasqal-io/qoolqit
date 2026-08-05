"""QoolQit colors and colormaps for Matplotlib.

Importing this module registers extra names with Matplotlib; it never touches
``rcParams``, so existing plots are unaffected. Palette entries become named
colors (``"mint_green"``) and colormaps follow ``<low>_<high>`` (diverging) and
``<hue>`` (sequential), each also available reversed with the usual ``_r``
suffix.

Examples:
    >>> import matplotlib.pyplot as plt
    >>> from qoolqit.utils import colors
    >>> plt.plot(x, y, color="mint_green")
    >>> plt.imshow(data, cmap="purple_mint")
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence

import matplotlib as mpl
from matplotlib.colors import LinearSegmentedColormap

__all__ = ["PALETTE", "DIVERGING", "SEQUENTIAL", "COLORMAPS"]

# Qoolqit palette, keyed by <qualifier>_<hue>. The underscore keeps these from
# colliding with any Matplotlib built-in color name.
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

# Colormaps are palette keys interpolated in order. Diverging maps go
# <low> -> <center> -> <high>: the plain name uses a near-white center, the
# _dark variant a near-black one.
DIVERGING: Mapping[str, Sequence[str]] = {
    "purple_mint": ("neon_purple", "bright_green", "mint_green"),
    "purple_mint_dark": ("neon_purple", "dark_green", "mint_green"),
    "orange_mint": ("soft_orange", "bright_green", "mint_green"),
    "orange_mint_dark": ("soft_orange", "dark_green", "mint_green"),
    "purple_orange": ("neon_purple", "bright_green", "soft_orange"),
    "purple_orange_dark": ("neon_purple", "dark_green", "soft_orange"),
    "blue_mint": ("neon_blue", "bright_green", "mint_green"),
    "blue_mint_dark": ("neon_blue", "dark_green", "mint_green"),
}

SEQUENTIAL: Mapping[str, Sequence[str]] = {
    "mint": ("bright_green", "mint_green"),
    "purple": ("bright_green", "neon_purple"),
    "orange": ("bright_green", "soft_orange"),
    "deep": ("bright_green", "mint_green", "metal_blue", "dark_green"),
    "night": ("dark_green", "metal_blue", "mint_green"),
}


def _build_colormaps() -> dict[str, LinearSegmentedColormap]:
    """Build every colormap plus its reversed ``_r`` variant."""
    cmaps: dict[str, LinearSegmentedColormap] = {}
    for name, keys in {**DIVERGING, **SEQUENTIAL}.items():
        cmaps[name] = LinearSegmentedColormap.from_list(name, [PALETTE[key] for key in keys])
    for name in list(cmaps):
        cmaps[f"{name}_r"] = cmaps[name].reversed(name=f"{name}_r")
    return cmaps


COLORMAPS: Mapping[str, LinearSegmentedColormap] = _build_colormaps()


def register() -> None:
    """Register the colors and colormaps with Matplotlib.

    Called automatically on import; idempotent.
    """
    mpl.colors.get_named_colors_mapping().update(PALETTE)

    for name, cmap in COLORMAPS.items():
        if name not in mpl.colormaps:
            mpl.colormaps.register(cmap, name=name)


register()
