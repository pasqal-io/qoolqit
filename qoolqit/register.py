from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING, Any, TypeGuard, cast

import matplotlib.pyplot as plt
import numpy as np
import numpy.typing as npt
from matplotlib.axes import Axes
from scipy.spatial.distance import cdist

from qoolqit.graphs import DataGraph, all_node_pairs, distances

#: The spatial dimensions a register can live in: planar (2) or volumetric (3) arrays.
SUPPORTED_DIMENSIONS: tuple[int, ...] = (2, 3)

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

    x = cast(npt.NDArray[np.float64], x)  # TypeGuard narrows only the torch branch above.
    np.fill_diagonal(x, value)
    return x


class Register:
    """A QoolQit register mapping qubit IDs to 2D or 3D coordinates.

    All the coordinates of a register share one dimension, `register.dimension`,
    which is 2 (a planar array, every Pasqal QPU) or 3 (a volumetric array, as in
    `pulser.register.Register3D`, compiled only to devices with `dimensions == 3`).

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

        A 3D register (a tetrahedron of unit edge):

        >>> reg = Register.from_coordinates([(0, 0, 0), (1, 0, 0), (0.5, 3**0.5 / 2, 0),
        ...                                  (0.5, 3**0.5 / 6, (2 / 3) ** 0.5)])
        >>> reg.dimension
        3
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
            qubits: a dictionary of qubits and respective coordinates, either all 2D,
                {q: (x, y), ...}, or all 3D, {q: (x, y, z), ...}. Each coordinate must be
                castable to a numpy or torch array of shape (2,) or (3,).

        Raises:
            TypeError: If `qubits` is not a Mapping.
            ValueError: If `qubits` dictionary is empty.
            ValueError: If a qubit coordinate cannot be converted to an array of
                floats, if the converted coordinate is not a point in 2D or 3D, or if
                the coordinates do not all have the same dimension.
        """
        if not isinstance(qubits, Mapping):
            raise TypeError("`qubits` must be a Mapping of qubit ids to coordinates.")
        if not qubits:
            raise ValueError("Register cannot be empty.")

        self._qubits_ids: tuple[str | int, ...] = tuple(qubits.keys())
        validated_coords = [self._validate_coord(k, c) for k, c in qubits.items()]
        dims = {int(c.shape[0]) for c in validated_coords}
        if len(dims) != 1:
            raise ValueError(
                "All the coordinates of a register must have the same dimension, "
                f"got dimensions {sorted(dims)}."
            )
        self._coords = self._stack_coords(validated_coords)

    def __len__(self) -> int:
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

        if valid_coord.ndim != 1 or valid_coord.shape[0] not in SUPPORTED_DIMENSIONS:
            raise ValueError(
                f"Coordinate for qubit {key!r} must be a 2D or 3D point, got {coord!r}."
            )
        return valid_coord

    @staticmethod
    def _stack_coords(
        coords: Sequence[npt.NDArray[np.float64] | torch.Tensor],
    ) -> npt.NDArray[np.float64] | torch.Tensor:
        """Stack already-validated coordinates of one dimension d into a single (n, d) array.

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
            coords: a sequence of 2D coordinates, [(x, y), ...], or of 3D coordinates,
                [(x, y, z), ...]. Each coordinate must be castable to a numpy or torch
                array of shape (2,) or (3,). If `coords` is a numpy array or a torch tensor,
                it must be of shape (N, 2) or (N, 3).

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

    @classmethod
    def cuboid(
        cls,
        rows: int,
        cols: int,
        layers: int,
        row_spacing: float = 1.0,
        col_spacing: float = 1.0,
        layer_spacing: float = 1.0,
    ) -> Register:
        """Initializes a 3D Register of qubits on a rectangular cuboid, centered at the origin.

        Args:
            rows: number of qubits along x.
            cols: number of qubits along y.
            layers: number of qubits along z.
            row_spacing: distance between adjacent qubits along x. Defaults to 1.0.
            col_spacing: distance between adjacent qubits along y. Defaults to 1.0.
            layer_spacing: distance between adjacent qubits along z. Defaults to 1.0.

        Raises:
            ValueError: If a number of qubits is smaller than 1 or a spacing is not positive.
        """
        if rows < 1 or cols < 1 or layers < 1:
            raise ValueError("Number of rows, columns and layers must be at least 1.")
        if row_spacing <= 0 or col_spacing <= 0 or layer_spacing <= 0:
            raise ValueError("Spacing must be positive.")

        # Define total offsets in x, y, and z directions
        x_offset = (rows - 1) * row_spacing / 2.0
        y_offset = (cols - 1) * col_spacing / 2.0
        z_offset = (layers - 1) * layer_spacing / 2.0
        # Define coordinates of a grid of quibits, centered at (0, 0, 0)
        coords = [
            (i * row_spacing - x_offset, j * col_spacing - y_offset, k * layer_spacing - z_offset)
            for i in range(rows)
            for j in range(cols)
            for k in range(layers)
        ]
        return cls.from_coordinates(coords)

    @classmethod
    def cubic(cls, n: int, spacing: float = 1.0) -> Register:
        """Initializes a 3D Register of n x n x n qubits on a simple cubic lattice.

        Args:
            n: number of qubits along each edge of the cube.
            spacing: distance between adjacent qubits. Defaults to 1.0.
        """
        return cls.cuboid(
            rows=n, cols=n, layers=n,
            row_spacing=spacing, col_spacing=spacing, layer_spacing=spacing)

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

    @property
    def dimension(self) -> int:
        """The spatial dimension of the register, 2 or 3."""
        return int(self._coords.shape[1])

    @property
    def is_3d(self) -> bool:
        """Whether the register is volumetric (dimension 3)."""
        return self.dimension == 3

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
        if self.is_3d:
            return self.__class__.__name__ + f"(n_qubits = {self.n_qubits}, dimension = 3)"
        return self.__class__.__name__ + f"(n_qubits = {self.n_qubits})"

    def draw(
        self, ax: Axes | None = None, marker_size: int = 100, node_color: str = "tab:green"
    ) -> None:
        """Draw the register.

        A 3D register is drawn on 3D axes, with equal scales on the three axes.

        Args:
            ax: an optional matplotlib Axes instance to draw on (3D axes for a 3D
                register). If None, a new Axes will be created.
            marker_size: size of the qubit markers in points squared. Defaults to 100.
            node_color: color of the qubit markers. Defaults to "tab:green".

        Raises:
            ValueError: If a 3D register is drawn on 2D axes.
        """
        if self.is_3d:
            self._draw_3d(ax=ax, marker_size=marker_size, node_color=node_color)
            return
        if ax is None:
            _, ax = plt.subplots()

        marker_radius = marker_size**0.5 / 2  # in points
        annotation_offset = 1.5 * marker_radius  # place label just outside the marker

        coords = self._coords.detach().cpu().numpy() if _is_torch(self._coords) else self._coords
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
        ax.margins(0.1)

    def _draw_3d(self, ax: Axes | None, marker_size: int, node_color: str) -> None:
        """Draw a 3D register on 3D axes (see `draw`)."""
        if ax is None:
            ax = plt.figure().add_subplot(projection="3d")
        elif getattr(ax, "name", "") != "3d":
            raise ValueError("A 3D register must be drawn on 3D axes (projection='3d').")
        coords = self._coords.detach().cpu().numpy() if _is_torch(self._coords) else self._coords
        ax.scatter(coords[:, 0], coords[:, 1], coords[:, 2], s=marker_size, color=node_color)
        for (xi, yi, zi), qid in zip(coords, self.qubits_ids, strict=True):
            ax.text(xi, yi, zi, f"  {qid}", fontsize=8)
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.set_zlabel("z")
        ax.set_box_aspect(tuple(np.ptp(coords, axis=0) + 1e-9))
