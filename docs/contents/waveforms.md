# Writing time-dependent functions

An essential part of writing programs in the Rydberg analog model is to write the time-dependent functions representing the amplitude and detuning terms in the drive Hamiltonian. For that, QoolQit includes a set of waveforms that can directly used and composed together.

```python exec="on" source="material-block" session="waveforms"
from qoolqit import Constant, Ramp, Delay

# An empty waveform
wf = Delay(1.0)

# A waveform with a constant value
wf = Constant(1.0, 2.0)

# A waveform that ramps linearly between two values
wf = Ramp(1.0, -1.0, 1.0)

print(wf)
```

