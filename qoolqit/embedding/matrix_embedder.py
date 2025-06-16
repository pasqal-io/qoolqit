from __future__ import annotations

import numpy as np

from qoolqit.graphs import DataGraph
from qoolqit.utils import ATOL_32

from .algorithms import InteractionEmbeddingConfig, interaction_embedding
from .base_embedder import BaseEmbedder


class MatrixToGraphEmbedder(BaseEmbedder[np.ndarray, DataGraph]):
    """A family of embedders that map a matrix to a graph.

    A custom algorithm and configuration can be set at initialization.
    """

    def validate_data(self, data: np.ndarray) -> None:
        if not isinstance(data, np.ndarray):
            raise TypeError(
                f"Data of type {type(data)} not supported. {self.__class__.__name__} "
                + "requires data to be a symmetric matrix of type np.ndarray."
            )
        if data.ndim != 2:
            raise ValueError("Data must be a 2D matrix.")
        if not np.allclose(data, data.T, rtol=0.0, atol=ATOL_32):
            raise ValueError("Data must be a symmetric matrix.")

    def _run_algorithm(self, data: np.ndarray) -> DataGraph:
        coords = self.algorithm(data, **self.config.dict())
        graph = DataGraph.from_coordinates(coords.tolist())
        return graph


class InteractionEmbedder(MatrixToGraphEmbedder):

    def __init__(self, config: InteractionEmbeddingConfig | None = None):
        algorithm = interaction_embedding
        if config is None:
            config = InteractionEmbeddingConfig()
        super().__init__(algorithm, config)
