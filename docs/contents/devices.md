# Initializing quantum devices

Each `Device` in QoolQit wraps a Pulser device and defines the hardware characteristics that the program will be compiled to and later executed on.

```python exec="on" source="material-block" session="devices"
from qoolqit import MockDevice, AnalogDevice

# An example of an ideal device
device_ideal = MockDevice()

# An example of a real device
device_real = AnalogDevice()
```

Each device has a default unit converter. These are the factors that will be used when converting an adimensional program in the Rydberg analog model to the physical units of Pulser devices for hardware execution.
```python exec="on" source="material-block" result="json" session="devices"

device_real.converter

print(device_real.converter)  # markdown-exec: hide
```

Customizing the unit conversion factors is possible

```python exec="on" source="material-block" result="json" session="devices"

device_real.set_time_unit(50.0)
print(device_real.converter)  # markdown-exec: hide

device_real.set_energy_unit(10.0)
print(device_real.converter)  # markdown-exec: hide

device_real.set_distance_unit(6.0)
print(device_real.converter)  # markdown-exec: hide
```
