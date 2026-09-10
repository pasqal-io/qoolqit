"""Visualization helpers for QoolQit results."""

from __future__ import annotations

from collections import Counter

import matplotlib.pyplot as plt
from matplotlib.axes import Axes

DEFAULT_BAR_COLOR = "#397378"


def plot_bitstrings(
    counts: dict[str, int],
    top: int | None = None,
    normalize: bool = False,
    color: str = DEFAULT_BAR_COLOR,
    highlight: dict[str, str] | None = None,
    label: str | None = None,
    ax: Axes | None = None,
) -> None:
    """Plot bitstring counts, optionally highlighting selected ones.

    Arguments:
        counts: Mapping of bitstrings to counts.
        top: Plot only the top N counts.
        normalize: Normalize counts to probabilities. Defaults to False.
        color: Bar color.
        highlight: Mapping of bitstrings to highlight colors. Highlighted
            outcomes get their bar and tick label colored accordingly.
        label: Legend label for the bars. Call ax.legend() to show it.
        ax: Axes to draw on. Creates new axes if omitted.
    """

    if not counts:
        raise ValueError("counts cannot be empty")

    total = sum(counts.values())
    if normalize and total == 0:
        raise ValueError("cannot plot normalized counts with zero total counts")

    if top is not None and top <= 0:
        raise ValueError("top must be a positive integer")

    # most_common(None) returns all entries, sorted by decreasing count
    selected_counts = Counter(counts).most_common(top)
    bitstrings = [bitstring for bitstring, _ in selected_counts]
    values = [count / total if normalize else count for _, count in selected_counts]

    highlight = highlight or {}

    # Create the plot if no axes are provided
    if ax is None:
        _, ax = plt.subplots(figsize=(12, 5))

    positions = range(len(bitstrings))
    bar_colors = [highlight.get(bitstring, color) for bitstring in bitstrings]
    ax.bar(positions, values, width=0.65, color=bar_colors)

    if label is not None:
        # A zero-height bar draws nothing but gives the legend a swatch in
        # `color`, regardless of which bitstrings are highlighted.
        ax.bar(0, 0, color=color, label=label)

    ax.set_xticks(list(positions))
    ax.set_xticklabels(bitstrings)

    # Highlighted outcomes are also marked on their tick label
    for tick_label in ax.get_xticklabels():
        if tick_label.get_text() in highlight:
            tick_label.set_color(highlight[tick_label.get_text()])
            tick_label.set_fontweight("bold")

    ax.tick_params(axis="x", labelrotation=90)
    ax.grid(axis="y", linestyle="--", alpha=0.4)

    # Default labels; the caller can override via ax.set_xlabel/ax.set_ylabel
    ax.set_ylabel("Probability" if normalize else "Counts")
    ax.set_xlabel("Bitstrings")
