# Creating a quantum program

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

Next, we have to choose a device and compile the program for it. In QoolQit, compilation refers to converting the dimensionless time, energy, and distance values used in the Rydberg analog model into concrete values. More detailed information on this conversion is provided in the [Rydberg analog model page](../../get_started/qoolqit_model.md) and in [Compilation](../compilation/index.md)