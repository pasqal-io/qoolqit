## waveforms

Composable, time-bounded scalar waveforms for pulse-level quantum control.

Modules:

- **`base_waveforms`** –

  Base classes for scalar time-bounded waveforms and their sequential composition.
- **`utils`** –

  Waveform utility functions.
- **`waveforms`** –

  Concrete waveform implementations.

Classes:

- **`BlackmanWaveform`** –

  A Blackman window of a specified duration and area under the curve.
- **`CompositeWaveform`** –

  A concatenation of waveforms played sequentially.
- **`ConstantWaveform`** –

  A constant waveform over a given duration.
- **`DelayWaveform`** –

  An empty waveform.
- **`InterpolatedWaveform`** –

  A waveform created from shape-preserving interpolation of data points.
- **`PiecewiseLinearWaveform`** –

  A piecewise linear waveform.
- **`RampWaveform`** –

  A ramp that linearly interpolates between an initial and final value.
- **`Waveform`** –

  Base class for scalar time-bounded waveforms.

### BlackmanWaveform

```
BlackmanWaveform(duration: float, area: float)
```

A Blackman window of a specified duration and area under the curve.

Implements the positive Blackman window shaped waveform blackman(t) = A*(0.42 - 0.5*cos(αt) + 0.08*cos(2αt)) A = area/(0.42*duration) α = 2π/duration

See: [https://en.wikipedia.org/wiki/Window\_function\#:\~:text=Blackman%20window](<https://en.wikipedia.org/wiki/Window_function#:~:text=Blackman window>)

Parameters:

- **`duration`** (`float`) –

  The waveform duration.
- **`area`** (`float`) –

  The integral of the waveform.

> [!NOTE]
>
> **Example**
>
> ```
> blackman_wf = BlackmanWaveform(100.0, area=3.14)
> ```

Methods:

- **`__call__`** –

  Evaluate the waveform at `t`: a single time, or a 1D list or array of times.
- **`__mul__`** –

  Rescale this waveform by a scalar.
- **`__repr__`** –

  Return the time interval and the waveform with its parameters.
- **`__rmul__`** –

  Rescale this waveform by a scalar (right-hand multiplication).
- **`__rshift__`** –

  Returns a new CompositeWaveform composed of this waveform and another.
- **`draw`** –

  Draw the waveform.
- **`function`** –

  Evaluates the waveform function at a given time t.
- **`max`** –

  Get the maximum value of the waveform.
- **`min`** –

  Get the minimum value of the waveform.

Attributes:

- **`duration`** (`float`) –

  Returns the duration of the waveform.
- **`params`** (`dict[str, float | ndarray]`) –

  Dictionary of parameters used by the waveform.
- **`waveforms`** (`list[Waveform]`) –

  Returns a list of the individual waveforms, which is just this waveform.

#### duration

```
duration: float
```

Returns the duration of the waveform.

#### params

```
params: dict[str, float | ndarray]
```

Dictionary of parameters used by the waveform.

#### waveforms

```
waveforms: list[Waveform]
```

Returns a list of the individual waveforms, which is just this waveform.

#### \_\_call\_\_

```
__call__(t: float) -> float
```

```
__call__(t: list[float] | ndarray) -> NDArray[float64]
```

```
__call__(
    t: float | list[float] | ndarray,
) -> float | NDArray[float64]
```

Evaluate the waveform at `t`: a single time, or a 1D list or array of times.

Returns a float for a single time, otherwise a 1D float64 array. Times outside \[0, duration\] give 0.

#### \_\_mul\_\_

```
__mul__(other: float) -> Waveform
```

Rescale this waveform by a scalar.

#### \_\_repr\_\_

```
__repr__() -> str
```

Return the time interval and the waveform with its parameters.

#### \_\_rmul\_\_

```
__rmul__(other: float) -> Waveform
```

Rescale this waveform by a scalar (right-hand multiplication).

#### \_\_rshift\_\_

```
__rshift__(other: Waveform) -> CompositeWaveform
```

Returns a new CompositeWaveform composed of this waveform and another.

#### draw

```
draw(
    ax: Axes | None = None,
    color: ColorType = "tab:blue",
    n_points: int = 250,
) -> None
```

Draw the waveform.

Parameters:

- **`ax`** (`Axes | None`, default: `None` ) –

  The axes to draw into. If None, a new pyplot figure is created.
- **`color`** (`ColorType`, default: `'tab:blue'` ) –

  The color of the line and the filled area. Defaults to matplotlib's "tab:blue".
- **`n_points`** (`int`, default: `250` ) –

  The number of time samples to draw. Defaults to 250.

#### function

```
function(t: float) -> float
```

Evaluates the waveform function at a given time t.

#### max

```
max() -> float
```

Get the maximum value of the waveform.

#### min

```
min() -> float
```

Get the minimum value of the waveform.

### CompositeWaveform

```
CompositeWaveform(*waveforms: Waveform)
```

A concatenation of waveforms played sequentially.

Waveforms are joined in the given order, each starting where the previous one ends, and the composition can be used as a single waveform.

Attributes:

- **`waveforms`** (`list[Waveform]`) –

  a list of waveforms in the composition.
- **`durations`** (`list[float]`) –

  a list of durations of each individual waveform.
- **`times`** (`list[float]`) –

  a list of times when each individual waveform starts.

Parameters:

- **`waveforms`** (`Waveform`, default: `()` ) –

  an iterator over waveforms.

Raises:

- `TypeError` –

  if any argument is not an instance of Waveform.
- `ValueError` –

  if no waveforms are provided.

Methods:

- **`__call__`** –

  Evaluate the waveform at `t`: a single time, or a 1D list or array of times.
- **`__mul__`** –

  Rescale this waveform by a scalar.
- **`__repr__`** –

  Return each sub-waveform with its time interval, one per line.
- **`__rmul__`** –

  Rescale this waveform by a scalar (right-hand multiplication).
- **`__rshift__`** –

  Returns a new CompositeWaveform composed of this waveform and another.
- **`draw`** –

  Draw the waveform.
- **`function`** –

  Evaluates the waveform function at a given time t.
- **`max`** –

  Get the maximum value of the waveform.
- **`min`** –

  Get the minimum value of the waveform.

#### duration

```
duration: float
```

Returns the duration of the waveform.

#### durations

```
durations: list[float]
```

Returns the list of durations of each individual waveform.

#### n\_waveforms

```
n_waveforms: int
```

Returns the number of waveforms.

#### params

```
params: dict[str, float | ndarray]
```

Dictionary of parameters used by the waveform.

#### times

```
times: list[float]
```

Returns the list of times when each individual waveform starts.

#### waveforms

```
waveforms: list[Waveform]
```

Returns a list of the individual waveforms.

#### \_\_call\_\_

```
__call__(t: float) -> float
```

```
__call__(t: list[float] | ndarray) -> NDArray[float64]
```

```
__call__(
    t: float | list[float] | ndarray,
) -> float | NDArray[float64]
```

Evaluate the waveform at `t`: a single time, or a 1D list or array of times.

Returns a float for a single time, otherwise a 1D float64 array. Times outside \[0, duration\] give 0.

#### \_\_mul\_\_

```
__mul__(other: float) -> CompositeWaveform
```

Rescale this waveform by a scalar.

#### \_\_repr\_\_

```
__repr__() -> str
```

Return each sub-waveform with its time interval, one per line.

#### \_\_rmul\_\_

```
__rmul__(other: float) -> Waveform
```

Rescale this waveform by a scalar (right-hand multiplication).

#### \_\_rshift\_\_

```
__rshift__(other: Waveform) -> CompositeWaveform
```

Returns a new CompositeWaveform composed of this waveform and another.

#### draw

```
draw(
    ax: Axes | None = None,
    color: ColorType = "tab:blue",
    n_points: int = 250,
) -> None
```

Draw the waveform.

Parameters:

- **`ax`** (`Axes | None`, default: `None` ) –

  The axes to draw into. If None, a new pyplot figure is created.
- **`color`** (`ColorType`, default: `'tab:blue'` ) –

  The color of the line and the filled area. Defaults to matplotlib's "tab:blue".
- **`n_points`** (`int`, default: `250` ) –

  The number of time samples to draw. Defaults to 250.

#### function

```
function(t: float) -> float
```

Evaluates the waveform function at a given time t.

#### max

```
max() -> float
```

Get the maximum value of the waveform.

#### min

```
min() -> float
```

Get the minimum value of the waveform.

### ConstantWaveform

```
ConstantWaveform(duration: float, value: float)
```

A constant waveform over a given duration.

Parameters:

- **`duration`** (`float`) –

  the total duration.
- **`value`** (`float`) –

  the value to take during the duration.

Methods:

- **`__call__`** –

  Evaluate the waveform at `t`: a single time, or a 1D list or array of times.
- **`__mul__`** –

  Rescale this waveform by a scalar.
- **`__repr__`** –

  Return the time interval and the waveform with its parameters.
- **`__rmul__`** –

  Rescale this waveform by a scalar (right-hand multiplication).
- **`__rshift__`** –

  Returns a new CompositeWaveform composed of this waveform and another.
- **`draw`** –

  Draw the waveform.
- **`function`** –

  Evaluates the waveform function at a given time t.
- **`max`** –

  Get the maximum value of the waveform.
- **`min`** –

  Get the minimum value of the waveform.

Attributes:

- **`duration`** (`float`) –

  Returns the duration of the waveform.
- **`params`** (`dict[str, float | ndarray]`) –

  Dictionary of parameters used by the waveform.
- **`waveforms`** (`list[Waveform]`) –

  Returns a list of the individual waveforms, which is just this waveform.

#### duration

```
duration: float
```

Returns the duration of the waveform.

#### params

```
params: dict[str, float | ndarray]
```

Dictionary of parameters used by the waveform.

#### waveforms

```
waveforms: list[Waveform]
```

Returns a list of the individual waveforms, which is just this waveform.

#### \_\_call\_\_

```
__call__(t: float) -> float
```

```
__call__(t: list[float] | ndarray) -> NDArray[float64]
```

```
__call__(
    t: float | list[float] | ndarray,
) -> float | NDArray[float64]
```

Evaluate the waveform at `t`: a single time, or a 1D list or array of times.

Returns a float for a single time, otherwise a 1D float64 array. Times outside \[0, duration\] give 0.

#### \_\_mul\_\_

```
__mul__(other: float) -> Waveform
```

Rescale this waveform by a scalar.

#### \_\_repr\_\_

```
__repr__() -> str
```

Return the time interval and the waveform with its parameters.

#### \_\_rmul\_\_

```
__rmul__(other: float) -> Waveform
```

Rescale this waveform by a scalar (right-hand multiplication).

#### \_\_rshift\_\_

```
__rshift__(other: Waveform) -> CompositeWaveform
```

Returns a new CompositeWaveform composed of this waveform and another.

#### draw

```
draw(
    ax: Axes | None = None,
    color: ColorType = "tab:blue",
    n_points: int = 250,
) -> None
```

Draw the waveform.

Parameters:

- **`ax`** (`Axes | None`, default: `None` ) –

  The axes to draw into. If None, a new pyplot figure is created.
- **`color`** (`ColorType`, default: `'tab:blue'` ) –

  The color of the line and the filled area. Defaults to matplotlib's "tab:blue".
- **`n_points`** (`int`, default: `250` ) –

  The number of time samples to draw. Defaults to 250.

#### function

```
function(t: float) -> float
```

Evaluates the waveform function at a given time t.

#### max

```
max() -> float
```

Get the maximum value of the waveform.

#### min

```
min() -> float
```

Get the minimum value of the waveform.

### DelayWaveform

```
DelayWaveform(duration: float, **kwargs: float | ndarray)
```

An empty waveform.

Parameters:

- **`duration`** (`float`) –

  the total duration of the waveform.
- **`**kwargs`** (`float | ndarray`, default: `{}` ) –

  optional keyword arguments for the waveform function.

Methods:

- **`__call__`** –

  Evaluate the waveform at `t`: a single time, or a 1D list or array of times.
- **`__mul__`** –

  Rescale this waveform by a scalar.
- **`__repr__`** –

  Return the time interval and the waveform with its parameters.
- **`__rmul__`** –

  Rescale this waveform by a scalar (right-hand multiplication).
- **`__rshift__`** –

  Returns a new CompositeWaveform composed of this waveform and another.
- **`draw`** –

  Draw the waveform.
- **`function`** –

  Evaluates the waveform function at a given time t.
- **`max`** –

  Get the maximum value of the waveform.
- **`min`** –

  Get the minimum value of the waveform.

Attributes:

- **`duration`** (`float`) –

  Returns the duration of the waveform.
- **`params`** (`dict[str, float | ndarray]`) –

  Dictionary of parameters used by the waveform.
- **`waveforms`** (`list[Waveform]`) –

  Returns a list of the individual waveforms, which is just this waveform.

#### duration

```
duration: float
```

Returns the duration of the waveform.

#### params

```
params: dict[str, float | ndarray]
```

Dictionary of parameters used by the waveform.

#### waveforms

```
waveforms: list[Waveform]
```

Returns a list of the individual waveforms, which is just this waveform.

#### \_\_call\_\_

```
__call__(t: float) -> float
```

```
__call__(t: list[float] | ndarray) -> NDArray[float64]
```

```
__call__(
    t: float | list[float] | ndarray,
) -> float | NDArray[float64]
```

Evaluate the waveform at `t`: a single time, or a 1D list or array of times.

Returns a float for a single time, otherwise a 1D float64 array. Times outside \[0, duration\] give 0.

#### \_\_mul\_\_

```
__mul__(other: float) -> Waveform
```

Rescale this waveform by a scalar.

#### \_\_repr\_\_

```
__repr__() -> str
```

Return the time interval and the waveform with its parameters.

#### \_\_rmul\_\_

```
__rmul__(other: float) -> Waveform
```

Rescale this waveform by a scalar (right-hand multiplication).

#### \_\_rshift\_\_

```
__rshift__(other: Waveform) -> CompositeWaveform
```

Returns a new CompositeWaveform composed of this waveform and another.

#### draw

```
draw(
    ax: Axes | None = None,
    color: ColorType = "tab:blue",
    n_points: int = 250,
) -> None
```

Draw the waveform.

Parameters:

- **`ax`** (`Axes | None`, default: `None` ) –

  The axes to draw into. If None, a new pyplot figure is created.
- **`color`** (`ColorType`, default: `'tab:blue'` ) –

  The color of the line and the filled area. Defaults to matplotlib's "tab:blue".
- **`n_points`** (`int`, default: `250` ) –

  The number of time samples to draw. Defaults to 250.

#### function

```
function(t: float) -> float
```

Evaluates the waveform function at a given time t.

#### max

```
max() -> float
```

Get the maximum value of the waveform.

#### min

```
min() -> float
```

Get the minimum value of the waveform.

### InterpolatedWaveform

```
InterpolatedWaveform(
    duration: float,
    values: ArrayLike,
    times: ArrayLike | None = None,
)
```

A waveform created from shape-preserving interpolation of data points.

This class creates a smooth waveform by interpolating between specified data points using PCHIP (Piecewise Cubic Hermite Interpolating Polynomial) interpolation. The interpolating curve preserves the shape of the input data: bounds (avoiding under/overshooting), monotonicity, and convexity.

Uses scipy's PchipInterpolator for the interpolation.

Attributes:

- **`duration`** (`float`) –

  The waveform duration.
- **`values`** (`float`) –

  Array-like sequence of waveform values at the interpolation points. Must be convertible to float. These values define the amplitude of the waveform at the corresponding time points.
- **`times`** (`float`) –

  Optional array-like sequence of fractional times in the range \[0, 1\] indicating where to place each value on the time axis. Must have the same length as `values`. If not provided, values are distributed evenly across the waveform duration. Default is None.

ValueError: If `times` contains values outside \[0, 1\] or if `times` and `values` have different lengths.

> [!NOTE]
>
> **Example**
>
> > > > #### Create a waveform with 4 points over 100ns
> > > >
> > > > values = \[0.0, 1.0, 0.5, 0.0\] wf = InterpolatedWaveform(100, values)
> > > >
> > > > #### Create with custom timing
> > > >
> > > > times = \[0.0, 0.2, 0.8, 1.0\] \# Non-uniform spacing wf = InterpolatedWaveform(100, values, times)

Parameters:

- **`duration`** (`float`) –

  The total duration of the waveform. Must be positive.
- **`values`** (`ArrayLike`) –

  Array-like sequence of waveform values at interpolation points. Can be a list, tuple, numpy array, or any sequence convertible to float.
- **`times`** (`ArrayLike | None`, default: `None` ) –

  Optional array-like sequence of fractional times in \[0, 1\]. If provided, must have the same length as `values`. If None, values are evenly spaced across the duration. Default is None.

Raises:

- `ValueError` –

  If any value in `times` is outside \[0, 1\], or if `times` and `values` have different lengths.

Methods:

- **`__call__`** –

  Evaluate the waveform at `t`: a single time, or a 1D list or array of times.
- **`__mul__`** –

  Rescale this waveform by a scalar.
- **`__repr__`** –

  Return the time interval and the waveform with its parameters.
- **`__rmul__`** –

  Rescale this waveform by a scalar (right-hand multiplication).
- **`__rshift__`** –

  Returns a new CompositeWaveform composed of this waveform and another.
- **`draw`** –

  Draw the waveform.
- **`function`** –

  Evaluates the waveform function at a given time t.
- **`max`** –

  Get the maximum value of the waveform.
- **`min`** –

  Get the minimum value of the waveform.

#### duration

```
duration: float
```

Returns the duration of the waveform.

#### params

```
params: dict[str, float | ndarray]
```

Dictionary of parameters used by the waveform.

#### waveforms

```
waveforms: list[Waveform]
```

Returns a list of the individual waveforms, which is just this waveform.

#### \_\_call\_\_

```
__call__(t: float) -> float
```

```
__call__(t: list[float] | ndarray) -> NDArray[float64]
```

```
__call__(
    t: float | list[float] | ndarray,
) -> float | NDArray[float64]
```

Evaluate the waveform at `t`: a single time, or a 1D list or array of times.

Returns a float for a single time, otherwise a 1D float64 array. Times outside \[0, duration\] give 0.

#### \_\_mul\_\_

```
__mul__(other: float) -> Waveform
```

Rescale this waveform by a scalar.

#### \_\_repr\_\_

```
__repr__() -> str
```

Return the time interval and the waveform with its parameters.

#### \_\_rmul\_\_

```
__rmul__(other: float) -> Waveform
```

Rescale this waveform by a scalar (right-hand multiplication).

#### \_\_rshift\_\_

```
__rshift__(other: Waveform) -> CompositeWaveform
```

Returns a new CompositeWaveform composed of this waveform and another.

#### draw

```
draw(
    ax: Axes | None = None,
    color: ColorType = "tab:blue",
    n_points: int = 250,
) -> None
```

Draw the waveform.

Parameters:

- **`ax`** (`Axes | None`, default: `None` ) –

  The axes to draw into. If None, a new pyplot figure is created.
- **`color`** (`ColorType`, default: `'tab:blue'` ) –

  The color of the line and the filled area. Defaults to matplotlib's "tab:blue".
- **`n_points`** (`int`, default: `250` ) –

  The number of time samples to draw. Defaults to 250.

#### function

```
function(t: float) -> float
```

Evaluates the waveform function at a given time t.

#### max

```
max() -> float
```

Get the maximum value of the waveform.

#### min

```
min() -> float
```

Get the minimum value of the waveform.

### PiecewiseLinearWaveform

```
PiecewiseLinearWaveform(
    durations: list[float] | tuple[float, ...] | ndarray,
    values: list[float] | tuple[float, ...] | ndarray,
)
```

A piecewise linear waveform.

Creates a composite waveform of N ramps that linearly interpolate through the given N+1 values.

Parameters:

- **`durations`** (`list[float] | tuple[float, ...] | ndarray`) –

  list or tuple of N duration values.
- **`values`** (`list[float] | tuple[float, ...] | ndarray`) –

  list or tuple of N+1 waveform values.

Methods:

- **`__call__`** –

  Evaluate the waveform at `t`: a single time, or a 1D list or array of times.
- **`__mul__`** –

  Rescale this waveform by a scalar.
- **`__repr__`** –

  Return each sub-waveform with its time interval, one per line.
- **`__rmul__`** –

  Rescale this waveform by a scalar (right-hand multiplication).
- **`__rshift__`** –

  Returns a new CompositeWaveform composed of this waveform and another.
- **`draw`** –

  Draw the waveform.
- **`function`** –

  Evaluates the waveform function at a given time t.
- **`max`** –

  Get the maximum value of the waveform.
- **`min`** –

  Get the minimum value of the waveform.

Attributes:

- **`duration`** (`float`) –

  Returns the duration of the waveform.
- **`durations`** (`list[float]`) –

  Returns the list of durations of each individual waveform.
- **`n_waveforms`** (`int`) –

  Returns the number of waveforms.
- **`params`** (`dict[str, float | ndarray]`) –

  Dictionary of parameters used by the waveform.
- **`times`** (`list[float]`) –

  Returns the list of times when each individual waveform starts.
- **`waveforms`** (`list[Waveform]`) –

  Returns a list of the individual waveforms.

#### duration

```
duration: float
```

Returns the duration of the waveform.

#### durations

```
durations: list[float]
```

Returns the list of durations of each individual waveform.

#### n\_waveforms

```
n_waveforms: int
```

Returns the number of waveforms.

#### params

```
params: dict[str, float | ndarray]
```

Dictionary of parameters used by the waveform.

#### times

```
times: list[float]
```

Returns the list of times when each individual waveform starts.

#### waveforms

```
waveforms: list[Waveform]
```

Returns a list of the individual waveforms.

#### \_\_call\_\_

```
__call__(t: float) -> float
```

```
__call__(t: list[float] | ndarray) -> NDArray[float64]
```

```
__call__(
    t: float | list[float] | ndarray,
) -> float | NDArray[float64]
```

Evaluate the waveform at `t`: a single time, or a 1D list or array of times.

Returns a float for a single time, otherwise a 1D float64 array. Times outside \[0, duration\] give 0.

#### \_\_mul\_\_

```
__mul__(other: float) -> CompositeWaveform
```

Rescale this waveform by a scalar.

#### \_\_repr\_\_

```
__repr__() -> str
```

Return each sub-waveform with its time interval, one per line.

#### \_\_rmul\_\_

```
__rmul__(other: float) -> Waveform
```

Rescale this waveform by a scalar (right-hand multiplication).

#### \_\_rshift\_\_

```
__rshift__(other: Waveform) -> CompositeWaveform
```

Returns a new CompositeWaveform composed of this waveform and another.

#### draw

```
draw(
    ax: Axes | None = None,
    color: ColorType = "tab:blue",
    n_points: int = 250,
) -> None
```

Draw the waveform.

Parameters:

- **`ax`** (`Axes | None`, default: `None` ) –

  The axes to draw into. If None, a new pyplot figure is created.
- **`color`** (`ColorType`, default: `'tab:blue'` ) –

  The color of the line and the filled area. Defaults to matplotlib's "tab:blue".
- **`n_points`** (`int`, default: `250` ) –

  The number of time samples to draw. Defaults to 250.

#### function

```
function(t: float) -> float
```

Evaluates the waveform function at a given time t.

#### max

```
max() -> float
```

Get the maximum value of the waveform.

#### min

```
min() -> float
```

Get the minimum value of the waveform.

### RampWaveform

```
RampWaveform(
    duration: float,
    initial_value: float,
    final_value: float,
)
```

A ramp that linearly interpolates between an initial and final value.

Parameters:

- **`duration`** (`float`) –

  the total duration.
- **`initial_value`** (`float`) –

  the initial value at t = 0.
- **`final_value`** (`float`) –

  the final value at t = duration.

Methods:

- **`__call__`** –

  Evaluate the waveform at `t`: a single time, or a 1D list or array of times.
- **`__mul__`** –

  Rescale this waveform by a scalar.
- **`__repr__`** –

  Return the time interval and the waveform with its parameters.
- **`__rmul__`** –

  Rescale this waveform by a scalar (right-hand multiplication).
- **`__rshift__`** –

  Returns a new CompositeWaveform composed of this waveform and another.
- **`draw`** –

  Draw the waveform.
- **`function`** –

  Evaluates the waveform function at a given time t.
- **`max`** –

  Get the maximum value of the waveform.
- **`min`** –

  Get the minimum value of the waveform.

Attributes:

- **`duration`** (`float`) –

  Returns the duration of the waveform.
- **`params`** (`dict[str, float | ndarray]`) –

  Dictionary of parameters used by the waveform.
- **`waveforms`** (`list[Waveform]`) –

  Returns a list of the individual waveforms, which is just this waveform.

#### duration

```
duration: float
```

Returns the duration of the waveform.

#### params

```
params: dict[str, float | ndarray]
```

Dictionary of parameters used by the waveform.

#### waveforms

```
waveforms: list[Waveform]
```

Returns a list of the individual waveforms, which is just this waveform.

#### \_\_call\_\_

```
__call__(t: float) -> float
```

```
__call__(t: list[float] | ndarray) -> NDArray[float64]
```

```
__call__(
    t: float | list[float] | ndarray,
) -> float | NDArray[float64]
```

Evaluate the waveform at `t`: a single time, or a 1D list or array of times.

Returns a float for a single time, otherwise a 1D float64 array. Times outside \[0, duration\] give 0.

#### \_\_mul\_\_

```
__mul__(other: float) -> Waveform
```

Rescale this waveform by a scalar.

#### \_\_repr\_\_

```
__repr__() -> str
```

Return the time interval and the waveform with its parameters.

#### \_\_rmul\_\_

```
__rmul__(other: float) -> Waveform
```

Rescale this waveform by a scalar (right-hand multiplication).

#### \_\_rshift\_\_

```
__rshift__(other: Waveform) -> CompositeWaveform
```

Returns a new CompositeWaveform composed of this waveform and another.

#### draw

```
draw(
    ax: Axes | None = None,
    color: ColorType = "tab:blue",
    n_points: int = 250,
) -> None
```

Draw the waveform.

Parameters:

- **`ax`** (`Axes | None`, default: `None` ) –

  The axes to draw into. If None, a new pyplot figure is created.
- **`color`** (`ColorType`, default: `'tab:blue'` ) –

  The color of the line and the filled area. Defaults to matplotlib's "tab:blue".
- **`n_points`** (`int`, default: `250` ) –

  The number of time samples to draw. Defaults to 250.

#### function

```
function(t: float) -> float
```

Evaluates the waveform function at a given time t.

#### max

```
max() -> float
```

Get the maximum value of the waveform.

#### min

```
min() -> float
```

Get the minimum value of the waveform.

### Waveform

```
Waveform(duration: float, **kwargs: float | ndarray)
```

Base class for scalar time-bounded waveforms.

A waveform is a scalar function of time defined over a finite interval \[0, duration\]. Outside this interval, it evaluates to zero.

To define a custom waveform, subclass this class and implement: - `function(t)`: the waveform value at time t within \[0, duration\]. - `max()`: the maximum value of the waveform. - `min()`: the minimum value of the waveform. - `__mul__(scalar)`: rescale this waveform by a scalar factor. - `_to_pulser(duration)`: conversion to a Pulser-compatible waveform.

Any additional parameters (e.g. amplitude, frequency) should be passed as keyword arguments to `__init__` and are automatically stored and accessible as attributes.

Parameters:

- **`duration`** (`float`) –

  the total duration of the waveform.
- **`**kwargs`** (`float | ndarray`, default: `{}` ) –

  optional keyword arguments for the waveform function.

Methods:

- **`__call__`** –

  Evaluate the waveform at `t`: a single time, or a 1D list or array of times.
- **`__mul__`** –

  Rescale this waveform by a scalar.
- **`__repr__`** –

  Return the time interval and the waveform with its parameters.
- **`__rmul__`** –

  Rescale this waveform by a scalar (right-hand multiplication).
- **`__rshift__`** –

  Returns a new CompositeWaveform composed of this waveform and another.
- **`draw`** –

  Draw the waveform.
- **`function`** –

  Evaluates the waveform function at a given time t.
- **`max`** –

  Get the maximum value of the waveform.
- **`min`** –

  Get the minimum value of the waveform.

Attributes:

- **`duration`** (`float`) –

  Returns the duration of the waveform.
- **`params`** (`dict[str, float | ndarray]`) –

  Dictionary of parameters used by the waveform.
- **`waveforms`** (`list[Waveform]`) –

  Returns a list of the individual waveforms, which is just this waveform.

#### duration

```
duration: float
```

Returns the duration of the waveform.

#### params

```
params: dict[str, float | ndarray]
```

Dictionary of parameters used by the waveform.

#### waveforms

```
waveforms: list[Waveform]
```

Returns a list of the individual waveforms, which is just this waveform.

#### \_\_call\_\_

```
__call__(t: float) -> float
```

```
__call__(t: list[float] | ndarray) -> NDArray[float64]
```

```
__call__(
    t: float | list[float] | ndarray,
) -> float | NDArray[float64]
```

Evaluate the waveform at `t`: a single time, or a 1D list or array of times.

Returns a float for a single time, otherwise a 1D float64 array. Times outside \[0, duration\] give 0.

#### \_\_mul\_\_

```
__mul__(other: float) -> Waveform
```

Rescale this waveform by a scalar.

#### \_\_repr\_\_

```
__repr__() -> str
```

Return the time interval and the waveform with its parameters.

#### \_\_rmul\_\_

```
__rmul__(other: float) -> Waveform
```

Rescale this waveform by a scalar (right-hand multiplication).

#### \_\_rshift\_\_

```
__rshift__(other: Waveform) -> CompositeWaveform
```

Returns a new CompositeWaveform composed of this waveform and another.

#### draw

```
draw(
    ax: Axes | None = None,
    color: ColorType = "tab:blue",
    n_points: int = 250,
) -> None
```

Draw the waveform.

Parameters:

- **`ax`** (`Axes | None`, default: `None` ) –

  The axes to draw into. If None, a new pyplot figure is created.
- **`color`** (`ColorType`, default: `'tab:blue'` ) –

  The color of the line and the filled area. Defaults to matplotlib's "tab:blue".
- **`n_points`** (`int`, default: `250` ) –

  The number of time samples to draw. Defaults to 250.

#### function

```
function(t: float) -> float
```

Evaluates the waveform function at a given time t.

#### max

```
max() -> float
```

Get the maximum value of the waveform.

#### min

```
min() -> float
```

Get the minimum value of the waveform.
