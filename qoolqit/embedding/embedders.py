from __future__ import annotations

from typing import Callable

from qoolqit.graphs import DataGraph

from .algorithms import SpringLayoutConfig, spring_layout_embedding
from .base_embedder import BaseEmbedder, EmbeddingConfig


class UnitDiskEmbedder(BaseEmbedder[DataGraph, DataGraph]):
    """A family of embedders that map a DataGraph to a DataGraph.

    Focused on unit-disk graph embedding, where the goal is to find a set of coordinates
    for a graph that has no coordinates, such that the final unit-disk graph matches the
    set of edges in the original graph.

    A custom algorithm and configuration can be set at initialization.
    """

    def __init__(self, algorithm: Callable, config: EmbeddingConfig) -> None:
        super().__init__(algorithm, config)

    def validate_data(self, data: DataGraph) -> bool:
        return isinstance(data, DataGraph)

    def _run_algorithm(self, data: DataGraph) -> DataGraph:
        graph = DataGraph(data.edges)
        graph.coords = self.algorithm(data, **self.config.dict())
        return graph


class SpringLayoutEmbedder(UnitDiskEmbedder):
    def __init__(self, config: SpringLayoutConfig | None = None):
        algorithm = spring_layout_embedding
        if config is None:
            config = SpringLayoutConfig()
        super().__init__(algorithm, config)
