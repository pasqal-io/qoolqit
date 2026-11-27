## qoolqit

A Python library for algorithm development in the Rydberg Analog Model.

Modules:

- **`devices`** –

  Neutral-atom devices and their physical constraints.
- **`drive`** –

  Drive Hamiltonian (amplitude, detuning, phase) and its Detuning Map Modulator (DMM).
- **`embedding`** –

  Collection of graph and matrix embedding algorithms.
- **`exceptions`** –

  QoolQit exceptions.
- **`execution`** –

  Execute quantum programs on QPUs or local/remote emulators.
- **`graphs`** –

  Graph creation and manipulation in QoolQit.
- **`program`** –

  QuantumProgram: a register and a drive, compilable to a Pulser sequence.
- **`register`** –

  Register mapping qubit IDs to 2D coordinates.
- **`visualization`** –

  Visualization helpers for QoolQit results.
- **`waveforms`** –

  Composable, time-bounded scalar waveforms for pulse-level quantum control.

Classes:

- **`AnalogDevice`** –

  A realistic device for analog sequence execution.
- **`AnalogDeviceWithDMM`** –

  A realistic device with DMM for analog sequence execution.
- **`BlackmanWaveform`** –

  A Blackman window of a specified duration and area under the curve.
- **`ConstantWaveform`** –

  A constant waveform over a given duration.
- **`DelayWaveform`** –

  An empty waveform.
- **`Device`** –

  QoolQit Device wrapper around a Pulser BaseDevice.
- **`DigitalAnalogDevice`** –

  A device with digital and analog capabilities.
- **`Drive`** –

  The drive Hamiltonian acting over a duration.
- **`InterpolatedWaveform`** –

  A waveform created from shape-preserving interpolation of data points.
- **`MockDevice`** –

  A virtual device for unconstrained prototyping.
- **`PiecewiseLinearWaveform`** –

  A piecewise linear waveform.
- **`QuantumProgram`** –

  A program representing a Sequence acting on a Register of qubits.
- **`RampWaveform`** –

  A ramp that linearly interpolates between an initial and final value.
- **`Register`** –

  A QoolQit register mapping qubit IDs to 2D coordinates.
- **`SequenceCompiler`** –

  Compiles a QoolQit Register and Drive to a Device.

Functions:

- **`available_default_devices`** –

  Show the default available devices in QooQit.

### AnalogDevice

```
AnalogDevice()
```

A realistic device for analog sequence execution.

Methods:

- **`__repr__`** –

  Return the device name.
- **`__str__`** –

  Return the device name, description and specs.
- **`from_connection`** –

  Return the specified device from the selected device from a connection.
- **`info`** –

  Show the device short description and constraints.
- **`reset_converter`** –

  Resets the unit converter to the default one.
- **`set_distance_unit`** –

  Changes the unit converter according to a reference distance unit.
- **`set_energy_unit`** –

  Changes the unit converter according to a reference energy unit.

Attributes:

- **`converter`** (`UnitConverter`) –

  The unit converter currently used by the device.
- **`name`** (`str`) –

  The device name.
- **`phase_jump_time`** (`float`) –

  Time to change the phase between two consecutive pulses, in adimensional units.
- **`specs`** (`dict[str, float | None]`) –

  Return the device specification constraints.

#### converter

```
converter: UnitConverter
```

The unit converter currently used by the device.

#### name

```
name: str
```

The device name.

#### phase\_jump\_time

```
phase_jump_time: float
```

Time to change the phase between two consecutive pulses, in adimensional units.

Read from the global Rydberg channel.

#### specs

```
specs: dict[str, float | None]
```

Return the device specification constraints.

#### \_\_repr\_\_

```
__repr__() -> str
```

Return the device name.

#### \_\_str\_\_

```
__str__() -> str
```

Return the device name, description and specs.

#### from\_connection

```
from_connection(
    connection: RemoteConnection, name: str
) -> Device
```

Return the specified device from the selected device from a connection.

Available devices through the provided connection are can be seen with the `connection.fetch_available_devices()` method.

Parameters:

- **`connection`** (`RemoteConnection`) –

  connection object to fetch the available devices.
- **`name`** (`str`) –

  The name of the desired device.

Returns:

- **`Device`** ( `Device` ) –

  The requested device.

Raises:

- `ValueError` –

  If the requested device is not available through the provided connection.

Example:

```
from pasqal_cloud import PasqalCloudConnection
fresnel_device = Device.from_connection(connection=PasqalCloudConnection(), name="FRESNEL")
```

#### info

```
info() -> None
```

Show the device short description and constraints.

#### reset\_converter

```
reset_converter() -> None
```

Resets the unit converter to the default one.

#### set\_distance\_unit

```
set_distance_unit(distance: float) -> None
```

Changes the unit converter according to a reference distance unit.

#### set\_energy\_unit

```
set_energy_unit(energy: float) -> None
```

Changes the unit converter according to a reference energy unit.

### AnalogDeviceWithDMM

```
AnalogDeviceWithDMM()
```

A realistic device with DMM for analog sequence execution.

Methods:

- **`__repr__`** –

  Return the device name.
- **`__str__`** –

  Return the device name, description and specs.
- **`from_connection`** –

  Return the specified device from the selected device from a connection.
- **`info`** –

  Show the device short description and constraints.
- **`reset_converter`** –

  Resets the unit converter to the default one.
- **`set_distance_unit`** –

  Changes the unit converter according to a reference distance unit.
- **`set_energy_unit`** –

  Changes the unit converter according to a reference energy unit.

Attributes:

- **`converter`** (`UnitConverter`) –

  The unit converter currently used by the device.
- **`name`** (`str`) –

  The device name.
- **`phase_jump_time`** (`float`) –

  Time to change the phase between two consecutive pulses, in adimensional units.
- **`specs`** (`dict[str, float | None]`) –

  Return the device specification constraints.

#### converter

```
converter: UnitConverter
```

The unit converter currently used by the device.

#### name

```
name: str
```

The device name.

#### phase\_jump\_time

```
phase_jump_time: float
```

Time to change the phase between two consecutive pulses, in adimensional units.

Read from the global Rydberg channel.

#### specs

```
specs: dict[str, float | None]
```

Return the device specification constraints.

#### \_\_repr\_\_

```
__repr__() -> str
```

Return the device name.

#### \_\_str\_\_

```
__str__() -> str
```

Return the device name, description and specs.

#### from\_connection

```
from_connection(
    connection: RemoteConnection, name: str
) -> Device
```

Return the specified device from the selected device from a connection.

Available devices through the provided connection are can be seen with the `connection.fetch_available_devices()` method.

Parameters:

- **`connection`** (`RemoteConnection`) –

  connection object to fetch the available devices.
- **`name`** (`str`) –

  The name of the desired device.

Returns:

- **`Device`** ( `Device` ) –

  The requested device.

Raises:

- `ValueError` –

  If the requested device is not available through the provided connection.

Example:

```
from pasqal_cloud import PasqalCloudConnection
fresnel_device = Device.from_connection(connection=PasqalCloudConnection(), name="FRESNEL")
```

#### info

```
info() -> None
```

Show the device short description and constraints.

#### reset\_converter

```
reset_converter() -> None
```

Resets the unit converter to the default one.

#### set\_distance\_unit

```
set_distance_unit(distance: float) -> None
```

Changes the unit converter according to a reference distance unit.

#### set\_energy\_unit

```
set_energy_unit(energy: float) -> None
```

Changes the unit converter according to a reference energy unit.

### BlackmanWaveform

```
BlackmanWaveform(duration: float, area: float)
```

A Blackman window of a specified duration and area under the curve.

Implements the positive Blackman window shaped waveform blackman(t) = A*(0.42 - 0.5*cos(alpha*t) + 0.08*cos(2*alpha*t)) A = area/(0.42\*duration) alpha = 2π/duration

See: [https://en.wikipedia.org/wiki/Window\_function\#:\~:text=Blackman%20window](<https://en.wikipedia.org/wiki/Window_function#:~:text=Blackman window>)

Parameters:

- **`duration`** (`float`) –

  The waveform duration.
- **`area`** (`float`) –

  The integral of the waveform.

> [!NOTE]
>
> **Example**
>
> ```
> blackman_wf = BlackmanWaveform(100.0, area=3.14)
> ```

Methods:

- **`__call__`** –

  Evaluate the waveform at `t`: a single time, or a 1D list or array of times.
- **`__mul__`** –

  Rescale this waveform by a scalar.
- **`__repr__`** –

  Return the time interval and the waveform with its parameters.
- **`__rmul__`** –

  Rescale this waveform by a scalar (right-hand multiplication).
- **`__rshift__`** –

  Returns a new CompositeWaveform composed of this waveform and another.
- **`draw`** –

  Draw the waveform.
- **`function`** –

  Evaluates the waveform function at a given time t.
- **`max`** –

  Get the maximum value of the waveform.
- **`min`** –

  Get the minimum value of the waveform.

Attributes:

- **`duration`** (`float`) –

  Returns the duration of the waveform.
- **`params`** (`dict[str, float | ndarray]`) –

  Dictionary of parameters used by the waveform.
- **`waveforms`** (`list[Waveform]`) –

  Returns a list of the individual waveforms, which is just this waveform.

#### duration

```
duration: float
```

Returns the duration of the waveform.

#### params

```
params: dict[str, float | ndarray]
```

Dictionary of parameters used by the waveform.

#### waveforms

```
waveforms: list[Waveform]
```

Returns a list of the individual waveforms, which is just this waveform.

#### \_\_call\_\_

```
__call__(t: float) -> float
```

```
__call__(t: list[float] | ndarray) -> NDArray[float64]
```

```
__call__(
    t: float | list[float] | ndarray,
) -> float | NDArray[float64]
```

Evaluate the waveform at `t`: a single time, or a 1D list or array of times.

Returns a float for a single time, otherwise a 1D float64 array. Times outside \[0, duration\] give 0.

#### \_\_mul\_\_

```
__mul__(other: float) -> Waveform
```

Rescale this waveform by a scalar.

#### \_\_repr\_\_

```
__repr__() -> str
```

Return the time interval and the waveform with its parameters.

#### \_\_rmul\_\_

```
__rmul__(other: float) -> Waveform
```

Rescale this waveform by a scalar (right-hand multiplication).

#### \_\_rshift\_\_

```
__rshift__(other: Waveform) -> CompositeWaveform
```

Returns a new CompositeWaveform composed of this waveform and another.

#### draw

```
draw(
    ax: Axes | None = None,
    color: ColorType = "tab:blue",
    n_points: int = 250,
) -> None
```

Draw the waveform.

Parameters:

- **`ax`** (`Axes | None`, default: `None` ) –

  The axes to draw into. If None, a new pyplot figure is created.
- **`color`** (`ColorType`, default: `'tab:blue'` ) –

  The color of the line and the filled area. Defaults to matplotlib's "tab:blue".
- **`n_points`** (`int`, default: `250` ) –

  The number of time samples to draw. Defaults to 250.

#### function

```
function(t: float) -> float
```

Evaluates the waveform function at a given time t.

#### max

```
max() -> float
```

Get the maximum value of the waveform.

#### min

```
min() -> float
```

Get the minimum value of the waveform.

### ConstantWaveform

```
ConstantWaveform(duration: float, value: float)
```

A constant waveform over a given duration.

Parameters:

- **`duration`** (`float`) –

  the total duration.
- **`value`** (`float`) –

  the value to take during the duration.

Methods:

- **`__call__`** –

  Evaluate the waveform at `t`: a single time, or a 1D list or array of times.
- **`__mul__`** –

  Rescale this waveform by a scalar.
- **`__repr__`** –

  Return the time interval and the waveform with its parameters.
- **`__rmul__`** –

  Rescale this waveform by a scalar (right-hand multiplication).
- **`__rshift__`** –

  Returns a new CompositeWaveform composed of this waveform and another.
- **`draw`** –

  Draw the waveform.
- **`function`** –

  Evaluates the waveform function at a given time t.
- **`max`** –

  Get the maximum value of the waveform.
- **`min`** –

  Get the minimum value of the waveform.

Attributes:

- **`duration`** (`float`) –

  Returns the duration of the waveform.
- **`params`** (`dict[str, float | ndarray]`) –

  Dictionary of parameters used by the waveform.
- **`waveforms`** (`list[Waveform]`) –

  Returns a list of the individual waveforms, which is just this waveform.

#### duration

```
duration: float
```

Returns the duration of the waveform.

#### params

```
params: dict[str, float | ndarray]
```

Dictionary of parameters used by the waveform.

#### waveforms

```
waveforms: list[Waveform]
```

Returns a list of the individual waveforms, which is just this waveform.

#### \_\_call\_\_

```
__call__(t: float) -> float
```

```
__call__(t: list[float] | ndarray) -> NDArray[float64]
```

```
__call__(
    t: float | list[float] | ndarray,
) -> float | NDArray[float64]
```

Evaluate the waveform at `t`: a single time, or a 1D list or array of times.

Returns a float for a single time, otherwise a 1D float64 array. Times outside \[0, duration\] give 0.

#### \_\_mul\_\_

```
__mul__(other: float) -> Waveform
```

Rescale this waveform by a scalar.

#### \_\_repr\_\_

```
__repr__() -> str
```

Return the time interval and the waveform with its parameters.

#### \_\_rmul\_\_

```
__rmul__(other: float) -> Waveform
```

Rescale this waveform by a scalar (right-hand multiplication).

#### \_\_rshift\_\_

```
__rshift__(other: Waveform) -> CompositeWaveform
```

Returns a new CompositeWaveform composed of this waveform and another.

#### draw

```
draw(
    ax: Axes | None = None,
    color: ColorType = "tab:blue",
    n_points: int = 250,
) -> None
```

Draw the waveform.

Parameters:

- **`ax`** (`Axes | None`, default: `None` ) –

  The axes to draw into. If None, a new pyplot figure is created.
- **`color`** (`ColorType`, default: `'tab:blue'` ) –

  The color of the line and the filled area. Defaults to matplotlib's "tab:blue".
- **`n_points`** (`int`, default: `250` ) –

  The number of time samples to draw. Defaults to 250.

#### function

```
function(t: float) -> float
```

Evaluates the waveform function at a given time t.

#### max

```
max() -> float
```

Get the maximum value of the waveform.

#### min

```
min() -> float
```

Get the minimum value of the waveform.

### DelayWaveform

```
DelayWaveform(duration: float, **kwargs: float | ndarray)
```

An empty waveform.

Parameters:

- **`duration`** (`float`) –

  the total duration of the waveform.
- **`**kwargs`** (`float | ndarray`, default: `{}` ) –

  optional keyword arguments for the waveform function.

Methods:

- **`__call__`** –

  Evaluate the waveform at `t`: a single time, or a 1D list or array of times.
- **`__mul__`** –

  Rescale this waveform by a scalar.
- **`__repr__`** –

  Return the time interval and the waveform with its parameters.
- **`__rmul__`** –

  Rescale this waveform by a scalar (right-hand multiplication).
- **`__rshift__`** –

  Returns a new CompositeWaveform composed of this waveform and another.
- **`draw`** –

  Draw the waveform.
- **`function`** –

  Evaluates the waveform function at a given time t.
- **`max`** –

  Get the maximum value of the waveform.
- **`min`** –

  Get the minimum value of the waveform.

Attributes:

- **`duration`** (`float`) –

  Returns the duration of the waveform.
- **`params`** (`dict[str, float | ndarray]`) –

  Dictionary of parameters used by the waveform.
- **`waveforms`** (`list[Waveform]`) –

  Returns a list of the individual waveforms, which is just this waveform.

#### duration

```
duration: float
```

Returns the duration of the waveform.

#### params

```
params: dict[str, float | ndarray]
```

Dictionary of parameters used by the waveform.

#### waveforms

```
waveforms: list[Waveform]
```

Returns a list of the individual waveforms, which is just this waveform.

#### \_\_call\_\_

```
__call__(t: float) -> float
```

```
__call__(t: list[float] | ndarray) -> NDArray[float64]
```

```
__call__(
    t: float | list[float] | ndarray,
) -> float | NDArray[float64]
```

Evaluate the waveform at `t`: a single time, or a 1D list or array of times.

Returns a float for a single time, otherwise a 1D float64 array. Times outside \[0, duration\] give 0.

#### \_\_mul\_\_

```
__mul__(other: float) -> Waveform
```

Rescale this waveform by a scalar.

#### \_\_repr\_\_

```
__repr__() -> str
```

Return the time interval and the waveform with its parameters.

#### \_\_rmul\_\_

```
__rmul__(other: float) -> Waveform
```

Rescale this waveform by a scalar (right-hand multiplication).

#### \_\_rshift\_\_

```
__rshift__(other: Waveform) -> CompositeWaveform
```

Returns a new CompositeWaveform composed of this waveform and another.

#### draw

```
draw(
    ax: Axes | None = None,
    color: ColorType = "tab:blue",
    n_points: int = 250,
) -> None
```

Draw the waveform.

Parameters:

- **`ax`** (`Axes | None`, default: `None` ) –

  The axes to draw into. If None, a new pyplot figure is created.
- **`color`** (`ColorType`, default: `'tab:blue'` ) –

  The color of the line and the filled area. Defaults to matplotlib's "tab:blue".
- **`n_points`** (`int`, default: `250` ) –

  The number of time samples to draw. Defaults to 250.

#### function

```
function(t: float) -> float
```

Evaluates the waveform function at a given time t.

#### max

```
max() -> float
```

Get the maximum value of the waveform.

#### min

```
min() -> float
```

Get the minimum value of the waveform.

### Device

```
Device(
    pulser_device: BaseDevice,
    default_converter: UnitConverter | None = None,
)
```

QoolQit Device wrapper around a Pulser BaseDevice.

Parameters:

- **`pulser_device`** (`BaseDevice`) –

  a `BaseDevice` to build the QoolQit device from.
- **`default_converter`** (`Optional[UnitConverter]`, default: `None` ) –

  optional unit converter to handle unit conversion.

Examples:

From Pulser device:

```
qoolqit_device = Device(pulser_device=pulser_device)
```

From remote Pulser device:

```
from pasqal_cloud import PasqalCloudConnection
from qoolqit import Device

# Fetch the remote device from the connection
connection = PasqalCloudConnection()
pulser_fresnel_device = connection.fetch_available_devices()["FRESNEL"]

# Wrap a Pulser device object into a QoolQit Device
fresnel_device = Device(pulser_device=PulserFresnelDevice)
```

From custom Pulser device:

```
from dataclasses import replace
from pulser import AnalogDevice
from qoolqit import Device

# Converting the pulser Device object in a VirtualDevice object
VirtualAnalog = AnalogDevice.to_virtual()
# Replacing desired values
ModdedAnalogDevice = replace(
    VirtualAnalog,
    max_radial_distance=100,
    max_sequence_duration=7000
    )

# Wrap a Pulser device object into a QoolQit Device
mod_analog_device = Device(pulser_device=ModdedAnalogDevice)
```

Methods:

- **`__repr__`** –

  Return the device name.
- **`__str__`** –

  Return the device name, description and specs.
- **`from_connection`** –

  Return the specified device from the selected device from a connection.
- **`info`** –

  Show the device short description and constraints.
- **`reset_converter`** –

  Resets the unit converter to the default one.
- **`set_distance_unit`** –

  Changes the unit converter according to a reference distance unit.
- **`set_energy_unit`** –

  Changes the unit converter according to a reference energy unit.

Attributes:

- **`converter`** (`UnitConverter`) –

  The unit converter currently used by the device.
- **`name`** (`str`) –

  The device name.
- **`phase_jump_time`** (`float`) –

  Time to change the phase between two consecutive pulses, in adimensional units.
- **`specs`** (`dict[str, float | None]`) –

  Return the device specification constraints.

#### converter

```
converter: UnitConverter
```

The unit converter currently used by the device.

#### name

```
name: str
```

The device name.

#### phase\_jump\_time

```
phase_jump_time: float
```

Time to change the phase between two consecutive pulses, in adimensional units.

Read from the global Rydberg channel.

#### specs

```
specs: dict[str, float | None]
```

Return the device specification constraints.

#### \_\_repr\_\_

```
__repr__() -> str
```

Return the device name.

#### \_\_str\_\_

```
__str__() -> str
```

Return the device name, description and specs.

#### from\_connection

```
from_connection(
    connection: RemoteConnection, name: str
) -> Device
```

Return the specified device from the selected device from a connection.

Available devices through the provided connection are can be seen with the `connection.fetch_available_devices()` method.

Parameters:

- **`connection`** (`RemoteConnection`) –

  connection object to fetch the available devices.
- **`name`** (`str`) –

  The name of the desired device.

Returns:

- **`Device`** ( `Device` ) –

  The requested device.

Raises:

- `ValueError` –

  If the requested device is not available through the provided connection.

Example:

```
from pasqal_cloud import PasqalCloudConnection
fresnel_device = Device.from_connection(connection=PasqalCloudConnection(), name="FRESNEL")
```

#### info

```
info() -> None
```

Show the device short description and constraints.

#### reset\_converter

```
reset_converter() -> None
```

Resets the unit converter to the default one.

#### set\_distance\_unit

```
set_distance_unit(distance: float) -> None
```

Changes the unit converter according to a reference distance unit.

#### set\_energy\_unit

```
set_energy_unit(energy: float) -> None
```

Changes the unit converter according to a reference energy unit.

### DigitalAnalogDevice

```
DigitalAnalogDevice()
```

A device with digital and analog capabilities.

Methods:

- **`__repr__`** –

  Return the device name.
- **`__str__`** –

  Return the device name, description and specs.
- **`from_connection`** –

  Return the specified device from the selected device from a connection.
- **`info`** –

  Show the device short description and constraints.
- **`reset_converter`** –

  Resets the unit converter to the default one.
- **`set_distance_unit`** –

  Changes the unit converter according to a reference distance unit.
- **`set_energy_unit`** –

  Changes the unit converter according to a reference energy unit.

Attributes:

- **`converter`** (`UnitConverter`) –

  The unit converter currently used by the device.
- **`name`** (`str`) –

  The device name.
- **`phase_jump_time`** (`float`) –

  Time to change the phase between two consecutive pulses, in adimensional units.
- **`specs`** (`dict[str, float | None]`) –

  Return the device specification constraints.

#### converter

```
converter: UnitConverter
```

The unit converter currently used by the device.

#### name

```
name: str
```

The device name.

#### phase\_jump\_time

```
phase_jump_time: float
```

Time to change the phase between two consecutive pulses, in adimensional units.

Read from the global Rydberg channel.

#### specs

```
specs: dict[str, float | None]
```

Return the device specification constraints.

#### \_\_repr\_\_

```
__repr__() -> str
```

Return the device name.

#### \_\_str\_\_

```
__str__() -> str
```

Return the device name, description and specs.

#### from\_connection

```
from_connection(
    connection: RemoteConnection, name: str
) -> Device
```

Return the specified device from the selected device from a connection.

Available devices through the provided connection are can be seen with the `connection.fetch_available_devices()` method.

Parameters:

- **`connection`** (`RemoteConnection`) –

  connection object to fetch the available devices.
- **`name`** (`str`) –

  The name of the desired device.

Returns:

- **`Device`** ( `Device` ) –

  The requested device.

Raises:

- `ValueError` –

  If the requested device is not available through the provided connection.

Example:

```
from pasqal_cloud import PasqalCloudConnection
fresnel_device = Device.from_connection(connection=PasqalCloudConnection(), name="FRESNEL")
```

#### info

```
info() -> None
```

Show the device short description and constraints.

#### reset\_converter

```
reset_converter() -> None
```

Resets the unit converter to the default one.

#### set\_distance\_unit

```
set_distance_unit(distance: float) -> None
```

Changes the unit converter according to a reference distance unit.

#### set\_energy\_unit

```
set_energy_unit(energy: float) -> None
```

Changes the unit converter according to a reference energy unit.

### Drive

```
Drive(
    *,
    amplitude: Waveform,
    detuning: Waveform | None = None,
    dmm: DetuningMapModulator | None = None,
    phase: float = 0.0,
)
```

The drive Hamiltonian acting over a duration.

The Drive specifies the control parameters for the time-dependent drive Hamiltonian in the Rydberg model (see [https://docs.pasqal.com/qoolqit/get\_started/qoolqit\_model/](<https://docs.pasqal.com/qoolqit/get_started/qoolqit_model/>) for details),

H\_drive(t) = Σᵢ \[Ω(t)/2 (cos φ(t) σˣᵢ - sin φ(t) σʸᵢ)\] - Σᵢ \[δ(t) + εᵢ Δ(t)\] nᵢ

representing: - Amplitude Ω(t): Controls the Rabi frequency that drives qubits. - Detuning δ(t): Controls the energy offset of the Rydberg state. - dmm εᵢ, Δ(t): Detuning Map Modulator (DMM) for additional qubit-specific detunings. - Phase φ: Global phase applied to the amplitude term.

Parameters:

- **`amplitude`** (`Waveform`) –

  Time-dependent amplitude waveform Ω(t) representing the Rabi frequency. Controls the strength of the coupling between ground and Rydberg states. Must be positive for all times.
- **`detuning`** (`Waveform | None`, default: `None` ) –

  Time-dependent detuning waveform δ(t) representing the energy offset of the Rydberg state relative to resonance. If None, defaults to zero detuning (Delay waveform) for the duration of the amplitude.
- **`dmm`** (`DetuningMapModulator | None`, default: `None` ) –

  DetuningMapModulator instance for additional negative detuning waveform Δ(t) ≤ 0 applied to individual qubits as specified by its `weights` attribute εᵢ.
- **`phase`** (`float`, default: `0.0` ) –

  Global phase φ applied to the amplitude term in the Hamiltonian. Defaults to 0.0 (no phase). Normalized to \[0, 2π) and stored as a ConstantWaveform spanning the full duration of the drive.

Raises:

- `TypeError` –

  If amplitude or detuning are not Waveform instances.
- `ValueError` –

  If the amplitude waveform has negative values, or if the phase is not finite.

> [!NOTE]
>
> - All arguments must be passed as keyword arguments.
> - If amplitude and detuning have different durations, the shorter one is automatically extended with a Delay to match the longer duration.
> - DetuningMapModulator waveform must be negative for all times (≤ 0) as it represents energy shifts below the resonance.

> [!NOTE]
>
> **Example**
>
> > > > from qoolqit import Drive from qoolqit.waveforms import ConstantWaveform, RampWaveform
> > > >
> > > > #### Simple constant drive
> > > >
> > > > drive = Drive(amplitude=ConstantWaveform(10.0, 1.5))
> > > >
> > > > #### Drive with time-varying amplitude and detuning
> > > >
> > > > amp = RampWaveform(5.0, 0.0, 2.0) det = ConstantWaveform(5.0, -1.0) drive = Drive(amplitude=amp, detuning=det, phase=0.5)

Methods:

- **`__repr__`** –

  Return a multi-line summary of the drive waveforms.
- **`__rshift__`** –

  Concatenate two drives in time: `self` followed by `other`.
- **`draw`** –

  Draw the amplitude, detuning, phase and DMM of the Drive.

Attributes:

- **`amplitude`** (`Waveform`) –

  The amplitude waveform in the drive.
- **`detuning`** (`Waveform`) –

  The detuning waveform in the drive.
- **`dmm`** (`DetuningMapModulator | None`) –

  Detuning Map Modulator (DMM) applied to individual qubits.
- **`duration`** (`float`) –

  The total duration of the drive.
- **`phase`** (`ConstantWaveform`) –

  The phase waveform in the drive.

#### amplitude

```
amplitude: Waveform
```

The amplitude waveform in the drive.

#### detuning

```
detuning: Waveform
```

The detuning waveform in the drive.

#### dmm

```
dmm: DetuningMapModulator | None
```

Detuning Map Modulator (DMM) applied to individual qubits.

#### duration

```
duration: float
```

The total duration of the drive.

#### phase

```
phase: ConstantWaveform
```

The phase waveform in the drive.

#### \_\_repr\_\_

```
__repr__() -> str
```

Return a multi-line summary of the drive waveforms.

#### \_\_rshift\_\_

```
__rshift__(other: Drive) -> Drive
```

Concatenate two drives in time: `self` followed by `other`.

Not supported for drives with a DMM or with different phases.

#### draw

```
draw(fig: FigureBase | None = None) -> None
```

Draw the amplitude, detuning, phase and DMM of the Drive.

The phase is drawn only if it is non-zero, and the DMM only if one is set.

Parameters:

- **`fig`** (`FigureBase | None`, default: `None` ) –

  The figure or subfigure to draw into. If None, a new pyplot figure is created.

### InterpolatedWaveform

```
InterpolatedWaveform(
    duration: float,
    values: ArrayLike,
    times: ArrayLike | None = None,
)
```

A waveform created from shape-preserving interpolation of data points.

This class creates a smooth waveform by interpolating between specified data points using PCHIP (Piecewise Cubic Hermite Interpolating Polynomial) interpolation. The interpolating curve preserves the shape of the input data: bounds (avoiding under/overshooting), monotonicity, and convexity.

Uses scipy's PchipInterpolator for the interpolation.

Attributes:

- **`duration`** (`float`) –

  The waveform duration.
- **`values`** (`float`) –

  Array-like sequence of waveform values at the interpolation points. Must be convertible to float. These values define the amplitude of the waveform at the corresponding time points.
- **`times`** (`float`) –

  Optional array-like sequence of fractional times in the range \[0, 1\] indicating where to place each value on the time axis. Must have the same length as `values`. If not provided, values are distributed evenly across the waveform duration. Default is None.

ValueError: If `times` contains values outside \[0, 1\] or if `times` and `values` have different lengths.

> [!NOTE]
>
> **Example**
>
> > > > #### Create a waveform with 4 points over 100ns
> > > >
> > > > values = \[0.0, 1.0, 0.5, 0.0\] wf = InterpolatedWaveform(100, values)
> > > >
> > > > #### Create with custom timing
> > > >
> > > > times = \[0.0, 0.2, 0.8, 1.0\] \# Non-uniform spacing wf = InterpolatedWaveform(100, values, times)

Parameters:

- **`duration`** (`float`) –

  The total duration of the waveform. Must be positive.
- **`values`** (`ArrayLike`) –

  Array-like sequence of waveform values at interpolation points. Can be a list, tuple, numpy array, or any sequence convertible to float.
- **`times`** (`ArrayLike | None`, default: `None` ) –

  Optional array-like sequence of fractional times in \[0, 1\]. If provided, must have the same length as `values`. If None, values are evenly spaced across the duration. Default is None.

Raises:

- `ValueError` –

  If any value in `times` is outside \[0, 1\], or if `times` and `values` have different lengths.

Methods:

- **`__call__`** –

  Evaluate the waveform at `t`: a single time, or a 1D list or array of times.
- **`__mul__`** –

  Rescale this waveform by a scalar.
- **`__repr__`** –

  Return the time interval and the waveform with its parameters.
- **`__rmul__`** –

  Rescale this waveform by a scalar (right-hand multiplication).
- **`__rshift__`** –

  Returns a new CompositeWaveform composed of this waveform and another.
- **`draw`** –

  Draw the waveform.
- **`function`** –

  Evaluates the waveform function at a given time t.
- **`max`** –

  Get the maximum value of the waveform.
- **`min`** –

  Get the minimum value of the waveform.

#### duration

```
duration: float
```

Returns the duration of the waveform.

#### params

```
params: dict[str, float | ndarray]
```

Dictionary of parameters used by the waveform.

#### waveforms

```
waveforms: list[Waveform]
```

Returns a list of the individual waveforms, which is just this waveform.

#### \_\_call\_\_

```
__call__(t: float) -> float
```

```
__call__(t: list[float] | ndarray) -> NDArray[float64]
```

```
__call__(
    t: float | list[float] | ndarray,
) -> float | NDArray[float64]
```

Evaluate the waveform at `t`: a single time, or a 1D list or array of times.

Returns a float for a single time, otherwise a 1D float64 array. Times outside \[0, duration\] give 0.

#### \_\_mul\_\_

```
__mul__(other: float) -> Waveform
```

Rescale this waveform by a scalar.

#### \_\_repr\_\_

```
__repr__() -> str
```

Return the time interval and the waveform with its parameters.

#### \_\_rmul\_\_

```
__rmul__(other: float) -> Waveform
```

Rescale this waveform by a scalar (right-hand multiplication).

#### \_\_rshift\_\_

```
__rshift__(other: Waveform) -> CompositeWaveform
```

Returns a new CompositeWaveform composed of this waveform and another.

#### draw

```
draw(
    ax: Axes | None = None,
    color: ColorType = "tab:blue",
    n_points: int = 250,
) -> None
```

Draw the waveform.

Parameters:

- **`ax`** (`Axes | None`, default: `None` ) –

  The axes to draw into. If None, a new pyplot figure is created.
- **`color`** (`ColorType`, default: `'tab:blue'` ) –

  The color of the line and the filled area. Defaults to matplotlib's "tab:blue".
- **`n_points`** (`int`, default: `250` ) –

  The number of time samples to draw. Defaults to 250.

#### function

```
function(t: float) -> float
```

Evaluates the waveform function at a given time t.

#### max

```
max() -> float
```

Get the maximum value of the waveform.

#### min

```
min() -> float
```

Get the minimum value of the waveform.

### MockDevice

```
MockDevice()
```

A virtual device for unconstrained prototyping.

Methods:

- **`__repr__`** –

  Return the device name.
- **`__str__`** –

  Return the device name, description and specs.
- **`from_connection`** –

  Return the specified device from the selected device from a connection.
- **`info`** –

  Show the device short description and constraints.
- **`reset_converter`** –

  Resets the unit converter to the default one.
- **`set_distance_unit`** –

  Changes the unit converter according to a reference distance unit.
- **`set_energy_unit`** –

  Changes the unit converter according to a reference energy unit.

Attributes:

- **`converter`** (`UnitConverter`) –

  The unit converter currently used by the device.
- **`name`** (`str`) –

  The device name.
- **`phase_jump_time`** (`float`) –

  Time to change the phase between two consecutive pulses, in adimensional units.
- **`specs`** (`dict[str, float | None]`) –

  Return the device specification constraints.

#### converter

```
converter: UnitConverter
```

The unit converter currently used by the device.

#### name

```
name: str
```

The device name.

#### phase\_jump\_time

```
phase_jump_time: float
```

Time to change the phase between two consecutive pulses, in adimensional units.

Read from the global Rydberg channel.

#### specs

```
specs: dict[str, float | None]
```

Return the device specification constraints.

#### \_\_repr\_\_

```
__repr__() -> str
```

Return the device name.

#### \_\_str\_\_

```
__str__() -> str
```

Return the device name, description and specs.

#### from\_connection

```
from_connection(
    connection: RemoteConnection, name: str
) -> Device
```

Return the specified device from the selected device from a connection.

Available devices through the provided connection are can be seen with the `connection.fetch_available_devices()` method.

Parameters:

- **`connection`** (`RemoteConnection`) –

  connection object to fetch the available devices.
- **`name`** (`str`) –

  The name of the desired device.

Returns:

- **`Device`** ( `Device` ) –

  The requested device.

Raises:

- `ValueError` –

  If the requested device is not available through the provided connection.

Example:

```
from pasqal_cloud import PasqalCloudConnection
fresnel_device = Device.from_connection(connection=PasqalCloudConnection(), name="FRESNEL")
```

#### info

```
info() -> None
```

Show the device short description and constraints.

#### reset\_converter

```
reset_converter() -> None
```

Resets the unit converter to the default one.

#### set\_distance\_unit

```
set_distance_unit(distance: float) -> None
```

Changes the unit converter according to a reference distance unit.

#### set\_energy\_unit

```
set_energy_unit(energy: float) -> None
```

Changes the unit converter according to a reference energy unit.

### PiecewiseLinearWaveform

```
PiecewiseLinearWaveform(
    durations: list[float] | tuple[float, ...] | ndarray,
    values: list[float] | tuple[float, ...] | ndarray,
)
```

A piecewise linear waveform.

Creates a composite waveform of N ramps that linearly interpolate through the given N+1 values.

Parameters:

- **`durations`** (`list[float] | tuple[float, ...] | ndarray`) –

  list or tuple of N duration values.
- **`values`** (`list[float] | tuple[float, ...] | ndarray`) –

  list or tuple of N+1 waveform values.

Methods:

- **`__call__`** –

  Evaluate the waveform at `t`: a single time, or a 1D list or array of times.
- **`__mul__`** –

  Rescale this waveform by a scalar.
- **`__repr__`** –

  Return each sub-waveform with its time interval, one per line.
- **`__rmul__`** –

  Rescale this waveform by a scalar (right-hand multiplication).
- **`__rshift__`** –

  Returns a new CompositeWaveform composed of this waveform and another.
- **`draw`** –

  Draw the waveform.
- **`function`** –

  Evaluates the waveform function at a given time t.
- **`max`** –

  Get the maximum value of the waveform.
- **`min`** –

  Get the minimum value of the waveform.

Attributes:

- **`duration`** (`float`) –

  Returns the duration of the waveform.
- **`durations`** (`list[float]`) –

  Returns the list of durations of each individual waveform.
- **`n_waveforms`** (`int`) –

  Returns the number of waveforms.
- **`params`** (`dict[str, float | ndarray]`) –

  Dictionary of parameters used by the waveform.
- **`times`** (`list[float]`) –

  Returns the list of times when each individual waveform starts.
- **`waveforms`** (`list[Waveform]`) –

  Returns a list of the individual waveforms.

#### duration

```
duration: float
```

Returns the duration of the waveform.

#### durations

```
durations: list[float]
```

Returns the list of durations of each individual waveform.

#### n\_waveforms

```
n_waveforms: int
```

Returns the number of waveforms.

#### params

```
params: dict[str, float | ndarray]
```

Dictionary of parameters used by the waveform.

#### times

```
times: list[float]
```

Returns the list of times when each individual waveform starts.

#### waveforms

```
waveforms: list[Waveform]
```

Returns a list of the individual waveforms.

#### \_\_call\_\_

```
__call__(t: float) -> float
```

```
__call__(t: list[float] | ndarray) -> NDArray[float64]
```

```
__call__(
    t: float | list[float] | ndarray,
) -> float | NDArray[float64]
```

Evaluate the waveform at `t`: a single time, or a 1D list or array of times.

Returns a float for a single time, otherwise a 1D float64 array. Times outside \[0, duration\] give 0.

#### \_\_mul\_\_

```
__mul__(other: float) -> CompositeWaveform
```

Rescale this waveform by a scalar.

#### \_\_repr\_\_

```
__repr__() -> str
```

Return each sub-waveform with its time interval, one per line.

#### \_\_rmul\_\_

```
__rmul__(other: float) -> Waveform
```

Rescale this waveform by a scalar (right-hand multiplication).

#### \_\_rshift\_\_

```
__rshift__(other: Waveform) -> CompositeWaveform
```

Returns a new CompositeWaveform composed of this waveform and another.

#### draw

```
draw(
    ax: Axes | None = None,
    color: ColorType = "tab:blue",
    n_points: int = 250,
) -> None
```

Draw the waveform.

Parameters:

- **`ax`** (`Axes | None`, default: `None` ) –

  The axes to draw into. If None, a new pyplot figure is created.
- **`color`** (`ColorType`, default: `'tab:blue'` ) –

  The color of the line and the filled area. Defaults to matplotlib's "tab:blue".
- **`n_points`** (`int`, default: `250` ) –

  The number of time samples to draw. Defaults to 250.

#### function

```
function(t: float) -> float
```

Evaluates the waveform function at a given time t.

#### max

```
max() -> float
```

Get the maximum value of the waveform.

#### min

```
min() -> float
```

Get the minimum value of the waveform.

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

### RampWaveform

```
RampWaveform(
    duration: float,
    initial_value: float,
    final_value: float,
)
```

A ramp that linearly interpolates between an initial and final value.

Parameters:

- **`duration`** (`float`) –

  the total duration.
- **`initial_value`** (`float`) –

  the initial value at t = 0.
- **`final_value`** (`float`) –

  the final value at t = duration.

Methods:

- **`__call__`** –

  Evaluate the waveform at `t`: a single time, or a 1D list or array of times.
- **`__mul__`** –

  Rescale this waveform by a scalar.
- **`__repr__`** –

  Return the time interval and the waveform with its parameters.
- **`__rmul__`** –

  Rescale this waveform by a scalar (right-hand multiplication).
- **`__rshift__`** –

  Returns a new CompositeWaveform composed of this waveform and another.
- **`draw`** –

  Draw the waveform.
- **`function`** –

  Evaluates the waveform function at a given time t.
- **`max`** –

  Get the maximum value of the waveform.
- **`min`** –

  Get the minimum value of the waveform.

Attributes:

- **`duration`** (`float`) –

  Returns the duration of the waveform.
- **`params`** (`dict[str, float | ndarray]`) –

  Dictionary of parameters used by the waveform.
- **`waveforms`** (`list[Waveform]`) –

  Returns a list of the individual waveforms, which is just this waveform.

#### duration

```
duration: float
```

Returns the duration of the waveform.

#### params

```
params: dict[str, float | ndarray]
```

Dictionary of parameters used by the waveform.

#### waveforms

```
waveforms: list[Waveform]
```

Returns a list of the individual waveforms, which is just this waveform.

#### \_\_call\_\_

```
__call__(t: float) -> float
```

```
__call__(t: list[float] | ndarray) -> NDArray[float64]
```

```
__call__(
    t: float | list[float] | ndarray,
) -> float | NDArray[float64]
```

Evaluate the waveform at `t`: a single time, or a 1D list or array of times.

Returns a float for a single time, otherwise a 1D float64 array. Times outside \[0, duration\] give 0.

#### \_\_mul\_\_

```
__mul__(other: float) -> Waveform
```

Rescale this waveform by a scalar.

#### \_\_repr\_\_

```
__repr__() -> str
```

Return the time interval and the waveform with its parameters.

#### \_\_rmul\_\_

```
__rmul__(other: float) -> Waveform
```

Rescale this waveform by a scalar (right-hand multiplication).

#### \_\_rshift\_\_

```
__rshift__(other: Waveform) -> CompositeWaveform
```

Returns a new CompositeWaveform composed of this waveform and another.

#### draw

```
draw(
    ax: Axes | None = None,
    color: ColorType = "tab:blue",
    n_points: int = 250,
) -> None
```

Draw the waveform.

Parameters:

- **`ax`** (`Axes | None`, default: `None` ) –

  The axes to draw into. If None, a new pyplot figure is created.
- **`color`** (`ColorType`, default: `'tab:blue'` ) –

  The color of the line and the filled area. Defaults to matplotlib's "tab:blue".
- **`n_points`** (`int`, default: `250` ) –

  The number of time samples to draw. Defaults to 250.

#### function

```
function(t: float) -> float
```

Evaluates the waveform function at a given time t.

#### max

```
max() -> float
```

Get the maximum value of the waveform.

#### min

```
min() -> float
```

Get the minimum value of the waveform.

### Register

```
Register(
    qubits: Mapping[
        str, Sequence[float] | NDArray[float64] | Tensor
    ]
    | Mapping[
        int, Sequence[float] | NDArray[float64] | Tensor
    ],
)
```

A QoolQit register mapping qubit IDs to 2D coordinates.

Examples:

From a dictionary of qubit IDs and coordinates:

```
>>> reg = Register({"a": (0.0, 0.0), "b": (1.0, 0.0), "c": (0.0, 1.0)})
>>> reg = Register({0: (0.0, 0.0), 1: (1.0, 0.0), 2: (0.0, 1.0)})
```

From a list of coordinates (qubit IDs are assigned automatically as strings "0", "1", ...):

```
>>> reg = Register.from_coordinates([(0.0, 0.0), (1.0, 0.0), (0.0, 1.0)])
```

Using numpy arrays as coordinates:

```
>>> import numpy as np
>>> reg = Register({"a": np.array([0.0, 0.0]), "b": np.array([1.0, 0.0])})
```

Using torch tensors as coordinates:

```
>>> import torch
>>> reg = Register({"a": torch.tensor([0.0, 0.0]), "b": torch.tensor([1.0, 0.0])})
```

Parameters:

- **`qubits`** (`Mapping[str, Sequence[float] | NDArray[float64] | Tensor] | Mapping[int, Sequence[float] | NDArray[float64] | Tensor]`) –

  a dictionary of qubits and respective 2D coordinates {q: (x, y), ...}. Each coordinate must be castable to a numpy or torch array of shape (2,).

Raises:

- `TypeError` –

  If `qubits` is not a Mapping.
- `ValueError` –

  If `qubits` dictionary is empty.
- `ValueError` –

  If a qubit coordinate cannot be converted to an array of floats, or if the converted coordinate is not a point in 2D.

Methods:

- **`__len__`** –

  Return the number of qubits.
- **`__repr__`** –

  Return the class name and number of qubits.
- **`circle`** –

  Initializes a Register with qubits arranged in a circle.
- **`distances`** –

  Distance between each qubit pair.
- **`draw`** –

  Draw the register.
- **`from_coordinates`** –

  Initializes a Register from a sequence or array of coordinates.
- **`from_graph`** –

  Initializes a Register from a graph that has coordinates.
- **`interaction_matrix`** –

  Interaction 1/r^6 between each qubit pair, as a matrix (0 on the diagonal).
- **`interactions`** –

  Interaction 1/r^6 between each qubit pair.
- **`line`** –

  Initializes a Register with qubits arranged in a line.
- **`max_radial_distance`** –

  Maximum radial distance between all qubits.
- **`min_distance`** –

  Minimum distance between all qubit pairs.
- **`radial_distances`** –

  Radial distance of each qubit from the origin.
- **`rectangular`** –

  Initializes a rectangular Register of qubits.
- **`square`** –

  Initializes a square Register of qubits.
- **`triangular`** –

  Initializes a triangular lattice Register of qubits.

Attributes:

- **`n_qubits`** (`int`) –

  Number of qubits in the Register.
- **`qubits`** (`dict`) –

  Returns a dictionary of qubits and respective coordinates.
- **`qubits_ids`** (`tuple[str | int, ...]`) –

  Returns the qubit IDs.

#### n\_qubits

```
n_qubits: int
```

Number of qubits in the Register.

#### qubits

```
qubits: dict
```

Returns a dictionary of qubits and respective coordinates.

#### qubits\_ids

```
qubits_ids: tuple[str | int, ...]
```

Returns the qubit IDs.

#### \_\_len\_\_

```
__len__() -> int
```

Return the number of qubits.

#### \_\_repr\_\_

```
__repr__() -> str
```

Return the class name and number of qubits.

#### circle

```
circle(n: int, spacing: float = 1.0) -> Register
```

Initializes a Register with qubits arranged in a circle.

Parameters:

- **`n`** (`int`) –

  number of qubits to place in the circle.
- **`spacing`** (`float`, default: `1.0` ) –

  distance between adjacent qubits. Defaults to 1.0.

#### distances

```
distances() -> dict
```

Distance between each qubit pair.

#### draw

```
draw(
    ax: Axes | None = None,
    marker_size: int = 100,
    node_color: str = "tab:green",
) -> None
```

Draw the register.

Parameters:

- **`ax`** (`Axes | None`, default: `None` ) –

  an optional matplotlib Axes instance to draw on. If None, a new Axes will be created.
- **`marker_size`** (`int`, default: `100` ) –

  size of the qubit markers in points squared. Defaults to 100.
- **`node_color`** (`str`, default: `'tab:green'` ) –

  color of the qubit markers. Defaults to "tab:green".

#### from\_coordinates

```
from_coordinates(
    coords: Sequence[
        Sequence[float] | NDArray[float64] | Tensor
    ]
    | NDArray[float64]
    | Tensor,
) -> Register
```

Initializes a Register from a sequence or array of coordinates.

Qubit IDs are assigned as integers 0,1,...,N-1, where N is the number of coordinates.

Parameters:

- **`coords`** (`Sequence[Sequence[float] | NDArray[float64] | Tensor] | NDArray[float64] | Tensor`) –

  a sequence of 2D coordinates, i.e. \[(x, y), ...\]. Each coordinate must be castable to a numpy or torch array of shape (2,). If `coords` is a numpy array or a torch tensor, it must be 2D and of shape (N, 2).

Raises:

- `TypeError` –

  If `coords` is a Mapping.

#### from\_graph

```
from_graph(graph: DataGraph) -> Register
```

Initializes a Register from a graph that has coordinates.

Parameters:

- **`graph`** (`DataGraph`) –

  a DataGraph instance.

#### interaction\_matrix

```
interaction_matrix() -> NDArray[float64] | Tensor
```

Interaction 1/r^6 between each qubit pair, as a matrix (0 on the diagonal).

#### interactions

```
interactions() -> dict
```

Interaction 1/r^6 between each qubit pair.

#### line

```
line(n: int, spacing: float = 1.0) -> Register
```

Initializes a Register with qubits arranged in a line.

Parameters:

- **`n`** (`int`) –

  number of qubits to place in the line.
- **`spacing`** (`float`, default: `1.0` ) –

  distance between adjacent qubits. Defaults to 1.0.

#### max\_radial\_distance

```
max_radial_distance() -> float
```

Maximum radial distance between all qubits.

#### min\_distance

```
min_distance() -> float
```

Minimum distance between all qubit pairs.

#### radial\_distances

```
radial_distances() -> dict
```

Radial distance of each qubit from the origin.

#### rectangular

```
rectangular(
    rows: int,
    cols: int,
    row_spacing: float = 1.0,
    col_spacing: float = 1.0,
) -> Register
```

Initializes a rectangular Register of qubits.

Parameters:

- **`rows`** (`int`) –

  number of rows in the rectangle.
- **`cols`** (`int`) –

  number of columns in the rectangle.
- **`row_spacing`** (`float`, default: `1.0` ) –

  distance between adjacent qubits in the row direction. Defaults to 1.0.
- **`col_spacing`** (`float`, default: `1.0` ) –

  distance between adjacent qubits in the column direction. Defaults to 1.0.

#### square

```
square(n: int, spacing: float = 1.0) -> Register
```

Initializes a square Register of qubits.

Parameters:

- **`n`** (`int`) –

  number of qubits along each side of the square.
- **`spacing`** (`float`, default: `1.0` ) –

  distance between adjacent qubits. Defaults to 1.0.

#### triangular

```
triangular(
    rows: int, atoms_per_row: int, spacing: float = 1.0
) -> Register
```

Initializes a triangular lattice Register of qubits.

Parameters:

- **`rows`** (`int`) –

  number of rows in the lattice.
- **`atoms_per_row`** (`int`) –

  number of qubits per row.
- **`spacing`** (`float`, default: `1.0` ) –

  distance between adjacent qubits. Defaults to 1.0.

### SequenceCompiler

```
SequenceCompiler(
    register: Register,
    drive: Drive,
    device: Device,
    profile: CompilerProfile,
    device_max_duration_ratio: float | None = None,
)
```

Compiles a QoolQit Register and Drive to a Device.

Parameters:

- **`register`** (`Register`) –

  the QoolQit Register.
- **`drive`** (`Drive`) –

  the QoolQit Drive.
- **`device`** (`Device`) –

  the QoolQit Device.
- **`profile`** (`CompilerProfile`) –

  the CompilerProfile to use.
- **`device_max_duration_ratio`** (`float | None`, default: `None` ) –

  optionally set the program duration to a fraction of the device's maximum allowed duration.

Methods:

- **`compile_sequence`** –

  Compiles the register and drive into a Pulser sequence.

Attributes:

- **`device`** (`Device`) –

  The target QoolQit device.
- **`device_max_duration_ratio`** (`float | None`) –

  Fraction of the device's maximum duration to use, if set.
- **`drive`** (`Drive`) –

  The QoolQit drive to compile.
- **`profile`** (`CompilerProfile`) –

  The compiler profile used for compilation.
- **`register`** (`Register`) –

  The QoolQit register to compile.

#### device

```
device: Device
```

The target QoolQit device.

#### device\_max\_duration\_ratio

```
device_max_duration_ratio: float | None
```

Fraction of the device's maximum duration to use, if set.

#### drive

```
drive: Drive
```

The QoolQit drive to compile.

#### profile

```
profile: CompilerProfile
```

The compiler profile used for compilation.

#### register

```
register: Register
```

The QoolQit register to compile.

#### compile\_sequence

```
compile_sequence() -> Sequence
```

Compiles the register and drive into a Pulser sequence.

Raises:

- `CompilationError` –

  if compilation fails.

### available\_default\_devices

```
available_default_devices() -> None
```

Show the default available devices in QooQit.
