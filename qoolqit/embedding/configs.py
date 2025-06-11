from __future__ import annotations

from abc import ABC
from dataclasses import asdict, dataclass


@dataclass
class EmbeddingConfig(ABC):
    """Base abstract dataclass for all embedding algorithm configurations.

    Subclasses define parameters specific to their algorithms.
    """

    def dict(self) -> dict:
        return asdict(self)


@dataclass
class SpringLayoutConfig(EmbeddingConfig):
    """Optimal distance between nodes."""

    k: float | None = None

    """Maximum number of iterations taken."""
    iterations: int = 50

    """Threshold for relative error in node position changes."""
    threshold: float = 1e-4
