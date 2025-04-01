from __future__ import annotations

from dataclasses import dataclass

from qoolqit.graphs import Graph


@dataclass
class EmbeddedGraph:
    """An EmbeddedGraph consists of two graphs: the original graph and the embedded graph.

    It can hold methods that automatically compute metrics that somehow characterize the
    embedded graph in comparison to the original graph.
    """

    original: Graph
    embedded: Graph
