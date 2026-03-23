# Writing the drive Hamiltonian

In this page, you will learn how to:

- build a `Drive` from waveform components,
- define amplitude and detuning waveforms,
- compose drives into longer pulse sequences,
- inspect the resulting drive object,
- visualize the drive Hamiltonian.

The `Drive` is a composition of waveforms defining the drive Hamiltonian.

```python exec="on" source="material-block" result="json" session="drives"
from qoolqit import Constant, Ramp
from qoolqit import Drive

# Defining two waveforms
wf0 = Constant(0.5, 1.0) >> Ramp(1.0, 0.0, 0.5)
wf1 = Ramp(2.0, -1.0, 1.0) >> Constant(1.0, 1.0)

# Defining the drive
drive = Drive(
    amplitude = wf0,
    detuning = wf1
)

# Expanding the drive through composition
drive = drive >> drive

print(drive)  # markdown-exec: hide
```

```python exec="on" source="material-block" html="1" session="drives"
import matplotlib.pyplot as plt # markdown-exec: hide
from docs.utils import fig_to_html # markdown-exec: hide
drive.draw()
fig = drive.draw(return_fig = True) # markdown-exec: hide
print(fig_to_html(fig)) # markdown-exec: hide
```

## Custom waveforms

Built-in waveforms cover the most common shapes, but any differentiable (or piecewise-smooth)
profile can be realised by subclassing `Waveform`.

### The base-class contract

To define a custom waveform you need to:

1. **Subclass** `Waveform` (imported from `qoolqit.waveforms`).
2. **Call `super().__init__(duration, **kwargs)`** in `__init__`, passing every extra
   parameter as a *keyword argument*.  The base class stores them in `self._params_dict`
   **and** sets them as instance attributes automatically, so `self.my_param` is available
   inside `function` without any extra bookkeeping.
3. **Implement `function(self, t: float) -> float`** — the value of the waveform at time
   `t ∈ [0, duration]`.  The base class guarantees that `function` is only called for
   `t` inside this interval.
4. **(Optional) Override `max()` and `min()`** if you know the analytic extrema.
   The default implementation samples the waveform over 500 points, which is correct
   but slower than a closed-form expression.

```python
from qoolqit.waveforms import Waveform

class MyWaveform(Waveform):
    def __init__(self, duration: float, my_param: float) -> None:
        super().__init__(duration, my_param=my_param)  # sets self.my_param

    def function(self, t: float) -> float:
        return self.my_param * t / self.duration   # linear ramp, for illustration
```

---

### Example 1 — Smooth pulse

A profile shaped by $f(t) = \Omega_\text{max} \cdot \sin^2\!\left(\tfrac{\pi}{2} \sin\!\left(\tfrac{\pi\, t}{T}\right)\right)$
starts and ends at zero and reaches $\Omega_\text{max}$ at $t = T/2$, with smooth derivatives
everywhere:

```python exec="on" source="material-block" result="json" session="smooth_pulse"
import math
from qoolqit.waveforms import Waveform

class SmoothPulse(Waveform):
    """Smooth bell-shaped pulse: Ω_max · sin²((π/2)·sin(πt/T))."""

    def __init__(self, duration: float, omega_max: float) -> None:
        super().__init__(duration, omega_max=omega_max)

    def function(self, t: float) -> float:
        return self.omega_max * math.sin(0.5 * math.pi * math.sin(math.pi * t / self.duration)) ** 2

    def max(self) -> float:
        return self.omega_max          # analytic maximum is always omega_max

    def min(self) -> float:
        return 0.0                     # starts and ends at zero

import math
pulse = SmoothPulse(2 * math.pi, omega_max=1.0)
print(pulse)  # markdown-exec: hide
```

```python exec="on" source="material-block" html="1" session="smooth_pulse"
import matplotlib.pyplot as plt # markdown-exec: hide
from docs.utils import fig_to_html # markdown-exec: hide
pulse.draw()
fig = pulse.draw(return_fig=True) # markdown-exec: hide
print(fig_to_html(fig)) # markdown-exec: hide
```

---

### Example 2 — Gaussian pulse

A Gaussian envelope centred in the middle of the window:

$$
f(t) = \Omega_\text{max} \cdot \exp\!\left(-\frac{(t - T/2)^2}{2\sigma^2}\right)
$$

```python exec="on" source="material-block" result="json" session="gaussian_pulse"
import math
from qoolqit.waveforms import Waveform

class GaussianPulse(Waveform):
    """Gaussian pulse centred at t = duration/2.

    Arguments:
        duration: total duration of the waveform.
        omega_max: peak amplitude (at the centre).
        sigma: standard deviation controlling the pulse width.
    """

    def __init__(self, duration: float, omega_max: float, sigma: float) -> None:
        super().__init__(duration, omega_max=omega_max, sigma=sigma)

    def function(self, t: float) -> float:
        centre = self.duration / 2.0
        return self.omega_max * math.exp(-((t - centre) ** 2) / (2 * self.sigma ** 2))

    def max(self) -> float:
        return self.omega_max          # peak is at the centre

    def min(self) -> float:
        # tails evaluated at t = 0 and t = duration are equal by symmetry
        centre = self.duration / 2.0
        return self.omega_max * math.exp(-(centre ** 2) / (2 * self.sigma ** 2))

import math
gpulse = GaussianPulse(2 * math.pi, omega_max=1.0, sigma=1.0)
print(gpulse)  # markdown-exec: hide
```

```python exec="on" source="material-block" html="1" session="gaussian_pulse"
import matplotlib.pyplot as plt # markdown-exec: hide
from docs.utils import fig_to_html # markdown-exec: hide
gpulse.draw()
fig = gpulse.draw(return_fig=True) # markdown-exec: hide
print(fig_to_html(fig)) # markdown-exec: hide
```

---

### Using a custom waveform in a Drive

Custom waveforms compose with built-in ones via `>>` and slot into a `Drive` exactly like any
other waveform:

```python exec="on" source="material-block" result="json" session="custom_drive"
import math
from qoolqit.waveforms import Waveform
from qoolqit import Ramp, Drive

class SmoothPulse(Waveform):
    def __init__(self, duration: float, omega_max: float) -> None:
        super().__init__(duration, omega_max=omega_max)

    def function(self, t: float) -> float:
        return self.omega_max * math.sin(0.5 * math.pi * math.sin(math.pi * t / self.duration)) ** 2

    def max(self) -> float:
        return self.omega_max

    def min(self) -> float:
        return 0.0

T = 2 * math.pi
amplitude = SmoothPulse(T, omega_max=1.0)
detuning  = Ramp(T, -1.0, 1.0)

drive = Drive(amplitude=amplitude, detuning=detuning)
print(drive)  # markdown-exec: hide
```

```python exec="on" source="material-block" html="1" session="custom_drive"
import matplotlib.pyplot as plt # markdown-exec: hide
from docs.utils import fig_to_html # markdown-exec: hide
drive.draw()
fig = drive.draw(return_fig=True) # markdown-exec: hide
print(fig_to_html(fig)) # markdown-exec: hide
```
