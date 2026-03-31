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

# Creating a quantum program

In this page, you will learn how to:

- create a `QuantumProgram` from a `Register` and a `Drive`,
- check whether a program has already been compiled,
- compile a dimensionless program to a target device,
- inspect the compiled Pulser `Sequence`,
- visualize both the original program and its compiled version.

A `QuantumProgram` combines a `Register` and a `Drive` and serves as the main interface for compilation and execution.

```python exec="on" source="material-block" result="json" session="drives"
from qoolqit import PiecewiseLinear
from qoolqit import Register, Drive, QuantumProgram

# Defining the Drive
wf0 = PiecewiseLinear([1.0, 2.0, 1.0], [0.0, 0.5, 0.5, 0.0])
wf1 = PiecewiseLinear([1.0, 2.0, 1.0], [-1.0, -1.0, 1.0, 1.0])
drive = Drive(amplitude = wf0, detuning = wf1)

# Defining the Register
coords = [(0.0, 0.0), (0.0, 1.0), (1.0, 0.0), (1.0, 1.0)]
register = Register.from_coordinates(coords)

# Creating the Program
program = QuantumProgram(register, drive)
print(program) # markdown-exec: hide
```

At this point, the program has not been compiled to any device. As shown above, this is conveniently displayed
when printing the program. It can also be checked through the `is_compiled` property.

```python exec="on" source="material-block" result="json" session="drives"
program.is_compiled
print(program.is_compiled) # markdown-exec: hide
```

Next, we create a device and compile the program for it. In QoolQit, compilation refers to converting the dimensionless time, energy, and distance values used in the Rydberg analog model into concrete values that execute the same instructions on a Pulser device, while accounting for the device’s units and specific parameters. More detailed information on this conversion is provided in the [Rydberg analog model page](../get_started/qoolqit_model.md).

```python exec="on" source="material-block" result="json" session="drives"
from qoolqit import AnalogDevice

device = AnalogDevice()
program.compile_to(device)
print(program) # markdown-exec: hide
```

Now that the program has been compiled, we can inspect the compiled sequence, which is an instance of a Pulser `Sequence`.

```python exec="on" source="material-block" html="1" session="drives"
pulser_sequence = program.compiled_sequence
```

Finally, we can draw both the original program and the compiled sequence.

```python exec="on" source="material-block" html="1" session="drives"
import matplotlib.pyplot as plt # markdown-exec: hide
from docs.utils import fig_to_html # markdown-exec: hide
program.draw()
fig_original = program.draw(return_fig = True) # markdown-exec: hide
print(fig_to_html(fig_original)) # markdown-exec: hidee
```

```python exec="on" source="material-block" html="1" session="drives"
program.draw(compiled = True)
fig_compiled = program.draw(compiled = True, return_fig = True) # markdown-exec: hide
print(fig_to_html(fig_compiled)) # markdown-exec: hide
```
