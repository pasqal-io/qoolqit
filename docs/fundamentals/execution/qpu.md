## Executing remotely on a QPU

A connection object can also be used to run the program directly on a QPU.
To see the list of available devices, run:

```python exec="on" source="material-block" session="execution"
connection = PasqalCloud()
connection.fetch_available_devices()
print(connection.fetch_available_devices())   # markdown-exec: hide
```

Finally, on a QPU there is no configuration and, as per the properties of the quantum hardware, results will come as a bitstrings counter of length specified by the `runs` parameter.

```python exec="on" source="material-block" session="execution"
from qoolqit.execution import QPU

qpu = QPU(connection=connection, runs=500)
```
