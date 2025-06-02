# Creating qubit registers

A `Register` defines the qubit resources to be used by a quantum program.

```python exec="on" source="material-block" result="json" session="registers"
from qoolqit import Register

qubits = {
    0: (0.0, 0.0),
    1: (0.0, 1.0),
    2: (1.0, 0.0),
    3: (1.0, 1.0),
}

register = Register(qubits)

print(register)  # markdown-exec: hide
```

```python exec="on" source="material-block" html="1" session="registers"

coords = [(0.0, 0.0), (0.0, 1.0), (1.0, 0.0), (1.0, 1.0)]

register = Register.from_coordinates(coords)

import matplotlib.pyplot as plt # markdown-exec: hide
from docs.utils import fig_to_html # markdown-exec: hide
register.draw()
fig = register.draw(return_fig = True) # markdown-exec: hide
plt.tight_layout() # markdown-exec: hide
print(fig_to_html(fig)) # markdown-exec: hide
```
