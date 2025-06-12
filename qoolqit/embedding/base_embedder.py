from __future__ import annotations

import inspect
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from typing import Callable, Generic, TypeVar

import numpy as np

from qoolqit.graphs import DataGraph

# List is a placeholder, the idea is to later extend the supported data types
InDataType = TypeVar("InDataType", DataGraph, np.ndarray)
OutDataType = TypeVar("OutDataType", DataGraph, np.ndarray)


@dataclass
class EmbeddingConfig(ABC):
    """Base abstract dataclass for all embedding algorithm configurations.

    Subclasses define parameters specific to their algorithms. Each config
    should define fields that directly translate to arguments in the respective
    embedding function it configurates.
    """

    def dict(self) -> dict:
        return asdict(self)


class BaseEmbedder(ABC, Generic[InDataType, OutDataType]):
    """Abstract base class for all embedders.

    An embedder is a function that maps a InDataType to an OutDataType
    through an embedding algorithm. Parameters of the embedding algorithm
    can be customized through the EmbeddingConfig.
    """

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
        print("-- Embedder docstring:")
        print(inspect.getdoc(self))
        print("")
        print("-- Embedding agorithm docstring:")
        print(inspect.getdoc(self.algorithm))

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
        InDataType to the OutDataType, including any intermediate steps or post processing.

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
