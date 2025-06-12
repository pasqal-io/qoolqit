from __future__ import annotations

from typing import Callable

import numpy as np

from qoolqit.graphs import DataGraph

from .algorithms import InteractionEmbeddingConfig, interaction_embedding
from .base_embedder import BaseEmbedder, EmbeddingConfig


class MatrixEmbedder(BaseEmbedder[np.ndarray, DataGraph]):
    """A family of embedders that map a matrix to a graph.

    A custom algorithm and configuration can be set at initialization.
    """

    def __init__(self, algorithm: Callable, config: EmbeddingConfig) -> None:
        super().__init__(algorithm, config)

    def validate_data(self, data: np.ndarray) -> bool:
        return isinstance(data, np.ndarray)

    def _run_algorithm(self, data: np.ndarray) -> DataGraph:
        coords = self.algorithm(data, **self.config.dict())
        graph = DataGraph.from_coordinates(coords.tolist())
        return graph


class InteractionEmbedder(MatrixEmbedder):
    def __init__(self, config: InteractionEmbeddingConfig | None = None):
        algorithm = interaction_embedding
        if config is None:
            config = InteractionEmbeddingConfig()
        super().__init__(algorithm, config)
