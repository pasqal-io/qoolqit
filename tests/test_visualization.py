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


def test_plot_bitstrings_label_shows_up_in_legend() -> None:
    _, ax = plt.subplots()
    plot_bitstrings(counts={"000": 1, "001": 2}, label="run 1", ax=ax)

    assert ax.get_legend() is None
    legend = ax.legend()
    assert legend.legend_handles[0].get_facecolor() == to_rgba(DEFAULT_BAR_COLOR)
    assert legend.get_texts()[0].get_text() == "run 1"


def test_plot_bitstrings_highlight_colors_the_bar() -> None:
    _, ax = plt.subplots()
    plot_bitstrings(counts={"000": 1, "001": 2}, highlight={"001": "tab:red"}, ax=ax)

    bars = dict(zip(["001", "000"], ax.containers[0]))
    assert bars["001"].get_facecolor() == to_rgba("tab:red")
    assert bars["000"].get_facecolor() == to_rgba(DEFAULT_BAR_COLOR)


def test_plot_bitstrings_legend_uses_base_color_even_if_first_bar_highlighted() -> None:
    _, ax = plt.subplots()
    # "001" has the higher count so it plots first, and is also highlighted.
    plot_bitstrings(counts={"000": 1, "001": 2}, highlight={"001": "tab:red"}, label="run 1", ax=ax)

    legend = ax.legend()
    assert legend.legend_handles[0].get_facecolor() == to_rgba(DEFAULT_BAR_COLOR)


def test_plot_bitstrings_two_calls_on_same_axes_keep_their_own_highlights() -> None:
    _, ax = plt.subplots()
    plot_bitstrings(counts={"000": 1, "001": 2}, highlight={"001": "tab:red"}, ax=ax)
    plot_bitstrings(counts={"000": 1, "001": 2}, color="C2", ax=ax)

    first_call_bars = dict(zip(["001", "000"], ax.containers[0]))
    assert first_call_bars["001"].get_facecolor() == to_rgba("tab:red")
