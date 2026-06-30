"""Concrete waveform implementations."""

from __future__ import annotations

import math

import numpy as np
import pulser
from numpy.typing import ArrayLike
from pulser.parametrized import ParamObj
from scipy.interpolate import PchipInterpolator

from qoolqit.waveforms.base_waveforms import CompositeWaveform, Waveform


class DelayWaveform(Waveform):
    """An empty waveform."""

    def function(self, t: float) -> float:
        return 0.0

    def max(self) -> float:
        return 0.0

    def min(self) -> float:
        return 0.0

    def __mul__(self, other: float) -> Waveform:
        return self

    def _to_pulser(self, duration: int) -> ParamObj | pulser.ConstantWaveform:
        return pulser.ConstantWaveform(duration, 0.0)


class RampWaveform(Waveform):
    """A ramp that linearly interpolates between an initial and final value.

    Arguments:
        duration: the total duration.
        initial_value: the initial value at t = 0.
        final_value: the final value at t = duration.
    """

    initial_value: float
    final_value: float

    def __init__(
        self,
        duration: float,
        initial_value: float,
        final_value: float,
    ) -> None:
        super().__init__(duration, initial_value=initial_value, final_value=final_value)

    def function(self, t: float) -> float:
        fraction = t / self._duration
        return self.initial_value + fraction * (self.final_value - self.initial_value)

    def max(self) -> float:
        return max([self.initial_value, self.final_value])

    def min(self) -> float:
        return min([self.initial_value, self.final_value])

    def __mul__(self, other: float) -> Waveform:
        return RampWaveform(
            self.duration,
            initial_value=self.initial_value * other,
            final_value=self.final_value * other,
        )

    def _to_pulser(self, duration: int) -> ParamObj | pulser.RampWaveform:
        return pulser.RampWaveform(duration, self.initial_value, self.final_value)


class ConstantWaveform(Waveform):
    """A constant waveform over a given duration.

    Arguments:
        duration: the total duration.
        value: the value to take during the duration.
    """

    value: float

    def __init__(
        self,
        duration: float,
        value: float,
    ) -> None:
        super().__init__(duration, value=value)

    def function(self, t: float) -> float:
        return self.value

    def max(self) -> float:
        return self.value

    def min(self) -> float:
        return self.value

    def __mul__(self, other: float) -> Waveform:
        return ConstantWaveform(self.duration, value=self.value * other)

    def _to_pulser(self, duration: int) -> ParamObj | pulser.ConstantWaveform:
        return pulser.ConstantWaveform(duration, self.value)


class BlackmanWaveform(Waveform):
    """A Blackman window of a specified duration and area under the curve.

    Implements the positive Blackman window shaped waveform
        blackman(t) = A*(0.42 - 0.5*cos(αt) + 0.08*cos(2αt))
                  A = area/(0.42*duration)
                  α = 2π/duration

    See:
    https://en.wikipedia.org/wiki/Window_function#:~:text=Blackman%20window

    Arguments:
        duration: The waveform duration.
        area: The integral of the waveform.

    Example:
        ```python
        blackman_wf = BlackmanWaveform(100.0, area=3.14)
        ```
    """

    area: float

    def __init__(self, duration: float, area: float) -> None:
        """Initializes a new BlackmanWaveform."""
        super().__init__(duration, area=area)

    def function(self, t: float) -> float:
        alpha = 2 * math.pi / self.duration
        A = self.area / (0.42 * self.duration)
        value = A * (0.42 - 0.5 * math.cos(alpha * t) + 0.08 * math.cos(2 * alpha * t))
        return max(value, 0.0)

    def max(self) -> float:
        return self.area / (0.42 * self.duration)

    def min(self) -> float:
        return 0.0

    def __mul__(self, other: float) -> Waveform:
        return BlackmanWaveform(self.duration, area=self.area * other)

    def _to_pulser(self, duration: int) -> ParamObj | pulser.BlackmanWaveform:
        return pulser.BlackmanWaveform(duration, self.area)


class PiecewiseLinearWaveform(CompositeWaveform):
    """A piecewise linear waveform.

    Creates a composite waveform of N ramps that linearly interpolate
    through the given N+1 values.

    Arguments:
        durations: list or tuple of N duration values.
        values: list or tuple of N+1 waveform values.
    """

    def __init__(
        self,
        durations: list[float] | tuple[float, ...] | np.ndarray,
        values: list[float] | tuple[float, ...] | np.ndarray,
    ) -> None:

        if len(durations) + 1 != len(values) or len(durations) == 1:
            raise ValueError(
                "A PiecewiseLinearWaveform requires N durations and N + 1 values, for N >= 2."
            )

        for duration in durations:
            if duration == 0.0:
                raise ValueError("A PiecewiseLinearWaveform interval cannot have zero duration.")

        self.values = values

        wfs = [RampWaveform(dur, values[i], values[i + 1]) for i, dur in enumerate(durations)]

        super().__init__(*wfs)

    def __mul__(self, other: float) -> CompositeWaveform:
        return PiecewiseLinearWaveform(
            self.durations, values=[value * other for value in self.values]
        )

    def __repr_header__(self) -> str:
        return "Piecewise linear waveform:\n"


class InterpolatedWaveform(Waveform):
    """A waveform created from shape-preserving interpolation of data points.

    This class creates a smooth waveform by interpolating between specified data points
    using PCHIP (Piecewise Cubic Hermite Interpolating Polynomial) interpolation. The
    interpolating curve preserves the shape of the input data:
    bounds (avoiding under/overshooting), monotonicity, and convexity.

    Uses scipy's PchipInterpolator for the interpolation.

    Attributes:
        duration: The waveform duration.
        values: Array-like sequence of waveform values at the interpolation points.
            Must be convertible to float. These values define the amplitude of the
            waveform at the corresponding time points.
        times: Optional array-like sequence of fractional times in the range [0, 1]
            indicating where to place each value on the time axis. Must have the same
            length as `values`. If not provided, values are distributed evenly across
            the waveform duration. Default is None.

    Raises:
    ValueError: If `times` contains values outside [0, 1] or if `times` and
        `values` have different lengths.

    Example:
        >>> # Create a waveform with 4 points over 100ns
        >>> values = [0.0, 1.0, 0.5, 0.0]
        >>> wf = InterpolatedWaveform(100, values)
        >>>
        >>> # Create with custom timing
        >>> times = [0.0, 0.2, 0.8, 1.0]  # Non-uniform spacing
        >>> wf = InterpolatedWaveform(100, values, times)
    """

    def __init__(
        self,
        duration: float,
        values: ArrayLike,
        times: ArrayLike | None = None,
    ):
        """Initialize an Interpolated waveform.

        Args:
            duration: The total duration of the waveform. Must be positive.
            values: Array-like sequence of waveform values at interpolation points.
                Can be a list, tuple, numpy array, or any sequence convertible to float.
            times: Optional array-like sequence of fractional times in [0, 1]. If provided,
                must have the same length as `values`. If None, values are evenly spaced
                across the duration. Default is None.

        Raises:
            ValueError: If any value in `times` is outside [0, 1], or if `times` and
                `values` have different lengths.
        """
        super().__init__(duration)
        self._values = np.array(values, dtype=float)
        if times is not None:
            self._times = np.array(times, dtype=float)
            if any([(ft < 0) or (ft > 1) for ft in self._times]):
                raise ValueError("All values in `times` must be in [0,1].")
            if len(self._times) != len(self._values):
                raise ValueError(
                    "Arguments `values` and `times` must be arrays of the same length."
                )
        else:
            self._times = np.linspace(0, 1, num=len(self._values))

        self._interp_func = PchipInterpolator(duration * self._times, values)

    def function(self, t: float) -> float:
        return float(self._interp_func(t))

    def min(self) -> float:
        return float(self._values.min())

    def max(self) -> float:
        return float(self._values.max())

    def __mul__(self, other: float) -> Waveform:
        return InterpolatedWaveform(self.duration, self._values * other, self._times)

    def _to_pulser(
        self,
        duration: int,
        energy_factor: float = 1.0,
    ) -> ParamObj | pulser.InterpolatedWaveform:
        truncated_values = self._values * energy_factor
        return pulser.InterpolatedWaveform(
            duration,
            values=truncated_values,
            times=self._times,
            interpolator="PchipInterpolator",
        )
