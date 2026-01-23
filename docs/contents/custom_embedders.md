# Defining custom embedders

In the [available embedders](available_embedders.md) page you saw the usage of some pre-defined embedders. The embedding module in QoolQit is designed to be flexible and extendable to various forms of embedding algorithms developed for the Rydberg analog model, with potentially different inputs and outputs, and different configuration parameters. It is structured in three levels:

**Level 0: Concretizing the interface**

The `BaseEmbedder` is the abstract base class for all embedders, but it is defined on generic input and output data types. It enforces the interface for all embedders by defining the `info` and `config` properties, as well as the `embed` method. It also defines abstract `validate_input` and `validate_output` methods that must be overwritten by subclasses.

**Level 1: Concretizing the data inputs and data outputs**

The next level is to define the concrete data types involved in the mapping, thus defining a *family* of embedders. Currently, there are two families of embedders defined in QoolQit:

- `GraphToGraphEmbedder` which concretizes the `BaseEmbedder` with a `DataGraph` input type and a `DataGraph` output type.
- `MatrixToGraphEmbedder` which concretizes the `BaseEmbedder` with a `np.ndarray` input type and a `DataGraph` output type.

In both cases, the `validate_input` and `validate_output` are overridden to check the input and output are of the correct type. In the case of the `MatrixToGraphEmbedder` conditions on the input matrix are also checked such as if the array has the right dimensions and is symmetric. Still, at this level, no specific embedding algorithm is defined.

In the future, more families of embedders can be defined that may require different input and output data types.

**Level 2: Concretizing the algorithms and configurations**

The final level is defining concrete embedders, such as the ones we have used in the [available embedders page](available_embedders.md). Here the requirement is to define a concrete function that maps the input to the output, along with any parameters required, and a config dataclass inheriting from `EmbeddingConfig` holding all the configuration parameters. In the previous examples, we used the `SpringLayoutEmbedder` which is a subclass of a `GraphToGraphEmbedder` and the `InteractionEmbedder` which is a subclass of the `MatrixToGraphEmbedder`.

Let's exemplify the case of defining a custom embedder in the family of graph to graph embedders.

```python exec="on" source="material-block" result="json" session="embedding"
from qoolqit.embedding import GraphToGraphEmbedder
from qoolqit.embedding import EmbeddingConfig
from qoolqit import DataGraph
from dataclasses import dataclass

def my_embedding_function(graph: DataGraph, param1: float) -> DataGraph:
    """Some embedding function that manipulates the input graph.

    This docstring should be clear on the embedding logic, because it will be
    directly accessed by the embedder.info property.

    Arguments:
        param1: a useless parameter...
    """
    return graph

@dataclass
class MyEmbeddingConfig(EmbeddingConfig):
    param1: float = 1.0

embedder = GraphToGraphEmbedder(my_embedding_function, MyEmbeddingConfig())
print(embedder) # markdown-exec: hide
```

It can now be used like any other embedder.

```python exec="on" source="material-block" result="json" session="embedding"
print(embedder.info)

embedder.config.param1 = 2.0

graph = DataGraph.random_er(5, 0.5)

embedded_graph = embedder.embed(graph)
```

To share this embedder or potentially add it to the QoolQit codebase, we might want to create a concrete embedder wrapper that users can easily import.

```python exec="on" source="material-block" session="embedding"
class MyNewEmbedder(GraphToGraphEmbedder):
    def __init__(self):
        super().__init__(my_embedding_function, MyEmbeddingConfig())
```

## Automatic validation

To define a custom embedder, the extra arguments in the embedding function (besides the data) must match the fields in the configuration dataclass, otherwise an error will be raised.

```python exec="on" source="material-block" result="json" session="embedding"
def my_embedding_function(graph: DataGraph, param1: float) -> DataGraph:
    return graph

@dataclass
class MyWrongConfig(EmbeddingConfig):
    some_other_param: float = 1.0

try:
    wrong_embedder = GraphToGraphEmbedder(my_embedding_function, MyWrongConfig())
except KeyError as error:
    print(error)
```

Furthermore, because we are defining an embedder in the `GraphToGraphEmbedder` the input must be an instance of a `DataGraph`:

```python exec="on" source="material-block" result="json" session="embedding"
embedder = GraphToGraphEmbedder(my_embedding_function, MyEmbeddingConfig())

try:
    data = 1.0 # Not a DataGraph
    embedded_data = embedder.embed(data)
except TypeError as error:
    print(error)
```

The output of the embedding function must also be a `DataGraph`:

```python exec="on" source="material-block" result="json" session="embedding"
def my_wrong_embedding_function(graph: DataGraph, param1: float) -> DataGraph:
    return param1 # Not a DataGraph

embedder = GraphToGraphEmbedder(my_wrong_embedding_function, MyEmbeddingConfig())

try:
    graph = DataGraph.random_er(5, 0.5)
    embedded_graph = embedder.embed(graph)
except TypeError as error:
    print(error)
```
