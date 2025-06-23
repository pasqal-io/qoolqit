from __future__ import annotations

from qoolqit.graphs import DataGraph

from .algorithms import SpringLayoutConfig, spring_layout_embedding
from .base_embedder import BaseEmbedder, ConfigType


class GraphToGraphEmbedder(BaseEmbedder[DataGraph, DataGraph, ConfigType]):
    """A family of embedders that map a graph to a graph.

    Focused on unit-disk graph embedding, where the goal is to find a set of coordinates
    for a graph that has no coordinates, such that the final unit-disk edges matches the
    set of edges in the original graph.

    A custom algorithm and configuration can be set at initialization.
    """

    def validate_input(self, data: DataGraph) -> None:
        if not isinstance(data, DataGraph):
            raise TypeError(
                f"Embedding data of type {type(data)} not supported by this embedder. "
                + f"{self.__class__.__name__} requires data of type DataGraph."
            )

    def validate_output(self, result: DataGraph) -> None:
        if not isinstance(result, DataGraph):
            raise TypeError(
                "Expected embedding result to be of type DataGraph, "
                + f"algorithm returned {type(result)} instead."
            )


class SpringLayoutEmbedder(GraphToGraphEmbedder[SpringLayoutConfig]):
    """A graph to graph embedder using the spring layout algorithm."""

    def __init__(self) -> None:
        super().__init__(spring_layout_embedding, SpringLayoutConfig())
