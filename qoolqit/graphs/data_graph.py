from __future__ import annotations

import random

import networkx as nx

from .base_graph import BaseGraph


class DataGraph(BaseGraph):
    """
    The main graph structure in QoolQit to represent data being manipulated.
    """

    def __init__(self, edges: list | tuple | None = None) -> None:
        super().__init__(edges)

        self._node_weights = {i: None for i in self.nodes}
        self._edge_weights = {e: None for e in self.edges}

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
        graph.ud_radius = spacing
        return graph

    @classmethod
    def circle(cls, n: int, spacing: float = 1.0) -> DataGraph:
        """Circle graph."""
        base_graph = nx.grid_2d_graph(n, 1, periodic=True)
        base_graph = nx.relabel_nodes(base_graph, {(i, 0): i for i in range(n)})
        coords = nx.circular_layout(base_graph)
        coords = {i: tuple(c) for i, c in coords.items()}
        graph = cls.from_coordinates(coords, spacing=spacing)
        graph.add_edges_from(list(base_graph.edges))
        graph.ud_radius = spacing
        return graph

    @classmethod
    def random(cls, n: int, p: float, seed: float | None = None) -> DataGraph:
        """ER random graph."""
        base_graph = nx.erdos_renyi_graph(n, p, seed)
        graph = cls(list(base_graph.edges))
        return graph

    @classmethod
    def random_ud(
        cls,
        n: int,
        radius: float = 1.0,
        mu: float = 0.0,
        seed: float | None = None,
    ) -> DataGraph:
        """Random unit disk graph."""
        sigma = ((n**0.5) ** 0.5) / 2
        pos = {i: (random.gauss(mu, sigma), random.gauss(mu, sigma)) for i in range(n)}
        base_graph = nx.random_geometric_graph(n, radius=radius, dim=2, pos=pos, seed=seed)
        graph = cls.from_coordinates(pos)
        graph.add_edges_from(base_graph.edges)
        graph.ud_radius = radius
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
        return self._node_weights

    @node_weights.setter
    def node_weights(self, weights: dict) -> None:
        if len(weights) != len(self.nodes):
            raise ValueError("Setting weights requires one weight per node.")
        self._node_weights = weights

    @property
    def edge_weights(self) -> dict | None:
        """Dictionary of edge weights."""
        return self._edge_weights

    @edge_weights.setter
    def edge_weights(self, weights: dict) -> None:
        if len(weights) != len(self.edges):
            raise ValueError("Setting weights requires one weight per edge.")
        self._edge_weights = weights

    @property
    def is_node_weighted(self) -> bool:
        return not ((None in self._node_weights.values()) or len(self._node_weights) == 0)

    @property
    def is_edge_weighted(self) -> bool:
        return not ((None in self._edge_weights.values()) or len(self._edge_weights) == 0)

    # @property
    # def adjacency_matrix(self) -> ArrayLike:
    #     """Return the adjacency matrix.

    #     Options:
    #     - Default to sparse or dense?
    #     - Default to np.array?

    #     """
    #     pass

    ###############
    ### METHODS ###
    ###############
