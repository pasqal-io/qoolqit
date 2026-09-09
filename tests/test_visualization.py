from __future__ import annotations

import matplotlib.pyplot as plt
import pytest
from matplotlib.colors import to_rgba

from qoolqit.visualization import DEFAULT_BAR_COLOR, plot_bitstrings


def test_plot_bitstrings_errors() -> None:
    with pytest.raises(ValueError, match="counts cannot be empty"):
        plot_bitstrings(counts={})
    with pytest.raises(ValueError, match="cannot plot normalized counts with zero total counts"):
        plot_bitstrings(counts={"000": 0}, normalize=True)
    with pytest.raises(ValueError, match="top must be a positive integer"):
        plot_bitstrings(counts={"000": 1, "001": 2}, top=0)


def test_plot_bitstrings_default_bar_color() -> None:
    _, ax = plt.subplots()
    plot_bitstrings(counts={"000": 1, "001": 2}, ax=ax)

    bars = ax.containers[0]
    assert all(bar.get_facecolor() == to_rgba(DEFAULT_BAR_COLOR) for bar in bars)


def test_plot_bitstrings_label_sets_bar_label() -> None:
    _, ax = plt.subplots()
    plot_bitstrings(counts={"000": 1, "001": 2}, label="run 1", ax=ax)

    assert ax.get_legend() is None
    assert ax.containers[0].get_label() == "run 1"
