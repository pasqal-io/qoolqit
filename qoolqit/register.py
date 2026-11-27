"""Register mapping qubit IDs to 2D coordinates."""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING, Any

import matplotlib.pyplot as plt
import numpy as np
import numpy.typing as npt
from matplotlib.axes import Axes
from matplotlib.colors import to_rgba
from matplotlib.patches import Circle
from scipy.spatial.distance import cdist
from typing_extensions import TypeIs

from qoolqit.graphs import DataGraph, all_node_pairs, distances
from qoolqit.visualization import COLORS

if TYPE_CHECKING:
    import torch


try:
    import torch

    _has_torch = True
except ImportError:
    _has_torch = False


def _is_torch(val: Any) -> TypeIs[torch.Tensor]:
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


def _norm(x: npt.NDArray[np.float64] | torch.Tensor) -> float:
    if _is_torch(x):
        return float(torch.linalg.norm(x))
    return float(np.linalg.norm(x))


def _copy(x: npt.NDArray | torch.Tensor) -> npt.NDArray | torch.Tensor:
    if _is_torch(x):
        return x.clone().detach()
    return np.copy(x)


def _pdist(x: npt.NDArray | torch.Tensor) -> npt.NDArray | torch.Tensor:
    """Compute the distance matrix of a collection of vectors."""
    if _is_torch(x):
        return torch.cdist(x, x, p=2)
    return np.asarray(cdist(x, x))


def _fill_diagonal(
    x: npt.NDArray[np.float64] | torch.Tensor, value: float
) -> npt.NDArray[np.float64] | torch.Tensor:
    if _is_torch(x):
        # Out-of-place: avoids corrupting x's autograd graph.
        diag = torch.full_like(x.diag(), value)
        return torch.diagonal_scatter(x, diag)

    np.fill_diagonal(x, value)
    return x


class Register:
    """A QoolQit register mapping qubit IDs to 2D coordinates.

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
            TypeError: If `qubits` is not a Mapping.
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

    def __len__(self) -> int:
        """Return the number of qubits."""
        return len(self._qubits_ids)

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

        Qubit IDs are assigned as integers 0,1,...,N-1, where N is the number of coordinates.

        Args:
            coords: a sequence of 2D coordinates, i.e. [(x, y), ...].
                Each coordinate must be castable to a numpy or torch array of shape (2,).
                If `coords` is a numpy array or a torch tensor, it must be 2D and of shape (N, 2).

        Raises:
            TypeError: If `coords` is a Mapping.
        """
        if isinstance(coords, Mapping):
            raise TypeError(
                "Register.from_coordinates expects a sequence of coordinates [(x, y), ...]; "
                "pass an id-to-coordinate mapping to Register(...) directly."
            )
        coords_dict = {i: pos for i, pos in enumerate(coords)}
        return cls(coords_dict)

    @classmethod
    def triangular(cls, rows: int, atoms_per_row: int, spacing: float = 1.0) -> Register:
        """Initializes a triangular lattice Register of qubits.

        Args:
            rows: number of rows in the lattice.
            atoms_per_row: number of qubits per row.
            spacing: distance between adjacent qubits. Defaults to 1.0.
        """
        if rows < 1 or atoms_per_row < 1:
            raise ValueError("Number of rows and atoms per row must be at least 1.")
        if spacing <= 0:
            raise ValueError("Spacing must be positive.")

        height = math.sqrt(3.0) / 2.0
        x_offset = ((atoms_per_row - 1) / 2.0 + 0.5 * (rows // 2) / rows) * spacing
        y_offset = (rows - 1) * height * spacing / 2.0
        coords = [
            ((i + 0.5 * (j % 2)) * spacing - x_offset, j * height * spacing - y_offset)
            for j in range(rows)
            for i in range(atoms_per_row)
        ]
        return cls.from_coordinates(coords)

    @classmethod
    def rectangular(
        cls, rows: int, cols: int, row_spacing: float = 1.0, col_spacing: float = 1.0
    ) -> Register:
        """Initializes a rectangular Register of qubits.

        Args:
            rows: number of rows in the rectangle.
            cols: number of columns in the rectangle.
            row_spacing: distance between adjacent qubits in the row direction. Defaults to 1.0.
            col_spacing: distance between adjacent qubits in the column direction. Defaults to 1.0.
        """
        if rows < 1 or cols < 1:
            raise ValueError("Number of rows and columns must be at least 1.")
        if row_spacing <= 0 or col_spacing <= 0:
            raise ValueError("Spacing must be positive.")

        x_offset = (rows - 1) * row_spacing / 2.0
        y_offset = (cols - 1) * col_spacing / 2.0
        coords = [
            (i * row_spacing - x_offset, j * col_spacing - y_offset)
            for i in range(rows)
            for j in range(cols)
        ]

        return cls.from_coordinates(coords)

    @classmethod
    def square(cls, n: int, spacing: float = 1.0) -> Register:
        """Initializes a square Register of qubits.

        Args:
            n: number of qubits along each side of the square.
            spacing: distance between adjacent qubits. Defaults to 1.0.
        """
        return cls.rectangular(n, n, row_spacing=spacing, col_spacing=spacing)

    @classmethod
    def line(cls, n: int, spacing: float = 1.0) -> Register:
        """Initializes a Register with qubits arranged in a line.

        Args:
            n: number of qubits to place in the line.
            spacing: distance between adjacent qubits. Defaults to 1.0.
        """
        return cls.rectangular(n, 1, row_spacing=spacing)

    @classmethod
    def circle(cls, n: int, spacing: float = 1.0) -> Register:
        """Initializes a Register with qubits arranged in a circle.

        Args:
            n: number of qubits to place in the circle.
            spacing: distance between adjacent qubits. Defaults to 1.0.
        """
        if n < 1:
            raise ValueError("Number of qubits must be at least 1.")
        if spacing <= 0:
            raise ValueError("Spacing must be positive.")
        if n == 1:
            return cls.from_coordinates([(0.0, 0.0)])

        step = 2.0 * math.pi / n
        r = spacing / (2.0 * math.sin(math.pi / n))
        coords = [(math.cos(step * i) * r, math.sin(step * i) * r) for i in range(n)]

        return cls.from_coordinates(coords)

    @property
    def qubits(self) -> dict:
        """Returns a dictionary of qubits and respective coordinates."""
        return {
            qid: _copy(coord) for qid, coord in zip(self._qubits_ids, self._coords, strict=True)
        }

    @property
    def qubits_ids(self) -> tuple[str | int, ...]:
        """Returns the qubit IDs."""
        return self._qubits_ids

    @property
    def n_qubits(self) -> int:
        """Number of qubits in the Register."""
        return len(self)

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
        return {qid: _norm(coord) for qid, coord in zip(self.qubits_ids, self._coords, strict=True)}

    def max_radial_distance(self) -> float:
        """Maximum radial distance between all qubits."""
        max_radial_distance: float = max(self.radial_distances().values())
        return max_radial_distance

    def interactions(self) -> dict:
        """Interaction 1/r^6 between each qubit pair."""
        return {p: 1.0 / (r**6) for p, r in self.distances().items()}

    def interaction_matrix(self) -> npt.NDArray[np.float64] | torch.Tensor:
        """Interaction 1/r^6 between each qubit pair, as a matrix (0 on the diagonal)."""
        dist_matrix = _pdist(self._coords)
        interactions = _fill_diagonal(dist_matrix, 1.0)
        interactions **= -6
        return _fill_diagonal(interactions, 0.0)

    def __repr__(self) -> str:
        """Return the class name and number of qubits."""
        return self.__class__.__name__ + f"(n_qubits = {self.n_qubits})"

    def draw(
        self,
        ax: Axes | None = None,
        marker_size: int = 100,
        node_color: str = COLORS["mintgreen"],
        blockade_radius: float | None = None,
    ) -> None:
        """Draw the register.

        The register is drawn to scale (equal aspect ratio).

        Args:
            ax: an optional matplotlib Axes instance to draw on.
                If None, a new Axes will be created.
            marker_size: size of the qubit markers in points squared. Defaults to 100.
            node_color: color of the qubit markers. Defaults to mint green.
            blockade_radius: an optional blockade radius, in the same dimensionless units as
                the coordinates. If given, a disk of radius blockade_radius / 2 is drawn
                around each qubit (see the note below), and a legend labels its dashed
                outline. For a drive amplitude Ω, the blockade radius is Ω^(-1/6)
                (see https://docs.pasqal.com/qoolqit/get_started/atoms_as_qubits/).

        Note:
            The disks drawn for `blockade_radius` have half the blockade radius, not the full
            radius: two qubits are blockaded exactly when their disks overlap. With full-radius
            circles one would instead check whether a qubit lies inside a neighbor's circle,
            and in a dense register the circles would overlap heavily.
        """
        if ax is None:
            _, ax = plt.subplots()

        marker_radius = marker_size**0.5 / 2  # in points
        annotation_offset = 1.5 * marker_radius  # place label just outside the marker

        coords = self._coords.detach().cpu().numpy() if _is_torch(self._coords) else self._coords
        if blockade_radius is not None:
            edgecolor = to_rgba(COLORS["neonpurple"], 0.8)
            linestyle = (0, (2, 4))
            # Added before the markers, so the qubits are drawn on top of the disks
            for xi, yi in coords:
                ax.add_patch(
                    Circle(
                        (xi, yi),
                        radius=blockade_radius / 2,
                        facecolor=to_rgba(COLORS["neonpurple"], 0.14),
                        edgecolor=edgecolor,
                        linestyle=linestyle,
                    )
                )
            # Legend entry for the dashed outline, drawn as an empty line so the limits don't change
            ax.plot([], [], color=edgecolor, linestyle=linestyle, label=r"$\tilde{r}_b / 2$")
            ax.legend()

        for xi, yi, qid in zip(coords[:, 0], coords[:, 1], self.qubits_ids, strict=True):
            ax.scatter(xi, yi, s=marker_size, color=node_color)
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
        # Pad by 10% of the register's extent on each side. The padding goes into the data
        # limits, not ax.margins: with adjustable="datalim", matplotlib may shrink an axis
        # back towards the data, which would put qubits on the frame.
        lo, hi = coords.min(axis=0), coords.max(axis=0)
        if blockade_radius is not None:
            lo, hi = lo - blockade_radius / 2, hi + blockade_radius / 2
        pad = 0.1 * (hi - lo)
        ax.update_datalim([lo - pad, hi + pad])
        ax.margins(0)
        ax.set_aspect("equal", adjustable="datalim")
