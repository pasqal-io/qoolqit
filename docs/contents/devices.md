# Initializing quantum devices

Each `Device` in QoolQit wraps a Pulser device and defines the hardware characteristics that the program will be compiled to and later executed on.

```python exec="on" source="material-block" session="devices"
from qoolqit import MockDevice, AnalogDevice, DigitalAnalogDevice

# An example of a mock device with no hardware constrains
device_ideal = MockDevice()

# An example of a real device
device_real = AnalogDevice()

# An example of a real device with digital-analog capabilities.
device_real_digital = DigitalAnalogDevice()
```

Besides available default devices, relevant for QPU emulation, new QPU devices can be:
- imported remotely
- created from custom Pulser devices

### Fetching a QoolQit device from a connection
Depending on your provider you might have different QPUs available to launch your quantum program to.
The list of available ones can be fetched through the specific connection handler object, with the generic `connection.fetch_available_devices()` method.
For the Pasqal Cloud service, for example, creating a QoolQit device from a connection object, simply reads as:

```python exec="on" source="material-block" result="json" session="devices"
from pulser_pasqal import PasqalCloud
from qoolqit import Device

connection = PasqalCloud()
print(connection.fetch_available_devices())

# fetch QoolQit device
fresnel_device = Device.from_connection(connection=connection, name="FRESNEL")
print(fresnel_device)   # markdown-exec: hide
```

### Create a QoolQit device from a Pulser device
A custom QoolQit device can be also built straight from any Pulser device, with any desired specification.
Please, refer to [Pulser documentation](https://docs.pasqal.com/pulser/tutorials/virtual_devices/) to learn how to make a custom device.

```python exec="on" source="material-block" result="json" session="devices"
from dataclasses import replace
from pulser import AnalogDevice
from qoolqit import Device

# Converting the pulser Device object in a VirtualDevice object
VirtualAnalog = AnalogDevice.to_virtual()
# Replacing desired values
ModdedAnalogDevice = replace(VirtualAnalog, max_radial_distance=100, max_sequence_duration=7000)

# Wrap a Pulser device object into a QoolQit Device
mod_analog_device = Device(pulser_device=ModdedAnalogDevice)
print(mod_analog_device)  # markdown-exec: hide
```

## Unit conversion

Each device has a default unit converter. These are the unit values used when converting an adimensional program in the Rydberg analog model to the physical units of Pulser devices for hardware execution.

```python exec="on" source="material-block" result="json" session="devices"
device_real.converter

print(device_real.converter)  # markdown-exec: hide
```

The converter handles the logic of converting the adimensional QoolQit model to Pulser units. For theoretical details on how this conversion works between the Rydberg analog model and the implementation that Pulser uses you can check the [Rydberg analog model page](../theory/rydberg_model.md).

By default, each device creates a default converter where the **energy unit** is set as that device’s **maximum amplitude**. If you make no changes to the device’s converter, this means that amplitude values in the range \( [0, 1] \) will be converted to values in the range \( [0, \Omega_{\max}] \).

### Customizing units

For advanced users, customizing the unit conversion factors is possible.

```python exec="on" source="material-block" result="json" session="devices"
device_real.set_time_unit(50.0)
print(device_real.converter)  # markdown-exec: hide

device_real.set_energy_unit(10.0)
print(device_real.converter)  # markdown-exec: hide

device_real.set_distance_unit(6.0)
print(device_real.converter)  # markdown-exec: hide
```

### Restoring defaults

You can always restore the default converter:

```python exec="on" source="material-block" result="json" session="devices"
device_real.reset_converter()
print(device_real.converter)  # markdown-exec: hide
```
