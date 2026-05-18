from __future__ import annotations

import math

import numpy as np
import pulser
from numpy.typing import ArrayLike
from pulser.parametrized import ParamObj
from scipy.interpolate import PchipInterpolator

from qoolqit.waveforms.base_waveforms import CompositeWaveform, Waveform


class Delay(Waveform):
    """An empty waveform."""

    def function(self, t: float) -> float:
        return 0.0

    def max(self) -> float:
        return 0.0

    def min(self) -> float:
        return 0.0

    def _to_pulser(self, duration: int) -> ParamObj | pulser.ConstantWaveform:
        return pulser.ConstantWaveform(duration, 0.0)


class Ramp(Waveform):
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

    def _to_pulser(self, duration: int) -> ParamObj | pulser.RampWaveform:
        return pulser.RampWaveform(duration, self.initial_value, self.final_value)


class Constant(Waveform):
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

    def _to_pulser(self, duration: int) -> ParamObj | pulser.ConstantWaveform:
        return pulser.ConstantWaveform(duration, self.value)


class Blackman(Waveform):
    """A Blackman window of a specified duration and area under the curve.

    Implements the Blackman window shaped waveform
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
        blackman_wf = Blackman(100.0, area=3.14)
        ```
    """

    area: float

    def __init__(self, duration: float, area: float) -> None:
        """Initializes a new Blackman waveform."""
        super().__init__(duration, area=area)

    def function(self, t: float) -> float:
        alpha = 2 * math.pi / self.duration
        A = self.area / (0.42 * self.duration)
        return A * (0.42 - 0.5 * math.cos(alpha * t) + 0.08 * math.cos(2 * alpha * t))

    def max(self) -> float:
        return self.area / (0.42 * self.duration)

    def min(self) -> float:
        return 0.0

    def _to_pulser(self, duration: int) -> ParamObj | pulser.BlackmanWaveform:
        return pulser.BlackmanWaveform(duration, self.area)


class PiecewiseLinear(CompositeWaveform):
    """A piecewise linear waveform.

    Creates a composite waveform of N ramps that linearly interpolate
    through the given N+1 values.

    Arguments:
        durations: list or tuple of N duration values.
        values: list or tuple of N+1 waveform values.
    """

    def __init__(
        self,
        durations: list | tuple,
        values: list | tuple,
    ) -> None:
        if not (isinstance(durations, (list, tuple)) or isinstance(values, (list, tuple))):
            raise TypeError(
                "A PiecewiseLinear waveform requires a list or tuple of durations and values."
            )

        if len(durations) + 1 != len(values) or len(durations) == 1:
            raise ValueError(
                "A PiecewiseLinear waveform requires N durations and N + 1 values, for N >= 2."
            )

        for duration in durations:
            if duration == 0.0:
                raise ValueError("A PiecewiseLinear interval cannot have zero duration.")

        self.values = values

        wfs = [Ramp(dur, values[i], values[i + 1]) for i, dur in enumerate(durations)]

        super().__init__(*wfs)

    def __repr_header__(self) -> str:
        return "Piecewise linear waveform:\n"


class Interpolated(Waveform):
    """A waveform created from interpolation of a set of data points.

    Attributes:
        duration: The waveform duration (in ns).
        values: Values of the interpolation points. Must be a list of castable
            to float or a parametrized object.
        times: Fractions of the total duration (between 0 and 1),
            indicating where to place each value on the time axis. Must be a list
            of castable to float or a parametrized object. If not given, the
            values are spread evenly throughout the full duration of the waveform.

    Notes:
        Uses scipy's PchipInterpolator for the interpolation.
        PCHIP (Piecewise Cubic Hermite Interpolating Polynomial) is a shape-preserving interpolator
        (C1 smooth), preserves monotonicity in the interpolation data and does not overshoot them.
    """

    def __init__(
        self,
        duration: float,
        values: ArrayLike,
        times: ArrayLike | None = None,
    ):
        """Initializes an Interpolated waveform.

        Args:
            duration: The waveform duration.
            values: Values of the interpolation points.
            times: Fractions of the total duration (between 0 and 1),
                indicating where to place each value on the time axis.
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


class Sin(Waveform):
    """An arbitrary sine over a given duration.

    Arguments:
        duration: the total duration.
        amplitude: the amplitude of the sine wave.
        omega: the frequency of the sine wave.
        phi: the phase of the sine wave.
        shift: the vertical shift of the sine wave.
    """

    amplitude: float
    omega: float
    phi: float
    shift: float

    def __init__(
        self,
        duration: float,
        amplitude: float = 1.0,
        omega: float = 1.0,
        phi: float = 0.0,
        shift: float = 0.0,
    ) -> None:
        super().__init__(duration, amplitude=amplitude, omega=omega, phi=phi, shift=shift)

    def function(self, t: float) -> float:
        return self.amplitude * math.sin(self.omega * t + self.phi) + self.shift
