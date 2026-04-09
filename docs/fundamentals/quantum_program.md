 In this page, you will learn how to build a quantum program, from its building blocks:

- Create a `Register` from a set of coordinates,
- Define `Waveforms` selecting amplitude and detuning,
- Build a `Drive` from waveform components,
- Instantiate a `QuantumProgram` from a `Register` and a `Drive`,
- Check whether a program has already been compiled.

---

The QuantumProgram defines the protocol used to solve your problem within the adimensional framework of the [Rydberg Analog model](../get_started/qoolqit_model.md).

In practice, this involves specifying both the interaction and the driving Hamiltonian. In QoolQit, these are set up by creating a `Register`, which determines the positions of the qubits, and a `Drive` object, which describes how laser fields drive the qubits over time.

To run the program on real quantum hardware, the abstract `QuantumProgram` must first be compiled into a form compatible with a specific QPU. This compilation process will be covered later in the [Compilation](./compilation/rationale.md) page.

## Registers

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


## Waveforms

An essential part of writing programs in the Rydberg analog model is to write the time-dependent functions representing the amplitude and detuning terms in the drive Hamiltonian. For that, QoolQit implements a set of waveforms that can be used directly and/or composed together.

### Base waveforms

A full list of the available waveforms can be found in the [API reference][qoolqit.waveforms].

```python exec="on" source="material-block" result="json" session="waveforms"
from qoolqit import Constant, Ramp, Delay

# An empty waveform
wf1 = Delay(1.0)

# A waveform with a constant value
wf2 = Constant(1.0, 2.0)

# A waveform that ramps linearly between two values
wf3 = Ramp(1.0, -1.0, 1.0)


print(wf1)  # markdown-exec: hide
print(wf2)  # markdown-exec: hide
print(wf3)  # markdown-exec: hide
```

As shown above, printing a waveform shows the duration interval over which it applies followed by the description of the waveform.

The first argument is always the `duration` of the waveform, and the remaining arguments depend on the information required by each waveform. The resulting object is a callable that can be evaluated at any time $t$.

```python exec="on" source="material-block" result="json" session="waveforms"
wf1(t = 0.0)
wf2(t = 0.5)
wf3(t = 1.0)

print("wf1(t = 0.0) =", wf1(t = 0.0))  # markdown-exec: hide
print("wf2(t = 0.5) =", wf2(t = 0.5))  # markdown-exec: hide
print("wf3(t = 1.0) =", wf3(t = 1.0))  # markdown-exec: hide
```

Each waveform also supports evaluation at multiple time steps by calling it on an array of times.
```python exec="on" source="material-block" result="json" session="waveforms"
import numpy as np

t_array = np.linspace(0.0, 2.0, 9)

wf3(t_array)
print("t =     ", t_array) # markdown-exec: hide
print("wf(t) = ", wf3(t_array)) # markdown-exec: hide
```

In the waveform above, we defined it with a duration of $1.0$, and then evaluated it over nine points from $t = 0.0$ to $t=2.0$. As you can see, all points after $t = 1.0$ evaluated to $0.0$. By default, any waveform evaluated at a time $t$ that falls outside the specified `duration` gives $0.0$.

Waveforms can be quickly drawn with the `draw()` method.

```python exec="on" source="material-block" html="1" session="waveforms"
import matplotlib.pyplot as plt # markdown-exec: hide
from docs.utils import fig_to_html # markdown-exec: hide

wf3.draw()
fig = wf3.draw(return_fig = True) # markdown-exec: hide
print(fig_to_html(fig)) # markdown-exec: hide
```

### Interpolated waveform

Special waveform to easily fit a set given values with a smooth function.
For the full set of available options please refer to the [API reference][qoolqit.waveforms].

```python exec="on" source="material-block" html="1" session="waveforms"
from qoolqit import Interpolated

values = np.sin(np.linspace(0,2*np.pi, 10))
wf_interpolated = Interpolated(100, values)
wf_interpolated.draw()
fig = wf_interpolated.draw(return_fig = True) # markdown-exec: hide
print(fig_to_html(fig)) # markdown-exec: hide
```

### Composite waveforms

The most straightforward way to arbitrarily compose waveforms is to use the `>>` operator. This will create a `CompositeWaveform` representing the waveforms in the order provided.

```python exec="on" source="material-block" result="json" session="waveforms"
wf_comp = wf1 >> wf2 >> wf3

print(wf_comp)  # markdown-exec: hide
```

The code above is equivalent to calling `CompositeWaveform(wf1, wf2, wf3)`. As shown, printing the composite waveform will automatically show the individual waveforms in the composition and the times at which they are active. These are automatically calculated from the individual waveforms. A
`CompositeWaveform` is by itself a subclass of `Waveform`, and thus the previous logic on calling it at arbitrary time values also applies.

A few convenient properties are directly available in a composite waveform:

```python exec="on" source="material-block" result="json" session="waveforms"
# Total duration
wf_comp.duration

# List of durations of the individual waveforms
wf_comp.durations

# List of times where each individual waveform starts / ends
wf_comp.times

print("Total duration :", wf_comp.duration)  # markdown-exec: hide
print("List of durations :", wf_comp.durations)  # markdown-exec: hide
print("List of times :", wf_comp.times)  # markdown-exec: hide
```

A custom waveform can directly be a `CompositeWaveform`. That is the case with the `PiecewiseLinear` waveform, which takes a list of durations (of size $N$) and a list of values (of size $N+1$) and creates a linear interpolation between all values using individual waveforms of type `Ramp`.

```python exec="on" source="material-block" html="1" session="waveforms"
import matplotlib.pyplot as plt # markdown-exec: hide
from docs.utils import fig_to_html # markdown-exec: hide

from qoolqit import PiecewiseLinear

durations = [1.0, 1.0, 2.0]
values = [0.0, 1.0, 0.5, 0.5]

wf_pwl = PiecewiseLinear(durations, values)

wf_pwl.draw()

fig = wf_pwl.draw(return_fig = True) # markdown-exec: hide
print(fig_to_html(fig)) # markdown-exec: hide
```


### Custom waveforms

Built-in waveforms cover the most common shapes, but any differentiable (or piecewise-smooth)
profile can be realized by subclassing `Waveform`. For a full walkthrough — including concrete
examples and how to use custom waveforms inside a `Drive` — see
[Defining custom waveforms](../extended_usage/custom_waveforms.md).


## Drives

The `Drive` is a collection of amplitude and detuning waveforms, plus an optional phase, fully specifying the drive Hamiltonian described in the [QoolQit model](../get_started/qoolqit_model.md#qoolqit-model) page.
Here is an example on how to create a drive:

```python exec="on" source="material-block" result="json" session="drives"
from qoolqit import Constant, Ramp
from qoolqit import Drive

# Defining two waveforms
amplitude = Constant(5.0, 1.0) >> Ramp(1.0, 0.0, 0.5)
detuning = Ramp(2.0, -1.0, 1.0) >> Constant(1.0, 1.0)

# Defining the drive
drive = Drive(
    amplitude = amplitude,
    detuning = detuning
)

# Expanding the drive through composition
drive = drive >> drive
print(drive)  # markdown-exec: hide
```

While defining an amplitude is required, if not provided, the detuning and the phase value will be assumed to be zero.
Finally, after creation, drives can be conveniently plotted and inspected as:

```python exec="on" source="material-block" html="1" session="drives"
import matplotlib.pyplot as plt # markdown-exec: hide
from docs.utils import fig_to_html # markdown-exec: hide
drive.draw()
fig = drive.draw(return_fig = True) # markdown-exec: hide
print(fig_to_html(fig)) # markdown-exec: hide
```

To understand the role of time and the duration of a drive in the Rydberg Analog model, please have a look at the [Time regimes](../get_started/qoolqit_model.md#time-regimes) page.
Alternatively, duration can also be overwritten at compilation time, as relative to the maximum duration allowed by a specific hardware device.
Such feature, is useful, for example, when working on adiabatic protocols.
For more details, please have a look at the [Device and compilation](../fundamentals/compilation/device_and_compilation.md) page of the documentation, specifically at the [Special compilation flags](../fundamentals/compilation/device_and_compilation.md#special-compilation-maximum-allowed-duration) section.

## Defining a quantum program

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

Next, we have to choose a device and compile the program for it. In QoolQit, compilation refers to converting the dimensionless time, energy, and distance values used in the Rydberg analog model into concrete values. More detailed information on this conversion is provided in the [Rydberg analog model page](../get_started/qoolqit_model.md) and in [Compilation](./compilation/rationale.md)
