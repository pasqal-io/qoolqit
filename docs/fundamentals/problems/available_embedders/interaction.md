# Interaction embedder

Interaction embedding means to encode a matrix in the interaction term of the Rydberg analog model. For a matrix $U$, the goal is to find the set of coordinates that minimize

$$
\min_{\{(x,\, y)\}}~\sum_{ij}\left\|U_{ij}-\frac{1}{r^6_{ij}}\right\|,
$$

where $r_{ij} = \sqrt{(x_i-x_j)^2 + (y_i-y_j)^2}$ is the distance between qubits $i$ and $j$. This requires the matrix $U$ to be positive and symmetric, and only the off-diagonal terms are embedded.

In QoolQit, the `InteractionEmbedder` performs this minimization using `scipy.minimize`, and it maps a `np.ndarray` to a `DataGraph` with coordinates.

```python exec="on" source="material-block" result="json" session="embedding"
from qoolqit.embedding import InteractionEmbedder

embedder = InteractionEmbedder()
print(embedder) # markdown-exec: hide
```

Checking the `info` on the embedder, we see a few parameters are available for customization through the `config`. There are parameters that get passed to `scipy.minimize`, and their description can be found in the [SciPy documentation](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.minimize.html).

```python exec="on" source="material-block" result="json" session="embedding"
print(embedder.info)
```

We can try it out with the default configuration by generating a random symmetric positive matrix.

```python exec="on" source="material-block" result="json" session="embedding"
import numpy as np

matrix = np.random.rand(6, 6)

matrix = matrix + matrix.T

print(matrix) # markdown-exec: hide
```

Finally, running the embedding we obtain a `DataGraph` with coordinates that can be easily converted to a `Register` of qubits.

```python exec="on" source="material-block" html="1" session="embedding"
import matplotlib.pyplot as plt
from qoolqit import Register

embedded_graph = embedder.embed(matrix)
register = Register.from_graph(embedded_graph)

fig1, ax1 = plt.subplots(figsize=(4,4), dpi=200)
embedded_graph.draw(ax=ax1)
register.draw()
fig2 = register.draw(return_fig = True) # markdown-exec: hide
print(fig_to_html(fig1)) # markdown-exec: hide
print(fig_to_html(fig2)) # markdown-exec: hide
```

To check how the embedding performed, we can inspect the interaction values in the `Register` and compare them to the off-diagonal elements in the matrix.

```python exec="on" source="material-block" result="json" session="embedding"

interactions = list(register.interactions().values())

triang_upper = np.triu(matrix, k = 1)
off_diagonal = triang_upper[triang_upper != 0].tolist()

print([f"{f:.4f}" for f in sorted(interactions)])
print([f"{f:.4f}" for f in sorted(off_diagonal)])
```
