from __future__ import annotations

import inspect
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from typing import Callable, Generic, TypeVar

from qoolqit.graphs import DataGraph

InDataType = TypeVar("InDataType", DataGraph, dict)
OutDataType = TypeVar("OutDataType", DataGraph, dict)


@dataclass
class EmbeddingConfig(ABC):
    """Base abstract dataclass for all embedding algorithm configurations.

    Subclasses define parameters specific to their algorithms.
    """

    def dict(self) -> dict:
        return asdict(self)


class BaseEmbedder(ABC, Generic[InDataType, OutDataType]):
    """Abstract base class for all embedders."""

    def __init__(self, algorithm: Callable, config: EmbeddingConfig) -> None:

        algo_signature = inspect.signature(algorithm)

        if not set(config.dict().keys()) <= set(algo_signature.parameters):
            raise KeyError("Config is not compatible with the given algorithm.")

        self._algorithm = algorithm
        self._config = config

    @property
    def config(self) -> EmbeddingConfig:
        """Returns the config for the embedding algorithm."""
        return self._config

    @property
    def algorithm(self) -> Callable:
        """Returns the callable to the embedding algorithm."""
        return self._algorithm

    @property
    def info(self) -> None:
        """Prints info about the embedding algorithm."""
        own_docstring = inspect.getdoc(self)
        algo_docstring = inspect.getdoc(self._algorithm)
        print("-- Embedder docstring:")
        print(own_docstring)
        print("")
        print("-- Embedding agorithm docstring:")
        print(algo_docstring)

    @abstractmethod
    def validate_data(self, data: InDataType) -> bool:
        """Checks if the given data is compatible with the embedder.

        Each embedder should write its own data validator returning True / False.

        Arguments:
            data: the data to validate.
        """
        ...

    @abstractmethod
    def _run_algorithm(self, data: InDataType) -> OutDataType:
        """Runs the embedding algorithm.

        Each embedder should write the specific steps required to go from the
        InDataType to the OutDataType, including any intermediate or post processing.

        Arguments:
            data: the data to embed.
        """
        ...

    def embed(self, data: InDataType) -> OutDataType:
        """Checks if the data is valid and then runs the embedding algorithm.

        Arguments:
            data: the data to embed.
        """
        if self.validate_data(data):
            return self._run_algorithm(data)
        else:
            raise TypeError(f"Embedder does not support data of type {type(data)}.")

    def __str__(self) -> str:
        string = (
            f"{self.__class__.__name__}:\n"
            + f"| Algorithm: {self._algorithm.__name__}\n"
            + f"| Config: {self._config.__repr__()}"
        )
        return string

    def __repr__(self) -> str:
        return self.__str__()
