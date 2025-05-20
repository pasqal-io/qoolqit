from __future__ import annotations

from abc import ABC, abstractmethod

import numpy as np


class TimeFunction(ABC):
    """Base class for time-functions."""

    def __init__(
        self,
        duration: float,
    ) -> None:

        if duration <= 0:
            raise ValueError("Duration needs to be a positive non-zero value.")

        self._duration = duration

    @property
    def duration(self) -> float:
        return self._duration

    @abstractmethod
    def _generating_function(self, t: float) -> float:
        """Evaluates the function at a given time t."""
        pass

    def __call__(self, t: float) -> float:
        if t < 0.0 or t > self.duration:
            return 0.0
        else:
            return self._generating_function(t)

    def __mul__(self, other: TimeFunction) -> SequentialTimeFunction:
        if isinstance(other, TimeFunction):
            if isinstance(other, SequentialTimeFunction):
                return SequentialTimeFunction(self, *other._functions)
            return SequentialTimeFunction(self, other)
        else:
            raise NotImplementedError


class Ramp(TimeFunction):
    """
    A ramp function that linearly interpolates between initial_value and final_value.

    over its duration.
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

    def _generating_function(self, t: float) -> float:
        fraction = t / self._duration
        return self.initial_value + fraction * (self.final_value - self.initial_value)


class Constant(TimeFunction):
    """
    A ramp function that linearly interpolates between initial_value and final_value.

    over its duration.
    """

    def __init__(
        self,
        duration: float,
        value: float,
    ) -> None:
        super().__init__(duration)
        self.value = value

    def _generating_function(self, t: float) -> float:
        return self.value


class SequentialTimeFunction(TimeFunction):
    def __init__(self, *functions: TimeFunction) -> None:
        if not all(isinstance(f, TimeFunction) for f in functions):
            raise TypeError("All arguments must be instances of TimeFunction.")
        if not functions:
            raise ValueError("At least one TimeFunction must be provided.")

        self._functions = functions
        self._durations = [f.duration for f in functions]
        self._n_functions = len(self._durations)

        # Transition times between the different functions
        self._times = np.cumsum([0.0] + self._durations).tolist()

        super().__init__(sum(self._durations))

    @property
    def durations(self) -> list[float]:
        return self._durations

    @property
    def n_functions(self) -> int:
        return self._n_functions

    def _generating_function(self, t: float) -> float:
        idx = np.searchsorted(self._times, t, side="right") - 1
        if idx == -1:
            return 0.0
        if idx == self.n_functions:
            if t == self._times[-1]:
                idx = idx - 1
            else:
                return 0.0

        local_t = t - self._times[idx]
        value: float = self._functions[idx](local_t)
        return value

    def __mul__(self, other: TimeFunction) -> SequentialTimeFunction:
        if isinstance(other, TimeFunction):
            if isinstance(other, SequentialTimeFunction):
                return SequentialTimeFunction(*self._functions, *other._functions)
            return SequentialTimeFunction(*self._functions, other)
        else:
            raise NotImplementedError


class PiecewiseLinear(SequentialTimeFunction):
    """
    A piecewise linear time function.

    Arguments:
        durations: List or tuple of N duration values.
        values: List or tuple of N+1 waveform values.
    """

    def __init__(
        self,
        durations: list | tuple,
        values: list | tuple,
    ) -> None:
        if not (isinstance(durations, (list, tuple)) or isinstance(values, (list, tuple))):
            raise TypeError(
                "A PiecewiseLinear time function requires a list or tuple of durations and values."
            )

        if len(durations) + 1 != len(values) or len(durations) == 1:
            raise ValueError(
                "A PiecewiseLinear time function requires N durations and N + 1 values, for N >= 2."
            )

        for duration in durations:
            if duration == 0.0:
                raise ValueError("A PiecewiseLinear interval cannot have zero duration.")

        self.values = values

        wfs = [Ramp(dur, values[i], values[i + 1]) for i, dur in enumerate(durations)]

        super().__init__(*wfs)

    def __repr__(self) -> str:
        intervals = [
            f"{d}: {float(self.values[i]):.3g}->{float(self.values[i + 1]):.3g}"
            for i, d in enumerate(self.durations)
        ]
        string = ""
        for i, interval in enumerate(intervals):
            string += interval
            if i != len(intervals) - 1:
                string += ", "
        return self.__class__.__name__ + "(" + string + ")"
