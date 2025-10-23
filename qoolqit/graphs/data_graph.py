# TODO:
# - refactor this to reuse common methods in constructors
# - refactor using rescale_coords method


from __future__ import annotations

from collections.abc import Iterable

import networkx as nx
import numpy as np
from numpy.typing import ArrayLike

from qoolqit.utils import ATOL_32

from .base_graph import BaseGraph
from .utils import random_coords


class DataGraph(BaseGraph):
    """The main graph structure to represent problem data."""

    def __init__(self, edges: Iterable = []) -> None:
        """
        Default constructor for the BaseGraph.

        Arguments:
            edges: set of edge tuples (i, j)
        """
        super().__init__(edges)

    def _reset_dicts(self) -> None:
        """Reset the default weight dictionaries."""
        self._node_weights = {n: None for n in self.nodes}
        self._edge_weights = {e: None for e in self.sorted_edges}

    # classmethods

    @classmethod
    def line(cls, n: int, spacing: float = 1.0) -> DataGraph:
        """Constructs a line graph, with the respective coordinates.

        Arguments:
            n: number of nodes.
            spacing: distance between each node.
        """
        coords = [(i * spacing, 0.0) for i in range(n)]
        graph = cls.from_coordinates(coords)
        edges = [(i, i + 1) for i in range(0, n - 1)]
        graph.add_edges_from(edges)
        graph._reset_dicts()
        return graph

    @classmethod
    def circle(
        cls,
        n: int,
        spacing: float = 1.0,
        center: tuple = (0.0, 0.0),
    ) -> DataGraph:
        """Constructs a circle graph, with the respective coordinates.

        Arguments:
            n: number of nodes.
            spacing: distance between each node.
            center: point (x, y) to set as the center of the graph.
        """

        d_theta = (2.0 * np.pi) / n
        r = spacing / (2.0 * np.sin(np.pi / n))
        theta = np.linspace(0.0, 2.0 * np.pi - d_theta, n)
        coords = [
            (x + center[0], y + center[1]) for x, y in zip(r * np.cos(theta), r * np.sin(theta))
        ]
        edges = [(i, i + 1) for i in range(n - 1)] + [(n - 1, 0)]
        graph = cls.from_coordinates(coords)
        graph.add_edges_from(edges)
        graph._reset_dicts()
        return graph

    @classmethod
    def random_er(cls, n: int, p: float, seed: int | None = None) -> DataGraph:
        """Constructs an Erdős–Rényi random graph.

        Arguments:
            n: number of nodes.
            p: probability that any two nodes connect.
            seed: random seed.
        """
        base_graph = nx.erdos_renyi_graph(n, p, seed)
        graph = DataGraph.from_nodes(list(base_graph.nodes))
        graph.add_edges_from(base_graph.edges)
        graph._reset_dicts()
        return graph

    @classmethod
    def triangular(
        cls,
        m: int,
        n: int,
        spacing: float = 1.0,
    ) -> DataGraph:
        """
        Constructs a triangular lattice graph, with respective coordinates.

        Arguments:
            m: Number of rows of triangles.
            n: Number of columns of triangles.
            spacing: The distance between adjacent nodes on the final lattice.
        """
        G = nx.triangular_lattice_graph(m, n, with_positions=True)
        G = nx.convert_node_labels_to_integers(G)
        pos_unit = nx.get_node_attributes(G, "pos")

        final_pos = {node: (x * spacing, y * spacing) for node, (x, y) in pos_unit.items()}

        graph = cls.from_coordinates(final_pos)
        graph.add_edges_from(G.edges)
        graph._reset_dicts()
        return graph

    @classmethod
    def hexagonal(
        cls,
        m: int,
        n: int,
        spacing: float = 1.0,
    ) -> DataGraph:
        """
        Constructs a hexagonal lattice graph, with respective coordinates.

        Arguments:
            m: Number of rows of hexagons.
            n: Number of columns of hexagons.
            spacing: The distance between adjacent nodes on the final lattice.
        """
        G = nx.hexagonal_lattice_graph(m, n, with_positions=True)
        G = nx.convert_node_labels_to_integers(G)
        pos_unit = nx.get_node_attributes(G, "pos")

        final_pos = {node: (x * spacing, y * spacing) for node, (x, y) in pos_unit.items()}

        graph = cls.from_coordinates(final_pos)
        graph.add_edges_from(G.edges)
        graph._reset_dicts()
        return graph

    @classmethod
    def heavy_hexagonal(
        cls,
        m: int,
        n: int,
        spacing: float = 1.0,
    ) -> DataGraph:
        """
        Constructs a heavy-hexagonal lattice graph, with respective coordinates.

        Arguments:
            m: Number of rows of hexagons.
            n: Number of columns of hexagons.
            spacing: The distance between adjacent nodes on the final lattice.

        Notes:
            The heavy-hexagonal lattice is a regular hexagonal lattice where
            each edge is decorated with an additional lattice site.
        """
        G_hex = nx.hexagonal_lattice_graph(m, n, with_positions=True)
        pos_unit = nx.get_node_attributes(G_hex, "pos")

        G_heavy = nx.Graph()
        scaling_factor = 2 * spacing

        label_map = {}
        for old_label, (x, y) in pos_unit.items():
            # Relabel to an even-integer grid to make space for midpoint nodes
            new_label = (2 * old_label[0], 2 * old_label[1])
            label_map[old_label] = new_label

            # Scale positions and add the node to the new graph
            new_pos = (x * scaling_factor, y * scaling_factor)
            G_heavy.add_node(new_label, pos=new_pos)

        for u_old, v_old in G_hex.edges():
            u_new, v_new = label_map[u_old], label_map[v_old]

            mid_label = ((u_new[0] + v_new[0]) // 2, (u_new[1] + v_new[1]) // 2)

            pos_u = G_heavy.nodes[u_new]["pos"]
            pos_v = G_heavy.nodes[v_new]["pos"]
            mid_pos = ((pos_u[0] + pos_v[0]) / 2, (pos_u[1] + pos_v[1]) / 2)

            G_heavy.add_node(mid_label, pos=mid_pos)
            G_heavy.add_edge(u_new, mid_label)
            G_heavy.add_edge(mid_label, v_new)

        final_nodes = sorted(list(G_heavy.nodes()))

        final_coords = [G_heavy.nodes[label]["pos"] for label in final_nodes]

        label_to_int = {label: i for i, label in enumerate(final_nodes)}

        final_edges = [(label_to_int[u], label_to_int[v]) for u, v in G_heavy.edges()]

        graph = cls.from_coordinates(final_coords)
        graph.add_edges_from(final_edges)
        graph._reset_dicts()
        return graph

    @classmethod
    def square(
        cls,
        m: int,
        n: int,
        spacing: float = 1.0,
    ) -> DataGraph:
        """
        Constructs a square lattice graph, with respective coordinates.

        Arguments:
            m: Number of rows of square.
            n: Number of columns of square.
            spacing: The distance between adjacent nodes on the final lattice.
        """
        G = nx.grid_2d_graph(m, n)
        final_coords = [(x * spacing, y * spacing) for (x, y) in list(G.nodes)]
        G = nx.convert_node_labels_to_integers(G)

        graph = DataGraph.from_coordinates(final_coords)
        graph.add_edges_from(G.edges)
        graph._reset_dicts()
        return graph

    @classmethod
    def random_ud(
        cls,
        n: int,
        radius: float = 1.0,
        L: float | None = None,
    ) -> DataGraph:
        """Constructs a random unit-disk graph.

        The nodes are sampled uniformly from a square of size (L x L).
        If L is not given, it is estimated based on a rough heuristic that
        of packing N nodes on a square of side L such that the expected
        minimum distance is R, leading to L ~ (R / 2) * sqrt(π * n).

        Arguments:
            n: number of nodes.
            radius: radius to use for defining the unit-disk edges.
            L: size of the square on which to sample the node coordinates.
        """
        if L is None:
            L = (radius / 2) * ((np.pi * n) ** 0.5)
        coords = random_coords(n, L)
        graph = cls.from_coordinates(coords)
        edges = graph.ud_edges(radius)
        graph.add_edges_from(edges)
        graph._reset_dicts()
        return graph

    @classmethod
    def from_matrix(cls, data: ArrayLike) -> DataGraph:
        """Constructs a graph from a symmetric square matrix.

        The diagonal values are set as the node weights. For each entry (i, j)
        where M[i, j] != 0 an edge (i, j) is added to the graph and the value
        M[i, j] is set as its weight.

        Arguments:
            data: symmetric square matrix.
        """
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

    @property
    def node_weights(self) -> dict:
        """Return the dictionary of node weights."""
        return self._node_weights

    @node_weights.setter
    def node_weights(self, weights: list | dict) -> None:
        """Set the dictionary of node weights.

        Arguments:
            weights: list or dictionary of weights.
        """
        if isinstance(weights, list):
            if len(weights) != self.number_of_nodes():
                raise ValueError("Size of the weights list does not match the number of nodes.")
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
        """Return the dictionary of edge weights."""
        return self._edge_weights

    @edge_weights.setter
    def edge_weights(self, weights: list | dict) -> None:
        """Set the dictionary of edge weights.

        Arguments:
            weights: list or dictionary of weights.
        """
        if isinstance(weights, list):
            if len(weights) != self.number_of_edges():
                raise ValueError("Size of the weights list does not match the number of nodes.")
            weights_dict = {i: w for i, w in zip(self.sorted_edges, weights)}
        elif isinstance(weights, dict):
            edges = set(weights.keys())
            if set(self.sorted_edges) != edges:
                raise ValueError(
                    "Set of edges in the given dictionary does not match the graph ordered edges."
                )
            weights_dict = weights
        self._edge_weights = weights_dict

    @property
    def has_node_weights(self) -> bool:
        """Check if the graph has node weights.

        Requires all nodes to have a weight.
        """
        return not ((None in self._node_weights.values()) or len(self._node_weights) == 0)

    @property
    def has_edge_weights(self) -> bool:
        """Check if the graph has edge weights.

        Requires all edges to have a weight.
        """
        return not ((None in self._edge_weights.values()) or len(self._edge_weights) == 0)

    def set_ud_edges(self, radius: float) -> None:
        """Reset the set of edges to be equal to the set of unit-disk edges."""
        super().set_ud_edges(radius=radius)
        self._edge_weights = {e: None for e in self.sorted_edges}
