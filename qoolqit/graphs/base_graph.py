"""Base graph class on top of NetworkX: coordinates, weights, matrix conversion, unit-disk utils."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import numpy.typing as npt
from matplotlib.axes import Axes

from .utils import (
    all_node_pairs,
    distances,
    less_or_equal,
    scale_coords,
    space_coords,
)


class BaseGraph(nx.Graph):
    """Base graph class, directly inheriting from the NetworkX Graph.

    On top of the standard networkx.Graph functionalities, adds alternative
    constructors, node coordinates and weights as first-class attributes,
    distance and Rydberg-interaction calculations, unit-disk graph analysis,
    and plotting.

    Attributes:
        coords: Dict mapping each node to its 2D coordinate, or None if unset.
        node_weights: Dict mapping each node to its weight, or None if unset.
        edge_weights: Dict mapping each edge to its weight, or None if unset.

    Note:
        Alternative constructors: `from_nodes`, `from_coordinates`, `from_nx`,
        `from_matrix` (with its inverse `to_matrix`).
        Coordinates and distances: `coords`, `distances`, `min_distance`,
        `max_distance`, `rescale_coords`.
        Unit-disk analysis: `is_ud_graph`, `ud_radius_range`, `ud_edges`,
        `set_ud_edges`.
        Rydberg-analog interactions: `interactions`, `interaction_matrix`.
        Plotting: `draw`.
    """

    @classmethod
    def from_nodes(cls, nodes: Iterable) -> BaseGraph:
        """Construct a base graph from a set of nodes.

        Args:
            nodes: Iterable container.
                Can be a container of nodes (list, dict, set, etc.) or
                a container of (node, attribute dict) tuples.
                Node attributes are updated using the attribute dict.
        """
        graph = cls()
        graph.add_nodes_from(nodes)
        return graph

    @classmethod
    def from_coordinates(cls, coords: list | dict) -> BaseGraph:
        """Construct a base graph from a set of coordinates.

        From a list of coordinates, nodes are labelled with their index.
        From a dictionary, nodes are labelled with their keys.
        Each node is added to the graph with its position as a node attribute `pos`.

        Args:
            coords: list or dictionary of coordinate pairs.
        """
        if isinstance(coords, list):
            coords_tuple = ((i, {"pos": pos}) for i, pos in enumerate(coords))
        elif isinstance(coords, dict):
            coords_tuple = ((key, {"pos": pos}) for key, pos in coords.items())

        return cls.from_nodes(coords_tuple)

    @classmethod
    def from_matrix(cls, data: npt.NDArray[np.float64]) -> BaseGraph:
        """Constructs a graph from a symmetric square matrix.

        The diagonal values are set as the node weights. For each entry (i, j)
        where M[i, j] != 0 an edge (i, j) is added to the graph and the value
        M[i, j] is set as its weight.

        Arguments:
            data: real symmetric square matrix.
        """
        if data.ndim != 2:
            raise ValueError("2D Matrix required.")
        if not np.allclose(data, data.T, rtol=0.0, atol=1e-7):
            raise ValueError("Matrix must be symmetric.")

        # Absolute values below this tolerance are treated as zeros.
        # The corresponding node or edge weight is neglected (weight = None).
        nonzero_tol = 1e-7

        diag = np.diag(data)
        n_nodes = len(diag)
        if np.allclose(diag, np.zeros(n_nodes), rtol=0.0, atol=nonzero_tol):
            node_weights = {i: None for i in range(n_nodes)}
        else:
            node_weights = {i: diag[i].item() for i in range(n_nodes)}

        edge_list = [
            (i, j)
            for i in range(n_nodes)
            for j in range(i + 1, n_nodes)
            if (np.abs(data[i, j]) >= nonzero_tol)
        ]
        edge_weights = {(i, j): data[i, j].item() for i, j in edge_list}

        graph = cls.from_nodes(range(n_nodes))
        graph.add_edges_from(edge_list)
        graph.node_weights = node_weights
        graph.edge_weights = edge_weights
        return graph

    def to_matrix(self) -> npt.NDArray[np.float64]:
        """Return the adjacency matrix of this graph.

        The inverse of `from_matrix`.
        Nodes are mapped to indices 0, ..., N-1 according to `self.nodes` insertion order.
        - Node weights are stored in the diagonal since self-loops are not supported.
            Nodes with no weight set (None) are left at 0.0 in the diagonal.
        - For each edge (i, j), the entries (i,j) and (j,i) are set to its weight,
            or to 1.0 if the edge has no weight set.

        Returns:
            Symmetric N x N matrix of dtype float64, where N is the number of nodes.
        """
        n_nodes = len(self.nodes)
        index = {node: i for i, node in enumerate(self.nodes)}
        matrix = np.zeros((n_nodes, n_nodes), dtype=np.float64)

        for node, weight in self.node_weights.items():
            if weight is not None:
                i = index[node]
                matrix[i, i] = weight

        for (u, v), weight in self.edge_weights.items():
            i, j = index[u], index[v]
            matrix[i, j] = matrix[j, i] = weight if weight is not None else 1.0

        return matrix

    @property
    def sorted_edges(self) -> set:
        """Returns the set of edges (u, v) such that (u < v)."""
        nx_edges = set(self.edges)
        unordered_edges = set(filter(lambda x: x[0] > x[1], nx_edges))
        corrected_edges = set((j, i) for (i, j) in unordered_edges)
        return (nx_edges - unordered_edges).union(corrected_edges)

    @property
    def all_node_pairs(self) -> set:
        """Return a list of all possible node pairs in the graph."""
        return all_node_pairs(self.nodes)

    @property
    def has_coords(self) -> bool:
        """Check if the graph has coordinates on all nodes."""
        return self.number_of_nodes() > 0 and all(
            pos is not None for _, pos in self.nodes(data="pos")
        )

    @property
    def has_node_weights(self) -> bool:
        """Check if the graph has node weights on all nodes."""
        return self.number_of_nodes() > 0 and all(
            w is not None for _, w in self.nodes(data="weight")
        )

    @property
    def has_edge_weights(self) -> bool:
        """Check if the graph has edge weights on all edges."""
        return self.number_of_edges() > 0 and all(
            w is not None for _, _, w in self.edges(data="weight")
        )

    @property
    def node_weights(self) -> dict:
        """Return the dictionary of node weights."""
        return dict(self.nodes(data="weight"))

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
        nx.set_node_attributes(self, weights_dict, "weight")

    @property
    def edge_weights(self) -> dict:
        """Return the dictionary of edge weights."""
        return {(u, v): w for u, v, w in self.edges(data="weight")}

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
        nx.set_edge_attributes(self, weights_dict, "weight")

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
    def coords(self) -> dict:
        """Return a dictionary of node coordinates."""
        return dict(self.nodes(data="pos"))

    @coords.setter
    def coords(self, coords: list | dict) -> None:
        """Set the dictionary of node coordinates.

        Args:
            coords: list or dictionary of coordinate pairs.
        """
        if isinstance(coords, list):
            coords_dict = {i: pos for i, pos in zip(self.nodes, coords)}
        elif isinstance(coords, dict):
            nodes = set(coords.keys())
            if set(self.nodes) != nodes:
                raise ValueError(
                    "Set of nodes in the given dictionary does not match the graph nodes."
                )
            coords_dict = coords
        nx.set_node_attributes(self, coords_dict, "pos")

    def distances(self, edge_list: Iterable | None = None) -> dict:
        """Returns a dictionary of distances for a given set of edges.

        Distances are calculated directly from the coordinates. Raises an error
        if there are no coordinates on the graph.

        Args:
            edge_list: set of edges.
        """
        if self.has_coords:
            if edge_list is None:
                edge_list = self.all_node_pairs
            elif len(edge_list) == 0:  # type: ignore [arg-type]
                raise ValueError("Trying to compute distances for an empty edge list.")
            return distances(self.coords, edge_list)
        else:
            raise AttributeError("Trying to compute distances for a graph without coordinates.")

    def interactions(self) -> dict:
        """Rydberg model interaction 1/r^6 between pair of nodes."""
        return {p: 1.0 / (r**6) for p, r in self.distances().items()}

    def interaction_matrix(self) -> np.ndarray:
        """Rydberg model interaction 1/r^6 between pairs of nodes, as a matrix.

        Node ordering follows `self.nodes` insertion order.
        The diagonal is 0, since there is no self-interaction.

        Returns:
            Symmetric N x N matrix of dtype float64, where N is the number of nodes.
        """
        index = {node: i for i, node in enumerate(self.nodes)}
        n_nodes = len(index)
        matrix = np.zeros((n_nodes, n_nodes), dtype=np.float64)

        for (u, v), interaction in self.interactions().items():
            i, j = index[u], index[v]
            matrix[i, j] = matrix[j, i] = interaction

        return matrix

    def min_distance(self, connected: bool | None = None) -> float:
        """Returns the minimum distance in the graph.

        Args:
            connected: if True/False, computes only over connected/disconnected nodes.
        """
        distance: float
        if connected is None:
            distance = min(self.distances(self.all_node_pairs).values())
        elif connected:
            distance = min(self.distances(self.sorted_edges).values())
        else:
            distance = min(self.distances(self.all_node_pairs - self.sorted_edges).values())
        return distance

    def max_distance(self, connected: bool | None = None) -> float:
        """Returns the maximum distance in the graph.

        Arguments:
            connected: if True/False, computes only over connected/disconnected nodes.
        """
        distance: float
        if connected is None:
            distance = max(self.distances(self.all_node_pairs).values())
        elif connected:
            distance = max(self.distances(self.sorted_edges).values())
        else:
            distance = max(self.distances(self.all_node_pairs - self.sorted_edges).values())
        return distance

    def ud_radius_range(self) -> tuple:
        """Return the range (R_min, R_max) where the graph is unit-disk.

        The graph is unit-disk if the maximum distance between all connected nodes is
        smaller than the minimum distance between disconnected nodes. This means that
        for any value R in that interval, the following condition is true:

        graph.ud_edges(radius = R) == graph.sorted edges
        """
        if self.has_coords:
            n_edges = len(self.sorted_edges)
            if n_edges == 0:
                # If the graph is empty and has coordinates
                return (0.0, self.min_distance(connected=False))
            elif n_edges == len(self.all_node_pairs):
                # If the graph is fully connected
                return (self.max_distance(connected=True), float("inf"))
            elif self.max_distance(connected=True) < self.min_distance(connected=False):
                return (self.max_distance(connected=True), self.min_distance(connected=False))
            else:
                raise ValueError("Graph is not unit disk.")
        else:
            raise AttributeError("Checking if graph is unit disk is not valid without coordinates.")

    def is_ud_graph(self) -> bool:
        """Check if the graph is unit-disk."""
        try:
            self.ud_radius_range()
            return True
        except ValueError:
            return False

    def ud_edges(self, radius: float) -> set:
        """Returns the set of edges given by the intersection of circles of a given radius.

        Args:
            radius: the value
        """
        if self.has_coords:
            return set(e for e, d in self.distances().items() if less_or_equal(d, radius))
        else:
            raise AttributeError("Getting unit disk edges is not valid without coordinates.")

    def rescale_coords(
        self,
        *args: Any,
        scaling: float | None = None,
        spacing: float | None = None,
    ) -> None:
        """Rescales the node coordinates by a factor.

        Accepts either a scaling or a spacing factor.

        Args:
            scaling: value to scale by.
            spacing: value to set as the minimum distance in the graph.
        """
        if self.has_coords:
            msg = "Please pass either a `scaling` or a `spacing` value as a keyword argument."
            if (len(args) > 0) or (scaling is None and spacing is None):
                raise TypeError(msg)
            if scaling is None and spacing is not None:
                self.coords = space_coords(self.coords, spacing)
            elif spacing is None and scaling is not None:
                self.coords = scale_coords(self.coords, scaling)
            else:
                raise TypeError(msg)
        else:
            raise AttributeError("Trying to rescale coordinates on a graph without coordinates.")

    def set_ud_edges(self, radius: float) -> None:
        """Reset the set of edges to be equal to the set of unit-disk edges.

        Args:
            radius: the radius to use in determining the set of unit-disk edges.
        """
        self.remove_edges_from(list(self.edges))
        self.add_edges_from(self.ud_edges(radius))

    @classmethod
    def from_nx(cls, g: nx.Graph) -> BaseGraph:
        """Convert a NetworkX Graph object into a QoolQit graph instance.

        The input `networkx.Graph` graph must be defined only with the following allowed

        Node attributes:
            pos (tuple): represents the node 2D position. Must be a list/tuple of real numbers.
            weight: represents the node weight. Must be a real number.
        Edge attributes:
            weight: represents the edge weight. Must be a real number.

        Returns an instance of the class with following attributes:
            - node_weights : dict[node, float or None]
            - edge_weights : dict[(u,v), float or None]
            - coords       : dict[node, (float,float) or None]
        """
        if not isinstance(g, nx.Graph):
            raise TypeError("Input must be a networkx.Graph instance.")

        g = nx.convert_node_labels_to_integers(g)
        num_nodes = len(g.nodes)
        num_edges = len(g.edges)

        # validate node attributes
        for name, data in g.nodes.data():
            unexpected_keys = set(data) - {"weight", "pos"}
            if unexpected_keys:
                raise ValueError(f"{unexpected_keys} not allowed in node attributes.")

        node_pos = nx.get_node_attributes(g, "pos")
        if node_pos:
            if len(node_pos) != num_nodes:
                raise ValueError("Node attribute `pos` must be defined for all nodes")
            for name, pos in node_pos.items():
                is_2D = isinstance(pos, (tuple, list)) & (len(pos) == 2)
                is_real = all(isinstance(p, (float, int)) for p in pos)
                if not (is_2D & is_real):
                    raise TypeError(
                        f"In node {name} the `pos` attribute must be a 2D tuple/list"
                        f" of real numbers, got {pos} instead."
                    )
        node_weights = nx.get_node_attributes(g, "weight")
        if node_weights:
            if len(node_weights) != num_nodes:
                raise ValueError("Node attribute `weight` must be defined for all nodes")
            for name, weight in node_weights.items():
                if not isinstance(weight, (float, int)):
                    raise TypeError(
                        f"In node {name} the `weight` attribute must be a real number, "
                        f"got {type(weight)} instead."
                        ""
                    )

        # validate edge attributes
        for u, v, data in g.edges.data():
            unexpected_keys = set(data) - {"weight"}
            if unexpected_keys:
                raise ValueError(f"{unexpected_keys} not allowed in edge attributes.")
        edge_weights = nx.get_edge_attributes(g, "weight")
        if edge_weights:
            if len(edge_weights) != num_edges:
                raise ValueError("Edge attribute `weight` must be defined for all edges")
            for name, weight in edge_weights.items():
                if not isinstance(weight, (float, int)):
                    raise TypeError(
                        f"In edge {name}, the attribute `weight` must be a real number, "
                        f"got {type(weight)} instead."
                    )

        return cls(g)

    def draw(self, ax: Axes | None = None, **kwargs: Any) -> None:
        """Draw the graph.

        Uses the draw_networkx function from NetworkX.

        Args:
            ax: Axes object to draw on. If None, uses the current Axes.
            **kwargs: keyword-arguments to pass to draw_networkx.
        """
        if self.has_coords:
            if "hide_ticks" not in kwargs:
                kwargs["hide_ticks"] = False

            nx.draw_networkx(self, pos=self.coords, ax=ax, **kwargs)

            if ax is None:
                ax = plt.gca()
            ax.set_xlabel("x")
            ax.set_ylabel("y")
            ax.grid(True, color="lightgray", linestyle="--", linewidth=0.7)

            # minimum ybox
            ylim = ax.get_ylim()
            if (ylim[1] - ylim[0]) < 2:
                y_center = (ylim[0] + ylim[1]) / 2
                ax.set_ylim(y_center - 1, y_center + 1)
            plt.tight_layout()
        else:
            nx.draw_networkx(self, ax=ax, **kwargs)
