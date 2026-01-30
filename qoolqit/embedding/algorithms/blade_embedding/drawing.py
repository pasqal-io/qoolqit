from __future__ import annotations

import logging
from typing import Any

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd
import scipy
import seaborn as sns
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
) -> None:
    fig, ax = plt.subplots(figsize=(30, 12), dpi=60)

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


def draw_graph_including_actual_weights(qubo_graph: nx.Graph, positions: np.ndarray) -> None:
    from IPython.display import display

    new_weights_matrix = np.full((len(qubo_graph), len(qubo_graph)), fill_value="", dtype=object)
    new_weights = dict()
    for u, v in qubo_graph.edges:
        dist = np.linalg.norm(positions[u] - positions[v])
        new_weights[(u, v)] = normalized_interaction(dist=float(dist))
        new_weights_matrix[min(u, v), max(u, v)] = eformat(new_weights[(u, v)])

    df = pd.DataFrame(new_weights_matrix)

    with pd.option_context(
        "display.max_rows", None, "display.max_columns", None, "max_colwidth", None
    ):
        display(df)

    draw_set_graph_coords(
        graph=qubo_graph,
        coords=positions,
    )


def plot_differences(target_qubo: np.ndarray, differences: np.ndarray) -> None:

    percent = 100 - 2 / (len(target_qubo) - 1) * 10
    percentile = np.percentile(differences, percent)

    difference_ceiling = np.maximum(0.0, percentile)
    limited_differences = np.minimum(differences, difference_ceiling)

    print(f"{percent=}, {percentile=}, {difference_ceiling=}, {max(limited_differences)=}")

    ax = sns.violinplot(
        {"differences": differences, "limited_differences": limited_differences}, inner=None
    )
    sns.stripplot(
        {"differences": differences, "limited_differences": limited_differences},
        edgecolor="black",
        linewidth=1,
        palette=["white"] * 1,
        ax=ax,
    )
    plt.show()

    ax = sns.violinplot({"limited_differences": limited_differences}, inner=None)
    sns.stripplot(
        {"limited_differences": limited_differences},
        edgecolor="black",
        linewidth=1,
        palette=["white"] * 1,
        ax=ax,
    )
    plt.show()


def draw_update_positions_step(
    positions: np.ndarray,
    interaction_resulting_forces: np.ndarray,
    min_constr_resulting_forces: np.ndarray,
    max_constr_resulting_forces: np.ndarray,
    resulting_forces_vectors: np.ndarray,
    max_dist: float | None,
) -> None:
    def keep_2_dims(a: np.ndarray) -> np.ndarray:
        return a[0:2]

    logger.debug(
        "Step that will be applied" + (" keeping only 2 dims" if positions.shape[1] > 2 else "")
    )
    plt.scatter(positions[:, 0], positions[:, 1])

    base_arrow_width = np.max(scipy.spatial.distance.pdist(positions)) / 100

    for u, force in enumerate(interaction_resulting_forces):
        if np.any(force):
            plt.arrow(
                *keep_2_dims(positions[u]),
                *keep_2_dims(force),
                color="blue",
                width=base_arrow_width,
            )

    for u, force in enumerate(min_constr_resulting_forces):
        if np.any(force):
            plt.arrow(
                *keep_2_dims(positions[u]),
                *keep_2_dims(force),
                color="green",
                width=base_arrow_width,
            )

    for u, force in enumerate(max_constr_resulting_forces):
        if np.any(force):
            plt.arrow(
                *keep_2_dims(positions[u]),
                *keep_2_dims(force),
                color="black",
                width=base_arrow_width,
            )

    for position, force in zip(positions, resulting_forces_vectors):
        plt.arrow(
            *keep_2_dims(position),
            *keep_2_dims(force),
            color="red",
            width=base_arrow_width * 0.4,
        )

    plt.gca().set_aspect("equal", "box")

    if max_dist is not None:
        circle = Circle((0, 0), max_dist / 2, color="r", fill=False, clip_on=True)
        ax = plt.gca()
        ax.add_patch(circle)
    plt.show()
