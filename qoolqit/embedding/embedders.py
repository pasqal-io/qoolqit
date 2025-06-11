from __future__ import annotations

from typing import Callable

import networkx as nx

from qoolqit.graphs import DataGraph

from .algorithms import spring_layout_embedding
from .base_embedder import BaseEmbedder
from .configs import SpringLayoutConfig


class UnitDiskEmbedder(BaseEmbedder):
    """An embedder that aims to find coordinates to a graph that has no coordinates."""

    def __init__(
        self,
        algorithm: Callable = spring_layout_embedding,
        config: SpringLayoutConfig = SpringLayoutConfig(),
    ) -> None:
        super().__init__(algorithm, config)

    def validate_data(self, data: DataGraph) -> None:
        if not isinstance(data, DataGraph):
            raise TypeError(f"Invalid data of type {type(data)}.")

    def embed(self, data: DataGraph) -> DataGraph:
        graph = DataGraph(data.edges)
        graph.coords = nx.spring_layout(data, self.config)
        return graph
