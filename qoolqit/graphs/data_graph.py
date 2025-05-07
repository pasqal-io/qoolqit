from __future__ import annotations

from typing import Any

from numpy.typing import ArrayLike

from .base_graph import BaseGraph


class Graph(BaseGraph):
    """
    The main graph structure in QoolQit to represent data being manipulated.

    Possible conventions:
    - Each node always has a "pos" feature which is either None or a tuple (x, y).
    - Each node and each edge always have a "weight" feature which is either None or a float.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        Some main initializer to create a basic graph

        Possible options:
        - Take in an int corresponding to the number of nodes, initialize a graph with no edges.
        - Take in a list of tuples, initialize a graph with a list of edges
        """
        super().__init__(*args, **kwargs)

        self._is_node_weighted: bool | None = None
        self._is_edge_weigthed: bool | None = None

    ####################
    ### CONSTRUCTORS ###
    ####################

    @classmethod
    def from_coordinates(cls, coords: list) -> Graph:  # type: ignore
        """Get a list of (x, y) tuples and initialize"""
        ...

    @classmethod
    def random(cls, n: int, p: float) -> Graph:  # type: ignore
        """ER random graph."""
        ...

    @classmethod
    def line(cls, n: int, spacing: float = 1.0) -> Graph:  # type: ignore
        """Line graph."""
        ...

    @classmethod
    def circle(cls, n: int, spacing: float = 1.0) -> Graph:  # type: ignore
        """Circle graph."""
        ...

    @classmethod
    def from_pyg(cls, data) -> Graph:  # type: ignore
        """Create a graph from a pyg data object."""
        ...

    ##################
    ### PROPERTIES ###
    ##################

    @property
    def node_weights(self) -> dict | None:
        """Dictionary of node weights."""
        pass

    @property
    def edge_weights(self) -> dict | None:
        """Dictionary of edge weights."""
        pass

    @property
    def adjacency_matrix(self) -> ArrayLike:
        """Return the adjacency matrix.

        Options:
        - Default to sparse or dense?
        - Default to np.array?

        """
        pass

    ###############
    ### METHODS ###
    ###############
