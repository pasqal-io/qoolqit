## Initializing a quantum device

Each `Device` in QoolQit wraps a [Pulser](<https://pulser.readthedocs.io/en/stable/tutorials/virtual_devices.html#>) device and defines the hardware characteristics that the program will be compiled to and later executed on.

```
from qoolqit import AnalogDevice, AnalogDeviceWithDMM, MockDevice

# An example of a mock device with no hardware constraints
device_ideal = MockDevice()

# An example of a real device
device_real = AnalogDevice()

# An example of a real device with a DMM channel.
device_real_digital = AnalogDeviceWithDMM()
```

The updated list of available devices is given below:

```
from qoolqit import available_default_devices

available_default_devices()
```

```
AnalogDevice: A realistic device for analog sequence execution.
 └── max_duration: 332.43763968
 └── max_amplitude: 0.22680411206965717
 └── max_abs_detuning: 2.268041120696572
 └── min_distance: 1.0
 └── max_radial_distance: 7.6

AnalogDeviceWithDMM: 
 └── max_duration: 332.43763968
 └── max_amplitude: 0.22680411206965717
 └── max_abs_detuning: 2.268041120696572
 └── min_distance: 1.0
 └── max_radial_distance: 7.6

MockDevice: A virtual device for unconstrained prototyping.
 └── max_duration: None
 └── max_amplitude: None
 └── max_abs_detuning: None
 └── min_distance: 0.0
 └── max_radial_distance: None
```

Besides available default devices, relevant for QPU emulation, new QPU devices can be: - imported remotely - created from custom Pulser devices

#### Fetching a QoolQit device from a connection

Depending on your provider you might have different QPUs available to launch your quantum program to. The list of available ones can be fetched through the specific connection handler object, with the generic `connection.fetch_available_devices()` method.

For the Pasqal Cloud service, for example, creating a QoolQit device from a connection object simply reads as:

```
from pasqal_cloud import PasqalCloudConnection

from qoolqit import Device

connection = PasqalCloudConnection()
print(connection.fetch_available_devices())

# fetch QoolQit device
fresnel_device = Device.from_connection(connection=connection, name="FRESNEL")
print(fresnel_device)
```

```
{'FRESNEL_CAN1': FRESNEL_CAN1, 'FRESNEL': FRESNEL}
FRESNEL: 
 └── max_duration: 332.43763968
 └── max_amplitude: 0.20412370086269147
 └── max_abs_detuning: 1.134020560348286
 └── min_distance: 1.0
 └── max_radial_distance: 9.2



<string>:26: DeprecationWarning: Defining the number of emulation trajectories via 'NoiseModel.runs' is deprecated since pulser v1.7. Please favour using 'EmulationConfig.n_trajectories' instead.
<string>:26: DeprecationWarning: Defining the number of emulation trajectories via 'NoiseModel.runs' is deprecated since pulser v1.7. Please favour using 'EmulationConfig.n_trajectories' instead.
```

On a QRMI-enabled cluster, you can pass `PulserQRMIConnection()` as the connection and submit the same script with `sbatch --qpu=<backend> ...` (for example `FRESNEL` or `EMU_FREE`).

For a Qaptiva managed cluster, you can similarly pass `PulserQLMConnection()`.

### Create a QoolQit device from a Pulser device

A custom QoolQit device can also be built straight from any Pulser device, with any desired specification. Please, refer to [Pulser documentation](<https://docs.pasqal.com/pulser/tutorials/virtual_devices/>) to learn how to make a custom device.

```
from dataclasses import replace

from pulser import AnalogDevice as PulserAnalogDevice

from qoolqit import Device

# Converting the pulser Device object into a VirtualDevice object
VirtualAnalog = PulserAnalogDevice.to_virtual()
# Replacing desired values
ModdedAnalogDevice = replace(VirtualAnalog, max_radial_distance=100, max_sequence_duration=7000)

# Wrap a Pulser device object into a QoolQit Device
mod_analog_device = Device(pulser_device=ModdedAnalogDevice)
print(mod_analog_device)
```

```
AnalogDevice: 
 └── max_duration: 387.84391296
 └── max_amplitude: 0.22680411206965717
 └── max_abs_detuning: 2.268041120696572
 └── min_distance: 1.0
 └── max_radial_distance: 20.0
```

## Compilation

Once a `QuantumProgram` is defined and a `Device` is selected one can proceed with the compilation by means of the method `compile_to`. This method will execute what has been discussed in the [introduction](<https://pasqal-io.github.io/qoolqit/fundamentals/compilation/rationale/index.md>) mapping adimensional parameters to physical quantities according to specific default rules.

```
from qoolqit import AnalogDevice, Drive, PiecewiseLinearWaveform, QuantumProgram, Register

# Defining the Drive
wf0 = PiecewiseLinearWaveform([1.0, 2.0, 1.0], [0.0, 0.5, 0.5, 0.0])
wf1 = PiecewiseLinearWaveform([1.0, 2.0, 1.0], [-1.0, -1.0, 1.0, 1.0])
drive = Drive(amplitude = wf0, detuning = wf1)

# Defining the Register
coords = [(0.0, 0.0), (0.0, 1.0), (1.0, 0.0), (1.0, 1.0)]
register = Register.from_coordinates(coords)

# Creating the Program
program = QuantumProgram(register, drive)
device = AnalogDevice()

# Compilation to AnalogDevice
program.compile_to(device, profile="max_energy")
print(program)
```

```
Quantum Program:
| Register(n_qubits = 4)
| Drive(duration = 4.000)
| Compiled: True
| Device: AnalogDevice
```

Now that the program has been compiled, we can inspect the compiled sequence, which is an instance of a Pulser `Sequence`.

```
pulser_sequence = program.compiled_sequence
```

Finally, we can draw both the original program and the compiled sequence.

```
program.draw()
program.draw(compiled = True)
```

png

png

## Special compilation: maximum allowed duration

Whenever possible, QoolQit compilation directly maps the input quantum program to hardware instructions while preserving energy-to-time ratios (see [compilation rationale](<https://pasqal-io.github.io/qoolqit/fundamentals/compilation/rationale/index.md>)). In some applications, however, it is advantageous to decouple time from compilation. For example, in adiabatic protocols, users may wish to set the program duration independently, such as using the longest duration supported by the hardware.

> [!WARNING]
>
> Programs compiled with the flag `device_max_duration_ratio` are not portable across different devices.

To do so, set the corresponding flag at compilation:

```
# Compilation to AnalogDevice max duration
program.compile_to(device, profile="max_energy", device_max_duration_ratio=1.0)
program.draw(compiled = True)
```

png

As anticipated, this flag will decouple time from the compilation, letting the user set a time relative to the maximum allowed by the selected device. Moreover, as a drive's amplitude/detuning can be composed of many waveforms, this feature will rescale them preserving their relative durations.
