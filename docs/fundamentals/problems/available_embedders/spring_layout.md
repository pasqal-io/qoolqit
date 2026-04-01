# Spring-layout embedder

The spring-layout embedding utilizes the Fruchterman-Reingold force-directed algorithm. It assigns spring-like forces to the edges that keep nodes closer, while treating nodes themselves as repelling objects. The system is then simulated until the nodes find an equilibrium position, which represent the final coordinates assigned to the nodes.

In QoolQit, the `SpringLayoutEmbedder` directly wraps the `nx.spring_layout` function, and it maps a `DataGraph` without coordinates to another `DataGraph` with coordinates.

```python exec="on" source="material-block" result="json" session="embedding"
from qoolqit.embedding import SpringLayoutEmbedder

embedder = SpringLayoutEmbedder()
print(embedder) # markdown-exec: hide
```

As you can see above it holds an algorithm and a config with a set of default parameters. For information on the algorithm and parameters, you can use the `embedder.info` property.

```python exec="on" source="material-block" result="json" session="embedding"
print(embedder.info)
```

In this case, the embedder is a direct wrapper on top of `nx.spring_layout`, and any parameters are the ones directly used by that function. For more information, you can check the [documentation for NetworkX](https://networkx.org/documentation/stable/reference/generated/networkx.drawing.layout.spring_layout.html). The parameters can be directly changed in the config.

```python exec="on" source="material-block" result="json" session="embedding"
embedder.config.iterations = 100
embedder.config.seed = 1

print(embedder)
```

Finally, we can run the embedder with the `embed` method.

```python exec="on" source="material-block" html="1" session="embedding"
import matplotlib.pyplot as plt
from qoolqit import DataGraph

graph_1 = DataGraph.random_er(n = 7, p = 0.3, seed = 3)
embedded_graph_1 = embedder.embed(graph_1)

fig, axs = plt.subplots(1, 2, figsize=(8,4), dpi=200)
graph_1.draw(ax=axs[0])
embedded_graph_1.draw(ax=axs[1])
from docs.utils import fig_to_html # markdown-exec: hide
print(fig_to_html(fig)) # markdown-exec: hide
```

Now, we can check if the resulting graph is a unit-disk graph

```python exec="on" source="material-block" result="json" session="embedding"
embedded_graph_1.is_ud_graph()
print(embedded_graph_1.is_ud_graph()) # markdown-exec: hide
```

In this case, the embedding was successful and we obtained a unit-disk graph. For more densely connected graphs, the spring layout algorithm tends to struggle with finding a unit-disk graph embedding, if it even exists.

```python exec="on" source="material-block" html="1" session="embedding"
graph_2 = DataGraph.random_er(n = 7, p = 0.8, seed = 3)
embedded_graph_2 = embedder.embed(graph_2)

fig, axs = plt.subplots(1, 2, figsize=(8,4), dpi=200)
graph_2.draw(ax=axs[0])
embedded_graph_2.draw(ax=axs[1])
from docs.utils import fig_to_html # markdown-exec: hide
print(fig_to_html(fig)) # markdown-exec: hide
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