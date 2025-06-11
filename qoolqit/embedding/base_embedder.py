from __future__ import annotations

import inspect
from abc import ABC, abstractmethod
from typing import Callable

from qoolqit.graphs import DataGraph

from .configs import EmbeddingConfig


class BaseEmbedder(ABC):
    """Abstract base class for all embedders."""

    def __init__(self, algorithm: Callable, config: EmbeddingConfig) -> None:

        self._algorithm = algorithm
        self._config = config

    @property
    def config(self) -> EmbeddingConfig:
        """Returns the config for the embedding algorithm."""
        return self._config

    @property
    def info(self) -> None:
        """Prints info about the embedding algorithm."""
        print(inspect.getdoc(self._algorithm))

    @abstractmethod
    def validate_data(self, data: DataGraph) -> None:
        """Checks if the given data is compatible with the embedder.

        Each embedder should write its own data validator.
        """
        ...

    @abstractmethod
    def embed(self, data: DataGraph) -> DataGraph:
        """Runs the embedding algorithm.

        Arguments:
            data: the data to embed.
        """
        ...


#     def __str__(self) -> str:
#         string = f"{self.__class__.__name__}:\n" + f"| Data: {self._initial_data.__repr__()}"
#         return string

#     def __repr__(self) -> str:
#         return self.__str__()
