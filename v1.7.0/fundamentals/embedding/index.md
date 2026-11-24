In this section, you will learn how to:

- understand how problem graphs are mapped into the analog Rydberg model through embedding,
- use QoolQit embedders to embed graphs, i.e. assigning coordinates to nodes,
- test whether an embedding satisfies hardware constraints (e.g. unit-disk condition),
- convert embedded graphs into qubit registers.

---

## The embedding problem

Embedding data and problems into the Rydberg analog model is an active area of research. An embedding is typically defined as a structure-preserving mapping \\(f\_\\text{embedding}: X \\rightarrow Y\\) that transforms an object \\(X\\) into an object \\(Y\\). In our context, we seek to develop effective embedding functions that map problem-specific data and structures into representations compatible with the Rydberg analog model.

Currently, QoolQit focuses on register embedders - algorithms that assign coordinates to graph nodes, enabling the creation of qubit registers from abstract graph structures.

In QoolQit, all embedders follow a basic interface. For example, the `InteractionEmbedder` (discussed in detail later) interface provides the following methods:

```
from qoolqit.embedding import InteractionEmbedder, InteractionEmbedderConfig

# Initialize the embedder
config = InteractionEmbedderConfig()
embedder = InteractionEmbedder(config=config)

# Access information about the embedding algorithm
embedder.info

# Access the configuration of the embedding algorithm
embedder.config

# Embed the data with the embedder
embedded_data = embedder.embed(data)
```

All the available embedders are listed in the following section. For more details on defining custom embedders, the reader can refer to [Custom embedders](<https://pasqal-io.github.io/qoolqit/v1.7.0/extended_usage/custom_embedders/index.md>).

## Available embedders

Below, we will exemplify how to use some of the pre-defined concrete embedders directly available in QoolQit, and then show some considerations when defining custom embedders.

- [Interaction embedder](<#interaction-embedder>)
- [Spring-layout embedder](<#spring-layout-embedder>)
- [Blade](<#blade>)

### Interaction embedder

Interaction embedding means to encode a matrix in the interaction term of the Rydberg analog model. For a matrix \\(U\\), the goal is to find the set of coordinates that minimize

\\\[ \\min\_{\\{(x,\\, y)\\}}\~\\sum\_{ij}\\left\\|U\_{ij}-\\frac{1}{r^6\_{ij}}\\right\\|, \\\]

where \\(r\_{ij} = \\sqrt{(x\_i-x\_j)^2 + (y\_i-y\_j)^2}\\) is the distance between qubits \\(i\\) and \\(j\\). This requires the matrix \\(U\\) to be positive and symmetric, and only the off-diagonal terms are embedded.

In QoolQit, the `InteractionEmbedder` performs this minimization using `scipy.minimize`, and it maps a `np.ndarray` to a `DataGraph` with coordinates.

```
from qoolqit.embedding import InteractionEmbedder

embedder = InteractionEmbedder()
print(embedder)
```

```
InteractionEmbedder:
| Algorithm: interaction_embedding
| Config: InteractionEmbedderConfig(method='Nelder-Mead', maxiter=200000, tol=1e-08, x0=None, seed=None)
```

Checking the `info` on the embedder, we see a few parameters are available for customization through the `config`. There are parameters that get passed to `scipy.minimize`, and their description can be found in the [SciPy documentation](<https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.minimize.html>).

```
print(embedder.info)
```

```
-- Embedding algorithm docstring:

Embed a matrix into the interaction term of the Rydberg analog model.

Finds node coordinates whose interactions 1/rᵢⱼ⁶ best approximate the
off-diagonal entries of `matrix`, using `scipy.optimize.minimize`.

Args:
    matrix: symmetric N x N target matrix to embed.
    method: optimization method passed to `scipy.optimize.minimize`.
    x0: initial node positions, of shape (N, 2).
        If None, positions are drawn uniformly in [0, 1), seeded by `seed`.
    maxiter: maximum number of optimizer iterations.
    tol: tolerance for termination.
    seed: seed for the random initial positions, ignored if `x0` is set.
        If None, results differ between runs.

Returns:
    DataGraph: graph with node coordinates centered on their median.
```

We can try it out with the default configuration by generating a random symmetric positive matrix.

```
import numpy as np

A = np.random.rand(6, 6)
A += A.T
print(A)
```

```
[[0.17782734 0.9945461  1.4854428  1.54001031 1.07362615 0.30760143]
 [0.9945461  0.57286401 1.65713039 0.95457692 0.93087802 0.64354438]
 [1.4854428  1.65713039 0.3292994  1.06790971 1.76677429 0.27125508]
 [1.54001031 0.95457692 1.06790971 1.08104692 1.6014086  0.66611802]
 [1.07362615 0.93087802 1.76677429 1.6014086  0.85551234 0.86709708]
 [0.30760143 0.64354438 0.27125508 0.66611802 0.86709708 1.46849472]]
```

Finally, running the embedding we obtain a `DataGraph` with coordinates that can be easily converted to a `Register` of qubits.

```
import matplotlib.pyplot as plt

from qoolqit import Register
from qoolqit.embedding import InteractionEmbedderConfig

config = InteractionEmbedderConfig(seed=1)
embedder = InteractionEmbedder(config)
embedded_graph = embedder.embed(A)
register = Register.from_graph(embedded_graph)

embedded_graph.draw()
register.draw()
```

png

png

To check how the embedding performed, we can inspect the interaction values in the `Register` and compare them to the off-diagonal elements in the matrix.

```
interactions = list(register.interactions().values())

triang_upper = np.triu(A, k = 1)
off_diagonal = triang_upper[triang_upper != 0].tolist()

print([f"{f:.4f}" for f in sorted(interactions)])
print([f"{f:.4f}" for f in sorted(off_diagonal)])
```

```
['0.0144', '0.0210', '0.0334', '0.0423', '0.0491', '0.0578', '0.6603', '0.8869', '0.9212', '1.0181', '1.0768', '1.1225', '1.6201', '1.6774', '1.7809']
['0.2713', '0.3076', '0.6435', '0.6661', '0.8671', '0.9309', '0.9546', '0.9945', '1.0679', '1.0736', '1.4854', '1.5400', '1.6014', '1.6571', '1.7668']
```

### Spring-layout embedder

The spring-layout embedding utilizes the Fruchterman-Reingold force-directed algorithm. It assigns spring-like forces to the edges that keep nodes closer, while treating nodes themselves as repelling objects. The system is then simulated until the nodes find an equilibrium position, which represents the final coordinates assigned to the nodes.

In QoolQit, the `SpringLayoutEmbedder` directly wraps the `nx.spring_layout` function, and it maps a `DataGraph` without coordinates to another `DataGraph` with coordinates.

```
from qoolqit.embedding import SpringLayoutEmbedder

embedder = SpringLayoutEmbedder()
print(embedder)
```

```
SpringLayoutEmbedder:
| Algorithm: spring_layout_embedding
| Config: SpringLayoutConfig(iterations=100, threshold=0.0001, seed=None)
```

As you can see above it holds an algorithm and a config with a set of default parameters. For information on the algorithm and parameters, you can use the `embedder.info` property.

```
print(embedder.info)
```

```
-- Embedding algorithm docstring:

Force-directed embedding, wrapping `nx.spring_layout`.

Generates a new graph with the same nodes and edges as the original graph, but with
node coordinates set to embed edge weights into pairwise distances as wᵢⱼ=1/rᵢⱼ^6.

The positions are generated by `nx.spring_layout`.
Since `nx.spring_layout` embeds edge weights as wᵢⱼ = (k/rᵢⱼ)^3, we set:
 - `k=1` and `scale=None` to disable global rescaling of positions.
 - rescale weights wᵢⱼ -> wᵢⱼ^1/2
to achieve our target embedding wᵢⱼ=1/rᵢⱼ^6.

Check the documentation for `nx.spring_layout` for more information about each parameter:
https://networkx.org/documentation/stable/reference/generated/networkx.drawing.layout.spring_layout.html

Args:
    graph: the graph to embed according to its edge weights.
    iterations: maximum number of iterations to take.
    threshold: Threshold for relative error in node position changes.
        The iteration stops if force-displacement is below this threshold.
    seed: random seed for reproducibility.

Returns:
    DataGraph: graph with the node coordinates set according to the spring-layout embedding.
```

In this case, the embedder is a direct wrapper on top of `nx.spring_layout`, and any parameters are the ones directly used by that function. For more information, you can check the [documentation for NetworkX](<https://networkx.org/documentation/stable/reference/generated/networkx.drawing.layout.spring_layout.html>). The parameters can be directly changed in the config.

```
embedder.config.iterations = 100
embedder.config.seed = 1
print(embedder)
```

```
SpringLayoutEmbedder:
| Algorithm: spring_layout_embedding
| Config: SpringLayoutConfig(iterations=100, threshold=0.0001, seed=1)
```

Finally, we can run the embedder with the `embed` method.

```
from qoolqit.graphs import DataGraph

graph_1 = DataGraph.random_er(n = 7, p = 0.3, seed = 3)
embedded_graph_1 = embedder.embed(graph_1)

fig, axs = plt.subplots(1, 2)
graph_1.draw(ax=axs[0])
embedded_graph_1.draw(ax=axs[1])
```

png

Now, we can check if the resulting graph is a unit-disk graph.

```
embedded_graph_1.is_ud_graph()
```

```
True
```

In this case, the embedding was successful and we obtained a unit-disk graph. For more densely connected graphs, the spring layout algorithm tends to struggle with finding a unit-disk graph embedding, if it even exists.

```
graph_2 = DataGraph.random_er(n = 7, p = 0.8, seed = 3)
embedded_graph_2 = embedder.embed(graph_2)

fig, axs = plt.subplots(1, 2)
graph_2.draw(ax=axs[0])
embedded_graph_2.draw(ax=axs[1])
```

png

While the algorithm converged and assigned positions to each node, the resulting embedded graph fails the unit-disk graph test.

However, in both cases, we have embedded the original data into a graph with coordinates, which is an object that is compatible with the Rydberg analog model. As such, we can directly instantiate a register of qubits from these graphs.

```
from qoolqit import Register

register_1 = Register.from_graph(embedded_graph_1)
register_2 = Register.from_graph(embedded_graph_2)

fig, axs = plt.subplots(1, 2)
register_1.draw(ax=axs[0])
register_2.draw(ax=axs[1])
fig.tight_layout()
```

png

While defining a graph, weights can also be directly assigned to edges.

```
n=6
graph_2 = DataGraph.circle(n)
for e in graph_2.edge_weights:
    graph_2.edge_weights[e]= np.random.rand()

embedded_graph_2 = embedder.embed(graph_2)

fig, axs = plt.subplots(1, 2)
graph_2.draw(ax=axs[0])
embedded_graph_2.draw(ax=axs[1])
```

png

The embedder will respect the edge weights, ensuring that edges with higher weights are closer in the embedded graph.

### Blade

The **Balanced Latently Dimensional Embedder (BLaDE)** is a physics-inspired algorithm that, like the `InteractionEmbedder`, maps an interaction matrix or QUBO directly to node positions. It starts from a higher-dimensional embedding and progressively projects it down to the target number of dimensions, which helps it escape local minima and tends to produce higher quality embeddings than the spring-layout approach, at the cost of being slower to run.

In QoolQit, the [`Blade`](<https://pasqal-io.github.io/qoolqit/v1.7.0/reference/embedding/index.md#qoolqit.embedding.Blade>) embedder wraps this algorithm, mapping a `np.ndarray` to a `DataGraph` with coordinates, in the same way as the `InteractionEmbedder`.

```
from qoolqit.embedding import Blade

blade_embedder = Blade()
embedded_graph = blade_embedder.embed(A)
register = Register.from_graph(embedded_graph)

register.draw()
```

png

The [`BladeConfig`](<https://pasqal-io.github.io/qoolqit/v1.7.0/reference/embedding/index.md#qoolqit.embedding.BladeConfig>) can also directly take a QoolQit `Device`, in which case it automatically sets the internal distance constraints so that the resulting embedding respects the device's hardware limitations. See the API reference for `BladeConfig` for the full list of usage and arguments.

For a more complete, real-world example of embedding a QUBO with Blade, check out the [Blade tutorial](<https://docs.pasqal.com/applicationsolvingtools/qubo/tutorial/05-blade>) in the `qubo-solver` documentation.
