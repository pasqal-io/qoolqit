# Writing the drive Hamiltonian

In this page, you will learn how to:

- build a `Drive` from waveform components,
- define amplitude and detuning waveforms,
- compose drives into longer pulse sequences,
- inspect the resulting drive object,
- visualize the drive Hamiltonian.

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
print(fig_to_html(fig)) # markdown-exec: hide
```

## Custom waveforms

Built-in waveforms cover the most common shapes, but any differentiable (or piecewise-smooth)
profile can be realised by subclassing `Waveform`. For a full walkthrough — including concrete
examples and how to use custom waveforms inside a `Drive` — see
[Defining custom waveforms](../extended_usage/custom_waveforms.md).
