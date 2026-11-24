# Defining custom embedders

In this notebook, you will learn how to:

- understand how the embedding module is structured,
- define a custom embedder from a function/algorithm and a config dataclass.

The [available embedders](<https://pasqal-io.github.io/qoolqit/main/fundamentals/embedding/index.md>) page described some pre-defined embedders. The embedding module in QoolQit is designed to be flexible and extendable to various forms of embedding algorithms developed for the Rydberg analog model, with potentially different inputs and outputs, and different configuration parameters. It is structured in three levels:

## Level 1: Concretizing the interface

The `BaseEmbedder` is the abstract base class for all embedders, but it is defined on generic input and output data types. It enforces the interface for all embedders by defining the `info` and `config` properties, as well as the `embed` method. It also defines abstract `validate_input` and `validate_output` methods that must be overridden by subclasses.

## Level 2: Concretizing input/output data

The next level is to define the concrete data types involved in the mapping, thus defining a *family* of embedders. Currently, there are two families of embedders defined in QoolQit:

- `GraphToGraphEmbedder` which concretizes the `BaseEmbedder` with a `DataGraph` input type and a `DataGraph` output type.
- `MatrixToGraphEmbedder` which concretizes the `BaseEmbedder` with a `np.ndarray` input type and a `DataGraph` output type.

In both cases, the `validate_input` and `validate_output` are overridden to check the input and output are of the correct type. In the case of the `MatrixToGraphEmbedder`, conditions on the input matrix are also checked such as if the array has the right dimensions and is symmetric. Still, at this level, no specific embedding algorithm is defined.

In the future, more families of embedders can be defined that may require different input and output data types.

## Level 3: Concretizing the algorithm and config

The final level is defining concrete embedders, such as the ones we have used in the [available embedders page](<https://pasqal-io.github.io/qoolqit/main/fundamentals/embedding/index.md>). Here the requirement is to define a concrete function that maps the input to the output, along with any parameters required, and a config dataclass inheriting from `EmbedderConfig` holding all the configuration parameters.

Let's exemplify the case of defining a custom embedder in the family of graph to graph embedders.

```
from dataclasses import dataclass

from qoolqit.embedding import EmbedderConfig, GraphToGraphEmbedder
from qoolqit.graphs import DataGraph


def my_embedding_function(graph: DataGraph, param1: float) -> DataGraph:
    """Some embedding function that manipulates the input graph.

    This docstring should be clear on the embedding logic, because it will be
    directly accessed by the embedder.info property.

    Args:
        graph: the graph to embed.
        param1: a useless parameter...
    """
    return graph

@dataclass
class MyEmbedderConfig(EmbedderConfig):
    """Configuration holding the parameters of `my_embedding_function`."""

    param1: float = 1.0

embedder = GraphToGraphEmbedder(my_embedding_function, MyEmbedderConfig())
print(embedder)
```

```
GraphToGraphEmbedder:
| Algorithm: my_embedding_function
| Config: MyEmbedderConfig(param1=1.0)
```

It can now be used like any other embedder.

```
print(embedder.info)

embedder.config.param1 = 2.0

graph = DataGraph.random_er(5, 0.5)

embedded_graph = embedder.embed(graph)
```

```
-- Embedding algorithm docstring:

Some embedding function that manipulates the input graph.

This docstring should be clear on the embedding logic, because it will be
directly accessed by the embedder.info property.

Args:
    graph: the graph to embed.
    param1: a useless parameter...
```

To share this embedder or potentially add it to the QoolQit codebase, we might want to create a concrete embedder wrapper that users can easily import.

```
class MyNewEmbedder(GraphToGraphEmbedder):
    """Embedder bundling `my_embedding_function` with its default configuration."""

    def __init__(self):
        """Initialize the embedder with its embedding function and default configuration."""
        super().__init__(my_embedding_function, MyEmbedderConfig())
```

## Automatic validation

To define a custom embedder, the extra arguments in the embedding function (besides the data) must match the fields in the configuration dataclass, otherwise an error will be raised.

```
def my_embedding_function(graph: DataGraph, param1: float) -> DataGraph:
    """Example embedding algorithm: here we return the same graph for simplicity."""
    return graph

@dataclass
class MyWrongConfig(EmbedderConfig):
    """Configuration whose parameters don't match the embedding function's signature."""

    some_other_param: float = 1.0

try:
    wrong_embedder = GraphToGraphEmbedder(my_embedding_function, MyWrongConfig())
except TypeError as error:
    print(error)
```

```
Config MyWrongConfig is not compatible with the algorithm my_embedding_function, as not all configuration fields correspond to keyword arguments in the algorithm function.

Config MyWrongConfig keys:
    - some_other_param

Algorithm signature parameters:
    - graph
    - param1
```

Furthermore, because we are defining an embedder in the `GraphToGraphEmbedder`, the input must be an instance of a `DataGraph`:

```
embedder = GraphToGraphEmbedder(my_embedding_function, MyEmbedderConfig())

try:
    data = 1.0 # Not a DataGraph
    embedded_data = embedder.embed(data)
except TypeError as error:
    print(error)
```

```
Embedding data of type <class 'float'> not supported by this embedder. GraphToGraphEmbedder requires data of type DataGraph.
```

The output of the embedding function must also be a `DataGraph`:

```
def my_wrong_embedding_function(graph: DataGraph, param1: float) -> DataGraph:
    """Invalid embedding function: returns a float instead of a DataGraph."""
    return param1 # Not a DataGraph

embedder = GraphToGraphEmbedder(my_wrong_embedding_function, MyEmbedderConfig())

try:
    graph = DataGraph.random_er(5, 0.5)
    embedded_graph = embedder.embed(graph)
except TypeError as error:
    print(error)
```

```
Expected embedding result to be of type DataGraph, algorithm returned <class 'float'> instead.
```
