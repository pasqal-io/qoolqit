# Creating qubit registers

A `Register` defines the qubit resources to be used by a quantum program.

```python exec="on" source="material-block" result="json" session="registers"
from qoolqit import Register

qubits = {
    0: (-0.5, -0.5),
    1: (-0.5, 0.5),
    2: (0.5, -0.5),
    3: (0.5, 0.5),
}

register = Register(qubits)

print(register)  # markdown-exec: hide
```

It can be instantiated from a list of coordinates.

```python exec="on" source="material-block" html="1" session="registers"

coords = [(-0.5, -0.5), (-0.5, 0.5), (0.5, -0.5), (0.5, 0.5)]

register = Register.from_coordinates(coords)

import matplotlib.pyplot as plt # markdown-exec: hide
from docs.utils import fig_to_html # markdown-exec: hide
register.draw()
fig = register.draw(return_fig = True) # markdown-exec: hide
print(fig_to_html(fig)) # markdown-exec: hide
```

The distances between all qubits can be directly accessed.

```python exec="on" source="material-block" result="json" session="registers"
register.distances()
print(register.distances())  # markdown-exec: hide
```

The minimum distance can be directly accessed.

```python exec="on" source="material-block" result="json" session="registers"
register.min_distance()
print(register.min_distance())  # markdown-exec: hide
```

The interaction coefficients $1/r_{ij}^6$ can be directly accessed.

```python exec="on" source="material-block" result="json" session="registers"
register.interactions()
print(register.interactions())  # markdown-exec: hide
```
