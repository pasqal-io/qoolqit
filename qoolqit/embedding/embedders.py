from __future__ import annotations

from typing import Callable

from qoolqit.graphs import DataGraph

from .algorithms import spring_layout_embedding
from .base_embedder import BaseEmbedder
from .configs import EmbeddingConfig, SpringLayoutConfig


class UnitDiskEmbedder(BaseEmbedder[DataGraph, DataGraph]):
    """An embedder that adds coordinates to a graph that has no coordinates.

    Maps a DataGraph to a DataGraph. By default, uses the spring layout algorithm
    directly from networkx. A custom algorithm and custom configuration can be
    set at initialization.
    """

    def __init__(
        self, algorithm: Callable | None = None, config: EmbeddingConfig | None = None
    ) -> None:

        if algorithm is None:
            algorithm = spring_layout_embedding
        if config is None:
            config = SpringLayoutConfig()

        super().__init__(algorithm, config)

    def validate_data(self, data: DataGraph) -> bool:
        return isinstance(data, DataGraph)

    def _run_algorithm(self, data: DataGraph) -> DataGraph:
        graph = DataGraph(data.edges)
        graph.coords = self.algorithm(data, **self.config.dict())
        return graph


class SpringLayoutEmbedder(UnitDiskEmbedder): ...
