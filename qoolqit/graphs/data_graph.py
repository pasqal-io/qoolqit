from __future__ import annotations

import networkx as nx
from numpy.typing import ArrayLike

from .base_graph import BaseGraph


class DataGraph(BaseGraph):
    """
    The main graph structure in QoolQit to represent data being manipulated.
    """

    def __init__(self, edges: list | tuple | None = None) -> None:
        super().__init__(edges)

        self._is_node_weighted: bool | None = None
        self._is_edge_weigthed: bool | None = None

    ####################
    ### CONSTRUCTORS ###
    ####################

    @classmethod
    def line(cls, n: int, spacing: float = 1.0) -> DataGraph:
        """Line graph."""
        coords = [(i * spacing, 0.0) for i in range(n)]
        graph = cls.from_coordinates(coords)
        edges = [(i - 1, i) for i in range(1, n)]
        graph.add_edges_from(edges)
        return graph

    @classmethod
    def circle(cls, n: int, spacing: float = 1.0) -> DataGraph:
        """Circle graph."""
        base_graph = nx.grid_2d_graph(n, 1, periodic=True)
        base_graph = nx.relabel_nodes(base_graph, {(i, 0): i for i in range(n)})
        coords = nx.circular_layout(base_graph)
        coords = {i: tuple(c) for i, c in coords.items()}
        graph = cls.from_coordinates(coords)
        graph.add_edges_from(list(base_graph.edges))
        return graph

    @classmethod
    def random(cls, n: int, p: float, seed: float | None = None) -> DataGraph:
        """ER random graph."""
        base_graph = nx.erdos_renyi_graph(n, p, seed)
        graph = cls(list(base_graph.edges))
        return graph

    @classmethod
    def from_pyg(cls, data) -> DataGraph:  # type: ignore
        """Create a graph from a pyg data object."""
        raise NotImplementedError

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
