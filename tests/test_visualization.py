from __future__ import annotations

import pytest

from qoolqit.visualization import plot_bitstrings


def test_plot_bitstrings_errors() -> None:
    with pytest.raises(ValueError, match="counts cannot be empty"):
        plot_bitstrings(counts={})
    with pytest.raises(ValueError, match="cannot plot normalized counts with zero total counts"):
        plot_bitstrings(counts={"000": 0}, normalize=True)
    with pytest.raises(ValueError, match="top must be a positive integer"):
        plot_bitstrings(counts={"000": 1, "001": 2}, top=0)
    with pytest.raises(ValueError, match="color must have one entry per counts mapping"):
        plot_bitstrings(counts=[{"000": 1}, {"001": 2}], color=["tab:blue"])
    with pytest.raises(ValueError, match="labels must have one entry per counts mapping"):
        plot_bitstrings(counts=[{"000": 1}, {"001": 2}], labels=["run 1"])
