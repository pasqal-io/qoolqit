from __future__ import annotations

import math

from .base_waveforms import CompositeWaveform, Waveform


class Delay(Waveform):
    """An empty waveform."""

    def function(self, t: float) -> float:
        return 0.0

    def max(self) -> float:
        return 0.0


class Ramp(Waveform):
    """A ramp that linearly interpolates between an initial and final value.

    Arguments:
        duration: the total duration.
        initial_value: the initial value at t = 0.
        final_value: the final value at t = duration.
    """

    def __init__(
        self,
        duration: float,
        initial_value: float,
        final_value: float,
    ) -> None:
        super().__init__(duration)
        self.initial_value = initial_value
        self.final_value = final_value

    def function(self, t: float) -> float:
        fraction = t / self._duration
        return self.initial_value + fraction * (self.final_value - self.initial_value)

    def max(self) -> float:
        return max([self.initial_value, self.final_value])

    def _repr_content(self) -> str:
        string = str(self.initial_value) + ", " + str(self.final_value)
        return self.__class__.__name__ + "(" + string + ")"


class Constant(Waveform):
    """A constant waveform over a given duration.

    Arguments:
        duration: the total duration.
        value: the value to take during the duration.
    """

    def __init__(
        self,
        duration: float,
        value: float,
    ) -> None:
        super().__init__(duration)
        self.value = value

    def function(self, t: float) -> float:
        return self.value

    def max(self) -> float:
        return self.value

    def _repr_content(self) -> str:
        string = str(self.value)
        return self.__class__.__name__ + "(" + string + ")"


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

    def _repr_header(self) -> str:
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
        k_candidate = math.ceil((min_theta - target_theta) / (2 * math.pi))
        if target_theta + 2 * k_candidate * math.pi <= max_theta:
            return global_max
        else:
            value_at_0: float = self(0.0)  # type: ignore [assignment]
            value_at_dur: float = self(self.duration)  # type: ignore [assignment]
            return max(value_at_0, value_at_dur)

    def _repr_content(self) -> str:
        params = [str(self.amplitude), str(self.omega), str(self.phi), str(self.shift)]
        string = ", ".join(params)
        return self.__class__.__name__ + "(" + string + ")"
