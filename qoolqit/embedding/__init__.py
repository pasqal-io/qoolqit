"""Collection of graph and matrix embedding algorithms."""

from __future__ import annotations

from .algorithms import BladeConfig, InteractionEmbedderConfig, SpringLayoutConfig
from .base_embedder import BaseEmbedder, EmbedderConfig
from .graph_embedder import GraphToGraphEmbedder, SpringLayoutEmbedder
from .matrix_embedder import Blade, InteractionEmbedder, MatrixToGraphEmbedder

__all__ = [
    "BaseEmbedder",
    "EmbedderConfig",
    "GraphToGraphEmbedder",
    "MatrixToGraphEmbedder",
    "InteractionEmbedderConfig",
    "InteractionEmbedder",
    "SpringLayoutConfig",
    "SpringLayoutEmbedder",
    "BladeConfig",
    "Blade",
]
