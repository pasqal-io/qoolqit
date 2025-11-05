from __future__ import annotations

import math
from typing import Any, Optional

import numpy as np
import pulser
from numpy.typing import ArrayLike
from pulser.parametrized import ParamObj
from scipy import interpolate

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

    Arguments:
        duration (int): The waveform duration (in ns).
        values (ArrayLike): Values of the interpolation points. Must be a list of castable
            to float or a parametrized object.
        times (ArrayLike): Fractions of the total duration (between 0 and 1),
            indicating where to place each value on the time axis. Must
            be a list of castable to float or a parametrized object. If
            not given, the values are spread evenly throughout the full
            duration of the waveform.
        interpolator: The SciPy interpolation class
            to use. Supports "PchipInterpolator" and "interp1d".
    """

    _valid_interpolators = ("PchipInterpolator", "interp1d")

    def __init__(
        self,
        duration: float,
        values: ArrayLike,
        times: Optional[ArrayLike] = None,
        interpolator: str = "PchipInterpolator",
        **interpolator_kwargs: Any,
    ):
        """Initializes a new InterpolatedWaveform."""
        super().__init__(duration)
        self._values = np.array(values, dtype=float)
        if times:  # fractional times in [0,1]
            if any([(ft < 0) or (ft > 1) for ft in times]):
                raise ValueError("All values in `times` must be in [0,1].")
            self._times = np.array(times, dtype=float)
            if len(times) != len(self._values):
                raise ValueError(
                    "Arguments `values` and `times` must be arrays of the same lenght."
                )
        else:
            self._times = np.linspace(0, 1, num=len(self._values))

        if interpolator not in self._valid_interpolators:
            raise ValueError(
                f"Invalid interpolator '{interpolator}', only "
                "accepts: " + ", ".join(self._valid_interpolators)
            )
        self._interpolator = interpolator
        self._interpolator_kwargs = interpolator_kwargs

        interp_cls = getattr(interpolate, interpolator)
        self._interp_func = interp_cls(duration * self._times, self._values, **interpolator_kwargs)

    def function(self, t: float) -> float:
        return float(self._interp_func(t))

    def min(self) -> float:
        return float(self._values.min())

    def max(self) -> float:
        return float(self._values.max())

    def _to_pulser(self, duration: int) -> ParamObj | pulser.InterpolatedWaveform:
        return pulser.InterpolatedWaveform(
            duration,
            values=self._values,
            times=self._times,
            interpolator=self._interpolator,
            **self._interpolator_kwargs,
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
