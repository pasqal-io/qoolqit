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

## Compiler profiles

In the example above the `AnalogDevice` was used, and no changes were made to the unit converter. As such, the default was used, which sets the reference energy unit as the maximum amplitude, as described in the [Devices page](devices.md).

When a QoolQit program is compiled to Pulser, several compiler profiles can be used. You can check them in the following enumeration:

```python exec="on" source="material-block" result="json" session="drives"
from qoolqit import CompilerProfile

print(CompilerProfile)
```

By defaul `CompilerProfile.DEFAULT` is used, which directly takes the unit converter present in the device and uses it when converting the values.

Other compiler profiles will ignore the unit converter present in the device and utilize their own logic to determine the best possible conversion to achieve a desired compilation directive.

The `CompilerProfile.MAX_AMPLITUDE` maps whatever is the maximum amplitude in the drive of your QoolQit program to the device's maximum allowed amplitude:
```python exec="on" source="material-block" html="1" session="drives"
program.compile_to(device, profile = CompilerProfile.MAX_AMPLITUDE)
program.draw(compiled = True)
fig_compiled = program.draw(compiled = True, return_fig = True) # markdown-exec: hide
print(fig_to_html(fig_compiled)) # markdown-exec: hide
```

The `CompilerProfile.MAX_DURATION` maps whatever is the duration of your QoolQit program to the device's maximum allowed sequence duration:
```python exec="on" source="material-block" html="1" session="drives"
program.compile_to(device, profile = CompilerProfile.MAX_DURATION)
program.draw(compiled = True)
fig_compiled = program.draw(compiled = True, return_fig = True) # markdown-exec: hide
print(fig_to_html(fig_compiled)) # markdown-exec: hide
```

The `CompilerProfile.MIN_DISTANCE` maps whatever is the minimum distance in the register of your QoolQit program to the device's minimum allowed atom separation:
```python exec="on" source="material-block" result="json" session="drives"
try:
    program.compile_to(device, profile = CompilerProfile.MIN_DISTANCE)
except ValueError as error:
    print(error)
```

In this case, you can see the compilation failed because putting the atoms that close together for this program would require setting an amplitude that is larger than what the device allows.
