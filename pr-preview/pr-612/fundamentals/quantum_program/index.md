In this page, you will learn how to build a quantum program, from its building blocks:

- Create a `Register` from a set of coordinates,
- Define `Waveforms` selecting amplitude and detuning,
- Build a `Drive` from waveform components,
- Instantiate a `QuantumProgram` from a `Register` and a `Drive`,
- Check whether a program has already been compiled.

---

The QuantumProgram defines the protocol used to solve your problem within the adimensional framework of the [Rydberg Analog model](<https://pasqal-io.github.io/qoolqit/get_started/qoolqit_model/index.md>).

In practice, this involves specifying both the interaction and the driving Hamiltonian. In QoolQit, these are set up by creating a `Register`, which determines the positions of the qubits, and a `Drive` object, which describes how laser fields control the qubits over time.

To run the program on real quantum hardware, the abstract `QuantumProgram` must first be compiled into a form compatible with a specific QPU. This compilation process will be covered later in the [Compilation](<https://pasqal-io.github.io/qoolqit/fundamentals/compilation/rationale/index.md>) section of this documentation.

## Registers

A `Register` defines the qubit coordinates map to be used by a quantum program. It can be instantiated from a dictionary of coordinates, or from a list of coordinates.

```
from qoolqit import Register

# Instantiate a Register from a dictionary of coordinates.
qubits = {
    0: (-0.5, -0.5),
    1: (-0.5, 0.5),
    2: (0.5, -0.5),
    3: (0.5, 0.5),
}

register = Register(qubits)

# Instantiate a Register from a list of coordinates.
coords = [(-0.5, -0.5), (-0.5, 0.5), (0.5, -0.5), (0.5, 0.5)]

register = Register.from_coordinates(coords)
print(register)
register.draw()
```

```
Register(n_qubits = 4)
```

png

The distances between all qubits can be directly accessed.

```
register.distances()
```

```
{(0, 1): 1.0,
 (1, 2): 1.4142135623730951,
 (0, 3): 1.4142135623730951,
 (2, 3): 1.0,
 (0, 2): 1.0,
 (1, 3): 1.0}
```

The minimum distance can be directly accessed.

```
register.distances()
```

```
{(0, 1): 1.0,
 (1, 2): 1.4142135623730951,
 (0, 3): 1.4142135623730951,
 (2, 3): 1.0,
 (0, 2): 1.0,
 (1, 3): 1.0}
```

```
register.min_distance()
```

```
1.0
```

The interaction coefficients \\(1/r\_{ij}^6\\) can be directly accessed.

```
register.interactions()
```

```
{(0, 1): 1.0,
 (1, 2): 0.12499999999999994,
 (0, 3): 0.12499999999999994,
 (2, 3): 1.0,
 (0, 2): 1.0,
 (1, 3): 1.0}
```

## Waveforms

An essential part of writing programs in the Rydberg analog model is to write the time-dependent functions representing the amplitude and detuning terms in the drive Hamiltonian. For that, QoolQit implements a set of waveforms that can be used directly and/or composed together.

### Base waveforms

A full list of the available waveforms can be found in the [API reference](<https://pasqal-io.github.io/qoolqit/reference/waveforms/index.md#qoolqit.waveforms>) page of this documentation.

```
from qoolqit import ConstantWaveform, DelayWaveform, RampWaveform

# An empty waveform
wf1 = DelayWaveform(1.0)
print(wf1)

# A waveform with a constant value
wf2 = ConstantWaveform(1.0, 2.0)
print(wf2)

# A waveform that ramps linearly between two values
wf3 = RampWaveform(1.0, -1.0, 1.0)
print(wf3)
```

```
0.00 ≤ t ≤ 1.00: DelayWaveform(t)
0.00 ≤ t ≤ 1.00: ConstantWaveform(t, 2.00)
0.00 ≤ t ≤ 1.00: RampWaveform(t, -1.00, 1.00)
```

As shown above, printing a waveform shows the duration interval over which it applies followed by the description of the waveform.

The first argument is always the `duration` of the waveform, and the remaining arguments depend on the information required by each waveform. The resulting object is a callable that can be evaluated at any time \\(t\\).

```
wf1(t = 0.0)
wf2(t = 0.5)
wf3(t = 1.0)

print("wf1(t = 0.0) =", wf1(t = 0.0))
print("wf2(t = 0.5) =", wf2(t = 0.5))
print("wf3(t = 1.0) =", wf3(t = 1.0))
```

```
wf1(t = 0.0) = 0.0
wf2(t = 0.5) = 2.0
wf3(t = 1.0) = 1.0
```

Each waveform also supports evaluation at multiple time steps by calling it on a 1D list or array of times.

```
import numpy as np

t_array = np.linspace(0.0, 2.0, 9)
wf3(t_array)
```

```
array([-1. , -0.5,  0. ,  0.5,  1. ,  0. ,  0. ,  0. ,  0. ])
```

In the waveform above, we defined it with a duration of \\(1.0\\), and then evaluated it over nine points from \\(t = 0.0\\) to \\(t=2.0\\). As you can see, all points after \\(t = 1.0\\) evaluated to \\(0.0\\). By default, any waveform evaluated at a time \\(t\\) that falls outside the specified `duration` gives \\(0.0\\).

Waveforms can be quickly drawn with the `draw()` method.

```
wf3.draw()
```

png

### Interpolated waveform

Special waveform to fit a set of given values with a smooth function. For the full set of available options please refer to the [API reference](<https://pasqal-io.github.io/qoolqit/reference/waveforms/index.md#qoolqit.waveforms>) section of this documentation.

```
from qoolqit import InterpolatedWaveform

values = np.sin(np.linspace(0,2*np.pi, 10))
wf_interpolated = InterpolatedWaveform(100, values)
wf_interpolated.draw()
```

png

### Composite waveforms

The most straightforward way to arbitrarily compose waveforms is to use the `>>` operator. This will create a `CompositeWaveform` representing the waveforms in the order provided.

```
wf_comp = wf1 >> wf2 >> wf3
```

The code above is equivalent to calling `CompositeWaveform(wf1, wf2, wf3)`. As shown, printing the composite waveform will automatically show the individual waveforms in the composition and the times at which they are active. These are automatically calculated from the individual waveforms. A `CompositeWaveform` is by itself a subclass of `Waveform`, and thus the previous logic on calling it at arbitrary time values also applies.

A few convenient properties are directly available in a composite waveform:

```
print("Total duration :", wf_comp.duration)
# List of durations of the individual waveforms
print("List of durations :", wf_comp.durations)
# List of times where each individual waveform starts / ends
print("List of times :", wf_comp.times)
```

```
Total duration : 3.0
List of durations : [1.0, 1.0, 1.0]
List of times : [0.0, 1.0, 2.0, 3.0]
```

A custom waveform can directly be a `CompositeWaveform`. That is the case with the `PiecewiseLinear` waveform, which takes a list of durations (of size \\(N\\)) and a list of values (of size \\(N+1\\)) and creates a linear interpolation between all values using individual waveforms of type `Ramp`.

```
from qoolqit import PiecewiseLinearWaveform

durations = [1.0, 1.0, 2.0]
values = [0.0, 1.0, 0.5, 0.5]

wf_pwl = PiecewiseLinearWaveform(durations, values)

wf_pwl.draw()
```

png

## Drives

The `Drive` is a collection of amplitude and detuning waveforms, plus an optional phase, fully specifying the drive Hamiltonian described in the [QoolQit model](<https://pasqal-io.github.io/qoolqit/get_started/qoolqit_model/index.md#qoolqit-dimensionless-model>) page. Here is an example on how to create a drive:

```
from qoolqit import ConstantWaveform, Drive, InterpolatedWaveform

# Defining two waveforms
amplitude = ConstantWaveform(5.0, value=1.0) >> InterpolatedWaveform(10.0, [0.0, 0.8, 0.8, 0.0])
detuning = RampWaveform(8.0, -1.0, 1.0) >> ConstantWaveform(4.0, 1.0)

# Defining the drive
drive = Drive(
    amplitude = amplitude,
    detuning = detuning
)

# Expanding the drive through composition
drive = drive >> drive
print(drive)
```

```
amplitude: 
| 0.00 ≤ t < 5.00: ConstantWaveform(t, 1.00)
| 5.00 ≤ t < 15.00: InterpolatedWaveform(t)
| 15.00 ≤ t < 20.00: ConstantWaveform(t, 1.00)
| 20.00 ≤ t ≤ 30.00: InterpolatedWaveform(t)
detuning: 
| 0.00 ≤ t < 8.00: RampWaveform(t, -1.00, 1.00)
| 8.00 ≤ t < 12.00: ConstantWaveform(t, 1.00)
| 12.00 ≤ t < 15.00: DelayWaveform(t)
| 15.00 ≤ t < 23.00: RampWaveform(t, -1.00, 1.00)
| 23.00 ≤ t < 27.00: ConstantWaveform(t, 1.00)
| 27.00 ≤ t ≤ 30.00: DelayWaveform(t)
```

While defining an amplitude is required, if not provided, the detuning and the phase value will be assumed to be zero. Finally, after creation, drives can be conveniently plotted and inspected as:

```
drive.draw()
```

png

To understand the role of time and the duration of a drive in the Rydberg Analog model, please have a look at the [Time regimes](<https://pasqal-io.github.io/qoolqit/get_started/qoolqit_model/index.md#time-regimes>) page. Alternatively, duration can also be overwritten at compilation time, as relative to the maximum duration allowed by a specific hardware device. Such a feature is useful, for example, when working on adiabatic protocols. For more details, please have a look at the [Device and compilation](<https://pasqal-io.github.io/qoolqit/fundamentals/compilation/device_and_compilation/index.md>) page of the documentation, specifically at the [Special compilation flags](<https://pasqal-io.github.io/qoolqit/fundamentals/compilation/device_and_compilation/index.md#special-compilation-maximum-allowed-duration>) section.

Finally, at the [compilation stage](<https://pasqal-io.github.io/qoolqit/fundamentals/compilation/device_and_compilation/index.md>), the duration set by the user might be higher than what the selected QPU device allows. Compilation will thus trigger an informative error about the hardware limitations and how to comply with those.

### Detuning Map Modulator

As introduced in the [QoolQit model](<https://pasqal-io.github.io/qoolqit/get_started/qoolqit_model/index.md>) section of this documentation, the driving Hamiltonian can also define a local detuning contribution, or Detuning Map Modulator (DMM). Such a detuning map is defined by a waveform and a dictionary specifying the mapping from the qubit indices to the corresponding modulation. At a given time, therefore, each qubit's local detuning contribution is given by the value of the DMM waveform, multiplied by the corresponding weight.

The `DetuningMapModulator` class allows the user to create such a custom detuning map:

```
from qoolqit.drive import DetuningMapModulator

dmm_waveform = ConstantWaveform(10.0, -1.0)
dmm_weights = {0:0.1, 1:0.3, 2:0.8}
dmm = DetuningMapModulator(dmm_waveform, dmm_weights)
print(dmm)
```

```
DetuningMapModulator(waveform=0.00 ≤ t ≤ 10.00: ConstantWaveform(t, -1.00), weights={0: 0.1, 1: 0.3, 2: 0.8})
```

Drawing the drive will show now the additional DMM waveform:

```
drive = Drive(amplitude=ConstantWaveform(10.0,1.0), dmm=dmm)
print(drive)
drive.draw()
```

```
amplitude: 
0.00 ≤ t ≤ 10.00: ConstantWaveform(t, 1.00)
detuning: 
0.00 ≤ t ≤ 10.00: DelayWaveform(t)
dmm: 
DetuningMapModulator(waveform=0.00 ≤ t ≤ 10.00: ConstantWaveform(t, -1.00), weights={0: 0.1, 1: 0.3, 2: 0.8})
```

png

Finally, note that this feature is not available on all devices and the defined DMM waveform must be negative at all times.

## Defining a quantum program

A `QuantumProgram` combines a `Register` and a `Drive` and serves as the main interface for compilation and execution.

```
from qoolqit import Drive, PiecewiseLinearWaveform, QuantumProgram, Register

# Defining the Drive
wf0 = PiecewiseLinearWaveform([1.0, 2.0, 1.0], [0.0, 0.5, 0.5, 0.0])
wf1 = PiecewiseLinearWaveform([1.0, 2.0, 1.0], [-1.0, -1.0, 1.0, 1.0])
drive = Drive(amplitude = wf0, detuning = wf1)

# Defining the Register
coords = [(0.0, 0.0), (0.0, 1.0), (1.0, 0.0), (1.0, 1.0)]
register = Register.from_coordinates(coords)

# Creating the Program
program = QuantumProgram(register, drive)
print(program)
```

```
Quantum Program:
| Register(n_qubits = 4)
| Drive(duration = 4.000)
| Compiled: False
```

At this point, the program has not been compiled to any device. As shown above, this is conveniently displayed when printing the program. It can also be checked through the `is_compiled` property.

```
program.is_compiled
```

```
False
```

Next, we have to choose a device and compile the program for it. In QoolQit, compilation refers to converting the dimensionless time, energy, and distance values used in the Rydberg analog model into concrete values. More detailed information on this conversion is provided in the [Rydberg analog model page](<https://pasqal-io.github.io/qoolqit/get_started/qoolqit_model/index.md>) and in [Compilation](<https://pasqal-io.github.io/qoolqit/fundamentals/compilation/rationale/index.md>).
