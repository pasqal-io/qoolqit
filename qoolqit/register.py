from __future__ import annotations

import matplotlib.pyplot as plt
from matplotlib.axes import Axes

from qoolqit.graphs import DataGraph, all_node_pairs, distances
from qoolqit.graphs.utils import radial_distances


class Register:
    """The Register in QoolQit, representing a set of qubits with coordinates."""

    def __init__(self, qubits: dict) -> None:
        """Default constructor for the Register.

        Arguments:
            qubits: a dictionary of qubits and respective coordinates {q: (x, y), ...}.
        """
        if not isinstance(qubits, dict):
            raise TypeError(
                "Register must be initialized with a dictionary of "
                "qubits and respective coordinates {q: (x, y), ...}."
            )

        self._qubits: dict = qubits

    @classmethod
    def from_graph(cls, graph: DataGraph) -> Register:
        """Initializes a Register from a graph that has coordinates.

        Arguments:
            graph: a DataGraph instance.
        """

        if not graph.has_coords:
            raise ValueError("Initializing a register from a graph requires node coordinates.")

        if len(graph.nodes) == 0:
            raise ValueError("Trying to initialize a register from an empty graph.")

        return cls(graph.coords)

    @classmethod
    def from_coordinates(cls, coords: list) -> Register:
        """Initializes a Register from a list of coordinates.

        Arguments:
            coords: a list of coordinates [(x, y), ...]
        """
        if not isinstance(coords, list):
            raise TypeError(
                "Register must be initialized with a dictionary of qubit and coordinates."
            )
        coords_dict = {i: pos for i, pos in enumerate(coords)}
        return cls(coords_dict)

    @property
    def qubits(self) -> dict:
        """Returns the dictionary of qubits and respective coordinates."""
        return self._qubits

    @property
    def qubits_ids(self) -> list:
        """Returns the qubit keys."""
        return list(self._qubits.keys())

    @property
    def n_qubits(self) -> int:
        """Number of qubits in the Register."""
        return len(self.qubits)

    def distances(self) -> dict:
        """Distance between each qubit pair."""
        pairs = all_node_pairs(list(self.qubits.keys()))
        return distances(self.qubits, pairs)

    def min_distance(self) -> float:
        """Minimum distance between all qubit pairs."""
        distance: float = min(self.distances().values())
        return distance

    def radial_distances(self) -> dict:
        """Radial distance of each qubit from the origin."""
        return radial_distances(self.qubits)

    def max_radial_distance(self) -> float:
        """Maximum radial distance between all qubits."""
        max_radial_distance: float = max(self.radial_distances().values())
        return max_radial_distance

    def interactions(self) -> dict:
        """Interaction 1/r^6 between each qubit pair."""
        return {p: 1.0 / (r**6) for p, r in self.distances().items()}

    def __repr__(self) -> str:
        return self.__class__.__name__ + f"(n_qubits = {self.n_qubits})"

    def draw(self, ax: Axes | None = None) -> None:
        """Draw the register.

        Args:
            ax: an optional matplotlib Axes instance to draw on.
                If None, it will use the current Axes.
        """
        if ax is None:
            _, ax = plt.subplots()

        marker_size = 100
        annotation_offset = marker_size**0.5  # in points, 2 times the marker radius

        x, y = zip(*self.qubits.values())
        ax.scatter(x, y, s=marker_size, color="green")

        for i, qubit_id in enumerate(self.qubits_ids):
            ax.annotate(
                qubit_id,
                xy=(x[i], y[i]),
                xytext=(annotation_offset, annotation_offset),
                textcoords="offset points",
                ha="center",
                va="center",
            )

        ax.grid(True, color="lightgray", linestyle="--", linewidth=0.7)
        ax.set_axisbelow(True)
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.margins(0.1)
