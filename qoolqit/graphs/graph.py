from __future__ import annotations

from itertools import product
from math import dist
from typing import Any, Collection, Iterable

import networkx as nx
from numpy.typing import ArrayLike


def _dist(p: Iterable | None, q: Iterable | None) -> float | None:
    """Wrapper on dist that accepts None."""
    return None if p is None or q is None else dist(p, q)


##################
### BASE GRAPH ###
##################


class BaseGraph(nx.Graph):
    """
    QoolQit may have graphs that correspond to data the user is manipulating, but also graphs
    that are structural to the algorithms, such as the layouts.

    The base graph is meant to hold information and functionalities that are common to all graphs.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._coords = {i: None for i in self.nodes}
        self._is_ud_graph: bool | None = None
        self._set_node_pos(self._coords)

    def _set_node_pos(self, coords: dict) -> None:
        """Sets the "pos" attribute in all nodes."""
        nx.set_node_attributes(self, coords, "pos")

    @classmethod
    def from_nodes(cls, nodes: Iterable) -> BaseGraph:
        graph = cls()
        graph.add_nodes_from(nodes)
        graph._coords = {i: None for i in graph.nodes}
        graph._set_node_pos(graph._coords)
        return graph

    @classmethod
    def from_coordinates(cls, coords: Collection) -> BaseGraph:
        """Get a list of (x, y) tuples and initialize."""
        nodes = list(range(len(coords)))
        graph = cls.from_nodes(nodes)
        graph._coords = {i: pos for i, pos in enumerate(coords)}
        graph._set_node_pos(graph._coords)
        return graph

    @property
    def has_coords(self) -> bool:
        return None not in self._coords.values()

    @property
    def has_edges(self) -> bool:
        return len(self.edges) > 0

    @property
    def all_node_pairs(self) -> nx.EdgeView:
        """Return a list of all possible node pairs in the graph."""
        return list(filter(lambda x: x[0] < x[1], product(self.nodes, self.nodes)))

    @property
    def coords(self) -> dict | None:
        """Return the dictionary of node coordinates."""
        return self._coords if self.has_coords else None

    @property
    def distances(self) -> dict | None:
        """Dictionary of distances for all node pairs in the graph."""
        if self.coords:
            coords = self.coords
            return {edge: _dist(coords[edge[0]], coords[edge[1]]) for edge in self.all_node_pairs}
        else:
            return None

    @property
    def edge_distances(self) -> dict | None:
        """Dictionary of distances for the node pairs that are connected by an edge."""
        if self.coords and self.has_edges:
            coords = self.coords
            return {edge: _dist(coords[edge[0]], coords[edge[1]]) for edge in self.edges}
        else:
            return None

    @property
    def is_ud_graph(self, radius: float = 1.0) -> bool:
        """Check if graph is unit-disk."""
        if self._is_ud_graph is None:
            ...
            # Check the method defined in the QEK solver
            ...
            self._is_ud_graph = True
        return self._is_ud_graph

    def draw(self, *args: Any, **kwargs: Any) -> None:
        nx.draw(self, *args, **kwargs)


##################
### MAIN GRAPH ###
##################


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
