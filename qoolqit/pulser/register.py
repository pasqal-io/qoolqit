from __future__ import annotations

from collections.abc import Mapping
from typing import Optional, cast

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from pulser.register import Register as _Register
from pulser.register.base_register import QubitId

from qoolqit.graphs import DataGraph


class Register(_Register):

    @classmethod
    def from_graph(cls, graph: DataGraph) -> Register:
        """Initializes a Register from a graph that has coordinates.

        Arguments:
            graph: a DataGraph instance.
        """

        if not graph.has_coords:
            raise ValueError("Initializing a a register from a graph requires node coordinates.")

        return cls(graph.coords)

    @property
    def n_qubits(self) -> int:
        return len(self.qubits)

    def __repr__(self) -> str:
        return self.__class__.__name__ + f"(n_qubits = {self.n_qubits})"

    ##########################
    ### COPIED FROM PULSER ###
    ##########################

    def draw(
        self,
        with_labels: bool = True,
        blockade_radius: Optional[float] = None,
        draw_graph: bool = True,
        draw_half_radius: bool = False,
        qubit_colors: Mapping[QubitId, str] = dict(),
        fig_name: str | None = None,
        kwargs_savefig: dict = {},
        custom_ax: Optional[Axes] = None,
        show: bool = True,
    ) -> None:
        """Draws the entire register.

        Args:
            with_labels: If True, writes the qubit ID's
                next to each qubit.
            blockade_radius: The distance (in μm) between
                atoms below the Rydberg blockade effect occurs.
            draw_half_radius: Whether or not to draw the
                half the blockade radius surrounding each atoms. If `True`,
                requires `blockade_radius` to be defined.
            draw_graph: Whether or not to draw the
                interaction between atoms as edges in a graph. Will only draw
                if the `blockade_radius` is defined.
            qubit_colors: By default, atoms are drawn with a common default
                color. If this parameter is present, it replaces the colors
                for the specified atoms. Non-specified ones are stilled colored
                with the default value.
            fig_name: The name on which to save the figure.
                If None the figure will not be saved.
            kwargs_savefig: Keywords arguments for
                ``matplotlib.pyplot.savefig``. Not applicable if `fig_name`
                is ``None``.
            custom_ax: If present, instead of creating its own Axes object,
                the function will use the provided one. Warning: if fig_name
                is set, it may save content beyond what is drawn in this
                function.
            show: Whether or not to call `plt.show()` before returning. When
                combining this plot with other ones in a single figure, one may
                need to set this flag to False.

        Note:
            When drawing half the blockade radius, we say there is a blockade
            effect between atoms whenever their respective circles overlap.
            This representation is preferred over drawing the full Rydberg
            radius because it helps in seeing the interactions between atoms.
        """
        super()._draw_checks(
            len(self._ids),
            blockade_radius=blockade_radius,
            draw_graph=draw_graph,
            draw_half_radius=draw_half_radius,
        )

        pos = self._coords_arr.as_array(detach=True)
        if custom_ax is None:
            custom_ax = cast(
                plt.Axes,
                self._initialize_fig_axes(
                    pos,
                    blockade_radius=blockade_radius,
                    draw_half_radius=draw_half_radius,
                )[1],
            )
        super()._draw_2D(
            custom_ax,
            pos,
            self._ids,
            with_labels=with_labels,
            blockade_radius=blockade_radius,
            draw_graph=draw_graph,
            draw_half_radius=draw_half_radius,
            qubit_colors=qubit_colors,
        )

        custom_ax.set_xlabel("x")
        custom_ax.set_ylabel("y")

        if fig_name is not None:
            plt.savefig(fig_name, **kwargs_savefig)

        if show:
            plt.show()
