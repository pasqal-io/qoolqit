## register

Register mapping qubit IDs to 2D coordinates.

Classes:

- **`Register`** –

  A QoolQit register mapping qubit IDs to 2D coordinates.

### Register

```
Register(
    qubits: Mapping[
        str, Sequence[float] | NDArray[float64] | Tensor
    ]
    | Mapping[
        int, Sequence[float] | NDArray[float64] | Tensor
    ],
)
```

A QoolQit register mapping qubit IDs to 2D coordinates.

Examples:

From a dictionary of qubit IDs and coordinates:

```
>>> reg = Register({"a": (0.0, 0.0), "b": (1.0, 0.0), "c": (0.0, 1.0)})
>>> reg = Register({0: (0.0, 0.0), 1: (1.0, 0.0), 2: (0.0, 1.0)})
```

From a list of coordinates (qubit IDs are assigned automatically as strings "0", "1", ...):

```
>>> reg = Register.from_coordinates([(0.0, 0.0), (1.0, 0.0), (0.0, 1.0)])
```

Using numpy arrays as coordinates:

```
>>> import numpy as np
>>> reg = Register({"a": np.array([0.0, 0.0]), "b": np.array([1.0, 0.0])})
```

Using torch tensors as coordinates:

```
>>> import torch
>>> reg = Register({"a": torch.tensor([0.0, 0.0]), "b": torch.tensor([1.0, 0.0])})
```

Parameters:

- **`qubits`** (`Mapping[str, Sequence[float] | NDArray[float64] | Tensor] | Mapping[int, Sequence[float] | NDArray[float64] | Tensor]`) –

  a dictionary of qubits and respective 2D coordinates {q: (x, y), ...}. Each coordinate must be castable to a numpy or torch array of shape (2,).

Raises:

- `TypeError` –

  If `qubits` is not a Mapping.
- `ValueError` –

  If `qubits` dictionary is empty.
- `ValueError` –

  If a qubit coordinate cannot be converted to an array of floats, or if the converted coordinate is not a point in 2D.

Methods:

- **`__len__`** –

  Return the number of qubits.
- **`__repr__`** –

  Return the class name and number of qubits.
- **`circle`** –

  Initializes a Register with qubits arranged in a circle.
- **`distances`** –

  Distance between each qubit pair.
- **`draw`** –

  Draw the register.
- **`from_coordinates`** –

  Initializes a Register from a sequence or array of coordinates.
- **`from_graph`** –

  Initializes a Register from a graph that has coordinates.
- **`interaction_matrix`** –

  Interaction 1/r^6 between each qubit pair, as a matrix (0 on the diagonal).
- **`interactions`** –

  Interaction 1/r^6 between each qubit pair.
- **`line`** –

  Initializes a Register with qubits arranged in a line.
- **`max_radial_distance`** –

  Maximum radial distance between all qubits.
- **`min_distance`** –

  Minimum distance between all qubit pairs.
- **`radial_distances`** –

  Radial distance of each qubit from the origin.
- **`rectangular`** –

  Initializes a rectangular Register of qubits.
- **`square`** –

  Initializes a square Register of qubits.
- **`triangular`** –

  Initializes a triangular lattice Register of qubits.

Attributes:

- **`n_qubits`** (`int`) –

  Number of qubits in the Register.
- **`qubits`** (`dict`) –

  Returns a dictionary of qubits and respective coordinates.
- **`qubits_ids`** (`tuple[str | int, ...]`) –

  Returns the qubit IDs.

#### n\_qubits

```
n_qubits: int
```

Number of qubits in the Register.

#### qubits

```
qubits: dict
```

Returns a dictionary of qubits and respective coordinates.

#### qubits\_ids

```
qubits_ids: tuple[str | int, ...]
```

Returns the qubit IDs.

#### \_\_len\_\_

```
__len__() -> int
```

Return the number of qubits.

#### \_\_repr\_\_

```
__repr__() -> str
```

Return the class name and number of qubits.

#### circle

```
circle(n: int, spacing: float = 1.0) -> Register
```

Initializes a Register with qubits arranged in a circle.

Parameters:

- **`n`** (`int`) –

  number of qubits to place in the circle.
- **`spacing`** (`float`, default: `1.0` ) –

  distance between adjacent qubits. Defaults to 1.0.

#### distances

```
distances() -> dict
```

Distance between each qubit pair.

#### draw

```
draw(
    ax: Axes | None = None,
    marker_size: int = 100,
    node_color: str = "tab:green",
) -> None
```

Draw the register.

Parameters:

- **`ax`** (`Axes | None`, default: `None` ) –

  an optional matplotlib Axes instance to draw on. If None, a new Axes will be created.
- **`marker_size`** (`int`, default: `100` ) –

  size of the qubit markers in points squared. Defaults to 100.
- **`node_color`** (`str`, default: `'tab:green'` ) –

  color of the qubit markers. Defaults to "tab:green".

#### from\_coordinates

```
from_coordinates(
    coords: Sequence[
        Sequence[float] | NDArray[float64] | Tensor
    ]
    | NDArray[float64]
    | Tensor,
) -> Register
```

Initializes a Register from a sequence or array of coordinates.

Qubit IDs are assigned as integers 0,1,...,N-1, where N is the number of coordinates.

Parameters:

- **`coords`** (`Sequence[Sequence[float] | NDArray[float64] | Tensor] | NDArray[float64] | Tensor`) –

  a sequence of 2D coordinates, i.e. \[(x, y), ...\]. Each coordinate must be castable to a numpy or torch array of shape (2,). If `coords` is a numpy array or a torch tensor, it must be 2D and of shape (N, 2).

Raises:

- `TypeError` –

  If `coords` is a Mapping.

#### from\_graph

```
from_graph(graph: DataGraph) -> Register
```

Initializes a Register from a graph that has coordinates.

Parameters:

- **`graph`** (`DataGraph`) –

  a DataGraph instance.

#### interaction\_matrix

```
interaction_matrix() -> NDArray[float64] | Tensor
```

Interaction 1/r^6 between each qubit pair, as a matrix (0 on the diagonal).

#### interactions

```
interactions() -> dict
```

Interaction 1/r^6 between each qubit pair.

#### line

```
line(n: int, spacing: float = 1.0) -> Register
```

Initializes a Register with qubits arranged in a line.

Parameters:

- **`n`** (`int`) –

  number of qubits to place in the line.
- **`spacing`** (`float`, default: `1.0` ) –

  distance between adjacent qubits. Defaults to 1.0.

#### max\_radial\_distance

```
max_radial_distance() -> float
```

Maximum radial distance between all qubits.

#### min\_distance

```
min_distance() -> float
```

Minimum distance between all qubit pairs.

#### radial\_distances

```
radial_distances() -> dict
```

Radial distance of each qubit from the origin.

#### rectangular

```
rectangular(
    rows: int,
    cols: int,
    row_spacing: float = 1.0,
    col_spacing: float = 1.0,
) -> Register
```

Initializes a rectangular Register of qubits.

Parameters:

- **`rows`** (`int`) –

  number of rows in the rectangle.
- **`cols`** (`int`) –

  number of columns in the rectangle.
- **`row_spacing`** (`float`, default: `1.0` ) –

  distance between adjacent qubits in the row direction. Defaults to 1.0.
- **`col_spacing`** (`float`, default: `1.0` ) –

  distance between adjacent qubits in the column direction. Defaults to 1.0.

#### square

```
square(n: int, spacing: float = 1.0) -> Register
```

Initializes a square Register of qubits.

Parameters:

- **`n`** (`int`) –

  number of qubits along each side of the square.
- **`spacing`** (`float`, default: `1.0` ) –

  distance between adjacent qubits. Defaults to 1.0.

#### triangular

```
triangular(
    rows: int, atoms_per_row: int, spacing: float = 1.0
) -> Register
```

Initializes a triangular lattice Register of qubits.

Parameters:

- **`rows`** (`int`) –

  number of rows in the lattice.
- **`atoms_per_row`** (`int`) –

  number of qubits per row.
- **`spacing`** (`float`, default: `1.0` ) –

  distance between adjacent qubits. Defaults to 1.0.
