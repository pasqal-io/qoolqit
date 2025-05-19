from __future__ import annotations

from collections.abc import Iterable
from math import ceil
from typing import Any

import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.ticker import MultipleLocator

from .utils import (
    all_node_pairs,
    distances,
    less_or_equal,
    scale_coords,
    space_coords,
)


class BaseGraph(nx.Graph):
    """
    The BaseGraph in QoolQit, direclty inheriting from the NetworkX Graph.

    Defines basic functionalities for graphs within the Rydberg Analog, such
    as instantiating from a set of node coordinates, directly accessing node
    distances, and checking if the graph is unit-disk.
    """

    def __init__(self, edges: Iterable = []) -> None:
        """
        Default constructor for the BaseGraph.

        Arguments:
            edges: set of edge tuples (i, j)
        """
        if edges and not isinstance(edges, Iterable):
            raise TypeError("Input is not a valid edge list.")

        super().__init__()
        self.add_edges_from(edges)
        self._coords = {i: None for i in self.nodes}
        self._reset_dicts()

    def _reset_dicts(self) -> None:
        """Placeholder method to reset attribute dictionaries."""
        pass

    ####################
    ### CONSTRUCTORS ###
    ####################

    @classmethod
    def from_nodes(cls, nodes: Iterable) -> BaseGraph:
        """Construct a base graph from a set of nodes.

        Arguments:
            nodes: set of nodes.
        """
        graph = cls()
        graph.add_nodes_from(nodes)
        graph._coords = {i: None for i in graph.nodes}
        graph._reset_dicts()
        return graph

    @classmethod
    def from_coordinates(cls, coords: list | dict) -> BaseGraph:
        """Construct a base graph from a set of coordinates.

        Arguments:
            coords: list or dictionary of coordinate pairs.
        """
        if isinstance(coords, list):
            nodes = list(range(len(coords)))
            coords_dict = {i: pos for i, pos in enumerate(coords)}
        elif isinstance(coords, dict):
            nodes = list(coords.keys())
            coords_dict = coords
        graph = cls.from_nodes(nodes)
        graph._coords = coords_dict
        graph._reset_dicts()
        return graph

    ##################
    ### PROPERTIES ###
    ##################

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
        """Check if the graph has coordinates.

        Requires all nodes to have coordinates.
        """
        return not ((None in self._coords.values()) or len(self._coords) == 0)

    @property
    def has_edges(self) -> bool:
        """Check if the graph has edges."""
        return len(self.edges) > 0

    @property
    def coords(self) -> dict:
        """Return the dictionary of node coordinates."""
        return self._coords

    @coords.setter
    def coords(self, coords: list | dict) -> None:
        """Set the dictionary of node coordinates.

        Arguments:
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
        self._coords = coords_dict

    ###############
    ### METHODS ###
    ###############

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
            raise ValueError("Trying to compute distances for a graph without coordinates.")

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

    def is_ud_graph(self) -> bool:
        """Check if the graph is unit-disk.

        The graph is unit-disk if the maximum distance between all connected nodes is
        smaller than the minimum distance between disconnected nodes. This means that
        for any value R in that interval, the following condition is true:

        graph.ud_edges(radius = R) == graph.sorted edges
        """
        if self.has_coords:
            n_edges = len(self.sorted_edges)
            if n_edges == 0 or n_edges == len(self.all_node_pairs):
                # If the graph is fully connected or empty and has coordinates
                return True
            else:
                return self.max_distance(connected=True) < self.min_distance(connected=False)
        else:
            raise ValueError("Checking if graph is unit disk is not valid without coordinates.")

    def ud_edges(self, radius: float) -> set:
        """Returns the set of edges given by the intersection of circles of a given radius.

        Arguments:
            radius: the value
        """
        if self.has_coords:
            return set(e for e, d in self.distances().items() if less_or_equal(d, radius))
        else:
            raise ValueError("Getting unit disk edges is not valid without coordinates.")

    def rescale_coords(self, scaling: float) -> None:
        """Rescales the node coordinates by a constant factor.

        Arguments:
            scaling: value to scale by.
        """
        if self.has_coords:
            self._coords = scale_coords(self._coords, scaling)
        else:
            raise ValueError("Trying to rescale coordinates on a graph without coordinates.")

    def respace_coords(self, spacing: float) -> None:
        """Rescales the node coordinates so the minimum distance is equal to a set spacing.

        Arguments:
            spacing: value to set as the minimum distance in the graph.
        """
        if not self.has_coords:
            raise ValueError("Trying to rescale coordinates on a graph without coordinates.")
        self._coords = space_coords(self._coords, spacing)

    def set_ud_edges(self, radius: float) -> None:
        """Reset the set of edges to be equal to the set of unit-disk edges.

        Arguments:
            radius: the radius to use in determining the set of unit-disk edges.
        """
        self.remove_edges_from(list(self.edges))
        self.add_edges_from(self.ud_edges(radius))

    def draw(self, return_fig: bool = False, *args: Any, **kwargs: Any) -> plt.Figure | None:
        """Draw the graph.

        Uses the draw_networkx function from NetworkX.

        Arguments:
            *args: arguments to pass to draw_networkx.
            **kwargs: keyword-arguments to pass to draw_networkx.
        """
        fig, ax = plt.subplots(1, 1, dpi=200)
        ax.set_aspect("equal")
        if self.has_coords:
            x_coords, y_coords = zip(*self.coords.values())
            x_min, x_max = min(x_coords), max(x_coords)
            y_min, y_max = min(y_coords), max(y_coords)

            grid_x_min, grid_x_max = min(-1, x_min), max(1, x_max)
            grid_y_min, grid_y_max = min(-1, y_min), max(1, y_max)

            grid_scale = ceil(max(grid_x_max - grid_x_min, grid_y_max - grid_y_min))

            ax.grid(True)

            eps = 0.05 * grid_scale
            ax.set_xlim(grid_x_min - eps, grid_x_max + eps)
            ax.set_ylim(grid_y_min - eps, grid_y_max + eps)

            possible_multiples = [0.2, 0.25, 0.5, 1.0, 2.0, 2.5, 5.0, 10.0]
            grid_multiple = min(possible_multiples, key=lambda x: abs(x - grid_scale / 8))
            majorLocatorX = MultipleLocator(grid_multiple)
            majorLocatorY = MultipleLocator(grid_multiple)
            ax.xaxis.set_major_locator(majorLocatorX)
            ax.yaxis.set_major_locator(majorLocatorY)

            nx.draw_networkx(self, *args, ax=ax, pos=self.coords, **kwargs)
            ax.tick_params(axis="both", which="both", labelbottom=True, labelleft=True, labelsize=8)
        else:
            nx.draw_networkx(self, *args, ax=ax, **kwargs)

        return fig if return_fig else None
