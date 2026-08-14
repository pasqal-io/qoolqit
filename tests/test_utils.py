import pytest

from qoolqit.utils import plot_histogram    

def test_plot_histogram_errors() -> None:
    with pytest.raises(ValueError, match="counts cannot be empty"):
        plot_histogram(counts={})
    with pytest.raises(ValueError, match="cannot plot normalized counts with zero total counts"):
        plot_histogram(counts={"000": 0}, normalize=True)
    with pytest.raises(ValueError, match="top must be a positive integer"):
        plot_histogram(counts={"000": 1, "001": 2}, top=0)
    with pytest.raises(ValueError, match="color must have one entry per counts mapping"):
        plot_histogram(counts=[{"000": 1}, {"001": 2}], color=["tab:blue"])
    with pytest.raises(ValueError, match="labels must have one entry per counts mapping"):
        plot_histogram(counts=[{"000": 1}, {"001": 2}], labels=["run 1"])