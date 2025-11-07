from __future__ import annotations

import inspect
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from typing import Callable, Generic, TypeVar


@dataclass
class EmbeddingConfig(ABC):
    """Base abstract dataclass for all embedding algorithm configurations.

    Subclasses define parameters specific to their algorithms. Each config
    should define fields that directly translate to arguments in the respective
    embedding function it configures.
    """

    def dict(self) -> dict:
        """Returns the dataclass as a dictionary."""
        return asdict(self)


InDataType = TypeVar("InDataType")
OutDataType = TypeVar("OutDataType")
ConfigType = TypeVar("ConfigType", bound=EmbeddingConfig)


class BaseEmbedder(ABC, Generic[InDataType, OutDataType, ConfigType]):
    """Abstract base class for all embedders.

    An embedder is a function that maps a InDataType to an OutDataType
    through an embedding algorithm. Parameters of the embedding algorithm
    can be customized through the EmbeddingConfig.
    """

    def __init__(self, algorithm: Callable, config: ConfigType) -> None:
        """Default initializer for all embedders, taking an algorithm and a config.

        An algorithm should be a standalone function that takes a piece of data of an
        InDataType and maps it to an OutDataType. Any extra configuration parameters
        taken as input by the algorithm function should be defined in the config dataclass,
        inheriting from EmbeddingConfig.

        Arguments:
            algorithm: a callable to the algorithm function.
            config: a config dataclass holding parameter values for the algorithm.
        """

        algo_signature = inspect.signature(algorithm)

        if not isinstance(config, EmbeddingConfig):
            raise TypeError(
                "The config must be an instance of a dataclass inheriting from EmbeddingConfig."
            )

        if not set(config.dict().keys()) <= set(algo_signature.parameters):
            raise KeyError(
                f"Config {config.__class__.__name__} is not compatible with the "
                + f"algorithm {algorithm.__name__}, as not all configuration fields "
                + "correspond to keyword arguments in the algorithm function."
            )

        self._algorithm = algorithm
        self._config = config

    @property
    def config(self) -> ConfigType:
        """Returns the config for the embedding algorithm."""
        return self._config

    @property
    def algorithm(self) -> Callable:
        """Returns the callable to the embedding algorithm."""
        return self._algorithm

    @property
    def info(self) -> str:
        """Prints info about the embedding algorithm."""
        header = "-- Embedding algorithm docstring:\n\n"
        docstring: str | None = inspect.getdoc(self.algorithm)
        if docstring is None:
            raise ValueError("No information found for the embedding algorithm.")
        else:
            return header + docstring

    @abstractmethod
    def validate_input(self, data: InDataType) -> None:
        """Checks if the given data is compatible with the embedder.

        Each embedder should write its own data validator. If the data
        is not of the supported type or in the specific supported format
        for that embedder, an error should be raised.

        Arguments:
            data: the data to validate.

        Raises:
            TypeError: if the data is not of the supported type.
            SomeError: some other error if other constraints are not met.
        """
        ...

    @abstractmethod
    def validate_output(self, result: OutDataType) -> None:
        """Checks if the resulting output is expected by the embedder.

        Each embedder should write its own output validator. If the result
        is not of the supported type or in the specific supported format
        for that embedder, an error should be raised.

        Arguments:
            result: the output to validate.

        Raises:
            TypeError: if the output is not of the supported type.
            SomeError: some other error if other constraints are not met.
        """
        ...

    def embed(self, data: InDataType) -> OutDataType:
        """Validates the input, runs the embedding algorithm, and validates the output.

        Arguments:
            data: the data to embed.
        """
        self.validate_input(data)
        result: OutDataType = self.algorithm(data, **self.config.dict())
        self.validate_output(result)
        return result

    def __str__(self) -> str:
        string = (
            f"{self.__class__.__name__}:\n"
            + f"| Algorithm: {self._algorithm.__name__}\n"
            + f"| Config: {self._config.__repr__()}"
        )
        return string

    def __repr__(self) -> str:
        return self.__str__()
