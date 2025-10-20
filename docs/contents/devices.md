# Initializing quantum devices

Each `Device` in QoolQit wraps a Pulser device and defines the hardware characteristics that the program will be compiled to and later executed on.

```python exec="on" source="material-block" session="devices"
from qoolqit import MockDevice, AnalogDevice

# An example of an ideal device
device_ideal = MockDevice()

# An example of a real device
device_real = AnalogDevice()
```

## Create a QoolQit device directly from a Pulser device

Custom QoolQit device can be created by either subclassing the `Device` class or build it straight from any `pulser.devices` object:

```python exec="on" source="material-block" result="json" session="devices"
from qoolqit.devices import Device
from pulser import devices

# Wrap a Pulser device object into a QoolQit Device
device_from_pulser = Device(pulser_device=devices.AnalogDevice)

print(device_from_pulser.name)  # markdown-exec: hide
```

**Notes**

- Advanced users may also pass a prebuilt `default_converter` to the constructor to start in a custom unit system:
  ```python
  from qoolqit import UnitConverter
  custom_default = UnitConverter.from_energy(C6=device_from_pulser._C6, upper_amp=2.0)
  device_custom = Device(pulser_device=devices.AnalogDevice, default_converter=custom_default)
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
