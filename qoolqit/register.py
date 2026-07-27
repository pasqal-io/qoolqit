from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING, Any, TypeGuard

import matplotlib.pyplot as plt
import numpy as np
import numpy.typing as npt
from matplotlib.axes import Axes

from qoolqit.graphs import DataGraph, all_node_pairs, distances

if TYPE_CHECKING:
    import torch


try:
    import torch

    _has_torch = True
except ImportError:
    _has_torch = False


def _is_torch(val: Any) -> TypeGuard[torch.Tensor]:
    return _has_torch and isinstance(val, torch.Tensor)


def _to_array(
    val: Sequence[float] | npt.NDArray[np.float64] | torch.Tensor,
) -> npt.NDArray[np.float64] | torch.Tensor:
    """Convert a value to a float array.

    Returns a torch tensor if the value is itself a tensor, otherwise a numpy
    array.
    """
    if _is_torch(val):
        return val.to(dtype=torch.float64)
    return np.asarray(val, dtype=np.float64)


def _norm(x: npt.NDArray[np.float64] | torch.Tensor) -> np.float64 | torch.Tensor:
    if _is_torch(x):
        norm: torch.Tensor = torch.linalg.norm(x)
        return norm
    return np.linalg.norm(x)


def _copy(x: npt.NDArray | torch.Tensor) -> npt.NDArray | torch.Tensor:
    if _is_torch(x):
        return x.clone()
    return np.copy(x)


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

        From a list of coordinates (qubit IDs are assigned automatically as strings "0", "1", ...):

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
        qubits: (
            Mapping[str, Sequence[float] | npt.NDArray[np.float64] | torch.Tensor]
            | Mapping[int, Sequence[float] | npt.NDArray[np.float64] | torch.Tensor]
        ),
    ) -> None:
        """Default constructor for the Register.

        Args:
            qubits: a dictionary of qubits and respective 2D coordinates {q: (x, y), ...}.
                Each coordinate must be castable to a numpy or torch array of shape (2,).

        Raises:
            TypeError: If `qubits` is not a dictionary.
            ValueError: If `qubits` dictionary is empty.
            ValueError: If a qubit coordinate cannot be converted to an array of
                floats, or if the converted coordinate is not a point in 2D.
        """
        if not isinstance(qubits, Mapping):
            raise TypeError("`qubits` must be a Mapping of qubit ids to coordinates.")
        if not qubits:
            raise ValueError("Register cannot be empty.")

        self._qubits_ids: tuple[str | int, ...] = tuple(qubits.keys())
        validated_coords = [self._validate_coord(k, c) for k, c in qubits.items()]
        self._coords = self._stack_coords(validated_coords)

    @staticmethod
    def _validate_coord(
        key: str | int, coord: Sequence[float] | npt.NDArray[np.float64] | torch.Tensor
    ) -> npt.NDArray[np.float64] | torch.Tensor:
        try:
            valid_coord = _to_array(coord)
        except (ValueError, TypeError) as err:
            raise ValueError(
                f"Coordinate for qubit {key!r} must be castable "
                f"to an array of floats, got {coord!r}."
            ) from err

        if valid_coord.ndim != 1 or valid_coord.shape[0] != 2:
            raise ValueError(f"Coordinate for qubit {key!r} must be a 2D point, got {coord!r}.")
        return valid_coord

    @staticmethod
    def _stack_coords(
        coords: Sequence[npt.NDArray[np.float64] | torch.Tensor],
    ) -> npt.NDArray[np.float64] | torch.Tensor:
        """Stack already-validated 2D coordinates into a single (n, 2) array.

        If any of the coordinates are torch tensors, the result will also be a torch tensor.
        """
        if any(_is_torch(c) for c in coords):
            return torch.vstack([c if _is_torch(c) else torch.asarray(c) for c in coords])
        return np.asarray(coords)

    @classmethod
    def from_graph(cls, graph: DataGraph) -> Register:
        """Initializes a Register from a graph that has coordinates.

        Args:
            graph: a DataGraph instance.
        """

        if not graph.has_coords:
            raise ValueError("Initializing a register from a graph requires node coordinates.")

        if len(graph.nodes) == 0:
            raise ValueError("Trying to initialize a register from an empty graph.")

        return cls(graph.coords)

    @classmethod
    def from_coordinates(
        cls,
        coords: (
            Sequence[Sequence[float] | npt.NDArray[np.float64] | torch.Tensor]
            | npt.NDArray[np.float64]
            | torch.Tensor
        ),
    ) -> Register:
        """Initializes a Register from a sequence or array of coordinates.

        Qubit IDs are assigned as integers 0,1,...,N, where N is the number of coordinates.

        Args:
            coords: a sequence of 2D coordinates, i.e. [(x, y), ...].
                Each coordinate must be castable to a numpy or torch array of shape (2,).
                If `coords` is a numpy array or a torch tensor, it must be 2D and of shape (N, 2).
        """
        if isinstance(coords, Mapping):
            raise TypeError(
                "Register.from_coordinates expects a sequence of coordinates [(x, y), ...]; "
                "pass an id-to-coordinate mapping to Register(...) directly."
            )
        coords_dict = {i: pos for i, pos in enumerate(coords)}
        return cls(coords_dict)

    @property
    def qubits(self) -> dict:
        """Returns a dictionary of qubits and respective coordinates."""
        return {qid: _copy(coord) for qid, coord in zip(self._qubits_ids, self._coords)}

    @property
    def qubits_ids(self) -> tuple[str | int, ...]:
        """Returns the qubit IDs."""
        return self._qubits_ids

    @property
    def n_qubits(self) -> int:
        """Number of qubits in the Register."""
        return len(self.qubits_ids)

    def distances(self) -> dict:
        """Distance between each qubit pair."""
        pairs = all_node_pairs(self.qubits_ids)
        return distances(self.qubits, pairs)

    def min_distance(self) -> float:
        """Minimum distance between all qubit pairs."""
        distance: float = min(self.distances().values())
        return distance

    def radial_distances(self) -> dict:
        """Radial distance of each qubit from the origin."""
        return {qid: _norm(coord) for qid, coord in zip(self.qubits_ids, self._coords)}

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

        coords = self._coords.detach().cpu().numpy() if _is_torch(self._coords) else self._coords
        for xi, yi, qid in zip(coords[:, 0], coords[:, 1], self.qubits_ids):
            ax.scatter(xi, yi, s=marker_size, color="green")
            ax.annotate(
                str(qid),
                xy=(xi, yi),
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
