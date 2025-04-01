from __future__ import annotations

from .graph import Graph


class Dataset:
    """A collection of Graphs.

    Centralize useful properties and methods for handling datasets.

    Include conversion to and from PyG dataset.
    """

    def __init__(self, graphs: list[Graph]) -> None:
        pass

    @classmethod
    def from_pyg(cls, dataset) -> Dataset:  # type: ignore
        """Create a graph from a pyg data object."""
        pass
