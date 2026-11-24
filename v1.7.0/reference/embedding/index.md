## embedding

Collection of graph and matrix embedding algorithms.

Modules:

- **`algorithms`** –

  Embedding algorithms and their configurations.
- **`base_embedder`** –

  Base classes for embedders and their configs.
- **`graph_embedder`** –

  Embedders mapping a graph to a graph with coordinates.
- **`matrix_embedder`** –

  Embedders mapping a matrix to a graph with coordinates.

Classes:

- **`BaseEmbedder`** –

  Abstract base class for all embedders.
- **`Blade`** –

  A matrix to graph embedder using the BLaDE algorithm.
- **`BladeConfig`** –

  Configuration parameters to embed with BLaDE.
- **`EmbedderConfig`** –

  Base dataclass for all embedding algorithm configurations.
- **`GraphToGraphEmbedder`** –

  A family of embedders that map a graph to a graph.
- **`InteractionEmbedder`** –

  A matrix to graph embedder using the interaction embedding algorithm.
- **`InteractionEmbedderConfig`** –

  Configuration parameters for the interaction embedding.
- **`MatrixToGraphEmbedder`** –

  A family of embedders that map a matrix to a graph.
- **`SpringLayoutConfig`** –

  Configuration parameters for the spring-layout embedding.
- **`SpringLayoutEmbedder`** –

  A graph to graph embedder using the spring layout algorithm.

### BaseEmbedder

```
BaseEmbedder(algorithm: Callable, config: ConfigType)
```

Abstract base class for all embedders.

An embedder is a function that maps a InDataType to an OutDataType through an embedding algorithm. Parameters of the embedding algorithm can be customized through the EmbedderConfig.

An algorithm should be a standalone function that takes a piece of data of an InDataType and maps it to an OutDataType. Any extra configuration parameters taken as input by the algorithm function should be defined in the config dataclass, inheriting from EmbedderConfig.

Parameters:

- **`algorithm`** (`Callable`) –

  a callable to the algorithm function.
- **`config`** (`ConfigType`) –

  a config dataclass holding parameter values for the algorithm.

Methods:

- **`__repr__`** –

  Return the embedder name, algorithm and config.
- **`embed`** –

  Validates the input, runs the embedding algorithm, and validates the output.
- **`validate_input`** –

  Checks if the given data is compatible with the embedder.
- **`validate_output`** –

  Checks if the resulting output is expected by the embedder.

Attributes:

- **`algorithm`** (`Callable`) –

  Returns the callable to the embedding algorithm.
- **`config`** (`ConfigType`) –

  Returns the config for the embedding algorithm.
- **`info`** (`str`) –

  Prints info about the embedding algorithm.

#### algorithm

```
algorithm: Callable
```

Returns the callable to the embedding algorithm.

#### config

```
config: ConfigType
```

Returns the config for the embedding algorithm.

#### info

```
info: str
```

Prints info about the embedding algorithm.

#### \_\_repr\_\_

```
__repr__() -> str
```

Return the embedder name, algorithm and config.

#### embed

```
embed(data: InDataType) -> OutDataType
```

Validates the input, runs the embedding algorithm, and validates the output.

Parameters:

- **`data`** (`InDataType`) –

  the data to embed.

#### validate\_input

```
validate_input(data: InDataType) -> None
```

Checks if the given data is compatible with the embedder.

Each embedder should write its own data validator. If the data is not of the supported type or in the specific supported format for that embedder, an error should be raised.

Parameters:

- **`data`** (`InDataType`) –

  the data to validate.

Raises:

- `TypeError` –

  if the data is not of the supported type.
- `SomeError` –

  some other error if other constraints are not met.

#### validate\_output

```
validate_output(result: OutDataType) -> None
```

Checks if the resulting output is expected by the embedder.

Each embedder should write its own output validator. If the result is not of the supported type or in the specific supported format for that embedder, an error should be raised.

Parameters:

- **`result`** (`OutDataType`) –

  the output to validate.

Raises:

- `TypeError` –

  if the output is not of the supported type.
- `SomeError` –

  some other error if other constraints are not met.

### Blade

```
Blade(config: BladeConfig | None = None)
```

A matrix to graph embedder using the BLaDE algorithm.

Parameters:

- **`config`** (`BladeConfig`, default: `None` ) –

  configuration object for the BLaDE algorithm.

Methods:

- **`__repr__`** –

  Return the embedder name, algorithm and config.
- **`embed`** –

  Return a DataGraph with coordinates that embeds the input matrix.
- **`validate_input`** –

  Checks that the data is a square 2D numpy array, symmetric or triangular.
- **`validate_output`** –

  Checks if the resulting output is expected by the embedder.

Attributes:

- **`algorithm`** (`Callable`) –

  Returns the callable to the embedding algorithm.
- **`config`** (`ConfigType`) –

  Returns the config for the embedding algorithm.
- **`info`** (`str`) –

  Prints info about the embedding algorithm.

#### algorithm

```
algorithm: Callable
```

Returns the callable to the embedding algorithm.

#### config

```
config: ConfigType
```

Returns the config for the embedding algorithm.

#### info

```
info: str
```

Prints info about the embedding algorithm.

#### \_\_repr\_\_

```
__repr__() -> str
```

Return the embedder name, algorithm and config.

#### embed

```
embed(data: ndarray) -> DataGraph
```

Return a DataGraph with coordinates that embeds the input matrix.

Validates the input, runs the embedding algorithm, and validates the output.

Parameters:

- **`data`** (`ndarray`) –

  the matrix to embed into a DataGraph with coordinates.

#### validate\_input

```
validate_input(data: ndarray) -> None
```

Checks that the data is a square 2D numpy array, symmetric or triangular.

Raises:

- `TypeError` –

  if `data` is not a numpy array.
- `ValueError` –

  if `data` is not square 2D, or neither symmetric nor triangular.

#### validate\_output

```
validate_output(result: DataGraph) -> None
```

Checks if the resulting output is expected by the embedder.

Each embedder should write its own output validator. If the result is not of the supported type or in the specific supported format for that embedder, an error should be raised.

Parameters:

- **`result`** (`OutDataType`) –

  the output to validate.

Raises:

- `TypeError` –

  if the output is not of the supported type.
- `SomeError` –

  some other error if other constraints are not met.

### BladeConfig

```
BladeConfig(
    max_min_dist_ratio: float | None = None,
    dimensions: tuple[int, ...] = default_dimensions,
    starting_positions: ndarray | None = None,
    pca: bool = default_pca,
    steps_per_round: int = default_steps_per_round,
    compute_weight_relative_threshold: Callable[
        [float], float
    ] = default_compute_weight_relative_threshold,
    compute_max_distance_to_walk: Callable[
        [float, float], float | tuple[float, float, float]
    ] = default_compute_max_distance_to_walk,
    compute_regulation_cursor: Callable[
        [float], float
    ] = default_compute_regulation_cursor,
    compute_ratio_step_factors: Callable[
        [float], float
    ] = default_compute_ratio_step_factors,
    ratio_rerun: int = default_ratio_rerun,
    count_symmetric_terms_twice: bool = False,
    device: InitVar[Device | None] = None,
)
```

Configuration parameters to embed with BLaDE.

Methods:

- **`__post_init__`** –

  Post initialization of the `BladeConfig` dataclass.
- **`dict`** –

  Returns the dataclass as a dictionary.

Attributes:

- **`compute_max_distance_to_walk`** (`Callable[[float, float], float | tuple[float, float, float]]`) –

  Function that is called at each step.
- **`compute_ratio_step_factors`** (`Callable[[float], float]`) –

  Function that is called at the boundaries of the rounds.
- **`compute_regulation_cursor`** (`Callable[[float], float]`) –

  Function that is called at each step.
- **`compute_weight_relative_threshold`** (`Callable[[float], float]`) –

  Function that is called at each step.
- **`count_symmetric_terms_twice`** (`bool`) –

  Whether the off-diagonal terms of a symmetric input matrix are counted twice.
- **`dimensions`** (`tuple[int, ...]`) –

  List of numbers of dimensions to explore one after the other.
- **`max_min_dist_ratio`** (`float | None`) –

  If present, sets the maximum radial-to-pairwise distance ratio.
- **`pca`** (`bool`) –

  Whether to apply Principal Component Analysis to prioritize dimensions to keep.
- **`ratio_rerun`** (`int`) –

  Maximum number of retries when the distance ratio constraint is not met.
- **`starting_positions`** (`ndarray | None`) –

  If provided, initial positions to start from.
- **`steps_per_round`** (`int`) –

  Number of elementary steps to perform for each dimension transition.

#### compute\_max\_distance\_to\_walk

```
compute_max_distance_to_walk: Callable[
    [float, float], float | tuple[float, float, float]
] = default_compute_max_distance_to_walk
```

Function that is called at each step.

It takes a float number between 0 and 1 that represents the progress on the steps, and takes another argument that is set to the current largest pairwise distance when `max_min_dist_ratio` is not enabled, otherwise, it is set to the maximum radial distance for the current step. It must return a float number that limits the distances nodes can move at one step (see `update_positions` to learn more).

#### compute\_ratio\_step\_factors

```
compute_ratio_step_factors: Callable[[float], float] = (
    default_compute_ratio_step_factors
)
```

Function that is called at the boundaries of the rounds.

It defines the target ratio to enforce during the evolution. It acts as a multiplying factor on the target ratio.

#### compute\_regulation\_cursor

```
compute_regulation_cursor: Callable[[float], float] = (
    default_compute_regulation_cursor
)
```

Function that is called at each step.

It takes a float number between 0 and 1 that represents the progress on the steps. It must return a float number between 0 (no regulation) and 1 (full regulation) that uniformizes the ability for the forces to achieve their objectives at each step by changing priorities.

#### compute\_weight\_relative\_threshold

```
compute_weight_relative_threshold: Callable[
    [float], float
] = default_compute_weight_relative_threshold
```

Function that is called at each step.

It takes a float number between 0 and 1 that represents the progress on the steps. It must return a float number between 0 and 1 that gives a threshold determining which weights are significant (see `update_positions` to learn more).

#### count\_symmetric\_terms\_twice

```
count_symmetric_terms_twice: bool = False
```

Whether the off-diagonal terms of a symmetric input matrix are counted twice.

If set, the target interaction of the pair (i, j) is `matrix[i, j] + matrix[j, i]`, as in the QUBO convention x^T Q x. By default, they are counted once: a symmetric input matrix is the interaction matrix itself. It has no effect on a triangular input matrix.

#### dimensions

```
dimensions: tuple[int, ...] = default_dimensions
```

List of numbers of dimensions to explore one after the other.

A list with one value is equivalent to a list containing twice the same value. For a 2D embedding, the last value should be 2. Increasing the number of intermediate dimensions can help to escape from local minima.

#### max\_min\_dist\_ratio

```
max_min_dist_ratio: float | None = None
```

If present, sets the maximum radial-to-pairwise distance ratio.

Bounds the ratio between the maximum radial distance and the minimum pairwise distances.

#### pca

```
pca: bool = default_pca
```

Whether to apply Principal Component Analysis to prioritize dimensions to keep.

Applies when transitioning from a space to a space with fewer dimensions. It is disabled by default because it can raise an error when there are too many dimensions compared to the number of nodes.

#### ratio\_rerun

```
ratio_rerun: int = default_ratio_rerun
```

Maximum number of retries when the distance ratio constraint is not met.

Defines how many additional computation steps the algorithm performs, putting priority on satisfying the constraint.

#### starting\_positions

```
starting_positions: ndarray | None = None
```

If provided, initial positions to start from.

Otherwise, random positions will be generated. The number of dimensions of the starting positions must be lower than or equal to the first dimension to explore. If it is lower, it is added dimensions filled with random values.

#### steps\_per\_round

```
steps_per_round: int = default_steps_per_round
```

Number of elementary steps to perform for each dimension transition.

At each step, move vectors are computed and applied on the nodes.

#### \_\_post\_init\_\_

```
__post_init__(device: Device | None) -> None
```

Post initialization of the `BladeConfig` dataclass.

Set the `max_min_dist_ratio` argument of the `blade_embedding` algorithm based on the specification of the selected device.

Parameters:

- **`device`** (`Device`) –

  the QoolQit device to use to set the maximum ratio between the maximum radial distance and the minimum pairwise distance between atoms.

#### dict

```
dict() -> dict
```

Returns the dataclass as a dictionary.

### EmbedderConfig

```
EmbedderConfig()
```

Base dataclass for all embedding algorithm configurations.

Subclasses define parameters specific to their algorithms. Each config should define fields that directly translate to arguments in the respective embedding function it configures.

Methods:

- **`dict`** –

  Returns the dataclass as a dictionary.

#### dict

```
dict() -> dict
```

Returns the dataclass as a dictionary.

### GraphToGraphEmbedder

```
GraphToGraphEmbedder(
    algorithm: Callable, config: ConfigType
)
```

A family of embedders that map a graph to a graph.

Focused on unit-disk graph embedding, where the goal is to find a set of coordinates for a graph that has no coordinates, such that the final unit-disk edges matches the set of edges in the original graph.

A custom algorithm and configuration can be set at initialization.

An algorithm should be a standalone function that takes a piece of data of an InDataType and maps it to an OutDataType. Any extra configuration parameters taken as input by the algorithm function should be defined in the config dataclass, inheriting from EmbedderConfig.

Parameters:

- **`algorithm`** (`Callable`) –

  a callable to the algorithm function.
- **`config`** (`ConfigType`) –

  a config dataclass holding parameter values for the algorithm.

Methods:

- **`__repr__`** –

  Return the embedder name, algorithm and config.
- **`embed`** –

  Validates the input, runs the embedding algorithm, and validates the output.
- **`validate_input`** –

  Checks if the given data is compatible with the embedder.
- **`validate_output`** –

  Checks if the resulting output is expected by the embedder.

Attributes:

- **`algorithm`** (`Callable`) –

  Returns the callable to the embedding algorithm.
- **`config`** (`ConfigType`) –

  Returns the config for the embedding algorithm.
- **`info`** (`str`) –

  Prints info about the embedding algorithm.

#### algorithm

```
algorithm: Callable
```

Returns the callable to the embedding algorithm.

#### config

```
config: ConfigType
```

Returns the config for the embedding algorithm.

#### info

```
info: str
```

Prints info about the embedding algorithm.

#### \_\_repr\_\_

```
__repr__() -> str
```

Return the embedder name, algorithm and config.

#### embed

```
embed(data: InDataType) -> OutDataType
```

Validates the input, runs the embedding algorithm, and validates the output.

Parameters:

- **`data`** (`InDataType`) –

  the data to embed.

#### validate\_input

```
validate_input(data: DataGraph) -> None
```

Checks if the given data is compatible with the embedder.

Each embedder should write its own data validator. If the data is not of the supported type or in the specific supported format for that embedder, an error should be raised.

Parameters:

- **`data`** (`InDataType`) –

  the data to validate.

Raises:

- `TypeError` –

  if the data is not of the supported type.
- `SomeError` –

  some other error if other constraints are not met.

#### validate\_output

```
validate_output(result: DataGraph) -> None
```

Checks if the resulting output is expected by the embedder.

Each embedder should write its own output validator. If the result is not of the supported type or in the specific supported format for that embedder, an error should be raised.

Parameters:

- **`result`** (`OutDataType`) –

  the output to validate.

Raises:

- `TypeError` –

  if the output is not of the supported type.
- `SomeError` –

  some other error if other constraints are not met.

### InteractionEmbedder

```
InteractionEmbedder(
    config: InteractionEmbedderConfig | None = None,
)
```

A matrix to graph embedder using the interaction embedding algorithm.

Starting positions are random unless `x0` is set in the config. For reproducible results, set `seed` to an integer:

```
import numpy as np
from qoolqit.embedding import InteractionEmbedder, InteractionEmbedderConfig

matrix = np.array([[0.0, 1.0, 0.5], [1.0, 0.0, 0.2], [0.5, 0.2, 0.0]])
embedder = InteractionEmbedder(InteractionEmbedderConfig(seed=3083257284))
graph = embedder.embed(matrix)
```

Parameters:

- **`config`** (`InteractionEmbedderConfig | None`, default: `None` ) –

  configuration for the interaction embedding. Defaults are used if None.

Methods:

- **`__repr__`** –

  Return the embedder name, algorithm and config.
- **`embed`** –

  Validates the input, runs the embedding algorithm, and validates the output.
- **`validate_input`** –

  Checks that the data is a symmetric 2D numpy array.
- **`validate_output`** –

  Checks if the resulting output is expected by the embedder.

Attributes:

- **`algorithm`** (`Callable`) –

  Returns the callable to the embedding algorithm.
- **`config`** (`ConfigType`) –

  Returns the config for the embedding algorithm.
- **`info`** (`str`) –

  Prints info about the embedding algorithm.

#### algorithm

```
algorithm: Callable
```

Returns the callable to the embedding algorithm.

#### config

```
config: ConfigType
```

Returns the config for the embedding algorithm.

#### info

```
info: str
```

Prints info about the embedding algorithm.

#### \_\_repr\_\_

```
__repr__() -> str
```

Return the embedder name, algorithm and config.

#### embed

```
embed(data: InDataType) -> OutDataType
```

Validates the input, runs the embedding algorithm, and validates the output.

Parameters:

- **`data`** (`InDataType`) –

  the data to embed.

#### validate\_input

```
validate_input(data: ndarray) -> None
```

Checks that the data is a symmetric 2D numpy array.

Raises:

- `TypeError` –

  if `data` is not a numpy array.
- `ValueError` –

  if `data` is not 2D or not symmetric.

#### validate\_output

```
validate_output(result: DataGraph) -> None
```

Checks if the resulting output is expected by the embedder.

Each embedder should write its own output validator. If the result is not of the supported type or in the specific supported format for that embedder, an error should be raised.

Parameters:

- **`result`** (`OutDataType`) –

  the output to validate.

Raises:

- `TypeError` –

  if the output is not of the supported type.
- `SomeError` –

  some other error if other constraints are not met.

### InteractionEmbedderConfig

```
InteractionEmbedderConfig(
    method: str = "Nelder-Mead",
    maxiter: int = 200000,
    tol: float = 1e-08,
    x0: ndarray | None = None,
    seed: int | None = None,
)
```

Configuration parameters for the interaction embedding.

Explicit initial positions, one (x, y) row per node:

```
import numpy as np
from qoolqit.embedding import InteractionEmbedderConfig

x0 = np.array([[0.0, 0.0], [1.0, 0.0], [0.0, 1.0]])
config = InteractionEmbedderConfig(x0=x0)
```

Random initial positions with a fixed seed:

```
from qoolqit.embedding import InteractionEmbedderConfig

config = InteractionEmbedderConfig(seed=3083257284)
```

Initial positions from an external seeded generator:

```
import numpy as np
from qoolqit.embedding import InteractionEmbedderConfig

rng = np.random.default_rng(seed=2754767221)
config = InteractionEmbedderConfig(x0=rng.random((5, 2)))
```

Attributes:

- **`method`** (`str`) –

  optimization method passed to `scipy.optimize.minimize`.
- **`maxiter`** (`int`) –

  maximum number of optimizer iterations.
- **`tol`** (`float`) –

  tolerance for termination.
- **`x0`** (`ndarray | None`) –

  initial node positions, of shape (N, 2) for an N x N matrix. If None, positions are drawn uniformly in \[0, 1), seeded by `seed`.
- **`seed`** (`int | None`) –

  seed for the random initial positions, ignored if `x0` is set. If None, results differ between runs.

Methods:

- **`dict`** –

  Returns the dataclass as a dictionary.

#### dict

```
dict() -> dict
```

Returns the dataclass as a dictionary.

### MatrixToGraphEmbedder

```
MatrixToGraphEmbedder(
    algorithm: Callable, config: ConfigType
)
```

A family of embedders that map a matrix to a graph.

A custom algorithm and configuration can be set at initialization.

An algorithm should be a standalone function that takes a piece of data of an InDataType and maps it to an OutDataType. Any extra configuration parameters taken as input by the algorithm function should be defined in the config dataclass, inheriting from EmbedderConfig.

Parameters:

- **`algorithm`** (`Callable`) –

  a callable to the algorithm function.
- **`config`** (`ConfigType`) –

  a config dataclass holding parameter values for the algorithm.

Methods:

- **`__repr__`** –

  Return the embedder name, algorithm and config.
- **`embed`** –

  Validates the input, runs the embedding algorithm, and validates the output.
- **`validate_input`** –

  Checks that the data is a symmetric 2D numpy array.
- **`validate_output`** –

  Checks if the resulting output is expected by the embedder.

Attributes:

- **`algorithm`** (`Callable`) –

  Returns the callable to the embedding algorithm.
- **`config`** (`ConfigType`) –

  Returns the config for the embedding algorithm.
- **`info`** (`str`) –

  Prints info about the embedding algorithm.

#### algorithm

```
algorithm: Callable
```

Returns the callable to the embedding algorithm.

#### config

```
config: ConfigType
```

Returns the config for the embedding algorithm.

#### info

```
info: str
```

Prints info about the embedding algorithm.

#### \_\_repr\_\_

```
__repr__() -> str
```

Return the embedder name, algorithm and config.

#### embed

```
embed(data: InDataType) -> OutDataType
```

Validates the input, runs the embedding algorithm, and validates the output.

Parameters:

- **`data`** (`InDataType`) –

  the data to embed.

#### validate\_input

```
validate_input(data: ndarray) -> None
```

Checks that the data is a symmetric 2D numpy array.

Raises:

- `TypeError` –

  if `data` is not a numpy array.
- `ValueError` –

  if `data` is not 2D or not symmetric.

#### validate\_output

```
validate_output(result: DataGraph) -> None
```

Checks if the resulting output is expected by the embedder.

Each embedder should write its own output validator. If the result is not of the supported type or in the specific supported format for that embedder, an error should be raised.

Parameters:

- **`result`** (`OutDataType`) –

  the output to validate.

Raises:

- `TypeError` –

  if the output is not of the supported type.
- `SomeError` –

  some other error if other constraints are not met.

### SpringLayoutConfig

```
SpringLayoutConfig(
    iterations: int = 100,
    threshold: float = 0.0001,
    seed: int | None = None,
)
```

Configuration parameters for the spring-layout embedding.

Methods:

- **`dict`** –

  Returns the dataclass as a dictionary.

#### dict

```
dict() -> dict
```

Returns the dataclass as a dictionary.

### SpringLayoutEmbedder

```
SpringLayoutEmbedder(
    config: SpringLayoutConfig | None = None,
)
```

A graph to graph embedder using the spring layout algorithm.

Methods:

- **`__repr__`** –

  Return the embedder name, algorithm and config.
- **`embed`** –

  Validates the input, runs the embedding algorithm, and validates the output.
- **`validate_input`** –

  Checks if the given data is compatible with the embedder.
- **`validate_output`** –

  Checks if the resulting output is expected by the embedder.

Attributes:

- **`algorithm`** (`Callable`) –

  Returns the callable to the embedding algorithm.
- **`config`** (`ConfigType`) –

  Returns the config for the embedding algorithm.
- **`info`** (`str`) –

  Prints info about the embedding algorithm.

#### algorithm

```
algorithm: Callable
```

Returns the callable to the embedding algorithm.

#### config

```
config: ConfigType
```

Returns the config for the embedding algorithm.

#### info

```
info: str
```

Prints info about the embedding algorithm.

#### \_\_repr\_\_

```
__repr__() -> str
```

Return the embedder name, algorithm and config.

#### embed

```
embed(data: InDataType) -> OutDataType
```

Validates the input, runs the embedding algorithm, and validates the output.

Parameters:

- **`data`** (`InDataType`) –

  the data to embed.

#### validate\_input

```
validate_input(data: DataGraph) -> None
```

Checks if the given data is compatible with the embedder.

Each embedder should write its own data validator. If the data is not of the supported type or in the specific supported format for that embedder, an error should be raised.

Parameters:

- **`data`** (`InDataType`) –

  the data to validate.

Raises:

- `TypeError` –

  if the data is not of the supported type.
- `SomeError` –

  some other error if other constraints are not met.

#### validate\_output

```
validate_output(result: DataGraph) -> None
```

Checks if the resulting output is expected by the embedder.

Each embedder should write its own output validator. If the result is not of the supported type or in the specific supported format for that embedder, an error should be raised.

Parameters:

- **`result`** (`OutDataType`) –

  the output to validate.

Raises:

- `TypeError` –

  if the output is not of the supported type.
- `SomeError` –

  some other error if other constraints are not met.
