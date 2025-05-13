from __future__ import annotations

from math import ceil, isclose
from typing import Any, Collection, Iterable

import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.ticker import MultipleLocator

from .utils import all_node_pairs, distances, min_distance, scale_coords, space_coords


def less_or_equal(a: float, b: float, rel_tol: float = 0.0, abs_tol: float = 1e-8) -> bool:
    """Less or approximately equal."""
    return a < b or isclose(a, b, rel_tol=rel_tol, abs_tol=abs_tol)


class BaseGraph(nx.Graph):
    """
    The BaseGraph in QoolQit, direclty inheriting from nx.Graph.
    """

    def __init__(self, edges: list | tuple | set = []) -> None:

        if edges and not isinstance(edges, (list, tuple, set)):
            raise TypeError("Graph must be initialized empty or with a set of edges")

        super().__init__()
        self.add_edges_from(edges)
        self._coords = {i: None for i in self.nodes}
        self._ud_radius: float | None = None

    ####################
    ### CONSTRUCTORS ###
    ####################

    @classmethod
    def from_nodes(cls, nodes: Iterable) -> BaseGraph:
        graph = cls()
        graph.add_nodes_from(nodes)
        graph._coords = {i: None for i in graph.nodes}
        return graph

    @classmethod
    def from_coordinates(cls, coords: Collection) -> BaseGraph:
        """Get a list of (x, y) tuples and initialize."""
        if isinstance(coords, list):
            nodes = list(range(len(coords)))
            coords_dict = {i: pos for i, pos in enumerate(coords)}
        elif isinstance(coords, dict):
            nodes = list(coords.keys())
            coords_dict = coords
        graph = cls.from_nodes(nodes)
        graph._coords = coords_dict
        return graph

    ##################
    ### PROPERTIES ###
    ##################

    @property
    def ordered_edges(self) -> set:
        """Edges (u, v) such that (u < v)."""
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
        return not ((None in self._coords.values()) or len(self._coords) == 0)

    @property
    def has_edges(self) -> bool:
        return len(self.edges) > 0

    @property
    def coords(self) -> dict:
        """Return the dictionary of node coordinates."""
        return self._coords

    @coords.setter
    def coords(self, coords: Collection) -> None:
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
        """Dictionary of distances for all node pairs in the graph."""
        return distances(self.coords, self.all_node_pairs)

    @property
    def edge_distances(self) -> dict:
        """Dictionary of distances for the node pairs that are connected by an edge."""
        return distances(self.coords, self.ordered_edges)

    @property
    def min_distance(self) -> float | None:
        """Return the minimum distance between two nodes in the graph."""
        return min_distance(self.coords) if self.has_coords else None

    @property
    def ud_radius(self) -> float | None:
        return self._ud_radius

    @ud_radius.setter
    def ud_radius(self, value: float) -> None:
        self._ud_radius = value

    @property
    def ud_edges(self) -> set:
        if self.has_coords:
            if not self.ud_radius:
                raise ValueError(
                    "Unit-disk edges requires setting the unit-disk radius. "
                    "You can set it in the `ud_radius` property."
                )
            return set(e for e, d in self.distances.items() if less_or_equal(d, self.ud_radius))
        else:
            return set()

    @property
    def is_ud_graph(self) -> bool:
        """Check if graph is unit-disk."""
        return set(self.ud_edges) == self.ordered_edges

    ###############
    ### METHODS ###
    ###############

    def rescale_coords(self, scaling: float) -> None:
        """Rescale node coords by a constant factor."""
        if not self.has_coords:
            raise ValueError("Trying to rescale coordinates on a graph without coordinates.")
        self._coords = scale_coords(self._coords, scaling)

    def respace_coords(self, spacing: float) -> None:
        """Respace node coords so the minimum distance is equal to a set spacing."""
        if not self.has_coords:
            raise ValueError("Trying to rescale coordinates on a graph without coordinates.")
        self._coords = space_coords(self._coords, spacing)

    def set_edges_ud(self) -> None:
        """Reset graph edges to be equal to the unit-disk set of edges."""
        self.remove_edges_from(list(self.edges))
        self.add_edges_from(self.ud_edges)

    def draw(self, *args: Any, **kwargs: Any) -> None:
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
