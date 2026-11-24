## Compilation errors with `max_energy` profile

At compilation, several errors might occur. In this notebook we describe the most common ones, show what the typical error messages are and how to interpret them, and explain how to handle them.

Let us start by defining a simple quantum program:

```
from qoolqit import Register

# create a square Register
register = Register.square(2, spacing=1.0)
register.draw()
```

png

```
from qoolqit import Drive
from qoolqit.waveforms import InterpolatedWaveform, RampWaveform

# Interpolated waveform: smooth curve through specified values
omega_wf = InterpolatedWaveform(duration=50, values=[0, 1, 0])
# Ramp waveform
delta_wf = RampWaveform(duration=50, initial_value=-2, final_value=2)

# Combine into a Drive
drive = Drive(amplitude=omega_wf, detuning=delta_wf)

drive.draw()
```

png

```
from qoolqit import AnalogDevice, QuantumProgram

# initialize the quantum program
program = QuantumProgram(register=register, drive=drive)

# compile the quantum program to a selected device
device = AnalogDevice()
program.compile_to(device, profile="max_energy")
```

We observe there that the compilation was successful and we can access the compiled sequence.

```
program.draw()
program.compiled_sequence.draw()
```

png

png

Let us now explore different cases where different error messages might arise. First let us define a small function that outputs the quantum program we want to compile:

```
# Or use built-in graph patterns
from qoolqit import Drive, QuantumProgram, Register
from qoolqit.waveforms import RampWaveform


def create_program(L, amp, det):
    """Build a program on an LxL square lattice with the given amplitude and detuning."""
    register = register = Register.square(L, spacing=1.0)
    omega_wf = InterpolatedWaveform(duration=50, values=[0, amp, 0])
    delta_wf = RampWaveform(duration=50, initial_value=-det, final_value=det)
    drive = Drive(amplitude=omega_wf, detuning=delta_wf)
    return QuantumProgram(register=register, drive=drive)
```

## Error 1: Amplitude too large

In this case the compilation routine will try to rescale the register in such a way to maintain the same relative amplitudes of the drive. If the amplitude of the drive is too large, the register may become too large, leading to an overflow error.

```
from qoolqit.exceptions import CompilationError

L = 4
amp = 100
det = 2
program = create_program(L, amp, det)
try:
    compiled_sequence = program.compile_to(device, profile="max_energy")
except CompilationError as err:
    print(err)
```

```
After rescaling the input program to the maximum energy scale available for the selected device, the following exception was raised:

The drive's duration went over the maximum value allowed.
To compile this program on the selected device `AnalogDevice`, set the drive's duration below 0.75398223686154
```

> #### What happened?
>
> We selected an amplitude that is 100 times larger than the maximum atomic pair-wise interaction. The compilation profile set the amplitude to the maximum allowed value and rescaled the register to keep the ratio between drive strength and interaction energy. As a result, the register grew too large, leading to an overflow error.

## Error 2: detuning too large

```
L = 4
amp = 1
det = 20
program = create_program(L, amp, det)
try:
    compiled_sequence = program.compile_to(device, profile="max_energy")
except CompilationError as err:
    print(err)
```

```
After rescaling the input program to the maximum energy scale available for the selected device, the following exception was raised:

The drive's maximum absolute detuning went over the maximum value allowed.
To compile this program on the selected device `AnalogDevice`, set the maximum absolute detuning below 10.000000000000139
```

> #### What happened?
>
> We selected a detuning that is 20 times larger than the maximum atomic pair-wise interaction. The compilation routine automatically rescales the amplitude to the maximum allowed value and all the other quantities accordingly. Hence, it rescaled the register and the detuning. This time the register is fitting the device but the detuning value goes beyond the allowed bounds.

## Error 3: duration too long

```
L = 2
amp = 10
det = 1
program = create_program(L, amp, det)
try:
    compiled_sequence = program.compile_to(device, profile="max_energy")
except CompilationError as err:
    print(err)
```

```
After rescaling the input program to the maximum energy scale available for the selected device, the following exception was raised:

The drive's duration went over the maximum value allowed.
To compile this program on the selected device `AnalogDevice`, set the drive's duration below 7.5398223686154004
```

### What happened?

The compilation profile `max_energy` automatically rescales the amplitude to the maximum allowed value and all the other quantities accordingly. This means that also the time is rescaled. In particular, as explained in [Adimensionalization and Compilation](<https://pasqal-io.github.io/qoolqit/main/extended_usage/adimensionalization/index.md#time-scaling>), when the amplitude is too large to fit the device and it has to be decreased and everything rescaled accordingly, then time is increased. In this case the total duration ended up being longer than the allowed value.
