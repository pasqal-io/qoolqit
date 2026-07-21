from __future__ import annotations

from typing import TYPE_CHECKING

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from numpy.typing import ArrayLike

from qoolqit.graphs import DataGraph, all_node_pairs, distances
from qoolqit.graphs.utils import radial_distances

if TYPE_CHECKING:
    import torch

try:
    import torch

    _has_torch = True
except ImportError:
    _has_torch = False


class Register:
    """A QoolQit register mapping qubit IDs to 2D coordinates.

    Attributes:
        qubits: a dictionary of qubit IDs and respective coordinates {q: (x, y),...}.
        qubits_ids: a list of qubit IDs.
        n_qubits: the number of qubits in the register.

    Examples:
        From a dictionary of qubit IDs and coordinates:

        >>> reg = Register({"a": (0.0, 0.0), "b": (1.0, 0.0), "c": (0.0, 1.0)})
        >>> reg = Register({0: (0.0, 0.0), 1: (1.0, 0.0), 2: (0.0, 1.0)})

        From a list of coordinates (qubit IDs are assigned automatically as integers):

        >>> reg = Register.from_coordinates([(0.0, 0.0), (1.0, 0.0), (0.0, 1.0)])

        Using numpy arrays as coordinates:

        >>> import numpy as np
        >>> reg = Register({"a": np.array([0.0, 0.0]), "b": np.array([1.0, 0.0])})

        Using torch tensors as coordinates:

        >>> import torch
        >>> reg = Register({"a": torch.tensor([0.0, 0.0]), "b": torch.tensor([1.0, 0.0])})
    """

    def __init__(
        self,
        qubits: dict[str, ArrayLike | torch.Tensor] | dict[int, ArrayLike | torch.Tensor],
    ) -> None:
        """Default constructor for the Register.

        Args:
            qubits: a dictionary of qubits and respective coordinates {q: (x, y), ...}.

        Raises:
            TypeError: If `qubits` is not a dictionary.
            ValueError: If `qubits` is empty.
            ValueError: If a qubit coordinate cannot be converted to an array of
                floats, or if the converted coordinate is not a point in 2D.
        """
        if not isinstance(qubits, dict):
            raise TypeError("`qubits` must be a dictionary mapping qubit ids to coordinates.")
        if len(qubits) == 0:
            raise ValueError("Register cannot be empty.")

        parsed = {}
        for key, val in qubits.items():
            try:
                if _has_torch and isinstance(val, torch.Tensor):
                    parsed[key] = torch.asarray(val, dtype=torch.float64)
                else:
                    parsed[key] = np.asarray(val, dtype=float)
            except (ValueError, TypeError) as err:
                raise ValueError(
                    f"Coordinate for qubit {key!r} must be castable to an array of floats, "
                    f"got {val!r}."
                ) from err

            converted = parsed[key]
            if converted.ndim != 1 or converted.shape[0] != 2:
                raise ValueError(f"Coordinate for qubit {key!r} must be a 2D point, got {val!r}.")

        self._qubits = parsed

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
                "Register.from_coordinates must be initialized with a list of"
                " coordinates [(x, y), ...]."
            )
        coords_dict = {i: pos for i, pos in enumerate(coords)}
        return cls(coords_dict)

    @property
    def qubits(self) -> dict:
        """Returns a copy of the dictionary of qubits and respective coordinates."""
        return dict(self._qubits)

    @property
    def qubits_ids(self) -> list:
        """Returns the qubit keys."""
        return list(self._qubits.keys())

    @property
    def n_qubits(self) -> int:
        """Number of qubits in the Register."""
        return len(self._qubits)

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

    def draw(self, ax: Axes | None = None, marker_size: int = 100) -> None:
        """Draw the register.

        Args:
            ax: an optional matplotlib Axes instance to draw on.
                If None, a new Axes will be created.
            marker_size: size of the qubit markers in points squared. Defaults to 100.
        """
        if ax is None:
            _, ax = plt.subplots()

        marker_radius = marker_size**0.5 / 2  # in points
        annotation_offset = 1.5 * marker_radius  # place label just outside the marker

        x, y = zip(
            *[
                (v.detach().numpy() if (_has_torch and isinstance(v, torch.Tensor)) else v)
                for v in self.qubits.values()
            ]
        )
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
