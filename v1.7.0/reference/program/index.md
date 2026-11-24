## program

QuantumProgram: a register and a drive, compilable to a Pulser sequence.

Classes:

- **`QuantumProgram`** –

  A program representing a Sequence acting on a Register of qubits.

### QuantumProgram

```
QuantumProgram(register: Register, drive: Drive)
```

A program representing a Sequence acting on a Register of qubits.

Parameters:

- **`register`** (`Register`) –

  the register of qubits, defining their positions.
- **`drive`** (`Drive`) –

  the drive acting on qubits, defining amplitude, detuning and phase.

Methods:

- **`__repr__`** –

  Return a summary of the register, drive and compilation status.
- **`compile_to`** –

  Compiles the quantum program for execution on a specific device.
- **`draw`** –

  Draw the drive of the program, or its compiled sequence.

Attributes:

- **`compiled_sequence`** (`Sequence`) –

  The Pulser sequence compiled to a specific device.
- **`drive`** (`Drive`) –

  The driving waveforms.
- **`is_compiled`** (`bool`) –

  Check if the program has been compiled.
- **`register`** (`Register`) –

  The register of qubits.

#### compiled\_sequence

```
compiled_sequence: Sequence
```

The Pulser sequence compiled to a specific device.

#### drive

```
drive: Drive
```

The driving waveforms.

#### is\_compiled

```
is_compiled: bool
```

Check if the program has been compiled.

#### register

```
register: Register
```

The register of qubits.

#### \_\_repr\_\_

```
__repr__() -> str
```

Return a summary of the register, drive and compilation status.

#### compile\_to

```
compile_to(
    device: Device,
    profile: Literal["default", "max_energy"]
    | CompilerProfile = DEFAULT,
    device_max_duration_ratio: float | None = None,
) -> None
```

Compiles the quantum program for execution on a specific device.

The compilation process translates a program to make it runnable on a specific device:

- Dimensionalization: Rescale the drive amplitude and the register positions to physical units compatible with the device.
- Translation: Translate the program to a lower-level representation (Pulser) that can be executed on the device.

There are two compilation profiles:

- "default": Compile the program as it is. The drive and the register positions must respect the hardware constraints of the device which can be inspected using `device.specs()`. `CompilerProfile.WORKING_POINT` is a deprecated alias for this profile.
- "max\_energy": Scale the program to utilize the device's maximum capabilities. The drive amplitude and the register positions are rescaled to achieve respectively the maximum amplitude and the minimum pairwise distance compatible with the input program and the device's constraints.

The following option does NOT preserve the input program, but rather adapts the program to the device's constraints. Programs compiled this way are not portable across devices.

- device\_max\_duration\_ratio: Rescale the drive duration to a fraction of the device's maximum allowed duration. Useful in adiabatic protocols where one simply seeks to minimize the time derivative of the drive's amplitude.

Parameters:

- **`device`** (`Device`) –

  The target device for compilation. Must be a QoolQit Device.
- **`profile`** (`Literal['default', 'max_energy'] | CompilerProfile`, default: `DEFAULT` ) –

  The compilation profile used to translate the program. Defaults to `"default"`.
- **`device_max_duration_ratio`** (`float | None`, default: `None` ) –

  The fraction of the device's maximum allowed duration to set the program duration to, or None to leave it unset. Must be a number in the range (0, 1\]. Can only be set if the device has a maximum allowed duration.

Raises:

- `TypeError` –

  If `device` is not a QoolQit Device.
- `ValueError` –

  If `device_max_duration_ratio` is set but the device has no maximum allowed duration, or if it is not in the range (0, 1\].
- `CompilationError` –

  If the compilation fails due to device constraints.

#### draw

```
draw(
    compiled: bool = False, fig: FigureBase | None = None
) -> None
```

Draw the drive of the program, or its compiled sequence.

Parameters:

- **`compiled`** (`bool`, default: `False` ) –

  Whether to draw the compiled pulser sequence instead of the drive.
- **`fig`** (`FigureBase | None`, default: `None` ) –

  The figure or subfigure to draw the drive into. If None, a new pyplot figure is created. Ignored when `compiled=True`.
