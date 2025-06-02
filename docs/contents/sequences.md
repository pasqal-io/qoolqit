# Writing the drive Hamiltonian

A `Sequence` is a composition of waveforms defining the drive Hamiltonian.

```python exec="on" source="material-block" result="json" session="sequences"
from qoolqit import Constant, Ramp
from qoolqit import Sequence

# Defining two waveforms
wf0 = Constant(0.5, 1.0) * Ramp(1.0, 0.0, 0.5)
wf1 = Ramp(2.0, -1.0, 1.0) * Constant(1.0, 1.0)

# Defining the sequence
sequence = Sequence(
    amplitude = wf0,
    detuning = wf1
)

# Expanding the sequence through composition
sequence = sequence * sequence

print(sequence)  # markdown-exec: hide
```

```python exec="on" source="material-block" html="1" session="sequences"
import matplotlib.pyplot as plt # markdown-exec: hide
from docs.utils import fig_to_html # markdown-exec: hide
sequence.draw()
fig = sequence.draw(return_fig = True) # markdown-exec: hide
plt.tight_layout() # markdown-exec: hide
print(fig_to_html(fig)) # markdown-exec: hide
```
