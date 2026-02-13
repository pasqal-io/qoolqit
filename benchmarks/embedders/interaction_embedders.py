import numpy as np
from qoolqit import InteractionEmbeddingConfig, BladeConfig

from qoolqit.embedding.algorithms.interaction_embedding import interaction_embedding
from qoolqit.embedding.algorithms.blade.blade import blade
from sklearn.manifold import smacof


def interaction_matrix(pos):
    n = len(pos)
    interactions = np.zeros((n, n))
    for i in range(n):
        for j in range(i+1, n):
            interaction = np.linalg.norm(pos[i]-pos[j])**(-6)
            interactions[i, j] = interaction
            interactions[j, i] = interaction
    return interactions


# qubo = np.random.random((5, 5))
# qubo += qubo.mT
# qubo /= qubo.max()
# np.fill_diagonal(qubo, 0.0)

qubo = interaction_matrix(np.random.random((4, 2)))
qubo /= qubo.max()
print(qubo)

qubo_for_smacof = qubo
mask = qubo > 0.0
qubo_for_smacof[mask] = qubo[mask]**(-1/6)


ie_config = InteractionEmbeddingConfig()
b_config = BladeConfig()

res_smacof = smacof(qubo_for_smacof)
pos_smacof = res_smacof[0]
pos_ie = interaction_embedding(qubo, **ie_config.dict())
pos_blade = blade(qubo, **b_config.dict())





print(interaction_matrix(pos_smacof))
print(interaction_matrix(pos_ie))
print(interaction_matrix(pos_blade))