In this section, you will learn how to:

- understand how problem graphs are mapped onto the analog Rydberg device through embedding,
- use QoolQit embedders to transform graphs into physically realizable configurations,
- test whether an embedding satisfies hardware constraints (e.g. unit-disk condition),
- convert embedded graphs into qubit registers.

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

All the available embedders are listed in [Available embedders](./available_embedders/index.md).

For more details on the definition of custom embedders the reader can refer to [Custom embedders](../extended_usage/custom_embedders.md).
