# Writing time-dependent functions

An essential part of writing programs in the Rydberg analog model is to write the time-dependent functions representing the amplitude and detuning terms in the drive Hamiltonian. For that, QoolQit implements a set of waveforms that can be used directly and/or composed together.

## Base waveforms

A full list of the available waveforms can be found in the [API reference](../api/qoolqit/waveforms/waveforms.md).

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
print("t =     ", t_array) # markdown-exec: hide
print("wf(t) = ", wf3(t_array)) # markdown-exec: hide
```

In the waveform above, we defined it with a duration of $1.0$, and then evaluated it over nine points from $t = 0.0$ to $t=2.0$. As you can see, all points after $t = 1.0$ evaluated to $0.0$. By default, any waveform evaluated at a time $t$ that falls outside the specified `duration` gives $0.0$.

Waveforms can be quickly drawn with the `draw()` method.

```python exec="on" source="material-block" html="1" session="waveforms"
import matplotlib.pyplot as plt # markdown-exec: hide
from docs.utils import fig_to_html # markdown-exec: hide

wf3.draw()
fig = wf3.draw(return_fig = True) # markdown-exec: hide
print(fig_to_html(fig)) # markdown-exec: hide
```

### Interpolated waveform

Special waveform to easily fit a set given values with a smooth function.
For the full set of available options please refer to the [API reference](../api/qoolqit/waveforms/waveforms.md).

```python exec="on" source="material-block" html="1" session="waveforms"
from qoolqit import Interpolated

values = np.sin(np.linspace(0,2*np.pi, 10))
wf_interpolated = Interpolated(100, values)
wf_interpolated.draw()
fig = wf_interpolated.draw(return_fig = True) # markdown-exec: hide
print(fig_to_html(fig)) # markdown-exec: hide
```

## Composite waveforms

The most straightforward way to arbitrarily compose waveforms is to use the `>>` operator. This will create a `CompositeWaveform` representing the waveforms in the order provided.

```python exec="on" source="material-block" result="json" session="waveforms"
wf_comp = wf1 >> wf2 >> wf3

print(wf_comp)  # markdown-exec: hide
```

The code above is equivalent to calling `CompositeWaveform(wf1, wf2, wf3)`. As shown, printing the composite waveform will automatically show the individual waveforms in the composition and the times at which they are active. These are automatically calculated from the individual waveforms. A
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
print(fig_to_html(fig)) # markdown-exec: hide
```

## Defining custom waveforms

The waveform system of QoolQit can be easily extended by subclassing the `Waveform` class and defining some key properties and methods. To exemplify this we will create a waveform representing a simple shifted sine function,

$$
    \text{Sin}(t)_{\omega, C} \equiv \sin(\omega t) + C
$$


```python exec="on" source="material-block" session="waveforms"
from qoolqit.waveforms import Waveform

import math

class Sin(Waveform):
    """A simple sine over a given duration.

    Arguments:
        duration: the total duration.
        omega: the frequency of the sine wave.
        shift: the vertical shift of the sine wave.
    """

    def __init__(
        self,
        duration: float,
        omega: float = 2.0 * math.pi,
        shift: float = 0.0,
    ) -> None:
        super().__init__(duration, omega = omega, shift = shift)

    def function(self, t: float) -> float:
        return math.sin(self.omega * t) + self.shift
```

A few things are crucial in the snippet above:

- Keeping the `duration` argument as the first one in the `__init__`, and initializing the parent class with that value, to be consistent with other waveforms.
- Passing every other parameter needed for the waveform in the `__init__` and passing it as a **keyword argument** to the parent class. This will automatically create a `params` dictionary of extra parameters, and set them as attributes to be used later.
- Overriding the `function` abstract method, which represents the evaluation of the waveform at some time `t`.
- **Optional**: overriding the `max` and `min` methods. The intended result of `wf.max()` and `wf.min()` is to get the maximum/minimum value the waveform takes over its duration. By default, the base `Waveform` class implements a brute-force sampling method that **approximates** the maximum and minimum values. However, if this value is easy to know from the waveform parameters, the method should be overridden.
- Internally, before being executed by an emulator or a QPU, custom defined waveforms will be converted to an `Interpolated` waveform with a maximum of 100 points. If you need a finer time resolution, please, consider using directly an `Interpolated` waveform.

To showcase the usage of the newly defined waveform, let's define a new sine waveform and compose it with a piecewise linear waveform.


```python exec="on" source="material-block" result="json" session="waveforms"
from qoolqit import PiecewiseLinear
import math

wf1 = Sin(
    duration = 1.0,
    omega = 2.0 * math.pi,
    shift = 1.0
)

wf2 = PiecewiseLinear(
    durations = [0.5, 0.5],
    values = [1.0, 1.0, 0.0],
)

wf_comp = wf1 >> wf2

print(wf_comp)  # markdown-exec: hide
```

```python exec="on" source="material-block" html="1" session="waveforms"
import matplotlib.pyplot as plt # markdown-exec: hide
from docs.utils import fig_to_html # markdown-exec: hide

wf_comp.draw()

fig = wf_comp.draw(return_fig = True) # markdown-exec: hide
print(fig_to_html(fig)) # markdown-exec: hide
```

Following this example, more complete `Sin` waveform is directly available in QoolQit implementing

$$
    \text{Sin}(t)_{A, \omega, \phi, C} \equiv A * \sin(\omega t + \phi) + C
$$

```python exec="on" source="material-block" result="json" session="waveforms"
from qoolqit import Sin

wf = Sin(
    duration = 1.0,
    amplitude = 2.0,
    omega = 6.0,
    phi = -5.0,
    shift = 1.0,
)

wf.max()
print(wf) # markdown-exec: hide
print("Maximum value: ", wf.max()) # markdown-exec: hide
```

```python exec="on" source="material-block" html="1" session="waveforms"
import matplotlib.pyplot as plt # markdown-exec: hide
from docs.utils import fig_to_html # markdown-exec: hide

wf.draw()

fig = wf.draw(return_fig = True) # markdown-exec: hide
print(fig_to_html(fig)) # markdown-exec: hide
```
