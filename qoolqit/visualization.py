"""Visualization helpers for QoolQit results."""

from __future__ import annotations

import matplotlib.pyplot as plt
from matplotlib.axes import Axes


def plot_bitstrings(
    counts: dict[str, int] | list[dict[str, int]],
    top: int | None = None,
    normalize: bool = False,
    color: str | list[str] | None = None,
    highlight: dict[str, str] | None = None,
    labels: list[str] | None = None,
    ax: Axes | None = None,
) -> None:
    """Plot bitstrings counts, optionally highlighting selected ones.

    Arguments:
        counts: dictionary of bitstrings to counts, or a list of dictionaries.
            the element of the list are drawn as grouped bars on the same axes.
        top: If provided, only the top N counts will be plotted. With several
            counts, outcomes are ranked by their total count.
        normalize: If True, counts will be normalized to probabilities. Each
            mapping is normalized independently. Defaults to False.
        color: Default bar color, or one color per mapping. Defaults to
            matplotlib's color cycle.
        highlight: Mapping of bitstrings to colors, for example
            ``{"001": "tab:green", "110": "tab:red"}``. The outcome is marked
            with a faint background band and a colored tick label, so that the
            bar colors keep identifying the counts they belong to.
            If highlighted bitstring is not in top N counts, it will not be shown.
        labels: Legend label for each mapping.
        ax: Axes to draw on. Uses a new axes if omitted.
    """

    # Accept a single dict or a list of dicts, and work with a list from here on
    counts_list = [counts] if isinstance(counts, dict) else list(counts)
    labels = [labels] if isinstance(labels, str) else labels
    n = len(counts_list)

    if not counts_list or any(not count for count in counts_list):
        raise ValueError("counts cannot be empty")

    # We check for zero total counts here, since the normalization would otherwise
    # produce NaN values that matplotlib cannot plot. We do not check for zero
    # counts when plotting a histogram, since matplotlib can handle that case.
    totals = [sum(count.values()) for count in counts_list]
    if normalize and any(total == 0 for total in totals):
        raise ValueError("cannot plot normalized counts with zero total counts")

    if top is not None and top <= 0:
        raise ValueError("top must be a positive integer")

    # Sort the union of all bitstrings by their total count, in descending order
    # We use set for unique bitstrings, and sorted across the union of all
    # counts to ensure that we have a consistent order for the x-axis.
    # When top is specified, we will select only the first N bitstrings after sorting
    bitstrings = sorted(
        set().union(*counts_list),
        key=lambda bitstring: sum(count.get(bitstring, 0) for count in counts_list),
        reverse=True,
    )

    # Select only the top N counts if requested
    if top is not None:
        bitstrings = bitstrings[:top]

    # One base color per set of counts
    if color is None:
        color = [f"C{index}" for index in range(n)]
    elif isinstance(color, str):
        color = [color] * n
    else:
        color = list(color)
    if len(color) != n:
        raise ValueError("color must have one entry per counts mapping")

    if labels is not None and len(labels) != n:
        raise ValueError("labels must have one entry per counts mapping")
    if n > 1 and labels is None:
        # If no labels are provided, we generate default labels for each series.
        labels = [f"Counts {index + 1}" for index in range(n)]

    # If no highlight mapping is provided, use an empty dict to avoid KeyErrors
    highlight = highlight or {}

    # Create the plot if no axes are provided
    if ax is None:
        _, ax = plt.subplots(figsize=(12, 5))

    # Plot one group of bars per set of counts, side by side on each bitstring
    positions = range(len(bitstrings))

    slot = 0.6 / n
    for index, count in enumerate(counts_list):
        # Compute the values to plot, normalizing if requested.
        # If a bitstring is not present in the counts, we use 0 as its value.
        values = [
            count.get(bitstring, 0) / totals[index] if normalize else count.get(bitstring, 0)
            for bitstring in bitstrings
        ]

        # Shift each group so that the bars are centered on the tick
        offset = (index - (n - 1) / 2) * slot
        ax.bar(
            [position + offset for position in positions],
            values,
            width=slot,
            color=color[index],
            label=labels[index] if labels else None,
        )

    # Mark highlighted outcomes with a faint band behind their group. zorder=0
    # keeps the band below the bars.
    for position, bitstring in enumerate(bitstrings):
        if bitstring in highlight:
            ax.axvspan(
                position - 0.45,
                position + 0.45,
                color=highlight[bitstring],
                alpha=0.15,
                zorder=0,
            )

    # Place one tick per bitstring
    ax.set_xticks(list(positions))
    ax.set_xticklabels(bitstrings)

    # Highlighted outcomes are also marked on their tick label
    for tick_label in ax.get_xticklabels():
        if tick_label.get_text() in highlight:
            tick_label.set_color(highlight[tick_label.get_text()])
            tick_label.set_fontweight("bold")

    # Rotate x-axis labels for better readability
    ax.tick_params(axis="x", labelrotation=90)
    ax.grid(axis="y", linestyle="--", alpha=0.4)

    # We set some default labels, the user can override
    # them by calling ax.set_xlabel and ax.set_ylabel after this function.
    ax.set_ylabel("Probability" if normalize else "Counts")
    ax.set_xlabel("Bitstrings")

    # Only show a legend when the series have been named
    if labels is not None:
        ax.legend()
