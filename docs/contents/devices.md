# Initializing quantum devices

Each `Device` in QoolQit wraps a Pulser device and defines the hardware characteristics that the program will be compiled to and later executed on.

```python exec="on" source="material-block" session="devices"
from qoolqit import MockDevice, AnalogDevice

# An example of an ideal device
device_ideal = MockDevice()

# An example of a real device
device_real = AnalogDevice()
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
