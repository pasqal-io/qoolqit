# Writing time-dependent functions

An essential part of writing programs in the Rydberg analog model is to write the time-dependent functions representing the amplitude and detuning terms in the drive Hamiltonian. For that, QoolQit implements a set of waveforms that can directly used and composed together.

## Base waveforms

```python exec="on" source="material-block" result="json" session="waveforms"
from qoolqit import Constant, Ramp, Delay

# An empty waveform
wf1 = Delay(1.0)

# A waveform with a constant value
wf2 = Constant(1.0, 2.0)

# A waveform that ramps linearly between two values
wf3 = Ramp(1.0, -1.0, 1.0)

print(wf1)  # markdown-exec: hide
print(wf2)  # markdown-exec: hide
print(wf3)  # markdown-exec: hide
```

As shown above, printing a waveform shows the duration interval over which it applies followed by the description of the waveform.

The first argument is always the `duration` of the waveform, and the remaining arguments depend on the information required by each waveform. The resulting object is a callable that can be evaluated at any time $t$.

```python exec="on" source="material-block" result="json" session="waveforms"
wf1(t = 0.0)
wf2(t = 0.5)
wf3(t = 1.0)

print("wf1(t = 0.0) =", wf1(t = 0.0))  # markdown-exec: hide
print("wf2(t = 0.5) =", wf2(t = 0.5))  # markdown-exec: hide
print("wf3(t = 1.0) =", wf3(t = 1.0))  # markdown-exec: hide
```

Each waveform also supports evaluation at multiple time steps by calling it on an array of times.
```python exec="on" source="material-block" result="json" session="waveforms"
import numpy as np

t_array = np.linspace(0.0, 2.0, 9)

wf3(t_array)
print("t =    ", t_array) # markdown-exec: hide
print("wf(t) =",wf3(t_array)) # markdown-exec: hide
```

In the waveform above, we defined it with a duration of $1.0$, and then evaluated it over nine points from $t = 0.0$ to $t=2.0$. As you can see, all points after $t = 1.0$ evaluated to $0.0$. By default, any waveform evaluated at a time $t$ that falls outside the specified `duration` gives $0.0$.

Waveforms can be quickly drawn with the `draw()` method.

```python exec="on" source="material-block" html="1" session="waveforms"
import matplotlib.pyplot as plt # markdown-exec: hide
from docs.utils import fig_to_html # markdown-exec: hide

wf3.draw()
fig = wf3.draw(return_fig = True) # markdown-exec: hide
plt.tight_layout() # markdown-exec: hide
print(fig_to_html(fig)) # markdown-exec: hide
```

## Composite waveforms

The most straightforward way to arbitrarily compose waveforms is to multiply them together. This will create a `CompositeWaveform` representing the waveforms in the order provided.

```python exec="on" source="material-block" result="json" session="waveforms"
wf_comp = wf1 * wf2 * wf3

print(wf_comp)  # markdown-exec: hide
```

The code above is equivalent to calling `CompositeWaveform(wf1, wf2, wf3)`. As shown, printing the composed waveform will automatically show the individual waveforms in the composition and the times at which they are active. These are automatically calculated from the individual waveforms. A
`CompositeWaveform` is by itself a subclass of `Waveform`, and thus the previous logic on calling it at arbitrary time values also applies.

A few convenient properties are directly available in a composite waveform:

```python exec="on" source="material-block" result="json" session="waveforms"
# Total duration
wf_comp.duration

# List of durations of the individual waveforms
wf_comp.durations

# List of times where each individual waveform starts / ends
wf_comp.times

print("Total duration :", wf_comp.duration)  # markdown-exec: hide
print("List of durations :", wf_comp.durations)  # markdown-exec: hide
print("List of times :", wf_comp.times)  # markdown-exec: hide
```

A custom waveform can directly be a `CompositeWaveform`. That is the case with the `PiecewiseLinear` waveform, which takes a list of durations (of size $N$) and a list of values (of size $N+1$) and creates a linear interpolation between all values using individual waveforms of type `Ramp`.

```python exec="on" source="material-block" html="1" session="waveforms"
import matplotlib.pyplot as plt # markdown-exec: hide
from docs.utils import fig_to_html # markdown-exec: hide

from qoolqit import PiecewiseLinear

durations = [1.0, 1.0, 2.0]
values = [0.0, 1.0, 0.5, 0.5]

wf_pwl = PiecewiseLinear(durations, values)

wf_pwl.draw()

fig = wf_pwl.draw(return_fig = True) # markdown-exec: hide
plt.tight_layout() # markdown-exec: hide
print(fig_to_html(fig)) # markdown-exec: hide
```

## Defining custom waveforms

The waveform system of QoolQit can be easily extended by subclassing the `Waveform` class and defining some key properties and methods. To exemplify this we will create a waveform representing an arbitary sine function,

$$
    \text{Sin}(t)_{A,\omega,\phi,D} \equiv A * \sin(\omega t + \phi) + D
$$

```python exec="on" source="material-block" session="waveforms"
from qoolqit.waveforms import Waveform

import math

class Sin(Waveform):
    """An arbitrary sine over a given duration.

    Arguments:
        duration: the total duration.
        amplitude: the amplitude of the sine wave.
        omega: the frequency of the sine wave.
        phi: the phase of the sine wave.
        shift: the vertical shift of the sine wave.
    """

    def __init__(
        self,
        duration: float,
        amplitude: float = 1.0,
        omega: float = 1.0,
        phi: float = 0.0,
        shift: float = 0.0,
    ) -> None:
        super().__init__(duration)
        self.amplitude = amplitude
        self.omega = omega
        self.phi = phi
        self.shift = shift

    def function(self, t: float) -> float:
        return self.amplitude * math.sin(self.omega * t + self.phi) + self.shift

    def max(self) -> float:
        global_max = abs(self.amplitude) + self.shift
        target_theta = math.pi / 2 if self.amplitude >= 0 else 3 * math.pi / 2
        theta_at_0 = self.omega * 0 + self.phi
        theta_at_dur = self.omega * self.duration + self.phi
        min_theta = min(theta_at_0, theta_at_dur)
        max_theta = max(theta_at_0, theta_at_dur)
        k_candidate = math.ceil((min_theta - target_angle_base) / (2 * math.pi))
        if target_theta + 2 * k_candidate * math.pi <= max_theta:
            return global_max
        else:
            return max(self(0.0), self(self.duration))

    def _repr_content(self) -> str:
        params = [str(self.amplitude), str(self.omega), str(self.phi), str(self.shift)]
        string = ", ".join(params)
        return self.__class__.__name__ + "(" + string + ")"
```

A few things are crucial in the snippet above:

- Keeping the `duration` argument as the first one in the `__init__`, and initializing the parent class with that value, to be consistent with other waveforms.
- Passing every other parameter needed for the waveform in the `__init__` and saving it as an attribute.
- Overriding the `function` abstract method, which represents the evaluation of the waveform at some time `t`.
- Overriding the `max` abstract method, which analytically defines the maximum value the waveform can take during its duration. This information is useful when compiling waveforms to Pulser.
- Overriding the `_repr_content` method is optional, but it ensures nice printing of the waveform with the parameters that characterize it. Otherwise, the default behaviour would be to just print the class name, `Sin()`

To showcase the usage of the newly defined waveform, let's define a new sine waveform and compose it with a piecewise linear waveform.


```python exec="on" source="material-block" result="json" session="waveforms"
from qoolqit import PiecewiseLinear
import math

wf1 = Sin(
    duration = 1.0,
    amplitude = 1.0,
    omega = 2.0 * math.pi,
    shift = 1.0
)

wf2 = PiecewiseLinear(
    durations = [0.5, 0.5],
    values = [1.0, 1.0, 0.0],
)

wf_comp = wf1 * wf2

print(wf_comp)  # markdown-exec: hide
```

```python exec="on" source="material-block" html="1" session="waveforms"
import matplotlib.pyplot as plt # markdown-exec: hide
from docs.utils import fig_to_html # markdown-exec: hide

wf_comp.draw()

fig = wf_comp.draw(return_fig = True) # markdown-exec: hide
plt.tight_layout() # markdown-exec: hide
print(fig_to_html(fig)) # markdown-exec: hide
```
