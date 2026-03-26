from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

import matplotlib.cm as mcm
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import scipy
import scipy.spatial
from matplotlib.axes import Axes
from matplotlib.patches import Circle
from numpy import format_float_scientific

from ._helpers import normalized_interaction

logger = logging.getLogger(__name__)


def eformat(f: Any) -> str:
    if 1 <= abs(f) < 1000:
        return f"{np.round(f, decimals=1)}"
    elif 0.01 <= abs(f):
        return f"{np.round(f, decimals=2)}"
    if f == 0:
        return "0"

    return format_float_scientific(f, exp_digits=1, precision=0)  # type: ignore


def draw_weighted_graph(
    graph: nx.Graph,
    thresholds: tuple[float, float, float] = (0.0, 0.3, 0.6),
    edge_labels: dict | None = None,
    ax: Axes | None = None,
) -> None:
    plt.figure(figsize=(30, 12), dpi=60)
    if ax is None:
        ax = plt.gca()

    print(f"{thresholds=}")
    t0, t1, t2 = thresholds
    elarge = [(u, v) for (u, v, w) in graph.edges.data("weight") if t2 < w]
    esmall = [(u, v) for (u, v, w) in graph.edges.data("weight") if t1 < w <= t2 and t0 < w]
    etiny = [(u, v) for (u, v, w) in graph.edges.data("weight") if t0 <= w <= t1]

    pos_all_dims = dict(graph.nodes.data("pos"))
    pos = {k: v[0:2] for k, v in pos_all_dims.items()}

    ax.set_aspect("equal", adjustable="box")

    # nodes
    nx.draw_networkx_nodes(graph, pos, node_size=700, ax=ax)

    # edges
    nx.draw_networkx_edges(graph, pos, edgelist=elarge, width=6, ax=ax)
    nx.draw_networkx_edges(
        graph,
        pos,
        edgelist=esmall,
        width=6,
        alpha=0.5,
        edge_color="b",
        style="dashed",
        ax=ax,
    )
    nx.draw_networkx_edges(
        graph,
        pos,
        edgelist=etiny,
        width=4,
        alpha=0.3,
        edge_color="g",
        style="dashed",
        ax=ax,
    )

    # node labels
    nx.draw_networkx_labels(graph, pos, font_size=20, font_family="sans-serif", ax=ax)

    for _, coords in pos_all_dims.items():
        plt.text(
            coords[0] + 0.1,
            coords[1] + 0.1,
            "(" + ", ".join(eformat(coord) for coord in coords) + ")",
            fontsize=15,
            color="black",
        )

    # edge weight labels
    edge_labels = {
        k: f'{eformat(v)} {edge_labels[k] if edge_labels else ""}'
        for k, v in nx.get_edge_attributes(graph, "weight").items()
        if v >= t0
    }
    pos = {k: [vi + 1 / 2 for vi in v] for k, v in pos.items()}

    print(f"{pos=}")

    nx.draw_networkx_edge_labels(graph, pos, edge_labels, ax=ax, font_size=15)

    ax.margins(0.08)
    ax.axis("off")


def draw_set_graph_coords(
    graph: nx.Graph, coords: np.ndarray, edge_labels: dict | None = None
) -> None:
    """Coords are positions in numerical order of the nodes."""
    nx.set_node_attributes(graph, dict(enumerate(coords)), "pos")
    draw_weighted_graph(graph, edge_labels=edge_labels)
    plt.show()


def draw_graph_including_actual_weights(
    target_interactions_graph: nx.Graph,
    positions: np.ndarray,
    print_interactions: bool = False,
    draw_weighted_graph: bool = False,
) -> None:
    if print_interactions:
        try:
            import pandas as pd
            from IPython.display import display
        except ImportError:
            raise ModuleNotFoundError(
                "To use `draw_steps=True` together with "
                "`print_interactions=True` in the BLaDE algorithm, "
                "please install the `pandas` and `IPython` libraries."
            )

        new_weights_matrix = np.full(
            (len(target_interactions_graph), len(target_interactions_graph)),
            fill_value="",
            dtype=object,
        )
        for u, v in target_interactions_graph.edges:
            dist = np.linalg.norm(positions[u] - positions[v]).item()
            interaction = normalized_interaction(dist)
            new_weights_matrix[min(u, v), max(u, v)] = eformat(interaction)

        df = pd.DataFrame(new_weights_matrix)

        with pd.option_context(
            "display.max_rows", None, "display.max_columns", None, "max_colwidth", None
        ):
            display(df)

    if draw_weighted_graph:
        draw_set_graph_coords(
            graph=target_interactions_graph,
            coords=positions,
        )


def plot_differences(differences: np.ndarray) -> None:
    try:
        import seaborn
    except ImportError:
        raise ModuleNotFoundError(
            "To use `draw_steps=True` in the BLaDE algorithm, "
            "please install the `seaborn` library."
        )

    ax = seaborn.violinplot({"differences": differences}, inner=None)
    seaborn.stripplot(
        {"differences": differences},
        edgecolor="black",
        linewidth=1,
        palette=["white"] * 1,
        ax=ax,
    )
    plt.show()


@dataclass(frozen=True, slots=True)
class ColorbarSpec:
    label: str = "target − current interaction"
    label_fontsize: int = 7
    tick_fontsize: int = 6
    n_ticks_each_side: int = 4
    n_cmap_samples: int = 256
    eps: float = 1e-9
    base_colors: tuple[tuple[float, float, float], ...] = (
        (1.0, 0.0, 0.0),
        (1.0, 1.0, 1.0),
        (0.0, 0.0, 1.0),
    )
    cbar_axes_rect: tuple[float, float, float, float] = (0.92, 0.05, 0.02, 0.45)


def as_2d(a: np.ndarray) -> np.ndarray:
    """Return the first two coordinates; expects last dim >= 2."""
    return a[..., :2]


def validate_shapes(
    positions: np.ndarray,
    *,
    interaction_resulting_forces: np.ndarray,
    min_constr_resulting_forces: np.ndarray,
    max_constr_resulting_forces: np.ndarray,
    resulting_forces_vectors: np.ndarray,
    target_interactions: np.ndarray | None = None,
    current_interactions: np.ndarray | None = None,
) -> None:
    if positions.ndim != 2 or positions.shape[1] < 2:
        raise ValueError(f"`positions` must be (n, d) with d>=2, got {positions.shape}.")

    n = positions.shape[0]
    for name, f in (
        ("interaction_resulting_forces", interaction_resulting_forces),
        ("min_constr_resulting_forces", min_constr_resulting_forces),
        ("max_constr_resulting_forces", max_constr_resulting_forces),
        ("resulting_forces_vectors", resulting_forces_vectors),
    ):
        if f.ndim != 2 or f.shape[1] < 2:
            raise ValueError(f"`{name}` must be (n, d) with d>=2, got {f.shape}.")
        if f.shape[0] != n:
            raise ValueError(f"`{name}` first dim must match n={n}, got {f.shape[0]}.")

    if (target_interactions is None) != (current_interactions is None):
        raise ValueError(
            "Provide both `target_interactions` and `current_interactions`, or neither."
        )

    if target_interactions is not None:
        assert current_interactions is not None  # Guaranteed by the check above
        if target_interactions.shape != (n, n):
            raise ValueError(
                f"`target_interactions` must be (n, n) with n={n}, got {target_interactions.shape}."
            )
        if current_interactions.shape != (n, n):
            raise ValueError(
                f"`current_interactions` must be (n, n) with n={n}, "
                f"got {current_interactions.shape}."
            )


def compute_base_arrow_width(pos2d: np.ndarray, *, default: float = 0.01) -> float:
    if pos2d.shape[0] < 2:
        return default
    return float(np.max(scipy.spatial.distance.pdist(pos2d)) / 100.0)


def draw_force_arrows(
    *,
    ax: plt.Axes,
    pos2d: np.ndarray,
    force2d: np.ndarray,
    color: str,
    width: float,
    scale: float = 1.0,
) -> None:
    nonzero = np.any(force2d != 0.0, axis=1)
    p = pos2d[nonzero]
    f = force2d[nonzero]
    for pi, fi in zip(p, f):
        ax.arrow(
            float(pi[0]),
            float(pi[1]),
            float(scale * fi[0]),
            float(scale * fi[1]),
            color=color,
            width=width,
        )


def draw_min_dist_circles(*, ax: plt.Axes, pos2d: np.ndarray, min_dist: float) -> None:
    r = float(min_dist) / 2.0
    for p in pos2d:
        ax.add_patch(
            Circle(
                (float(p[0]), float(p[1])),
                radius=r,
                color="orange",
                fill=False,
                clip_on=False,
                linestyle="--",
                alpha=0.5,
            )
        )


def draw_max_radius_circle(*, ax: plt.Axes, max_radius: float) -> None:
    ax.add_patch(Circle((0.0, 0.0), float(max_radius), color="r", fill=False, clip_on=True))


def add_step_annotation(*, ax: plt.Axes, step: int) -> None:
    ax.annotate(
        f"step = {step}",
        xy=(1.05, 1.02),
        xycoords="axes fraction",
        fontsize=9,
        color="black",
        fontweight="bold",
        va="bottom",
    )


def draw_scale_bar(*, ax: plt.Axes, fig: plt.Figure, max_dist_to_walk: float) -> None:
    fig.canvas.draw()

    x_min, x_max = ax.get_xlim()
    y_min, y_max = ax.get_ylim()

    bar_x = x_min + (x_max - x_min) * 0.05
    bar_y = y_min + (y_max - y_min) * 0.05
    tick_h = (y_max - y_min) * 0.02

    ax.plot([bar_x, bar_x + max_dist_to_walk], [bar_y, bar_y], color="purple", linewidth=2)
    ax.plot([bar_x, bar_x], [bar_y - tick_h, bar_y + tick_h], color="purple", linewidth=2)
    ax.plot(
        [bar_x + max_dist_to_walk, bar_x + max_dist_to_walk],
        [bar_y - tick_h, bar_y + tick_h],
        color="purple",
        linewidth=2,
    )
    ax.text(
        bar_x + max_dist_to_walk / 2.0,
        bar_y + tick_h * 2.0,
        f"max dist to walk = {max_dist_to_walk:.2g}",
        color="purple",
        fontsize=7,
        ha="center",
        va="bottom",
    )


def linspace_ticks(vmin: float, vmax: float, *, n: int) -> np.ndarray:
    n_ = int(n)
    if n_ <= 0:
        return np.array([], dtype=float)
    if vmin == vmax:
        return np.array([vmin], dtype=float)
    return np.linspace(vmin, vmax, n_, dtype=float)


def legend_line(
    *, color: str, label: str, linestyle: str = "-", marker: str = ">"
) -> plt.matplotlib.lines.Line2D:
    return plt.matplotlib.lines.Line2D(
        [0],
        [0],
        color=color,
        linestyle=linestyle,
        marker=marker,
        markersize=6,
        label=label,
    )


def legend_text(label: str) -> plt.matplotlib.lines.Line2D:
    return plt.matplotlib.lines.Line2D([0], [0], color="none", label=label)


def interaction_min_max_label(name: str, mat: np.ndarray) -> str | None:
    upper_mask = np.triu(np.ones(mat.shape, dtype=bool), k=1)
    vals = mat[upper_mask]
    nonzero = vals[vals != 0]
    if nonzero.size == 0:
        return None
    return f"{name}: min={np.min(nonzero):.3g}, max={np.max(nonzero):.3g}"


def build_truncated_diverging_cmap(
    *,
    max_neg: float,
    max_pos: float,
    spec: ColorbarSpec,
) -> mcolors.Colormap:
    abs_max = float(np.maximum(max_pos, np.abs(max_neg)))
    abs_global_max = float(np.maximum(abs_max, spec.eps))

    s_low = max_neg / abs_global_max
    s_high = max_pos / abs_global_max

    t_low = (s_low + 1.0) / 2.0
    t_high = (s_high + 1.0) / 2.0
    t_low, t_high = float(np.minimum(t_low, t_high)), float(np.maximum(t_low, t_high))
    t_low = float(np.clip(t_low, 0.0, 1.0))
    t_high = float(np.clip(t_high, 0.0, 1.0))

    base_cmap = mcolors.LinearSegmentedColormap.from_list("discrepancy", list(spec.base_colors))
    samples = np.linspace(t_low, t_high, int(spec.n_cmap_samples), dtype=float)
    return mcolors.LinearSegmentedColormap.from_list(
        "discrepancy_truncated",
        [base_cmap(float(x)) for x in samples],
    )


def draw_discrepancy_lines_and_colorbar(
    *,
    fig: plt.Figure,
    ax: plt.Axes,
    pos2d: np.ndarray,
    target_interactions: np.ndarray,
    current_interactions: np.ndarray,
    spec: ColorbarSpec = ColorbarSpec(),
) -> None:
    discrepancies = np.triu(target_interactions - current_interactions, k=1)

    max_pos = float(np.max(discrepancies))
    max_neg = float(np.min(discrepancies))
    abs_max = float(np.maximum(max_pos, np.abs(max_neg)))
    if abs_max == 0.0:
        return

    n = pos2d.shape[0]
    for i in range(n):
        for j in range(i + 1, n):
            d = float(discrepancies[i, j])
            if d == 0.0:
                continue
            alpha = abs(d) / abs_max
            rgb = (0.0, 0.0, 1.0) if d > 0.0 else (1.0, 0.0, 0.0)
            ax.plot(
                [float(pos2d[i, 0]), float(pos2d[j, 0])],
                [float(pos2d[i, 1]), float(pos2d[j, 1])],
                color=(*rgb, alpha),
                linewidth=2,
                zorder=1,
            )

    truncated_cmap = build_truncated_diverging_cmap(max_neg=max_neg, max_pos=max_pos, spec=spec)

    vmin = float(np.minimum(max_neg, 0.0))
    vmax = float(np.maximum(max_pos, 0.0))
    norm = mcolors.Normalize(vmin=vmin, vmax=vmax)

    sm = mcm.ScalarMappable(cmap=truncated_cmap, norm=norm)
    sm.set_array([])

    cbar = fig.colorbar(
        sm, ax=ax, orientation="horizontal", location="bottom", pad=0.15, shrink=0.8
    )
    cbar.set_label(spec.label, fontsize=spec.label_fontsize)
    cbar.ax.tick_params(labelsize=spec.tick_fontsize)

    has_neg = max_neg < 0.0
    has_pos = max_pos > 0.0
    neg_ticks = (
        linspace_ticks(vmin, 0.0, n=spec.n_ticks_each_side)
        if has_neg
        else np.array([], dtype=float)
    )
    pos_ticks = (
        linspace_ticks(0.0, vmax, n=spec.n_ticks_each_side)
        if has_pos
        else np.array([], dtype=float)
    )
    tick_vals = np.unique(np.concatenate([neg_ticks, pos_ticks]))

    cbar.set_ticks(tick_vals)
    cbar.set_ticklabels([f"{v:.2g}" for v in tick_vals])


def draw_update_positions_step(
    positions: np.ndarray,
    *,
    interaction_resulting_forces: np.ndarray,
    min_constr_resulting_forces: np.ndarray,
    max_constr_resulting_forces: np.ndarray,
    resulting_forces_vectors: np.ndarray,
    min_dist: float | None,
    max_radius: float | None,
    max_dist_to_walk: float | None = None,
    step: int | None = None,
    target_interactions: np.ndarray | None = None,
    current_interactions: np.ndarray | None = None,
    modulated_target_interactions: np.ndarray | None = None,
) -> None:
    validate_shapes(
        positions,
        interaction_resulting_forces=interaction_resulting_forces,
        min_constr_resulting_forces=min_constr_resulting_forces,
        max_constr_resulting_forces=max_constr_resulting_forces,
        resulting_forces_vectors=resulting_forces_vectors,
        target_interactions=target_interactions,
        current_interactions=current_interactions,
    )

    keep_only_2d = positions.shape[1] > 2
    logger.debug("Step that will be applied%s", " keeping only 2 dims" if keep_only_2d else "")

    pos2d = as_2d(positions)
    inter_f2d = as_2d(interaction_resulting_forces)
    min_f2d = as_2d(min_constr_resulting_forces)
    max_f2d = as_2d(max_constr_resulting_forces)
    res_f2d = as_2d(resulting_forces_vectors)

    use_two_panels = modulated_target_interactions is not None
    if use_two_panels:
        fig, axes = plt.subplots(
            1, 2, figsize=plt.rcParams.get("figure.figsize", (6.4, 4.8))[:1] * np.array([2, 1])  # type: ignore
        )
        ax_left, ax_right = axes[0], axes[1]
        panels: list[tuple[plt.Axes, np.ndarray | None, str]] = [
            (ax_left, target_interactions, "Target interactions"),
            (ax_right, modulated_target_interactions, "Modulated target interactions"),
        ]
    else:
        fig, ax_single = plt.subplots()
        panels = [(ax_single, target_interactions, "Target interactions")]

    def _draw_panel(ax: plt.Axes, panel_target_interactions: np.ndarray | None) -> None:
        if panel_target_interactions is not None:
            draw_discrepancy_lines_and_colorbar(
                fig=fig,
                ax=ax,
                pos2d=pos2d,
                target_interactions=panel_target_interactions,
                current_interactions=current_interactions,
            )

        ax.scatter(pos2d[:, 0], pos2d[:, 1], zorder=2)

        if min_dist is not None:
            draw_min_dist_circles(ax=ax, pos2d=pos2d, min_dist=min_dist)

        base_arrow_width = compute_base_arrow_width(pos2d)

        draw_force_arrows(
            ax=ax, pos2d=pos2d, force2d=inter_f2d, color="blue", width=base_arrow_width
        )
        draw_force_arrows(
            ax=ax, pos2d=pos2d, force2d=min_f2d, color="green", width=base_arrow_width
        )
        draw_force_arrows(
            ax=ax, pos2d=pos2d, force2d=max_f2d, color="black", width=base_arrow_width
        )
        draw_force_arrows(ax=ax, pos2d=pos2d, force2d=res_f2d, color="red", width=base_arrow_width)

        ax.set_aspect("equal", "box")

        if max_radius is not None:
            draw_max_radius_circle(ax=ax, max_radius=max_radius)

        if max_dist_to_walk is not None and np.isfinite(max_dist_to_walk) and max_dist_to_walk > 0:
            draw_scale_bar(ax=ax, fig=fig, max_dist_to_walk=float(max_dist_to_walk))

    for ax, panel_target_interactions, panel_title in panels:
        _draw_panel(ax, panel_target_interactions)
        if use_two_panels:
            ax.set_title(panel_title, fontsize=9)

    # Build legend and attach to the rightmost axes
    rightmost_ax: plt.Axes = panels[-1][0]

    legend_handles = [
        legend_line(color="blue", label="Interaction forces"),
        legend_line(color="green", label="Min dist constraint forces"),
        legend_line(color="black", label="Max radius constraint forces"),
        legend_line(color="red", label="Resulting forces"),
    ]

    if min_dist is not None:
        legend_handles.append(
            legend_line(
                color="orange",
                linestyle="--",
                marker="o",
                label=f"Current min dist constraint: {min_dist:.2g}",
            )
        )

    if max_radius is not None:
        legend_handles.append(
            legend_line(
                color="red",
                linestyle="-",
                marker="o",
                label=f"Current max radius constraint: {max_radius:.2g}",
            )
        )

    if min_dist is not None and max_radius is not None:
        legend_handles.append(
            legend_text(f"Current max-min ratio constraint: {max_radius / min_dist:.2g}")
        )

    if current_interactions is not None:
        s = interaction_min_max_label("Current interactions", current_interactions)
        if s is not None:
            legend_handles.append(legend_text(s))

    if target_interactions is not None:
        s = interaction_min_max_label("Target interactions", target_interactions)
        if s is not None:
            legend_handles.append(legend_text(s))

    if modulated_target_interactions is not None:
        s = interaction_min_max_label(
            "Modulated target interactions", modulated_target_interactions
        )
        if s is not None:
            legend_handles.append(legend_text(s))

    rightmost_ax.legend(
        handles=legend_handles,
        loc="upper left",
        bbox_to_anchor=(1.05, 1),
        borderaxespad=0.0,
        fontsize=8,
    )

    if step is not None:
        add_step_annotation(ax=rightmost_ax, step=step)

    plt.tight_layout()
    plt.show()
