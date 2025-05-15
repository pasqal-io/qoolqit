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
    min_distance,
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
            edges: Iterable of edge tuples (i, j)
        """
        if edges and not isinstance(edges, Iterable):
            raise TypeError("Input is not a valid edge list.")

        super().__init__()
        self.add_edges_from(edges)
        self._coords = {i: None for i in self.nodes}
        self._ud_radius: float | None = None
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
            nodes: Iterable of nodes.
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

    @property
    def distances(self) -> dict:
        """Dictionary of distances for all node pairs in the graph.

        Distances are calculated directly the coordinates. If the graph has no coordinates
        the distance will be set as None.
        """
        return distances(self.coords, self.all_node_pairs)

    @property
    def edge_distances(self) -> dict:
        """Dictionary of distances for all edges in the graph.

        Distances are calculated directly the coordinates. If the graph has no coordinates
        the distance will be set as None.
        """
        return distances(self.coords, self.sorted_edges)

    @property
    def min_distance(self) -> float | None:
        """Return the distance between the two closest nodes in the graph."""
        return min_distance(self.coords) if self.has_coords else None

    @property
    def ud_radius(self) -> float | None:
        """Return the unit-disk radius currently used in the graph."""
        return self._ud_radius

    @ud_radius.setter
    def ud_radius(self, radius: float) -> None:
        """Set the unit-disk radius to be used in the graph.

        Arguments:
            radius: value for the unit-disk radius.
        """
        self._ud_radius = radius

    @property
    def ud_edges(self) -> set:
        """Return the set of unit-disk edges.

        This is defined as the set of edges where the distance d[u, v] <= r, where r
        is the ud_radius currently set in the graph. If the graph has no coordinates,
        the set of unit-disk edges is empty. The set of unit-disk edges is computed
        directly from all pairs of nodes in the graph, and has no direct connection with
        the set of edges defined in the graph.
        """
        if self.has_coords:
            if self.ud_radius is None:
                raise ValueError(
                    "Unit-disk edges requires setting the unit-disk radius. "
                    "You can set it in the `ud_radius` property."
                )
            return set(e for e, d in self.distances.items() if less_or_equal(d, self.ud_radius))
        else:
            return set()

    @property
    def is_ud_graph(self) -> bool:
        """Check if the graph is unit-disk.

        The graph is considered unit-disk if the set of edges
        is equal to its set of unit-disk edges.
        """
        if self.has_coords:
            return set(self.ud_edges) == self.sorted_edges
        else:
            return False

    ###############
    ### METHODS ###
    ###############

    def rescale_coords(self, scaling: float) -> None:
        """Rescales the node coordinates by a constant factor.

        Arguments:
            scaling: value to scale by.
        """
        if not self.has_coords:
            raise ValueError("Trying to rescale coordinates on a graph without coordinates.")
        self._coords = scale_coords(self._coords, scaling)

    def respace_coords(self, spacing: float) -> None:
        """Rescales the node coordinates so the minimum distance is equal to a set spacing.

        Arguments:
            spacing: value to set as the minimum distance in the graph.
        """
        if not self.has_coords:
            raise ValueError("Trying to rescale coordinates on a graph without coordinates.")
        self._coords = space_coords(self._coords, spacing)

    def set_edges_ud(self) -> None:
        """Reset the set of edges to be equal to the set of unit-disk edges."""
        self.remove_edges_from(list(self.edges))
        self.add_edges_from(self.ud_edges)

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
