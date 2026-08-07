from __future__ import annotations

from collections.abc import Iterable
from typing import Any

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from matplotlib.axes import Axes

from .utils import (
    all_node_pairs,
    distances,
    less_or_equal,
    scale_coords,
    space_coords,
)


class BaseGraph(nx.Graph):
    """
    The BaseGraph in QoolQit, directly inheriting from the NetworkX Graph.

    Defines basic functionalities for graphs within the Rydberg Analog, such
    as instantiating from a set of node coordinates, directly accessing node
    distances, and checking if the graph is unit-disk.
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
        return all(pos for _, pos in self.nodes(data="pos"))

    @property
    def has_node_weights(self) -> bool:
        """Check if the graph has node weights on all nodes."""
        return all(w for _, w in self.nodes(data="weight"))

    @property
    def has_edge_weights(self) -> bool:
        """Check if the graph has edge weights on all edges."""
        return all(w for _, _, w in self.edges(data="weight"))

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

        Arguments:
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

        Arguments:
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

        Arguments:
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

        Arguments:
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

        Arguments:
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
            - _node_weights : dict[node, float or None]
            - _edge_weights : dict[(u,v), float or None]
            - _coords       : dict[node, (float,float) or None]
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

        # build the instance of the graph
        graph = cls()
        graph.add_nodes_from(g.nodes)
        graph.add_edges_from(g.edges)
        graph._node_weights = nx.get_node_attributes(g, "weight", default=None)
        graph._coords = nx.get_node_attributes(g, "pos", default=None)
        graph._edge_weights = nx.get_edge_attributes(g, "weight", default=None)

        return graph

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
