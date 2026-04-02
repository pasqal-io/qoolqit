# Graph constructors

Class constructors can help you create a variety of graphs. A useful constructor is starting from a set of coordinates. By default, it will create an empty set of edges, but we can use the `set_ud_edges` method to specify the edges as the unit-disk intersections.

```python exec="on" source="material-block" html="1" session="graph-constructors"
from qoolqit import DataGraph
import matplotlib.pyplot as plt # markdown-exec: hide
from docs.utils import fig_to_html # markdown-exec: hide

coords = [(-1.0, 0.0), (0.0, 0.0), (1.0, 0.0), (0.0, 1.0), (0.0, -1.0)]

graph = DataGraph.from_coordinates(coords)

assert len(graph.edges) == 0

graph.set_ud_edges(radius = 1.0)

assert len(graph.edges) > 0

fig, ax = plt.subplots(figsize=(4,4), dpi=200) # markdown-exec: hide
graph.draw()
print(fig_to_html(fig)) # markdown-exec: hide
```

Some geometric graph constructors will already have coordinates by default.

## Line
A line graph on n nodes.

```python exec="on" source="material-block" html="1" session="graph-constructors"
from qoolqit import DataGraph # markdown-exec: hide
from docs.utils import fig_to_html # markdown-exec: hide
graph = DataGraph.line(n = 10, spacing = 1.0)
fig, ax = plt.subplots(figsize=(4,4), dpi=200) # markdown-exec: hide
graph.draw()
print(fig_to_html(fig)) # markdown-exec: hide
```

## Circle
A circle graph on n nodes.

```python exec="on" source="material-block" html="1" session="graph-constructors"
from qoolqit import DataGraph # markdown-exec: hide
from docs.utils import fig_to_html # markdown-exec: hide
graph = DataGraph.circle(n = 10, spacing = 1.0, center = (0.0, 0.0))
fig, ax = plt.subplots(figsize=(4,4), dpi=200) # markdown-exec: hide
graph.draw()
print(fig_to_html(fig)) # markdown-exec: hide
```

## Triangular
A triangular lattice graph with m rows and n columns of triangles.

```python exec="on" source="material-block" html="1" session="graph-constructors"
from qoolqit import DataGraph # markdown-exec: hide
from docs.utils import fig_to_html # markdown-exec: hide
graph = DataGraph.triangular(m = 2, n = 2, spacing = 1.0)
fig, ax = plt.subplots(figsize=(4,4), dpi=200) # markdown-exec: hide
graph.draw()
print(fig_to_html(fig)) # markdown-exec: hide
```

### Square
A square lattice graph with m rows and n columns of square.

```python exec="on" source="material-block" html="1" session="graph-constructors"
from qoolqit import DataGraph # markdown-exec: hide
from docs.utils import fig_to_html # markdown-exec: hide
graph = DataGraph.square(m = 2, n = 2, spacing = 1.0)
fig, ax = plt.subplots(figsize=(4,4), dpi=200) # markdown-exec: hide
graph.draw()
print(fig_to_html(fig)) # markdown-exec: hide
```

## Hexagonal
A Hexagonal lattice graph with m rows and n columns of hexagons.

```python exec="on" source="material-block" html="1" session="graph-constructors"
from qoolqit import DataGraph # markdown-exec: hide
from docs.utils import fig_to_html # markdown-exec: hide
graph = DataGraph.hexagonal(m = 2, n = 2, spacing = 1.0)
fig, ax = plt.subplots(figsize=(4,4), dpi=200) # markdown-exec: hide
graph.draw()
print(fig_to_html(fig)) # markdown-exec: hide
```

## Heavy-hexagonal
An Heavy-Hexagonal lattice graph with m rows and n columns of hexagons where each edge is decorated with an additional lattice site.

```python exec="on" source="material-block" html="1" session="graph-constructors"
from qoolqit import DataGraph # markdown-exec: hide
from docs.utils import fig_to_html # markdown-exec: hide
graph = DataGraph.heavy_hexagonal(m = 2, n = 2, spacing = 1.0)
fig, ax = plt.subplots(figsize=(4,4), dpi=200) # markdown-exec: hide
graph.draw()
print(fig_to_html(fig)) # markdown-exec: hide
```

## Random unit-disk
A random unit-disk graph by uniformly sampling points in area of side L.

```python exec="on" source="material-block" html="1" session="graph-constructors"
from qoolqit import DataGraph # markdown-exec: hide
from docs.utils import fig_to_html # markdown-exec: hide
graph = DataGraph.random_ud(n = 10, radius = 1.0, L = 2.0)
fig, ax = plt.subplots(figsize=(4,4), dpi=200) # markdown-exec: hide
graph.draw()
print(fig_to_html(fig)) # markdown-exec: hide
```

Other generic constructors are also available which have no information on node coordinates.

### Erdős–Rényi
A random Erdős–Rényi graph of n nodes.

```python exec="on" source="material-block" html="1" session="graph-constructors"
from qoolqit import DataGraph # markdown-exec: hide
from docs.utils import fig_to_html # markdown-exec: hide
graph = DataGraph.random_er(n = 10, p = 0.5, seed = 1)
fig, ax = plt.subplots(figsize=(4,4), dpi=200) # markdown-exec: hide
graph.draw()
print(fig_to_html(fig)) # markdown-exec: hide
```

## Loading from a matrix

Loading an adjacency matrix into a graph is also possible.

- Given that graphs in QoolQit are undirected, the matrix must be symmetric.
- As in the standard adjacency matrix interpretation, off-diagonal elements are loaded as edge-weights as long as they are non-zero.
- Given that QoolQit does not consider graphs with self-loops, diagonal elements are loaded as node-weights.

```python exec="on" source="material-block" html="1" session="graph-constructors"
import numpy as np

n_nodes = 5
data = np.random.rand(n_nodes, n_nodes)

# Matrix must be symmetric
data = data + data.T

graph = DataGraph.from_matrix(data)

assert graph.has_node_weights
assert graph.has_edge_weights
```

If all values in the diagonal are 0, then no node-weights will be set. Furthermore, edges and edge-weights will only be set for non-zero off-diagonal elements.

```python exec="on" source="material-block" html="1" session="graph-constructors"
# Setting the diagonal to zero
np.fill_diagonal(data, 0.0)

# Removing the value for the pair (1, 2)
data[1, 2] = 0.0
data[2, 1] = 0.0

graph = DataGraph.from_matrix(data)

# Checking there are no node weights and the edge (1, 2) was not added
assert not graph.has_node_weights
assert (1, 2) not in graph.edges
```
