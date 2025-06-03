# Creating a quantum program

A `QuantumProgram` combines a `Register` and a `Drive` and serves as the main interface for compilation and execution.

```python exec="on" source="material-block" result="json" session="drives"
from qoolqit import PiecewiseLinear
from qoolqit import Register, Drive, QuantumProgram

# Defining the Drive
wf0 = PiecewiseLinear([1.0, 2.0, 1.0], [0.0, 1.0, 1.0, 0.0])
wf1 = PiecewiseLinear([1.0, 2.0, 1.0], [-1.0, -1.0, 1.0, 1.0])
drive = Drive(amplitude = wf0, detuning = wf1)

# Defining the Register
coords = [(0.0, 0.0), (0.0, 1.0), (1.0, 0.0), (1.0, 1.0)]
register = Register.from_coordinates(coords)

# Creating the Program
program = QuantumProgram(register, drive)
print(program) # markdown-exec: hide
```

We can draw the drive to compare it with the compiled sequence later.
```python exec="on" source="material-block" html="1" session="drives"
import matplotlib.pyplot as plt # markdown-exec: hide
from docs.utils import fig_to_html # markdown-exec: hide
program.drive.draw()
fig = program.drive.draw(return_fig = True) # markdown-exec: hide
plt.tight_layout() # markdown-exec: hide
print(fig_to_html(fig)) # markdown-exec: hide
```
At this point, the program has not been compiled to any device. As shown above, this is conveniently displayed
when printing the program. It can also be checked through the `is_compiled` property.

```python exec="on" source="material-block" result="json" session="drives"
program.is_compiled
print(program.is_compiled) # markdown-exec: hide
```

Now we instantiate a device and compile the program to that device.

```python exec="on" source="material-block" result="json" session="drives"
from qoolqit import AnalogDevice

device = AnalogDevice()

program.compile_to(device)

print(program) # markdown-exec: hide
```

Now that the program has been compiled, we can inspect the compiled sequence, which in instance of a Pulser `Sequence`.

```python exec="on" source="material-block" html="1" session="drives"
pulser_sequence = program.compiled_sequence
```

## Compiler profiles
