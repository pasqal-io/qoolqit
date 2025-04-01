from __future__ import annotations

import networkx as nx
from numpy.typing import ArrayLike

##################
### BASE GRAPH ###
##################


class _BaseGraph(nx.Graph):
    """

    QoolQit may have graphs that correspond to data the user is manipulating, but also graphs
    that are structural to the algorithms, such as the layouts.

    The base graph is meant to hold information and functionalities that are common to all graphs.
    """

    def __init__(self) -> None:
        self._is_ud_graph: bool | None = None

    @property
    def coords(self) -> dict | None:
        """Return the dictionary of node coordinates."""
        pass

    @property
    def distances(self) -> dict | None:
        """Dictionary of distances for all node pairs in the graph."""
        # coords = self.coords
        # return {edge: dist(coords[edge[0]], coords[edge[1]]) for edge in self.all_node_pairs}
        pass

    @property
    def edge_distances(self) -> dict | None:
        """Dictionary of distances for the node pairs that are connected by an edge."""
        # coords = self.coords
        # return {edge: dist(coords[edge[0]], coords[edge[1]]) for edge in self.edges}
        pass

    @property
    def is_ud_graph(self, radius: float = 1.0) -> bool:
        """Check if graph is unit-disk."""
        if self._is_ud_graph is None:
            ...
            # Check the method defined in the QEK solver
            ...
            self._is_ud_graph = True
        return self._is_ud_graph

    def draw(self) -> None: ...


##################
### MAIN GRAPH ###
##################


class Graph(_BaseGraph):
    """
    The main graph structure in QoolQit to represent data being manipulated.

    Possible conventions:
    - Each node always has a "pos" feature which is either None or a tuple (x, y).
    - Each node and each edge always have a "weight" feature which is either None or a float.
    """

    def __init__(self) -> None:
        """
        Some main initializer to create a basic graph

        Possible options:
        - Take in an int corresponding to the number of nodes, initialize a graph with no edges.
        - Take in a list of tuples, initialize a graph with a list of edges
        """

        self._is_node_weighted: bool | None = None
        self._is_edge_weigthed: bool | None = None

        pass

    ####################
    ### CONSTRUCTORS ###
    ####################

    @classmethod
    def from_coordinates(cls, coords: list) -> Graph:  # type: ignore
        """Get a list of (x, y) tuples and initialize"""
        pass

    @classmethod
    def random(cls, n: int, p: float) -> Graph:  # type: ignore
        """ER random graph."""
        pass

    @classmethod
    def line(cls, n: int, spacing: float = 1.0) -> Graph:  # type: ignore
        """Line graph."""
        pass

    @classmethod
    def circle(cls, n: int, spacing: float = 1.0) -> Graph:  # type: ignore
        """Circle graph."""
        pass

    @classmethod
    def from_pyg(cls, data) -> Graph:  # type: ignore
        """Create a graph from a pyg data object."""
        pass

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
