# Initializing a quantum device

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

## Create a QoolQit device from a Pulser device
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

# Compilation

Once a `QuantumProgram` is defined and a `Device` is selected one can proceed with the compilation by means of the method `compile_to`. This method will execute what has been discussed in the [introduction](./rationale.md) mapping adimensional parameters to physical quantities according to specific default rules.

```python exec="on" source="material-block" result="json" session="drives"
from qoolqit import PiecewiseLinear
from qoolqit import Register, Drive, QuantumProgram
from qoolqit import AnalogDevice

# Defining the Drive
wf0 = PiecewiseLinear([1.0, 2.0, 1.0], [0.0, 0.5, 0.5, 0.0])
wf1 = PiecewiseLinear([1.0, 2.0, 1.0], [-1.0, -1.0, 1.0, 1.0])
drive = Drive(amplitude = wf0, detuning = wf1)

# Defining the Register
coords = [(0.0, 0.0), (0.0, 1.0), (1.0, 0.0), (1.0, 1.0)]
register = Register.from_coordinates(coords)

# Creating the Program
program = QuantumProgram(register, drive)
device = AnalogDevice()

# Compilation to AnalogDevice
program.compile_to(device)
print(program) # markdown-exec: hide
```

Now that the program has been compiled, we can inspect the compiled sequence, which is an instance of a Pulser `Sequence`.

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
