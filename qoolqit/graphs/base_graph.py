from __future__ import annotations

from collections.abc import Iterable
from typing import TYPE_CHECKING, Any

import matplotlib.pyplot as plt
import networkx as nx
import torch
from matplotlib.figure import Figure

from .utils import (
    all_node_pairs,
    distances,
    less_or_equal,
    scale_coords,
    space_coords,
)

# import only for the static type checker, not during runtime
if TYPE_CHECKING:
    import torch_geometric


class BaseGraph(nx.Graph):
    """
    The BaseGraph in QoolQit, directly inheriting from the NetworkX Graph.

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
        ...

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

    @classmethod
    def from_pyg(
        cls,
        data: torch_geometric.data.Data,
        node_attrs: Iterable[str] | None = None,
        edge_attrs: Iterable[str] | None = None,
        graph_attrs: Iterable[str] | None = None,
    ) -> BaseGraph:
        """Convert a PyTorch Geometric Data object into a QoolQit graph instance.

        This method requires installing the `torch_geometric` package.
        Uses PyG's to_networkx internally. Only explicitly specified attributes
        are copied, plus default PyG attributes (x, edge_attr, y) and QoolQit
        attributes (pos, weight, edge_weight).

        Arguments:
            data: PyTorch Geometric Data object.
            node_attrs: Node attributes to copy (in addition to defaults).
            edge_attrs: Edge attributes to copy (in addition to defaults).
            graph_attrs: Graph-level attributes to copy as graph attributes.

        Returns:
            BaseGraph instance.

        Notes:
            The input graph will be converted to an undirected graph.
        """
        try:
            from torch_geometric.data import Data
            from torch_geometric.utils import to_networkx
        except ImportError as e:
            raise ImportError("Please, install the `torch_geometric` package.") from e

        if not isinstance(data, Data):
            raise TypeError("Input must be a torch_geometric.data.Data object.")

        node_attrs_list = list(node_attrs) if node_attrs else []
        edge_attrs_list = list(edge_attrs) if edge_attrs else []
        graph_attrs_list = list(graph_attrs) if graph_attrs else []

        # Add default PyG attributes to the lists if present
        if hasattr(data, "x") and data.x is not None:
            node_attrs_list.append("x")
        if hasattr(data, "edge_attr") and data.edge_attr is not None:
            edge_attrs_list.append("edge_attr")
        if hasattr(data, "y") and data.y is not None:
            graph_attrs_list.append("y")

        # Convert via PyG's to_networkx
        nx_graph = to_networkx(
            data,
            node_attrs=node_attrs_list or None,
            edge_attrs=edge_attrs_list or None,
            graph_attrs=graph_attrs_list or None,
            to_undirected=True,
        )

        # Build the graph instance
        graph = cls()
        graph.add_nodes_from(nx_graph.nodes)
        graph.add_edges_from(nx_graph.edges)

        # Initialize internal attributes (same as from_nx)
        graph._coords = {i: None for i in graph.nodes}
        graph._node_weights = {n: None for n in graph.nodes}
        graph._edge_weights = {e: None for e in graph.sorted_edges}

        # Copy attributes from nx_graph
        for node, node_data in nx_graph.nodes(data=True):
            for key, value in node_data.items():
                graph.nodes[node][key] = value
        for u, v, edge_data in nx_graph.edges(data=True):
            for key, value in edge_data.items():
                graph.edges[u, v][key] = value
        for key, value in nx_graph.graph.items():
            graph.graph[key] = value

        # Handle QoolQit attributes: pos -> coords, weight -> node_weights, edge_weight
        if hasattr(data, "pos") and data.pos is not None:
            for i in range(data.num_nodes):
                graph._coords[i] = data.pos[i].tolist()
        if hasattr(data, "weight") and data.weight is not None:
            for i in range(data.num_nodes):
                graph._node_weights[i] = data.weight[i].item()
        if hasattr(data, "edge_weight") and data.edge_weight is not None:
            edge_index = data.edge_index
            seen_edges: set = set()
            for idx in range(edge_index.shape[1]):
                u, v = int(edge_index[0, idx].item()), int(edge_index[1, idx].item())
                edge_key = (min(u, v), max(u, v))
                if edge_key not in seen_edges:
                    graph._edge_weights[edge_key] = data.edge_weight[idx].item()
                    seen_edges.add(edge_key)

        return graph

    def to_pyg(
        self,
        node_attrs: Iterable[str] | None = None,
        edge_attrs: Iterable[str] | None = None,
        graph_attrs: Iterable[str] | None = None,
    ) -> torch_geometric.data.Data:
        """Convert the BaseGraph to a PyTorch Geometric Data object.

        Uses PyG's from_networkx internally. Only explicitly specified attributes
        are exported, plus default attributes (x, edge_attr, pos) and QoolQit
        attributes (weight, edge_weight).

        Arguments:
            node_attrs: Node attributes to export (in addition to defaults).
            edge_attrs: Edge attributes to export (in addition to defaults).
            graph_attrs: Graph-level attributes to copy to the Data object.

        Returns:
            PyTorch Geometric Data object with edge_index and requested attributes.
        """
        try:
            from torch_geometric.utils import from_networkx
        except ImportError as e:
            raise ImportError("Please, install the `torch_geometric` package.") from e

        node_attrs_set = set(node_attrs) if node_attrs else set()
        edge_attrs_set = set(edge_attrs) if edge_attrs else set()
        graph_attrs_list = list(graph_attrs) if graph_attrs else []

        # Add default PyG attributes to the sets if present
        if any("x" in d for _, d in self.nodes(data=True)):
            node_attrs_set.add("x")
        if any("edge_attr" in d for _, _, d in self.edges(data=True)):
            edge_attrs_set.add("edge_attr")
        if "y" in self.graph:
            graph_attrs_list.append("y")

        # Create a filtered copy of the graph with only requested attributes
        filtered_graph = nx.Graph()
        filtered_graph.add_nodes_from(self.nodes())
        filtered_graph.add_edges_from(self.edges())

        for node, node_data in self.nodes(data=True):
            for key, value in node_data.items():
                if key in node_attrs_set:
                    filtered_graph.nodes[node][key] = value
        for u, v, edge_data in self.edges(data=True):
            for key, value in edge_data.items():
                if key in edge_attrs_set:
                    filtered_graph.edges[u, v][key] = value
        for attr in graph_attrs_list:
            if attr in self.graph:
                filtered_graph.graph[attr] = self.graph[attr]

        # Convert via PyG's from_networkx
        data = from_networkx(filtered_graph)

        # Export QoolQit internal attributes: coords -> pos
        if self.has_coords:
            positions = [self._coords[n] for n in sorted(self.nodes())]
            data.pos = torch.tensor(positions, dtype=torch.float64)

        # Export node_weights -> weight
        if hasattr(self, "_node_weights") and any(
            v is not None for v in self._node_weights.values()
        ):
            weights = [self._node_weights.get(n, 0.0) or 0.0 for n in sorted(self.nodes())]
            data.weight = torch.tensor(weights, dtype=torch.float64)

        # Export edge_weights -> edge_weight
        if hasattr(self, "_edge_weights") and any(
            v is not None for v in self._edge_weights.values()
        ):
            edge_weights = []
            for i in range(data.edge_index.shape[1]):
                u, v = int(data.edge_index[0, i].item()), int(data.edge_index[1, i].item())
                edge_key = (min(u, v), max(u, v))
                weight = self._edge_weights.get(edge_key, 0.0) or 0.0
                edge_weights.append(weight)
            data.edge_weight = torch.tensor(edge_weights, dtype=torch.float64)

        return data

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
        is_any_coord_none = any(value is None for value in self._coords.values())
        return not (is_any_coord_none or len(self._coords) == 0)

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

    # methods

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
                self._coords = space_coords(self._coords, spacing)
            elif spacing is None and scaling is not None:
                self._coords = scale_coords(self._coords, scaling)
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

    def draw(self, return_fig: bool = False, *args: Any, **kwargs: Any) -> Figure | None:
        """Draw the graph.

        Uses the draw_networkx function from NetworkX.

        Arguments:
            *args: arguments to pass to draw_networkx.
            **kwargs: keyword-arguments to pass to draw_networkx.
        """
        fig, ax = plt.subplots(figsize=(4, 4), dpi=250)
        ax.set_aspect("equal")
        if self.has_coords:
            ax.set_xlabel("x")
            ax.set_ylabel("y")
            ax.grid(True, color="lightgray", linestyle="--", linewidth=0.7)
            ax.tick_params(direction="in")
            ax.set_axisbelow(True)

            if "hide_ticks" not in kwargs:
                kwargs["hide_ticks"] = False

            nx.draw_networkx(self, *args, ax=ax, pos=self.coords, **kwargs)

            # minimum ybox
            ylim = ax.get_ylim()
            if (ylim[1] - ylim[0]) < 2:
                y_center = (ylim[0] + ylim[1]) / 2
                ax.set_ylim(y_center - 1, y_center + 1)
            plt.tight_layout()
        else:
            nx.draw_networkx(self, *args, ax=ax, **kwargs)

        if return_fig:
            plt.close()
            return fig
        else:
            return None
