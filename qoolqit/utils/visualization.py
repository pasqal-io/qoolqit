"""Visualization helpers for QoolQit results."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from matplotlib.axes import Axes

__all__ = ["plot_histogram"]


def plot_histogram(
    counts: dict[str, int] | list[dict[str, int]],
    top: int | None = None,
    normalize: bool = False,
    ax: Axes | None = None,
    title: str | None = None,
    color: str | list[str] | None = None,
    highlight: dict[str, str] | None = None,
    labels: list[str] | None = None,
    xlabel: str | None = None,
    ylabel: str | None = None,
) -> Axes:
    """Plot measurement counts, optionally highlighting selected outcomes.

    Parameters
    ----------
    counts: dict or list of dict
        Mapping of bitstrings to counts, or a list of such mappings. Several
        mappings are drawn as grouped bars on the same axes.
    top: int, optional
        If provided, only the top N counts will be plotted. With several
        mappings, outcomes are ranked by their total count.
    normalize: bool, default False
        If True, counts will be normalized to probabilities. Each mapping is
        normalized independently.
    ax: matplotlib.axes.Axes, optional
        If provided, the plot will be drawn on this axes.
    title: str, optional
        Plot title.
    color: str or list of str, optional
        Default bar color, or one color per mapping. Defaults to matplotlib's
        color cycle.
    highlight: dict, optional
        Mapping of labels to colors, for example:
        {"001": "tab:green", "110": "tab:red"}. Meant for a single mapping of
        counts: with several mappings a highlighted outcome takes the same
        color in every group, so the run it belongs to becomes ambiguous.
    labels: str or list of str, optional
        Legend label for each mapping.
    xlabel: str, optional
        Label for the x-axis. Defaults to "Bitstring".
    ylabel: str, optional
        Label for the y-axis. Defaults to "Counts", or "Probability" when
        `normalize` is True.

    Returns
    -------
    matplotlib.axes.Axes
        The axes object containing the plot.
    """
    import matplotlib.pyplot as plt

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

    # If no highlight mapping is provided, use an empty dict to avoid KeyErrors
    highlight = highlight or {}

    # Create the plot if no axes are provided
    if ax is None:
        _, ax = plt.subplots(figsize=(12, 5))

    # Plot one group of bars per set of counts, side by side on each bitstring
    positions = range(len(bitstrings))

    # Bars are slightly narrower than their slot, so that neighbours sharing a
    # highlight color do not merge into a single wide bar
    slot = 0.6 / n
    width = slot if n == 1 else slot * 0.85
    for index, count in enumerate(counts_list):
        # Compute the values to plot, normalizing if requested.
        # If a bitstring is not present in the counts, we use 0 as its value.
        values = [
            count.get(bitstring, 0) / totals[index] if normalize else count.get(bitstring, 0)
            for bitstring in bitstrings
        ]

        # Determine bar colors, using the highlight mapping if provided
        # If a bitstring is not in the highlight mapping, use this series' color.
        bar_colors = [highlight.get(bitstring, color[index]) for bitstring in bitstrings]

        # Shift each group so that the bars are centered on the tick
        offset = (index - (n - 1) / 2) * slot
        ax.bar(
            [position + offset for position in positions],
            values,
            width=width,
            color=bar_colors,
            label=labels[index] if labels else None,
        )

    # Place one tick per bitstring, since the bars now sit at numeric positions
    ax.set_xticks(list(positions))
    ax.set_xticklabels(bitstrings)
    ax.set_xlabel("Bitstring" if xlabel is None else xlabel)
    ax.set_ylabel(("Probability" if normalize else "Counts") if ylabel is None else ylabel)

    # Set the title of the plot, using a default title if none is provided
    ax.set_title(title or ("Measurement distribution" if normalize else "Measurement histogram"))

    # Rotate x-axis labels for better readability
    ax.tick_params(axis="x", labelrotation=90)
    ax.grid(axis="y", linestyle="--", alpha=0.4)

    # Only show a legend when the series have been named. The handles are built
    # explicitly from the base colors, since matplotlib would otherwise take the
    # color of the first bar of each series, which may be a highlighted one.
    if labels:
        from matplotlib.patches import Patch

        ax.legend(
            handles=[Patch(color=color[index], label=label) for index, label in enumerate(labels)]
        )

    return ax
