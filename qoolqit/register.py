from __future__ import annotations

from math import ceil
from typing import Any

import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
from pulser.register import Register as _Register

from qoolqit.graphs import DataGraph

__all__ = ["Register"]


class Register:

    def __init__(self, qubits: dict) -> None:
        self._register = _Register(qubits)
        self._qubits: dict = self._register.qubits

    @classmethod
    def from_graph(cls, graph: DataGraph) -> Register:
        """Initializes a Register from a graph that has coordinates.

        Arguments:
            graph: a DataGraph instance.
        """

        if not graph.has_coords:
            raise ValueError("Initializing a a register from a graph requires node coordinates.")

        return cls(graph.coords)

    @classmethod
    def from_coordinates(cls, coords: list) -> Register:
        pulser_register = _Register.from_coordinates(coords)
        return cls(pulser_register.qubits)

    @property
    def qubits(self) -> dict:
        return self._qubits

    @property
    def n_qubits(self) -> int:
        return len(self.qubits)

    def __repr__(self) -> str:
        return self.__class__.__name__ + f"(n_qubits = {self.n_qubits})"

    def draw(self, return_fig: bool = False, *args: Any, **kwargs: Any) -> plt.Figure | None:
        """Draw the graph.

        Uses the draw_networkx function from NetworkX.

        Arguments:
            *args: arguments to pass to draw_networkx.
            **kwargs: keyword-arguments to pass to draw_networkx.
        """
        fig, ax = plt.subplots(1, 1, figsize=(4, 4), dpi=150)
        ax.set_aspect("equal")

        x_coords, y_coords = zip(*self.qubits.values())
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

        ax.scatter(x_coords, y_coords)

        ax.tick_params(axis="both", which="both", labelbottom=True, labelleft=True, labelsize=8)

        return fig if return_fig else None
