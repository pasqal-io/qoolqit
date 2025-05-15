# Standard structure for Graphs

Working with graphs is an essential part of computations with the Rydberg-Ising analog model. For that reason, QoolQit implements a specific `DataGraph` class to serve as the basis of all graph creation and manipulation. The `DataGraph` inherits from the `BaseGraph`, which sets base logic related to unit-disk graphs, but is not meant to be used directly. For many graph operations QoolQit relies on [NetworkX](https://networkx.org/), and the `BaseGraph` itself inherits from `nx.Graph`.


## Basic construction

The `DataGraph` is an undirected graph with no self loops. Like a `nx.Graph` it can be instantiated empty and nodes or edges added afterwords. However, currently this is not advised. Instead, the default way to instantiate a `DataGraph` should be directly with a set of edges.

```python exec="on" source="material-block" session="graphs"
from qoolqit import DataGraph

edges = [(0, 1), (1, 2), (2, 3), (3, 0)]
graph = DataGraph(edges)
```

As with any NetworkX graph, the set of nodes and edges can be accessed:

```python exec="on" source="material-block" result="json" session="graphs"
print(graph.nodes)
```
```python exec="on" source="material-block" result="json" session="graphs"
print(graph.edges)
```

These are the standard `NodeView` and `EdgeView` objects from NetworkX, and thus can be used add and access node and edge attributes.

## Drawing

We can draw the graph with `graph.draw()`, which calls [`draw_networkx`](https://networkx.org/documentation/stable/reference/generated/networkx.drawing.nx_pylab.draw_networkx.html). As such, optional arguments can be passed that will be fed to NetworkX.
```python exec="on" source="material-block" html="1" session="graphs"
import networkx as nx
import matplotlib.pyplot as plt # markdown-exec: hide
from docs.utils import fig_to_html # markdown-exec: hide

pos = nx.circular_layout(graph)

graph.draw(pos = pos)
fig = graph.draw(pos = pos, return_fig = True) # markdown-exec: hide
plt.tight_layout() # markdown-exec: hide
print(fig_to_html(fig)) # markdown-exec: hide
```

## Convenient properties and attributes

One convenient property added by QoolQit is the `sorted_edges`, which guarantees that the indices in each edge tuple are always provided as $(u, v):u<v$. In this case, `graph.sorted_edges` gives a set with the same edges as above, but NetworkX does not save the order of the nodes in an undirected edge and is sometimes inconsistent about this. However, QoolQit relies on that information for some of the logic related to unit-disk graphs.

```python exec="on" source="material-block" result="json" session="graphs"
print(graph.sorted_edges)
```

Another convenient property is accessing the pairs of all nodes in the graph, which again follow the convention of $(u, v):u<v$. This is useful for the Rydberg-Ising model when dealing with unit-disk graphs.
```python exec="on" source="material-block" result="json" session="graphs"
print(graph.all_node_pairs)
```

In QoolQit there are three attributes that take center stage when dealing with graphs: **node coordinates**, **node weights** and **edge weights**. These are the most relevant for the Rydberg-Ising model. For that reason, they are saved as dictionaries and accessible through a dedicated property in QoolQit. The previous graph did not have any of these properties, but they can be directly set:

```python exec="on" source="material-block" session="graphs"
import random

# A must have the same length as the number of nodes:
graph.coords = [(-0.5, -0.5), (-0.5, 0.5), (0.5, 0.5), (0.5, -0.5)]

# A dictionary is also accepted, in which case the keys must match the graph
graph.node_weights = {i: random.random() for i in graph.nodes}

# For edges it is expected that the (u, v) : u<v convention is kept
graph.edge_weights = {edge: random.random() for edge in graph.sorted_edges}
```

If the graph does not have these attributes, the dictionaries will still be returned with `None` in place of the value.
A set of boolean properties allows quickly checking if the graph has these attributes. It only returns `True` if there is a value set for every node / edge in the graph.

```python exec="on" source="material-block" session="graphs"
assert graph.has_coords
assert graph.has_node_weights
assert graph.has_edge_weights
```

Because the graph now has a set of node coordinates, when calling `graph.draw()` this information will be automatically used.

```python exec="on" source="material-block" html="1" session="graphs"
import matplotlib.pyplot as plt # markdown-exec: hide
from docs.utils import fig_to_html # markdown-exec: hide
graph.draw()
fig = graph.draw(return_fig = True) # markdown-exec: hide
plt.tight_layout() # markdown-exec: hide
print(fig_to_html(fig)) # markdown-exec: hide
```
