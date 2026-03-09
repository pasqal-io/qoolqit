# TODO:
# - refactor this to reuse common methods in constructors
# - refactor using rescale_coords method


from __future__ import annotations

from collections.abc import Iterable
from typing import TYPE_CHECKING, Any

import networkx as nx
import numpy as np
from numpy.typing import ArrayLike

from qoolqit.utils import ATOL_32

from .base_graph import BaseGraph
from .utils import random_coords

if TYPE_CHECKING:
    import torch
    import torch_geometric


class DataGraph(BaseGraph):
    """The main graph structure to represent problem data."""

    def __init__(self, edges: Iterable = []) -> None:
        """
        Default constructor for the BaseGraph.

        Arguments:
            edges: set of edge tuples (i, j)
        """
        super().__init__(edges)

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

    @classmethod
    def from_pyg(
        cls,
        data: torch_geometric.data.Data,
        node_attrs: Iterable[str] | None = None,
        edge_attrs: Iterable[str] | None = None,
        graph_attrs: Iterable[str] | None = None,
        node_weights_attr: str | None = None,
        edge_weights_attr: str | None = None,
    ) -> DataGraph:
        """Convert a PyTorch Geometric Data object into a DataGraph instance.

        Requires ``torch_geometric``. Uses ``to_networkx`` internally.

        **Default attributes copied (if present on** ``data`` **):**

        - Node: ``x``, ``pos`` (``pos`` is also stored in ``_coords``)
        - Edge: ``edge_attr``
        - Graph: ``y``

        Use ``node_attrs``, ``edge_attrs``, ``graph_attrs`` for extras.

        **QoolQit weights** (``_node_weights``, ``_edge_weights``) are not
        populated automatically — use the explicit parameters:

        - ``node_weights_attr``: real-valued tensor of shape ``(N,)`` or
          ``(N, 1)``. Defaults to ``None``.
        - ``edge_weights_attr``: real-valued tensor of shape ``(E,)`` or
          ``(E, 1)`` where ``E = edge_index.shape[1]`` (directed count).
          Defaults to ``None``.

        The weight attribute is also stored as a regular node/edge attribute.

        Arguments:
            data: PyTorch Geometric Data object to convert.
            node_attrs: extra node attributes to copy (beyond x and pos).
            edge_attrs: extra edge attributes to copy (beyond edge_attr).
            graph_attrs: extra graph-level attributes to copy (beyond y).
            node_weights_attr: Data attribute to use as node weights.
            edge_weights_attr: Data attribute to use as edge weights.

        Returns:
            DataGraph with ``_coords``, ``_node_weights``, ``_edge_weights``
            populated where applicable.

        Raises:
            ImportError: if ``torch_geometric`` is not installed.
            TypeError: if ``data`` is not a ``torch_geometric.data.Data``
                instance, or if a weight attribute is not a ``torch.Tensor``.
            AttributeError: if a specified weight attribute is missing.
            ValueError: if a weight tensor has an incompatible shape or size.
        """
        try:
            from torch_geometric.data import Data
            from torch_geometric.utils import to_networkx
        except ImportError as e:
            raise ImportError("Please, install the `torch_geometric` package.") from e

        if not isinstance(data, Data):
            raise TypeError("Input must be a torch_geometric.data.Data object.")

        # Validate weight attrs early and keep the squeezed tensors
        node_tensor = (
            cls._validate_weights_attr(data, node_weights_attr, data.num_nodes, "node")
            if node_weights_attr is not None
            else None
        )
        edge_tensor = (
            cls._validate_weights_attr(data, edge_weights_attr, data.num_edges, "edge")
            if edge_weights_attr is not None
            else None
        )

        # Select unique attributes and add default ones only if present in the data
        node_attrs_set = {k for k in {"x", "pos"} if k in data}
        if node_attrs is not None:
            node_attrs_set |= set(node_attrs)
        if node_weights_attr is not None:
            node_attrs_set.add(node_weights_attr)

        edge_attrs_set = {k for k in {"edge_attr"} if k in data}
        if edge_attrs is not None:
            edge_attrs_set |= set(edge_attrs)
        if edge_weights_attr is not None:
            edge_attrs_set.add(edge_weights_attr)

        graph_attrs_set = {k for k in {"y"} if k in data}
        if graph_attrs is not None:
            graph_attrs_set |= set(graph_attrs)

        # Convert to NetworkX (undirected, no self-loops)
        nx_graph = to_networkx(
            data,
            node_attrs=list(node_attrs_set),
            edge_attrs=list(edge_attrs_set),
            graph_attrs=list(graph_attrs_set),
            to_undirected=True,
            remove_self_loops=True,
        )

        # Build the DataGraph: edges carry their data, nodes carry their data
        graph = cls(nx_graph.edges(data=True))
        graph.add_nodes_from(nx_graph.nodes(data=True))
        graph.graph = nx_graph.graph

        # Re-initialize QoolQit internal dicts for all nodes/edges
        graph._coords = {n: None for n in graph.nodes}
        graph._reset_dicts()

        # pos → _coords (stored as list [x, y] by to_networkx)
        for node, node_data in nx_graph.nodes(data=True):
            if "pos" in node_data:
                graph._coords[node] = tuple(node_data["pos"])  # type: ignore[assignment]

        # node_weights_attr → _node_weights
        if node_tensor is not None:
            for i in range(data.num_nodes):
                graph._node_weights[i] = node_tensor[i].item()

        # edge_weights_attr → _edge_weights
        if edge_tensor is not None:
            seen: set = set()
            for idx in range(data.edge_index.shape[1]):
                u = int(data.edge_index[0, idx].item())
                v = int(data.edge_index[1, idx].item())
                key = (min(u, v), max(u, v))
                if key not in seen:
                    graph._edge_weights[key] = edge_tensor[idx].item()
                    seen.add(key)

        return graph

    def to_pyg(
        self,
        node_attrs: Iterable[str] | None = None,
        edge_attrs: Iterable[str] | None = None,
        graph_attrs: Iterable[str] | None = None,
        node_weights_attr: str = "weight",
        edge_weights_attr: str = "edge_weight",
    ) -> torch_geometric.data.Data:
        """Convert the DataGraph to a PyTorch Geometric Data object.

        Requires ``torch_geometric``. Uses ``from_networkx`` internally.

        **Default attributes exported (if present on the graph):**

        - Node ``"x"`` → ``data.x``; Edge ``"edge_attr"`` → ``data.edge_attr``
        - Graph ``"y"`` → ``data.y``

        Use ``node_attrs``, ``edge_attrs``, ``graph_attrs`` for extras.

        **QoolQit internal dicts exported when populated:**

        - ``_coords`` → ``data.pos`` (float64, shape ``(N, 2)``)
        - ``_node_weights`` → ``data.<node_weights_attr>`` (float64, shape
          ``(N,)``). Defaults to ``"weight"``.
        - ``_edge_weights`` → ``data.<edge_weights_attr>`` (float64, shape
          ``(2*E,)``). Defaults to ``"edge_weight"``.

        Arguments:
            node_attrs: extra node attributes to export (beyond x).
            edge_attrs: extra edge attributes to export (beyond edge_attr).
            graph_attrs: extra graph-level attributes to export (beyond y).
            node_weights_attr: Data attribute name for node weights.
                Defaults to ``"weight"``.
            edge_weights_attr: Data attribute name for edge weights.
                Defaults to ``"edge_weight"``.

        Returns:
            PyTorch Geometric Data object.

        Raises:
            ImportError: if ``torch_geometric`` is not installed.
        """
        try:
            import torch
            from torch_geometric.utils import from_networkx
        except ImportError as e:
            raise ImportError("Please, install the `torch_geometric` package.") from e

        node_attrs_set = set(node_attrs) if node_attrs else set()
        edge_attrs_set = set(edge_attrs) if edge_attrs else set()
        graph_attrs_list = list(graph_attrs) if graph_attrs else []

        # Add default PyG attributes if present in the graph
        if any("x" in d for _, d in self.nodes(data=True)):
            node_attrs_set.add("x")
        if any("edge_attr" in d for _, _, d in self.edges(data=True)):
            edge_attrs_set.add("edge_attr")
        if "y" in self.graph:
            graph_attrs_list.append("y")

        # Build a filtered copy with only the requested attributes
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

        data = from_networkx(filtered_graph)

        # Export _coords → pos
        if self.has_coords:
            positions = [self._coords[n] for n in sorted(self.nodes())]
            data.pos = torch.tensor(positions, dtype=torch.float64)

        # Export _node_weights → node_weights_attr
        if self.has_node_weights:
            weights = [self._node_weights[n] for n in sorted(self.nodes())]
            setattr(data, node_weights_attr, torch.tensor(weights, dtype=torch.float64))

        # Export _edge_weights → edge_weights_attr (one value per directed edge in edge_index)
        if self.has_edge_weights:
            edge_weights: list[float] = []
            for i in range(data.edge_index.shape[1]):
                u, v = int(data.edge_index[0, i].item()), int(data.edge_index[1, i].item())
                edge_key = (min(u, v), max(u, v))
                edge_weights.append(float(self._edge_weights[edge_key]))  # type: ignore[arg-type]
            setattr(data, edge_weights_attr, torch.tensor(edge_weights, dtype=torch.float64))

        return data

    @staticmethod
    def _validate_weights_attr(
        data: Any,
        attr_name: str,
        expected_size: int,
        kind: str,
    ) -> torch.Tensor:
        """Validate a weight attribute tensor from a PyG Data object.

        Checks that the attribute exists, is a real ``torch.Tensor``, and has
        shape ``(expected_size,)`` or ``(expected_size, 1)``.

        Arguments:
            data: PyTorch Geometric Data object.
            attr_name: name of the attribute to validate.
            expected_size: expected first dimension (num_nodes or num_edges).
            kind: ``"node"`` or ``"edge"``, used in error messages.

        Returns:
            The validated 1D tensor of shape ``(expected_size,)``.

        Raises:
            AttributeError: if the attribute is missing or ``None``.
            TypeError: if the attribute is not a ``torch.Tensor``.
            ValueError: if the tensor contains complex values or has an
                incompatible shape.
        """
        import torch

        if attr_name not in data:
            raise AttributeError(
                f"Data object has no attribute '{attr_name}' to use as {kind} weights."
            )

        weights = data[attr_name]

        if not isinstance(weights, torch.Tensor):
            raise TypeError(
                f"The {kind} weights attribute '{attr_name}' must be a torch.Tensor, "
                f"got {type(weights)} instead."
            )

        if not weights.isreal().all():
            raise ValueError(
                f"The {kind} weights attribute '{attr_name}' must contain only real numbers."
            )

        # Accept (N,) or (N, 1) — reject anything else
        if weights.ndim == 2 and weights.shape[1] == 1:
            weights = weights.squeeze(1)
        elif weights.ndim != 1:
            raise ValueError(
                f"The {kind} weights attribute '{attr_name}' must have shape "
                f"({expected_size},) or ({expected_size}, 1), "
                f"got {tuple(weights.shape)} instead."
            )

        if weights.shape[0] != expected_size:
            raise ValueError(
                f"The {kind} weights attribute '{attr_name}' has "
                f"{weights.shape[0]} elements, expected {expected_size}."
            )

        return weights

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

    def set_ud_edges(self, radius: float) -> None:
        """Reset the set of edges to be equal to the set of unit-disk edges."""
        super().set_ud_edges(radius=radius)
        self._edge_weights = {e: None for e in self.sorted_edges}
