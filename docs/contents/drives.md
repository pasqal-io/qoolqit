# Writing the drive Hamiltonian

The `Drive` is a composition of waveforms defining the drive Hamiltonian.

```python exec="on" source="material-block" result="json" session="drives"
from qoolqit import Constant, Ramp
from qoolqit import Drive

# Defining two waveforms
wf0 = Constant(0.5, 1.0) >> Ramp(1.0, 0.0, 0.5)
wf1 = Ramp(2.0, -1.0, 1.0) >> Constant(1.0, 1.0)

# Defining the drive
drive = Drive(
    amplitude = wf0,
    detuning = wf1
)

# Expanding the drive through composition
drive = drive >> drive

print(drive)  # markdown-exec: hide
```

```python exec="on" source="material-block" html="1" session="drives"
import matplotlib.pyplot as plt # markdown-exec: hide
from docs.utils import fig_to_html # markdown-exec: hide
drive.draw()
fig = drive.draw(return_fig = True) # markdown-exec: hide
plt.tight_layout() # markdown-exec: hide
print(fig_to_html(fig)) # markdown-exec: hide
```
