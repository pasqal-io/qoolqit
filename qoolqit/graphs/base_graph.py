from __future__ import annotations

from itertools import product
from math import ceil, dist
from typing import Any, Collection, Iterable

import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.ticker import MultipleLocator


def _all_node_pairs(nodes: list) -> list:
    return list(filter(lambda x: x[0] < x[1], product(nodes, nodes)))


def _dist(p: Iterable | None, q: Iterable | None) -> float | None:
    """Wrapper on dist that accepts None."""
    return None if p is None or q is None else dist(p, q)


def _distances(coords: dict, edge_list: list | None) -> dict:
    if edge_list is None:
        edge_list = _all_node_pairs(list(coords.keys()))
    return {edge: _dist(coords[edge[0]], coords[edge[1]]) for edge in edge_list}


def _min_distance(coords: dict) -> float:
    all_node_pairs = _all_node_pairs(list(coords.keys()))
    distances = _distances(coords, all_node_pairs)
    min_distance: float = min(distances.values())
    return min_distance


def _scale_coords(coords: dict, spacing: float) -> dict:
    min_distance = _min_distance(coords)
    scale_factor = spacing / min_distance
    scaled_coords = {i: (c[0] * scale_factor, c[1] * scale_factor) for i, c in coords.items()}
    return scaled_coords


class BaseGraph(nx.Graph):
    """
    The BaseGraph in QoolQit, direclty inheriting from nx.Graph.
    """

    def __init__(self, edges: list | tuple | None = None) -> None:

        if edges and not isinstance(edges, (list, tuple, set)):
            raise TypeError("Graph must be initialized empty or with a set of edges")

        super().__init__(edges)
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
    def from_coordinates(cls, coords: Collection, spacing: float | None = None) -> BaseGraph:
        """Get a list of (x, y) tuples and initialize."""
        if isinstance(coords, list):
            nodes = list(range(len(coords)))
            coords_dict = {i: pos for i, pos in enumerate(coords)}
        elif isinstance(coords, dict):
            nodes = list(coords.keys())
            coords_dict = coords
        if spacing is not None:
            coords_dict = _scale_coords(coords_dict, spacing)
        graph = cls.from_nodes(nodes)
        graph._coords = coords_dict
        graph._set_node_pos(graph._coords)
        return graph

    @property
    def has_coords(self) -> bool:
        return not ((None in self._coords.values()) or len(self._coords) == 0)

    @property
    def has_edges(self) -> bool:
        return len(self.edges) > 0

    @property
    def all_node_pairs(self) -> nx.EdgeView:
        """Return a list of all possible node pairs in the graph."""
        return _all_node_pairs(self.nodes)

    @property
    def coords(self) -> dict:
        """Return the dictionary of node coordinates."""
        return self._coords

    @property
    def distances(self) -> dict:
        """Dictionary of distances for all node pairs in the graph."""
        return _distances(self.coords, self.all_node_pairs) if self.has_coords else dict()

    @property
    def edge_distances(self) -> dict:
        """Dictionary of distances for the node pairs that are connected by an edge."""
        return _distances(self.coords, self.edges) if self.has_coords else dict()

    @property
    def min_distance(self) -> float | None:
        """Return the minimum distance between two nodes in the graph."""
        return _min_distance(self.coords) if self.has_coords else None

    @property
    def ud_radius(self) -> float:
        return self._ud_radius
    
    @ud_radius.setter
    def ud_radius(self, value: float) -> None:
        self._ud_radius = value

    @property
    def is_ud_graph(self) -> bool:
        """Check if graph is unit-disk."""
        return set(self.ud_edges) == set(self.edges)
    
    @property
    def ud_edges(self) -> list:
        all_node_pairs = self.all_node_pairs
        return [edge for edge in all_node_pairs if self.distances[edge] <= self.ud_radius]

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

    ###########################################
    ### Graph modification methods.         ###
    ### Need to be handled later for safety ###
    ###########################################

    # def add_edge(*args, **kwargs) -> None:
    #     raise NotImplementedError

    # def add_edges_from(self) -> None:
    #     raise NotImplementedError

    # def add_node(self) -> None:
    #     raise NotImplementedError

    # def add_nodes_from(self) -> None:
    #     raise NotImplementedError

    # def add_weighted_edges_from(self) -> None:
    #     raise NotImplementedError

    # def update(self) -> None:
    #     raise NotImplementedError
