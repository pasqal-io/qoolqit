from __future__ import annotations

import numpy as np
from sklearn.manifold import smacof

from qoolqit import BladeConfig, InteractionEmbeddingConfig
from qoolqit.embedding.algorithms.blade.blade import blade
from qoolqit.embedding.algorithms.interaction_embedding import interaction_embedding


def interaction_matrix(pos: np.ndarray) -> np.ndarray:
    n = len(pos)
    interactions = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            interaction = np.linalg.norm(pos[i] - pos[j]) ** (-6)
            interactions[i, j] = interaction
            interactions[j, i] = interaction
    return interactions


def stress_from_positions(target: np.ndarray, pos: np.ndarray) -> np.floating:
    return np.linalg.norm(target - interaction_matrix(pos))


# qubo = np.random.random((5, 5))
# qubo += qubo.mT
# qubo /= qubo.max()
# np.fill_diagonal(qubo, 0.0)


qubo = interaction_matrix(np.random.random((6, 2)))
qubo /= qubo.max()
print(qubo)

qubo_for_smacof = np.zeros_like(qubo)
mask = qubo > 0.0
qubo_for_smacof[mask] = qubo[mask] ** (-1 / 6)

ie_config = InteractionEmbeddingConfig(tol=1e-9)
b_config = BladeConfig()

res_smacof = smacof(qubo_for_smacof, eps=1e-7, max_iter=1000)
pos_smacof = np.array(res_smacof[0])
pos_ie = interaction_embedding(qubo, **ie_config.dict())
pos_blade = blade(qubo, **b_config.dict())


print(stress_from_positions(qubo, pos_smacof))
print(stress_from_positions(qubo, pos_ie))
print(stress_from_positions(qubo, pos_blade))
