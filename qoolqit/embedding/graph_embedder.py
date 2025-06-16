from __future__ import annotations

from qoolqit.graphs import DataGraph

from .algorithms import SpringLayoutConfig, spring_layout_embedding
from .base_embedder import BaseEmbedder


class GraphToGraphEmbedder(BaseEmbedder[DataGraph, DataGraph]):
    """A family of embedders that map a graph to a graph.

    Focused on unit-disk graph embedding, where the goal is to find a set of coordinates
    for a graph that has no coordinates, such that the final unit-disk edges matches the
    set of edges in the original graph.

    A custom algorithm and configuration can be set at initialization.
    """

    def validate_data(self, data: DataGraph) -> None:
        if not isinstance(data, DataGraph):
            raise TypeError(
                f"Data of type {type(data)} not supported. "
                + f"{self.__class__.__name__} requires data of type DataGraph."
            )

    def _run_algorithm(self, data: DataGraph) -> DataGraph:
        graph = DataGraph(data.edges)
        graph.coords = self.algorithm(data, **self.config.dict())
        return graph


class SpringLayoutEmbedder(GraphToGraphEmbedder):
    def __init__(self, config: SpringLayoutConfig | None = None):
        algorithm = spring_layout_embedding
        if config is None:
            config = SpringLayoutConfig()
        super().__init__(algorithm, config)
