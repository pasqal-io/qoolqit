# Initializing quantum devices

Each `Device` in QoolQit wraps a [Pulser](https://pulser.readthedocs.io/en/stable/tutorials/virtual_devices.html#) device and defines the hardware characteristics that the program will be compiled to and later executed on.

```python exec="on" source="material-block" session="devices"
from qoolqit import MockDevice, AnalogDevice, DigitalAnalogDevice

# An example of a mock device with no hardware constraints
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
A custom QoolQit device can also be built straight from any Pulser device, with any desired specification.
Please, refer to [Pulser documentation](https://docs.pasqal.com/pulser/tutorials/virtual_devices/) to learn how to make a custom device.

```python exec="on" source="material-block" result="json" session="devices"
from dataclasses import replace
from pulser import AnalogDevice
from qoolqit import Device

# Converting the pulser Device object into a VirtualDevice object
VirtualAnalog = AnalogDevice.to_virtual()
# Replacing desired values
ModdedAnalogDevice = replace(VirtualAnalog, max_radial_distance=100, max_sequence_duration=7000)

# Wrap a Pulser device object into a QoolQit Device
mod_analog_device = Device(pulser_device=ModdedAnalogDevice)
print(mod_analog_device)  # markdown-exec: hide
```
