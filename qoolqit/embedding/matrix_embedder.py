"""Embedders mapping a matrix to a graph with coordinates."""

from __future__ import annotations

import numpy as np
from typing_extensions import override

from qoolqit.graphs import DataGraph

from .algorithms import (
    BladeConfig,
    InteractionEmbedderConfig,
    _blade,
    interaction_embedding,
)
from .base_embedder import BaseEmbedder, ConfigType


class MatrixToGraphEmbedder(BaseEmbedder[np.ndarray, DataGraph, ConfigType]):
    """A family of embedders that map a matrix to a graph.

    A custom algorithm and configuration can be set at initialization.
    """

    @override
    def validate_input(self, data: np.ndarray) -> None:
        """Checks that the data is a symmetric 2D numpy array.

        Raises:
            TypeError: if `data` is not a numpy array.
            ValueError: if `data` is not 2D or not symmetric.
        """
        if not isinstance(data, np.ndarray):
            raise TypeError(
                f"Data of type {type(data)} not supported. {self.__class__.__name__} "
                + "requires data to be a symmetric matrix of type np.ndarray."
            )
        if data.ndim != 2:
            raise ValueError("Data must be a 2D matrix.")
        if not np.allclose(data, data.T, rtol=0.0, atol=1e-7):
            raise ValueError("Data must be a symmetric matrix.")

    @override
    def validate_output(self, result: DataGraph) -> None:
        if not isinstance(result, DataGraph):
            raise TypeError(
                "Expected embedding result to be of type DataGraph, "
                + f"algorithm returned {type(result)} instead."
            )


class InteractionEmbedder(MatrixToGraphEmbedder[InteractionEmbedderConfig]):
    """A matrix to graph embedder using the interaction embedding algorithm.

    Starting positions are random unless `x0` is set in the config. For reproducible
    results, set `seed` to an integer:

    ```python
    import numpy as np
    from qoolqit.embedding import InteractionEmbedder, InteractionEmbedderConfig

    matrix = np.array([[0.0, 1.0, 0.5], [1.0, 0.0, 0.2], [0.5, 0.2, 0.0]])
    embedder = InteractionEmbedder(InteractionEmbedderConfig(seed=3083257284))
    graph = embedder.embed(matrix)
    ```
    """

    def __init__(self, config: InteractionEmbedderConfig | None = None) -> None:
        """Inits InteractionEmbedder.

        Args:
            config: configuration for the interaction embedding. Defaults are used if None.
        """
        super().__init__(interaction_embedding, config=config or InteractionEmbedderConfig())


class Blade(MatrixToGraphEmbedder[BladeConfig]):
    """A matrix to graph embedder using the BLaDE algorithm."""

    def __init__(self, config: BladeConfig | None = None) -> None:
        """Inits Blade.

        Args:
            config (BladeConfig): configuration object for the BLaDE algorithm.
        """
        super().__init__(_blade, config=config or BladeConfig())

    def embed(self, data: np.ndarray) -> DataGraph:
        """Return a DataGraph with coordinates that embeds the input matrix.

        Validates the input, runs the embedding algorithm, and validates the output.

        Args:
            data (np.ndarray): the matrix to embed into a DataGraph with coordinates.
        """
        self.validate_input(data)
        positions = self.algorithm(data, **self.config.dict())
        graph = DataGraph.from_coordinates(positions.tolist())
        return graph
