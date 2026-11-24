## devices

Neutral-atom devices and their physical constraints.

Modules:

- **`device`** –

  QoolQit devices: hardware specs with adimensional unit conversion, plus built-in devices.
- **`unit_converter`** –

  Conversion factors between QoolQit's adimensional units and Pulser's physical units.

Classes:

- **`AnalogDevice`** –

  A realistic device for analog sequence execution.
- **`AnalogDeviceWithDMM`** –

  A realistic device with DMM for analog sequence execution.
- **`Device`** –

  QoolQit Device wrapper around a Pulser BaseDevice.
- **`DigitalAnalogDevice`** –

  A device with digital and analog capabilities.
- **`MockDevice`** –

  A virtual device for unconstrained prototyping.

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

### available\_default\_devices

```
available_default_devices() -> None
```

Show the default available devices in QooQit.
