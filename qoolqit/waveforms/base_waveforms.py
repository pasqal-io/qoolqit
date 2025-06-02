from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable
from typing import Any

import matplotlib.pyplot as plt
import numpy as np


class Waveform(ABC):
    """Base class for waveforms.

    A Waveform is a function of time for t >= 0. Custom waveforms can be defined by
    inheriting from the base class and overriding the `function` method corresponding
    to the function f(t) that returns the value of the waveform evaluated at time t.

    A waveform is always a 1D function, so if it includes other parameters, these should be
    passed and saved at initialization for usage within the `function` method.
    """

    def __init__(
        self,
        duration: float,
    ) -> None:
        """Initializes the Waveform.

        Arguments:
            duration: the total duration of the waveform.
        """

        if duration <= 0:
            raise ValueError("Duration needs to be a positive non-zero value.")

        self._duration = duration

    @property
    def duration(self) -> float:
        """Returns the duration of the waveform."""
        return self._duration

    @abstractmethod
    def function(self, t: float) -> float:
        """Evaluates the waveform function at a given time t."""
        pass

    @abstractmethod
    def max(self) -> float:
        """Get the maximum value of the waveform."""
        pass

    def __single_call__(self, t: float) -> float:
        return 0.0 if (t < 0.0 or t > self.duration) else self.function(t)

    def __call__(self, t: float | Iterable) -> float | list[float] | np.ndarray:
        if isinstance(t, Iterable):
            value_array: list[float] | np.ndarray
            if isinstance(t, np.ndarray):
                value_array = np.array([self.__single_call__(ti) for ti in t])
                return
            elif isinstance(t, list):
                value_array = [self.__single_call__(ti) for ti in t]
            else:
                raise TypeError(
                    "Waveform array calling is supported on Python lists or NumPy arrays."
                )
            return value_array
        else:
            return self.__single_call__(t)

    def __mul__(self, other: Waveform) -> CompositeWaveform:
        if isinstance(other, Waveform):
            if isinstance(other, CompositeWaveform):
                return CompositeWaveform(self, *other._waveforms)
            return CompositeWaveform(self, other)
        else:
            raise NotImplementedError(f"Composing with object of type {type(other)} not supported.")

    def _repr_header(self) -> str:
        return f"0 ≤ t < {float(self.duration):.3g}: "

    def _repr_content(self) -> str:
        return self.__class__.__name__ + "()"

    def __repr__(self) -> str:
        return self._repr_header() + self._repr_content()

    def draw(
        self, n_points: int = 500, return_fig: bool = False, **kwargs: Any
    ) -> plt.Figure | None:
        fig, ax = plt.subplots(1, 1, figsize=(8, 4), dpi=150)
        ax.grid(True)
        t_array = np.linspace(0.0, self.duration, n_points)
        y_array = self(t_array)
        ax.plot(t_array, self(t_array))
        ax.fill_between(t_array, y_array, color="skyblue", alpha=0.4)
        ax.set_xlabel("Time t")
        ax.set_ylabel("Waveform")
        return fig if return_fig else None


class CompositeWaveform(Waveform):
    """Base class for composite waveforms.

    A CompositeWaveform stores a sequence of waveforms occuring one after the other
    by the order given. When it is evaluated at time t, the corresponding waveform
    from the sequence is identified depending on the duration of each one, and it is
    then evaluated for a time t' = t minus the duration of all previous waveforms.
    """

    def __init__(self, *waveforms: Waveform) -> None:
        """Initializes the CompositeWaveform.

        Arguments:
            waveforms: an iterator over waveforms.
        """
        if not all(isinstance(wf, Waveform) for wf in waveforms):
            raise TypeError("All arguments must be instances of Waveform.")
        if not waveforms:
            raise ValueError("At least one Waveform must be provided.")

        self._waveforms = list(waveforms)

        super().__init__(sum(self.durations))

    @property
    def durations(self) -> list[float]:
        """Returns the list of durations of each individual waveform."""
        return [wf.duration for wf in self._waveforms]

    @property
    def times(self) -> list[float]:
        """Returns the list of times when each individual waveform starts."""
        time_array: list[float] = np.cumsum([0.0] + self.durations).tolist()
        return time_array

    @property
    def waveforms(self) -> list[Waveform]:
        """Returns a list of the individual waveforms."""
        return list(self._waveforms)

    @property
    def n_waveforms(self) -> int:
        """Returns the number of waveforms."""
        return len(self.waveforms)

    def function(self, t: float) -> float:
        """Identifies the right waveform in the composition and evaluates it at time t."""
        idx = np.searchsorted(self.times, t, side="right") - 1
        if idx == -1:
            return 0.0
        if idx == self.n_waveforms:
            if t == self.times[-1]:
                idx = idx - 1
            else:
                return 0.0

        local_t = t - self.times[idx]
        value: float = self.waveforms[idx](local_t)
        return value

    def max(self) -> float:
        """Get the maximum value of the waveform."""
        return max([wf.max() for wf in self.waveforms])

    def __mul__(self, other: Waveform) -> CompositeWaveform:
        if isinstance(other, Waveform):
            if isinstance(other, CompositeWaveform):
                return CompositeWaveform(*self.waveforms, *other.waveforms)
            return CompositeWaveform(*self.waveforms, other)
        else:
            raise NotImplementedError(f"Composing with object of type {type(other)} not supported.")

    def _repr_header(self) -> str:
        return "Composite waveform:\n"

    def _repr_content(self) -> str:
        wf_strings = []
        for i, wf in enumerate(self.waveforms):
            t_str = "≤ t <" if i < self.n_waveforms - 1 else "≤ t ≤"
            interval_str = (
                f"| {float(self.times[i]):.3g} " + t_str + f" {float(self.times[i + 1]):.3g}: "
            )
            wf_strings.append(interval_str + wf._repr_content())
        return "\n".join(wf_strings)

    def __repr__(self) -> str:
        return self._repr_header() + self._repr_content()
