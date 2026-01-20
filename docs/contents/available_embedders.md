# The embedding problem

Embedding data and problems into the Rydberg analog model is a broad research topic. Typically, an embedding is a structure preserving map $f_\text{embedding}: X \rightarrow Y$, such that an object $X$ is embedded into an object $Y$. Our goal is to define optimal embedding functions such that problem-specific data and definitions are embedded into model-compatible objects with the Rydberg analog model.

In QoolQit, all concrete embedders follow a basic interface set by the `BaseEmbedder` abstract base class:

```python
from qoolqit import ConcreteEmbedder

# Initialize the embedder
embedder = ConcreteEmbedder()

# Access information about the embedding algorithm
embedder.info

# Access the configuration of the embedding algorithm
embedder.config

# Change some value of the embedding configuration
embedder.config.param = new_value

# Define some initial data object
data = some_data_generator()

# Embed the data with the embedder
embedded_data = embedder.embed(data)
```

In this case, `ConcreteEmbedder` exemplifies an embedder that already has a mapping function and the respective configuration dataclass for that mapping function. Below, we will exemplify how to use some of the pre-defined concrete embedders directly available in QoolQit, and then show some considerations when defining custom embedders.

## Unit-disk graph embedding

Unit-disk graph embedding is the problem of finding a suitable function $f_\text{UD}: V\rightarrow\mathbb{R}^2$ that assigns coordinates to each node in the graph, such that the resulting unit-disk graph exactly matches the original graph (see the [graphs page](graphs.md#unit-disk) for the definition of a unit-disk graph). In general, not all graphs can be embedded into unit-disk graphs, and deciding if a graph can be embedded into a unit-disk graph is a NP-Hard problem.

However, several heuristic algorithms can be developed to tackle the unit-disk graph embedding problem.

### Spring-layout embedding

The spring-layout embedding utilizes the Fruchterman-Reingold force-directed algorithm. It assigns spring-like forces to the edges that keep nodes closer, while treating nodes themselves as repelling objects. The system is then simulated until the nodes find an equilibrium position, which represent the final coordinates assigned to the nodes.

In QoolQit, the `SpringLayoutEmbedder` directly wraps the `nx.spring_layout` function, and it maps a `DataGraph` without coordinates to another `DataGraph` with coordinates.

```python exec="on" source="material-block" result="json" session="embedding"
from qoolqit import SpringLayoutEmbedder

embedder = SpringLayoutEmbedder()
print(embedder) # markdown-exec: hide
```

As you can see above it holds an algorithm and a config with a set of default parameters. For information on the algorithm and parameters, you can use the `embedder.info` property.

```python exec="on" source="material-block" result="json" session="embedding"
print(embedder.info)
```

In this case, this embedder is a direct wrapper on top of `nx.spring_layout`, and any parameters are the ones directly used by that function. For more information, you can check the [documentation for NetworkX](https://networkx.org/documentation/stable/reference/generated/networkx.drawing.layout.spring_layout.html). The parameters can be directly changed in the config.

```python exec="on" source="material-block" result="json" session="embedding"
embedder.config.iterations = 100
embedder.config.seed = 1

print(embedder)
```

Finally, we can run the embedder with the `embed` method.

```python exec="on" source="material-block" html="1" session="embedding"
from qoolqit import DataGraph

graph_1 = DataGraph.random_er(n = 7, p = 0.3, seed = 3)

embedded_graph_1 = embedder.embed(graph_1)

graph_1.draw()
embedded_graph_1.draw()

import matplotlib.pyplot as plt # markdown-exec: hide
from docs.utils import fig_to_html # markdown-exec: hide

fig1 = graph_1.draw(return_fig = True) # markdown-exec: hide
fig2 = embedded_graph_1.draw(return_fig = True) # markdown-exec: hide
print(fig_to_html(fig1)) # markdown-exec: hide
print(fig_to_html(fig2)) # markdown-exec: hide
```

Now, we can check if the resulting graph is a unit-disk graph

```python exec="on" source="material-block" result="json" session="embedding"
embedded_graph_1.is_ud_graph()
print(embedded_graph_1.is_ud_graph()) # markdown-exec: hide
```

In this case the embedding was successful and we obtained a unit-disk graph. For more densely connected graphs, the spring layout algorithm tends to struggle with finding a unit-disk graph embedding, if it even exists.

```python exec="on" source="material-block" html="1" session="embedding"
graph_2 = DataGraph.random_er(n = 7, p = 0.8, seed = 3)

embedded_graph_2 = embedder.embed(graph_2)

graph_2.draw()
embedded_graph_2.draw()

import matplotlib.pyplot as plt # markdown-exec: hide
from docs.utils import fig_to_html # markdown-exec: hide

fig1 = graph_2.draw(return_fig = True) # markdown-exec: hide
fig2 = embedded_graph_2.draw(return_fig = True) # markdown-exec: hide
print(fig_to_html(fig1)) # markdown-exec: hide
print(fig_to_html(fig2)) # markdown-exec: hide
```

```python exec="on" source="material-block" result="json" session="embedding"
embedded_graph_2.is_ud_graph()
print(embedded_graph_2.is_ud_graph()) # markdown-exec: hide
```
While the algorithm converged and assigned positions to each node, the resulting embedded graph fails the unit-disk graph test.

However, in both cases, we have embedded the original data into a graph with coordinates, which is an object that is compatible with the Rydberg analog model. As such, we can directly instantiate a register of qubits from these graphs.

```python exec="on" source="material-block" html="1" session="embedding"
from qoolqit import Register

register_1 = Register.from_graph(embedded_graph_1)
register_2 = Register.from_graph(embedded_graph_2)

register_1.draw()
register_2.draw()

fig1 = register_1.draw(return_fig = True) # markdown-exec: hide
fig2 = register_2.draw(return_fig = True) # markdown-exec: hide
print(fig_to_html(fig1)) # markdown-exec: hide
print(fig_to_html(fig2)) # markdown-exec: hide
```


## Matrix embedding

<a name="matrix-embedding"></a>

Matrix embedding is the problem of encoding a matrix into the Rydberg analog model. Several approaches can be taken, using different algorithms.

### Interaction embedding

Interaction embedding means to encode a matrix in the interaction term of the Rydberg analog model. For a matrix $U$, the goal is to find the set of coordinates that minimize

$$
\min_{\{(x,\, y)\}}~\sum_{ij}\left\|U_{ij}-\frac{1}{r^6_{ij}}\right\|,
$$

where $r_{ij} = \sqrt{(x_i-x_j)^2 + (y_i-y_j)^2}$ is the distance between qubits $i$ and $j$. This requires the matrix $U$ to be positive and symmetric, and only the off-diagonal terms are embedded.

In QoolQit, the `InteractionEmbedder` performs this minimization using `scipy.minimize`, and it maps a `np.ndarray` to a `DataGraph` with coordinates.

```python exec="on" source="material-block" result="json" session="embedding"
from qoolqit import InteractionEmbedder

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
import numpy as np

embedded_graph = embedder.embed(matrix)

register = Register.from_graph(embedded_graph)

embedded_graph.draw()
register.draw()

fig1 = embedded_graph.draw(return_fig = True) # markdown-exec: hide
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
