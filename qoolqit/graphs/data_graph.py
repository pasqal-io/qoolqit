from __future__ import annotations

from typing import Collection

import networkx as nx
import numpy as np
from numpy.typing import ArrayLike

from qoolqit.utils import ATOL_32

from .base_graph import BaseGraph
from .utils import random_coords


class DataGraph(BaseGraph):
    """
    The main graph structure in QoolQit to represent data being manipulated.
    """

    def __init__(self, edges: list | tuple | set = []) -> None:
        super().__init__(edges)

        self._node_weights = {i: None for i in self.nodes}
        self._edge_weights = {e: None for e in self.ordered_edges}

    ####################
    ### CONSTRUCTORS ###
    ####################

    @classmethod
    def line(cls, n: int, spacing: float = 1.0, ud_radius: float = 1.0) -> DataGraph:
        """Line graph."""
        coords = [(i * spacing, 0.0) for i in range(n)]
        graph = cls.from_coordinates(coords)
        edges = [(i, i + 1) for i in range(0, n - 1)]
        graph.add_edges_from(edges)
        graph.ud_radius = ud_radius
        graph._node_weights = {i: None for i in graph.nodes}
        graph._edge_weights = {e: None for e in graph.ordered_edges}
        return graph

    @classmethod
    def circle(cls, n: int, spacing: float = 1.0, ud_radius: float = 1.0) -> DataGraph:
        """Circle graph."""

        d_theta = (2.0 * np.pi) / n
        r = spacing / (2.0 * np.sin(np.pi / n))
        theta = np.linspace(0.0, 2.0 * np.pi - d_theta, n)
        coords = [(x, y) for x, y in zip(r * np.cos(theta), r * np.sin(theta))]
        edges = [(i, i + 1) for i in range(n - 1)] + [(n - 1, 0)]
        graph = cls.from_coordinates(coords)
        graph.add_edges_from(edges)
        graph.ud_radius = ud_radius
        graph._node_weights = {i: None for i in graph.nodes}
        graph._edge_weights = {e: None for e in graph.ordered_edges}
        return graph

    @classmethod
    def random_er(cls, n: int, p: float) -> DataGraph:
        """ER random graph."""
        base_graph = nx.erdos_renyi_graph(n, p)
        graph = cls(list(base_graph.edges))
        graph._node_weights = {i: None for i in graph.nodes}
        graph._edge_weights = {e: None for e in graph.ordered_edges}
        return graph

    @classmethod
    def random_ud(
        cls,
        n: int,
        ud_radius: float = 1.0,
        scale: float | None = None,
    ) -> DataGraph:
        """Random unit disk graph."""
        if scale is None:
            scale = ((n**0.5) ** 0.5) / 2
        coords = random_coords(n, scale)
        graph = cls.from_coordinates(coords)
        graph.ud_radius = ud_radius
        graph.set_edges_ud()
        graph._node_weights = {i: None for i in graph.nodes}
        graph._edge_weights = {e: None for e in graph.ordered_edges}
        return graph

    @classmethod
    def from_matrix(cls, data: ArrayLike) -> DataGraph:
        """NEEDS TO BE MADE FASTER."""
        if data.ndim != 2:
            raise ValueError("2D Matrix required.")
        if not np.allclose(data, data.T, rtol=0.0, atol=ATOL_32):
            raise ValueError("Matrix must be symmetric.")

        diag = np.diag(data)
        n_nodes = len(diag)
        node_weights = {i: diag[i] for i in range(n_nodes)}
        if np.allclose(diag, np.zeros(n_nodes), rtol=0.0, atol=ATOL_32):
            node_weights = {i: None for i in range(n_nodes)}
        else:
            node_weights = {i: diag[i].item() for i in range(n_nodes)}

        data[data <= ATOL_32] = 0.0
        non_zero = data.nonzero()
        i_list = non_zero[0].tolist()
        j_list = non_zero[1].tolist()

        edge_list = [(i, j) for i, j in zip(i_list, j_list) if i < j]
        edge_weights = {(i, j): data[i, j].item() for i, j in edge_list}

        graph = cls.from_nodes(range(n_nodes))
        graph.add_edges_from(edge_list)
        graph.node_weights = node_weights
        graph.edge_weights = edge_weights
        return graph

    @classmethod
    def from_pyg(cls, data) -> DataGraph:  # type: ignore
        """Create a graph from a pyg data object."""
        raise NotImplementedError

    ##################
    ### PROPERTIES ###
    ##################

    @property
    def node_weights(self) -> dict:
        """Dictionary of node weights."""
        return self._node_weights

    @node_weights.setter
    def node_weights(self, weights: Collection) -> None:
        if isinstance(weights, list):
            weights_dict = {i: w for i, w in zip(self.nodes, weights)}
        elif isinstance(weights, dict):
            nodes = set(weights.keys())
            if set(self.nodes) != nodes:
                raise ValueError(
                    "Set of nodes in the given dictionary does not match the graph nodes."
                )
            weights_dict = weights
        self._node_weights = weights_dict

    @property
    def edge_weights(self) -> dict:
        """Dictionary of edge weights."""
        return self._edge_weights

    @edge_weights.setter
    def edge_weights(self, weights: Collection) -> None:
        if isinstance(weights, list):
            weights_dict = {i: w for i, w in zip(self.ordered_edges, weights)}
        elif isinstance(weights, dict):
            edges = set(weights.keys())
            if set(self.ordered_edges) != edges:
                raise ValueError(
                    "Set of edges in the given dictionary does not match the graph ordered edges."
                )
            weights_dict = weights
        self._edge_weights = weights_dict

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

    def set_edges_ud(self) -> None:
        """Reset graph edges to be equal to the unit-disk set of edges."""
        super().set_edges_ud()
        self._edge_weights = {e: None for e in self.ordered_edges}
