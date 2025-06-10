from __future__ import annotations

import math

from .base_waveforms import CompositeWaveform, Waveform


class Delay(Waveform):
    """An empty waveform."""

    def function(self, t: float) -> float:
        return 0.0

    def max(self) -> float:
        return 0.0

    def min(self) -> float:
        return 0.0


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
