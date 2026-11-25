## graphs

Graph creation and manipulation in QoolQit.

Modules:

- **`base_graph`** –

  Base graph class on top of NetworkX: coordinates, weights, matrix conversion, unit-disk utils.
- **`data_graph`** –

  Graph structure for problem data, with named topology constructors and PyG interchange.
- **`utils`** –

  Utility functions for graph coordinates and edges.

Classes:

- **`BaseGraph`** –

  Base graph class, directly inheriting from `networkx.Graph`.
- **`DataGraph`** –

  Graph structure to represent problem data.

Functions:

- **`all_node_pairs`** –

  Return all pairs of nodes (u, v) where u \< v.
- **`distances`** –

  Return a dictionary of edge distances.
- **`random_coords`** –

  Generate a random set of node coordinates on a square of side L.
- **`random_edge_list`** –

  Generates a random set of k edges linkings items from a set of nodes.
- **`scale_coords`** –

  Scale the coordinates by a given value.
- **`space_coords`** –

  Spaces the coordinates so the minimum distance is equal to a set spacing.

### BaseGraph

Base graph class, directly inheriting from `networkx.Graph`.

Represents a simple graph (undirected and without self-loops), with optional node coordinates and node/edge weights.

On top of the standard networkx.Graph functionality, adds alternative constructors, node coordinates and weights as first-class attributes, distance and Rydberg-interaction calculations, unit-disk graph analysis, and plotting.

Attributes:

- **`coords`** (`dict`) –

  Dict mapping each node to its 2D coordinate, or None if unset.
- **`node_weights`** (`dict`) –

  Dict mapping each node to its weight, or None if unset.
- **`edge_weights`** (`dict`) –

  Dict mapping each edge to its weight, or None if unset.

> [!NOTE]
>
> Alternative constructors: `from_nodes`, `from_coordinates`, `from_nx`, `from_matrix` (with its inverse `to_matrix`). Coordinates and distances: `coords`, `distances`, `min_distance`, `max_distance`, `rescale_coords`. Unit-disk analysis: `is_ud_graph`, `ud_radius_range`, `ud_edges`, `set_ud_edges`. Rydberg analog model utils: `interactions`, `interaction_matrix`. Plotting: `draw`.

Methods:

- **`distances`** –

  Returns a dictionary of distances for a given set of edges.
- **`draw`** –

  Draw the graph.
- **`from_coordinates`** –

  Construct a base graph from a set of coordinates.
- **`from_matrix`** –

  Constructs a graph from a symmetric square matrix.
- **`from_nodes`** –

  Construct a base graph from a set of nodes.
- **`from_nx`** –

  Convert a NetworkX Graph object into a QoolQit graph instance.
- **`interaction_matrix`** –

  Rydberg model interaction 1/r^6 between pairs of nodes, as a matrix.
- **`interactions`** –

  Rydberg model interaction 1/r^6 between pair of nodes.
- **`is_ud_graph`** –

  Check if the graph is unit-disk.
- **`max_distance`** –

  Returns the maximum distance in the graph.
- **`min_distance`** –

  Returns the minimum distance in the graph.
- **`rescale_coords`** –

  Rescales the node coordinates by a factor.
- **`set_ud_edges`** –

  Reset the set of edges to be equal to the set of unit-disk edges.
- **`to_matrix`** –

  Return the adjacency matrix of this graph.
- **`ud_edges`** –

  Returns the set of edges whose distance is at most the given radius.
- **`ud_radius_range`** –

  Return the range (R\_min, R\_max) where the graph is unit-disk.

#### all\_node\_pairs

```
all_node_pairs: set
```

Return a list of all possible node pairs in the graph.

#### coords

```
coords: dict
```

Return a dictionary of node coordinates.

#### edge\_weights

```
edge_weights: dict
```

Return the dictionary of edge weights.

#### has\_coords

```
has_coords: bool
```

Check if the graph has coordinates on all nodes.

#### has\_edge\_weights

```
has_edge_weights: bool
```

Check if the graph has edge weights on all edges.

#### has\_node\_weights

```
has_node_weights: bool
```

Check if the graph has node weights on all nodes.

#### node\_weights

```
node_weights: dict
```

Return the dictionary of node weights.

#### sorted\_edges

```
sorted_edges: set
```

Returns the set of edges (u, v) such that (u \< v).

#### distances

```
distances(edge_list: Collection | None = None) -> dict
```

Returns a dictionary of distances for a given set of edges.

Distances are calculated directly from the coordinates. Raises an error if there are no coordinates on the graph.

Parameters:

- **`edge_list`** (`Collection | None`, default: `None` ) –

  set of edges.

#### draw

```
draw(ax: Axes | None = None, **kwargs: Any) -> None
```

Draw the graph.

Uses the draw\_networkx function from NetworkX.

Parameters:

- **`ax`** (`Axes | None`, default: `None` ) –

  Axes object to draw on. If None, uses the current Axes.
- **`**kwargs`** (`Any`, default: `{}` ) –

  keyword-arguments to pass to draw\_networkx.

#### from\_coordinates

```
from_coordinates(coords: list | dict) -> Self
```

Construct a base graph from a set of coordinates.

Parameters:

- **`coords`** (`list | dict`) –

  list or dictionary of coordinate pairs.

#### from\_matrix

```
from_matrix(data: NDArray[float64]) -> Self
```

Constructs a graph from a symmetric square matrix.

The diagonal values are set as the node weights. For each entry (i, j) where M\[i, j\] != 0 an edge (i, j) is added to the graph and the value M\[i, j\] is set as its weight.

Parameters:

- **`data`** (`NDArray[float64]`) –

  real symmetric square matrix.

#### from\_nodes

```
from_nodes(nodes: Iterable) -> Self
```

Construct a base graph from a set of nodes.

Parameters:

- **`nodes`** (`Iterable`) –

  set of nodes.

#### from\_nx

```
from_nx(g: Graph) -> Self
```

Convert a NetworkX Graph object into a QoolQit graph instance.

The input `networkx.Graph` graph must be defined only with the following allowed

**Node attributes**

pos (tuple): represents the node 2D position. Must be a list/tuple of real numbers. weight: represents the node weight. Must be a real number.

Edge attributes: weight: represents the edge weight. Must be a real number.

**Returns an instance of the class with following attributes**

- node\_weights : dict\[node, float or None\]
- edge\_weights : dict\[(u,v), float or None\]
- coords : dict\[node, (float,float) or None\]

#### interaction\_matrix

```
interaction_matrix() -> ndarray
```

Rydberg model interaction 1/r^6 between pairs of nodes, as a matrix.

Node ordering follows `self.nodes` insertion order. The diagonal is 0, since there is no self-interaction.

Returns:

- `ndarray` –

  Symmetric N x N matrix of dtype float64, where N is the number of nodes.

#### interactions

```
interactions() -> dict
```

Rydberg model interaction 1/r^6 between pair of nodes.

#### is\_ud\_graph

```
is_ud_graph() -> bool
```

Check if the graph is unit-disk.

#### max\_distance

```
max_distance(connected: bool | None = None) -> float
```

Returns the maximum distance in the graph.

Parameters:

- **`connected`** (`bool | None`, default: `None` ) –

  if True/False, computes only over connected/disconnected nodes.

#### min\_distance

```
min_distance(connected: bool | None = None) -> float
```

Returns the minimum distance in the graph.

Parameters:

- **`connected`** (`bool | None`, default: `None` ) –

  if True/False, computes only over connected/disconnected nodes.

#### rescale\_coords

```
rescale_coords(
    *,
    scaling: float | None = None,
    spacing: float | None = None,
) -> None
```

Rescales the node coordinates by a factor.

Accepts either a scaling or a spacing factor.

Parameters:

- **`scaling`** (`float | None`, default: `None` ) –

  value to scale by.
- **`spacing`** (`float | None`, default: `None` ) –

  value to set as the minimum distance in the graph.

#### set\_ud\_edges

```
set_ud_edges(radius: float) -> None
```

Reset the set of edges to be equal to the set of unit-disk edges.

Parameters:

- **`radius`** (`float`) –

  the radius to use in determining the set of unit-disk edges.

#### to\_matrix

```
to_matrix() -> NDArray[float64]
```

Return the adjacency matrix of this graph.

The inverse of `from_matrix`. Nodes are mapped to indices 0, ..., N-1 according to `self.nodes` insertion order. - Node weights are stored in the diagonal since self-loops are not supported. Nodes with no weight set (None) are left at 0.0 in the diagonal. - For each edge (i, j), the entries (i,j) and (j,i) are set to its weight, or to 1.0 if the edge has no weight set.

Returns:

- `NDArray[float64]` –

  Symmetric N x N matrix of dtype float64, where N is the number of nodes.

#### ud\_edges

```
ud_edges(radius: float, tol: float = 1e-07) -> set
```

Returns the set of edges whose distance is at most the given radius.

Parameters:

- **`radius`** (`float`) –

  the unit-disk radius; a pair of nodes is included if their distance is at most this value.
- **`tol`** (`float`, default: `1e-07` ) –

  numerical tolerance added to the radius to account for floating point error.

#### ud\_radius\_range

```
ud_radius_range() -> tuple
```

Return the range (R\_min, R\_max) where the graph is unit-disk.

The graph is unit-disk if the maximum distance between all connected nodes is smaller than the minimum distance between disconnected nodes. This means that for any value R in that interval, the following condition is true:

graph.ud\_edges(radius = R) == graph.sorted edges

### DataGraph

Graph structure to represent problem data.

Represents a simple graph (undirected and without self-loops), with node coordinates and node/edge weights, distance and Rydberg-interaction calculations, conversion to/from adjacency matrix, unit-disk graph analysis, and plotting (inherited from BaseGraph). Adds named topology constructors and conversion to/from PyTorch Geometric data objects.

Attributes:

- **`coords`** (`dict`) –

  Dict mapping each node to its 2D coordinate, or None if unset.
- **`node_weights`** (`dict`) –

  Dict mapping each node to its weight, or None if unset.
- **`edge_weights`** (`dict`) –

  Dict mapping each edge to its weight, or None if unset.

> [!NOTE]
>
> Named topology constructors: `line`, `circle`, `triangular`, `hexagonal`, `heavy_hexagonal`, `square`, `random_er`, `random_ud`. PyTorch Geometric conversion: `from_pyg`, `to_pyg`.

Methods:

- **`circle`** –

  Constructs a circle graph, with the respective coordinates.
- **`distances`** –

  Returns a dictionary of distances for a given set of edges.
- **`draw`** –

  Draw the graph.
- **`from_coordinates`** –

  Construct a base graph from a set of coordinates.
- **`from_matrix`** –

  Constructs a graph from a symmetric square matrix.
- **`from_nodes`** –

  Construct a base graph from a set of nodes.
- **`from_nx`** –

  Convert a NetworkX Graph object into a QoolQit graph instance.
- **`from_pyg`** –

  Convert a PyTorch Geometric Data object into a DataGraph instance.
- **`heavy_hexagonal`** –

  Constructs a heavy-hexagonal lattice graph, with respective coordinates.
- **`hexagonal`** –

  Constructs a hexagonal lattice graph, with respective coordinates.
- **`interaction_matrix`** –

  Rydberg model interaction 1/r^6 between pairs of nodes, as a matrix.
- **`interactions`** –

  Rydberg model interaction 1/r^6 between pair of nodes.
- **`is_ud_graph`** –

  Check if the graph is unit-disk.
- **`line`** –

  Constructs a line graph, with the respective coordinates.
- **`max_distance`** –

  Returns the maximum distance in the graph.
- **`min_distance`** –

  Returns the minimum distance in the graph.
- **`random_er`** –

  Constructs an Erdős-Rényi random graph.
- **`random_ud`** –

  Constructs a random unit-disk graph.
- **`rescale_coords`** –

  Rescales the node coordinates by a factor.
- **`set_ud_edges`** –

  Reset the set of edges to be equal to the set of unit-disk edges.
- **`square`** –

  Constructs a square lattice graph, with respective coordinates.
- **`to_matrix`** –

  Return the adjacency matrix of this graph.
- **`to_pyg`** –

  Convert the DataGraph to a PyTorch Geometric Data object.
- **`triangular`** –

  Constructs a triangular lattice graph, with respective coordinates.
- **`ud_edges`** –

  Returns the set of edges whose distance is at most the given radius.
- **`ud_radius_range`** –

  Return the range (R\_min, R\_max) where the graph is unit-disk.

#### all\_node\_pairs

```
all_node_pairs: set
```

Return a list of all possible node pairs in the graph.

#### coords

```
coords: dict
```

Return a dictionary of node coordinates.

#### edge\_weights

```
edge_weights: dict
```

Return the dictionary of edge weights.

#### has\_coords

```
has_coords: bool
```

Check if the graph has coordinates on all nodes.

#### has\_edge\_weights

```
has_edge_weights: bool
```

Check if the graph has edge weights on all edges.

#### has\_node\_weights

```
has_node_weights: bool
```

Check if the graph has node weights on all nodes.

#### node\_weights

```
node_weights: dict
```

Return the dictionary of node weights.

#### sorted\_edges

```
sorted_edges: set
```

Returns the set of edges (u, v) such that (u \< v).

#### circle

```
circle(
    n: int, spacing: float = 1.0, center: tuple = (0.0, 0.0)
) -> DataGraph
```

Constructs a circle graph, with the respective coordinates.

Parameters:

- **`n`** (`int`) –

  number of nodes.
- **`spacing`** (`float`, default: `1.0` ) –

  distance between each node.
- **`center`** (`tuple`, default: `(0.0, 0.0)` ) –

  point (x, y) to set as the center of the graph.

#### distances

```
distances(edge_list: Collection | None = None) -> dict
```

Returns a dictionary of distances for a given set of edges.

Distances are calculated directly from the coordinates. Raises an error if there are no coordinates on the graph.

Parameters:

- **`edge_list`** (`Collection | None`, default: `None` ) –

  set of edges.

#### draw

```
draw(ax: Axes | None = None, **kwargs: Any) -> None
```

Draw the graph.

Uses the draw\_networkx function from NetworkX.

Parameters:

- **`ax`** (`Axes | None`, default: `None` ) –

  Axes object to draw on. If None, uses the current Axes.
- **`**kwargs`** (`Any`, default: `{}` ) –

  keyword-arguments to pass to draw\_networkx.

#### from\_coordinates

```
from_coordinates(coords: list | dict) -> Self
```

Construct a base graph from a set of coordinates.

Parameters:

- **`coords`** (`list | dict`) –

  list or dictionary of coordinate pairs.

#### from\_matrix

```
from_matrix(data: NDArray[float64]) -> Self
```

Constructs a graph from a symmetric square matrix.

The diagonal values are set as the node weights. For each entry (i, j) where M\[i, j\] != 0 an edge (i, j) is added to the graph and the value M\[i, j\] is set as its weight.

Parameters:

- **`data`** (`NDArray[float64]`) –

  real symmetric square matrix.

#### from\_nodes

```
from_nodes(nodes: Iterable) -> Self
```

Construct a base graph from a set of nodes.

Parameters:

- **`nodes`** (`Iterable`) –

  set of nodes.

#### from\_nx

```
from_nx(g: Graph) -> Self
```

Convert a NetworkX Graph object into a QoolQit graph instance.

The input `networkx.Graph` graph must be defined only with the following allowed

**Node attributes**

pos (tuple): represents the node 2D position. Must be a list/tuple of real numbers. weight: represents the node weight. Must be a real number.

Edge attributes: weight: represents the edge weight. Must be a real number.

**Returns an instance of the class with following attributes**

- node\_weights : dict\[node, float or None\]
- edge\_weights : dict\[(u,v), float or None\]
- coords : dict\[node, (float,float) or None\]

#### from\_pyg

```
from_pyg(
    data: Data,
    node_attrs: Iterable[str] | None = None,
    edge_attrs: Iterable[str] | None = None,
    graph_attrs: Iterable[str] | None = None,
    node_weights_attr: str | None = None,
    edge_weights_attr: str | None = None,
) -> DataGraph
```

Convert a PyTorch Geometric Data object into a DataGraph instance.

Requires `torch_geometric`. Uses `to_networkx` internally.

**Default attributes copied (if present on** `data` **):**

- Node: `x`, `pos` (`pos` is also stored in `coords`)
- Edge: `edge_attr`
- Graph: `y`

Use `node_attrs`, `edge_attrs`, `graph_attrs` for extras.

**QoolQit weights** (`node_weights`, `edge_weights`) are not populated automatically — use the explicit parameters:

- `node_weights_attr`: real-valued tensor of shape `(N,)` or `(N, 1)`. Defaults to `None`.
- `edge_weights_attr`: real-valued tensor of shape `(E,)` or `(E, 1)` where `E = edge_index.shape[1]` (directed count). Defaults to `None`.

The weight attribute is also stored as a regular node/edge attribute.

Parameters:

- **`data`** (`Data`) –

  PyTorch Geometric Data object to convert.
- **`node_attrs`** (`Iterable[str] | None`, default: `None` ) –

  extra node attributes to copy (beyond x and pos).
- **`edge_attrs`** (`Iterable[str] | None`, default: `None` ) –

  extra edge attributes to copy (beyond edge\_attr).
- **`graph_attrs`** (`Iterable[str] | None`, default: `None` ) –

  extra graph-level attributes to copy (beyond y).
- **`node_weights_attr`** (`str | None`, default: `None` ) –

  Data attribute to use as node weights.
- **`edge_weights_attr`** (`str | None`, default: `None` ) –

  Data attribute to use as edge weights.

Returns:

- `DataGraph` –

  DataGraph with `coords`, `node_weights`, `edge_weights`
- `DataGraph` –

  populated where applicable.

Raises:

- `ImportError` –

  if `torch_geometric` is not installed.
- `TypeError` –

  if `data` is not a `torch_geometric.data.Data` instance, or if a weight attribute is not a `torch.Tensor`.
- `AttributeError` –

  if a specified weight attribute is missing.
- `ValueError` –

  if a weight tensor has an incompatible shape or size.

#### heavy\_hexagonal

```
heavy_hexagonal(
    m: int, n: int, spacing: float = 1.0
) -> DataGraph
```

Constructs a heavy-hexagonal lattice graph, with respective coordinates.

Parameters:

- **`m`** (`int`) –

  Number of rows of hexagons.
- **`n`** (`int`) –

  Number of columns of hexagons.
- **`spacing`** (`float`, default: `1.0` ) –

  The distance between adjacent nodes on the final lattice.

**Notes**

The heavy-hexagonal lattice is a regular hexagonal lattice where each edge is decorated with an additional lattice site.

#### hexagonal

```
hexagonal(
    m: int, n: int, spacing: float = 1.0
) -> DataGraph
```

Constructs a hexagonal lattice graph, with respective coordinates.

Parameters:

- **`m`** (`int`) –

  Number of rows of hexagons.
- **`n`** (`int`) –

  Number of columns of hexagons.
- **`spacing`** (`float`, default: `1.0` ) –

  The distance between adjacent nodes on the final lattice.

#### interaction\_matrix

```
interaction_matrix() -> ndarray
```

Rydberg model interaction 1/r^6 between pairs of nodes, as a matrix.

Node ordering follows `self.nodes` insertion order. The diagonal is 0, since there is no self-interaction.

Returns:

- `ndarray` –

  Symmetric N x N matrix of dtype float64, where N is the number of nodes.

#### interactions

```
interactions() -> dict
```

Rydberg model interaction 1/r^6 between pair of nodes.

#### is\_ud\_graph

```
is_ud_graph() -> bool
```

Check if the graph is unit-disk.

#### line

```
line(n: int, spacing: float = 1.0) -> DataGraph
```

Constructs a line graph, with the respective coordinates.

Parameters:

- **`n`** (`int`) –

  number of nodes.
- **`spacing`** (`float`, default: `1.0` ) –

  distance between each node.

#### max\_distance

```
max_distance(connected: bool | None = None) -> float
```

Returns the maximum distance in the graph.

Parameters:

- **`connected`** (`bool | None`, default: `None` ) –

  if True/False, computes only over connected/disconnected nodes.

#### min\_distance

```
min_distance(connected: bool | None = None) -> float
```

Returns the minimum distance in the graph.

Parameters:

- **`connected`** (`bool | None`, default: `None` ) –

  if True/False, computes only over connected/disconnected nodes.

#### random\_er

```
random_er(
    n: int, p: float, seed: int | None = None
) -> DataGraph
```

Constructs an Erdős-Rényi random graph.

Parameters:

- **`n`** (`int`) –

  number of nodes.
- **`p`** (`float`) –

  probability that any two nodes connect.
- **`seed`** (`int | None`, default: `None` ) –

  random seed.

#### random\_ud

```
random_ud(
    n: int, radius: float = 1.0, L: float | None = None
) -> DataGraph
```

Constructs a random unit-disk graph.

The nodes are sampled uniformly from a square of size (L x L). If L is not given, it is estimated based on a rough heuristic that of packing N nodes on a square of side L such that the expected minimum distance is R, leading to L \~ (R / 2) \* sqrt(π \* n).

Parameters:

- **`n`** (`int`) –

  number of nodes.
- **`radius`** (`float`, default: `1.0` ) –

  radius to use for defining the unit-disk edges.
- **`L`** (`float | None`, default: `None` ) –

  size of the square on which to sample the node coordinates.

#### rescale\_coords

```
rescale_coords(
    *,
    scaling: float | None = None,
    spacing: float | None = None,
) -> None
```

Rescales the node coordinates by a factor.

Accepts either a scaling or a spacing factor.

Parameters:

- **`scaling`** (`float | None`, default: `None` ) –

  value to scale by.
- **`spacing`** (`float | None`, default: `None` ) –

  value to set as the minimum distance in the graph.

#### set\_ud\_edges

```
set_ud_edges(radius: float) -> None
```

Reset the set of edges to be equal to the set of unit-disk edges.

#### square

```
square(m: int, n: int, spacing: float = 1.0) -> DataGraph
```

Constructs a square lattice graph, with respective coordinates.

Parameters:

- **`m`** (`int`) –

  Number of rows of square.
- **`n`** (`int`) –

  Number of columns of square.
- **`spacing`** (`float`, default: `1.0` ) –

  The distance between adjacent nodes on the final lattice.

#### to\_matrix

```
to_matrix() -> NDArray[float64]
```

Return the adjacency matrix of this graph.

The inverse of `from_matrix`. Nodes are mapped to indices 0, ..., N-1 according to `self.nodes` insertion order. - Node weights are stored in the diagonal since self-loops are not supported. Nodes with no weight set (None) are left at 0.0 in the diagonal. - For each edge (i, j), the entries (i,j) and (j,i) are set to its weight, or to 1.0 if the edge has no weight set.

Returns:

- `NDArray[float64]` –

  Symmetric N x N matrix of dtype float64, where N is the number of nodes.

#### to\_pyg

```
to_pyg(
    node_attrs: Iterable[str] | None = None,
    edge_attrs: Iterable[str] | None = None,
    graph_attrs: Iterable[str] | None = None,
    node_weights_attr: str = "weight",
    edge_weights_attr: str = "edge_weight",
) -> Data
```

Convert the DataGraph to a PyTorch Geometric Data object.

Requires `torch_geometric`. Uses `from_networkx` internally.

**Default attributes exported (if present on the graph):**

- Node `"x"` → `data.x`; Edge `"edge_attr"` → `data.edge_attr`
- Graph `"y"` → `data.y`

Use `node_attrs`, `edge_attrs`, `graph_attrs` for extras.

**QoolQit internal dicts exported when populated:**

- `coords` → `data.pos` (float64, shape `(N, 2)`)
- `node_weights` → `data.<node_weights_attr>` (float64, shape `(N,)`). Defaults to `"weight"`.
- `edge_weights` → `data.<edge_weights_attr>` (float64, shape `(2*E,)`). Defaults to `"edge_weight"`.

Parameters:

- **`node_attrs`** (`Iterable[str] | None`, default: `None` ) –

  extra node attributes to export (beyond x).
- **`edge_attrs`** (`Iterable[str] | None`, default: `None` ) –

  extra edge attributes to export (beyond edge\_attr).
- **`graph_attrs`** (`Iterable[str] | None`, default: `None` ) –

  extra graph-level attributes to export (beyond y).
- **`node_weights_attr`** (`str`, default: `'weight'` ) –

  Data attribute name for node weights. Defaults to `"weight"`.
- **`edge_weights_attr`** (`str`, default: `'edge_weight'` ) –

  Data attribute name for edge weights. Defaults to `"edge_weight"`.

Returns:

- `Data` –

  PyTorch Geometric Data object.

Raises:

- `ImportError` –

  if `torch_geometric` is not installed.

#### triangular

```
triangular(
    m: int, n: int, spacing: float = 1.0
) -> DataGraph
```

Constructs a triangular lattice graph, with respective coordinates.

Parameters:

- **`m`** (`int`) –

  Number of rows of triangles.
- **`n`** (`int`) –

  Number of columns of triangles.
- **`spacing`** (`float`, default: `1.0` ) –

  The distance between adjacent nodes on the final lattice.

#### ud\_edges

```
ud_edges(radius: float, tol: float = 1e-07) -> set
```

Returns the set of edges whose distance is at most the given radius.

Parameters:

- **`radius`** (`float`) –

  the unit-disk radius; a pair of nodes is included if their distance is at most this value.
- **`tol`** (`float`, default: `1e-07` ) –

  numerical tolerance added to the radius to account for floating point error.

#### ud\_radius\_range

```
ud_radius_range() -> tuple
```

Return the range (R\_min, R\_max) where the graph is unit-disk.

The graph is unit-disk if the maximum distance between all connected nodes is smaller than the minimum distance between disconnected nodes. This means that for any value R in that interval, the following condition is true:

graph.ud\_edges(radius = R) == graph.sorted edges

### all\_node\_pairs

```
all_node_pairs(nodes: Iterable) -> set
```

Return all pairs of nodes (u, v) where u \< v.

Parameters:

- **`nodes`** (`Iterable`) –

  set of node indices.

### distances

```
distances(coords: dict, edge_list: Iterable) -> dict
```

Return a dictionary of edge distances.

Parameters:

- **`coords`** (`dict`) –

  dictionary of node coordinates.
- **`edge_list`** (`Iterable`) –

  edge list to compute the distances for.

### random\_coords

```
random_coords(n: int, L: float = 1.0) -> list
```

Generate a random set of node coordinates on a square of side L.

Parameters:

- **`n`** (`int`) –

  number of coordinate pairs to generate.
- **`L`** (`float`, default: `1.0` ) –

  side of the square.

### random\_edge\_list

```
random_edge_list(nodes: Iterable, k: int) -> list
```

Generates a random set of k edges linkings items from a set of nodes.

### scale\_coords

```
scale_coords(coords: dict, scaling: float) -> dict
```

Scale the coordinates by a given value.

Parameters:

- **`coords`** (`dict`) –

  dictionary of node coordinates.
- **`scaling`** (`float`) –

  value to scale by.

### space\_coords

```
space_coords(coords: dict, spacing: float) -> dict
```

Spaces the coordinates so the minimum distance is equal to a set spacing.

Parameters:

- **`coords`** (`dict`) –

  dictionary of node coordinates.
- **`spacing`** (`float`) –

  value to set as minimum distance.
