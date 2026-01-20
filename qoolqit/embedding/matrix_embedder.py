from __future__ import annotations

import numpy as np

from qoolqit.graphs import DataGraph

from .algorithms import (
    BladeEmbeddingConfig,
    InteractionEmbeddingConfig,
    blade_embedding,
    interaction_embedding,
)
from .base_embedder import BaseEmbedder, ConfigType


class MatrixToGraphEmbedder(BaseEmbedder[np.ndarray, DataGraph, ConfigType]):
    """A family of embedders that map a matrix to a graph.

    A custom algorithm and configuration can be set at initialization.
    """

    def validate_input(self, data: np.ndarray) -> None:
        if not isinstance(data, np.ndarray):
            raise TypeError(
                f"Data of type {type(data)} not supported. {self.__class__.__name__} "
                + "requires data to be a symmetric matrix of type np.ndarray."
            )
        if data.ndim != 2:
            raise ValueError("Data must be a 2D matrix.")
        if not np.allclose(data, data.T, rtol=0.0, atol=1e-7):
            raise ValueError("Data must be a symmetric matrix.")

    def validate_output(self, result: DataGraph) -> None:
        if not isinstance(result, DataGraph):
            raise TypeError(
                "Expected embedding result to be of type DataGraph, "
                + f"algorithm returned {type(result)} instead."
            )


class InteractionEmbedder(MatrixToGraphEmbedder[InteractionEmbeddingConfig]):
    """A matrix to graph embedder using the interaction embedding algorithm."""

    def __init__(self) -> None:
        super().__init__(interaction_embedding, InteractionEmbeddingConfig())


class BladeEmbedder(MatrixToGraphEmbedder[BladeEmbeddingConfig]):
    """A matrix to graph embedder using the blade embedding algorithm."""

    def embed(self, data: np.ndarray) -> DataGraph:
        """Validates the input, runs the embedding algorithm, and validates the output.

        Arguments:
            data: the data to embed.
        """
        self.validate_input(data)
        positions = self.algorithm(data, **self.config.dict())
        centered_coords = positions - np.mean(positions, axis=0)
        graph = DataGraph.from_coordinates(centered_coords.tolist())
        return graph

    def __init__(self, config: BladeEmbeddingConfig = BladeEmbeddingConfig()) -> None:
        super().__init__(blade_embedding, config=config)
