"""Visualization helpers for QoolQit results."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from matplotlib.axes import Axes


def _plot_counts(
    counts: dict[str, int],
    top: int | None = None,
    distribution: bool = False,
    ax: Axes | None = None,
    title: str | None = None,
    color: str = "tab:blue",
    highlight: dict[str, str] | None = None,
) -> Axes:
    """Plot counts, optionally highlighting selected outcomes.

    Parameters
    ----------
    counts: dict
        Mapping of bitstrings to counts.
    top: int, optional
        If provided, only the top N counts will be plotted.
    distribution: bool, default False
        If True, counts will be normalized to probabilities.
    ax: matplotlib.axes.Axes, optional
        If provided, the plot will be drawn on this axes.
    title: str, optional
        Plot title.
    color: str, default "tab:blue"
        Default bar color.
    highlight: dict, optional
        Mapping of labels to colors, for example:
        {"001": "tab:green", "110": "tab:red"}.

    Returns
    -------
    matplotlib.axes.Axes
        The axes object containing the plot.
    """
    import matplotlib.pyplot as plt

    if not counts:
        raise ValueError("counts cannot be empty")

    total = sum(counts.values())
    if distribution and total == 0:
        raise ValueError("cannot plot a distribution with zero total counts")

    # Sort counts in descending order
    items = sorted(
        counts.items(),
        key=lambda item: item[1],
        reverse=True,
    )

    # Select only the top N counts if requested
    if top is not None:
        items = items[:top]

    # Extract labels and values from items for plotting
    labels = [label for label, _ in items]
    values = [value / total if distribution else value for _, value in items]

    # Determine bar colors, using the highlight mapping if provided
    # If a label is not in the highlight mapping, use the default color.
    highlight = highlight or {}
    colors = [highlight.get(label, color) for label in labels]

    # Create the plot if no axes are provided
    if ax is None:
        _, ax = plt.subplots(figsize=(12, 5))

    # Plot the bar chart
    ax.bar(labels, values, width=0.6, color=colors)
    ax.set_xlabel("Bitstring")
    ax.set_ylabel("Probability" if distribution else "Count")

    # Set the title of the plot, using a default title if none is provided
    ax.set_title(title or ("Measurement distribution" if distribution else "Measurement histogram"))

    # Rotate x-axis labels for better readability
    ax.tick_params(axis="x", labelrotation=90)
    ax.grid(axis="y", linestyle="--", alpha=0.4)

    return ax


def plot_histogram(
    counts: dict[str, int],
    top: int | None = None,
    ax: Axes | None = None,
    title: str | None = None,
    color: str = "tab:blue",
    highlight: dict[str, str] | None = None,
) -> Axes:
    """Plot raw measurement counts as a histogram.

    Parameters
    ----------
    counts: dict
        Mapping of bitstrings to counts.
    top: int, optional
        If provided, only the top N counts will be plotted.
    ax: matplotlib.axes.Axes, optional
        If provided, the plot will be drawn on this axes.
    title: str, optional
        Plot title.
    color: str, default "tab:blue"
        Default bar color.
    highlight: dict, optional
        Mapping of labels to colors, for example:
        {"001": "tab:green", "110": "tab:red"}.

    Returns
    -------
    matplotlib.axes.Axes
        The axes object containing the plot.
    """
    return _plot_counts(
        counts,
        highlight=highlight,
        top=top,
        color=color,
        distribution=False,
        ax=ax,
        title=title,
    )


def plot_distribution(
    counts: dict[str, int],
    top: int | None = None,
    ax: Axes | None = None,
    title: str | None = None,
    color: str = "tab:blue",
    highlight: dict[str, str] | None = None,
) -> Axes:
    """Plot normalized measurement counts as a probability distribution.

    Parameters
    ----------
    counts: dict
        Mapping of bitstrings to counts.
    top: int, optional
        If provided, only the top N counts will be plotted.
    ax: matplotlib.axes.Axes, optional
        If provided, the plot will be drawn on this axes.
    title: str, optional
        Plot title.
    color: str, default "tab:blue"
        Default bar color.
    highlight: dict, optional
        Mapping of labels to colors, for example:
        {"001": "tab:green", "110": "tab:red"}.

    Returns
    -------
    matplotlib.axes.Axes
        The axes object containing the plot.
    """
    return _plot_counts(
        counts,
        highlight=highlight,
        top=top,
        distribution=True,
        color=color,
        ax=ax,
        title=title,
    )


__all__ = ["plot_histogram", "plot_distribution"]
