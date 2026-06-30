"""Base classes for scalar time-bounded waveforms and their sequential composition."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, overload

import matplotlib.pyplot as plt
import numpy as np
import pulser
from matplotlib.figure import Figure
from pulser.parametrized import ParamObj
from pulser.waveforms import Waveform as PulserWaveform

from qoolqit.waveforms.utils import round_to_sum


class Waveform(ABC):
    """Base class for scalar time-bounded waveforms.

    A waveform is a scalar function of time defined over a finite interval [0, duration].
    Outside this interval, it evaluates to zero.

    To define a custom waveform, subclass this class and implement:
        - `function(t)`: the waveform value at time t within [0, duration].
        - `max()`: the maximum value of the waveform.
        - `min()`: the minimum value of the waveform.
        - `_to_pulser(duration)`: conversion to a Pulser-compatible waveform.

    Any additional parameters (e.g. amplitude, frequency) should be passed as keyword
    arguments to `__init__` and are automatically stored and accessible as attributes.
    """

    def __init__(
        self,
        duration: float,
        *args: float,
        **kwargs: float | np.ndarray,
    ) -> None:
        """Initializes the Waveform.

        Args:
            duration: the total duration of the waveform.
            **kwargs: optional keyword arguments for the waveform function.
        """

        if duration <= 0:
            raise ValueError("Duration needs to be a positive non-zero value.")

        if len(args) > 0:
            raise ValueError(
                f"Extra arguments in {type(self).__name__} need to be passed as keyword arguments"
            )

        self._duration = duration
        self._params_dict = kwargs

        for key, value in kwargs.items():
            setattr(self, key, value)

    @abstractmethod
    def function(self, t: float) -> float:
        """Evaluates the waveform function at a given time t."""
        pass

    @abstractmethod
    def max(self) -> float:
        """Get the maximum value of the waveform."""
        pass

    @abstractmethod
    def min(self) -> float:
        """Get the minimum value of the waveform."""
        pass

    @abstractmethod
    def __mul__(self, other: float) -> Waveform:
        """Rescale this waveform by a scalar."""
        pass

    def __rmul__(self, other: float) -> Waveform:
        """Rescale this waveform by a scalar (right-hand multiplication)."""
        return self.__mul__(other)

    @abstractmethod
    def _to_pulser(self, duration: int) -> ParamObj | PulserWaveform:
        """Converts QoolQit waveform to a Pulser Waveform."""
        pass

    @property
    def duration(self) -> float:
        """Returns the duration of the waveform."""
        return self._duration

    @property
    def params(self) -> dict[str, float | np.ndarray]:
        """Dictionary of parameters used by the waveform."""
        return self._params_dict

    def _single_call(self, t: float) -> float:
        return 0.0 if (t < 0.0 or t > self.duration) else self.function(t)

    @overload
    def __call__(self, t: float) -> float: ...

    @overload
    def __call__(self, t: list[float] | np.ndarray) -> list | np.ndarray: ...

    def __call__(self, t: float | list[float] | np.ndarray) -> float | list[float] | np.ndarray:
        if isinstance(t, np.ndarray):
            return np.vectorize(self._single_call)(t)
        if isinstance(t, list):
            return [self._single_call(ti) for ti in t]
        return self._single_call(t)

    def __rshift__(self, other: Waveform) -> CompositeWaveform:
        """Returns a new CompositeWaveform composed of this waveform and another."""
        if isinstance(other, Waveform):
            if isinstance(other, CompositeWaveform):
                return CompositeWaveform(self, *other._waveforms)
            return CompositeWaveform(self, other)
        else:
            raise NotImplementedError(f"Composing with object of type {type(other)} not supported.")

    def __repr_header__(self) -> str:
        return f"0.00 ≤ t ≤ {float(self.duration):.2f}: "

    def __repr_content__(self) -> str:
        if len(self.params) > 0:
            params_list = [f"{value:.2f}" for value in self.params.values()]
            string = ", ".join(params_list)
            return self.__class__.__name__ + "(t, " + string + ")"
        else:
            return self.__class__.__name__ + "(t)"

    def __repr__(self) -> str:
        return self.__repr_header__() + self.__repr_content__()

    def draw(self, n_points: int = 500, return_fig: bool = False, **kwargs: Any) -> Figure | None:
        fig, ax = plt.subplots(1, 1, figsize=(8, 4), dpi=150)
        ax.grid(True)
        t_array = np.linspace(0.0, self.duration, n_points)
        y_array = self(t_array)
        ax.plot(t_array, y_array)
        ax.fill_between(t_array, y_array, color="skyblue", alpha=0.4)
        ax.set_xlabel("Time t")
        ax.set_ylabel("Waveform")
        if return_fig:
            plt.close()
            return fig
        else:
            return None


class CompositeWaveform(Waveform):
    """A concatenation of waveforms played sequentially.

    Waveforms are joined in the given order, each starting where the previous one ends,
    and the composition can be used as a single waveform.

    Attributes:
        waveforms: a list of waveforms in the composition.
        durations: a list of durations of each individual waveform.
        times: a list of times when each individual waveform starts.
    """

    def __init__(self, *waveforms: Waveform) -> None:
        """Initializes the CompositeWaveform.

        Arguments:
            waveforms: an iterator over waveforms.

        Raises:
            TypeError: if any argument is not an instance of Waveform.
            ValueError: if no waveforms are provided.
        """
        if not all(isinstance(wf, Waveform) for wf in waveforms):
            raise TypeError("All arguments must be instances of Waveform.")
        if not waveforms:
            raise ValueError("At least one Waveform must be provided.")

        self._waveforms = []
        for wf in waveforms:
            if isinstance(wf, CompositeWaveform):
                self._waveforms += wf.waveforms
            else:
                self._waveforms.append(wf)

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
        idx = np.searchsorted(self.times, t, side="right") - 1
        # clip to valid waveform index range
        idx = np.clip(idx, 0, self.n_waveforms - 1)

        local_t = t - self.times[idx]
        value: float = self.waveforms[idx](local_t)
        return value

    def max(self) -> float:
        """Get the maximum value of the waveform."""
        return max([wf.max() for wf in self.waveforms])

    def min(self) -> float:
        """Get the minimum value of the waveform."""
        return min([wf.min() for wf in self.waveforms])

    def __mul__(self, other: float) -> CompositeWaveform:
        return CompositeWaveform(*[wf * other for wf in self.waveforms])

    def __rshift__(self, other: Waveform) -> CompositeWaveform:
        if isinstance(other, Waveform):
            if isinstance(other, CompositeWaveform):
                return CompositeWaveform(*self.waveforms, *other.waveforms)
            return CompositeWaveform(*self.waveforms, other)
        else:
            raise NotImplementedError(f"Composing with object of type {type(other)} not supported.")

    def __repr_header__(self) -> str:
        return "Composite waveform:\n"

    def __repr_content__(self) -> str:
        wf_strings = []
        for i, wf in enumerate(self.waveforms):
            t_str = "≤ t <" if i < self.n_waveforms - 1 else "≤ t ≤"
            interval_str = (
                f"| {float(self.times[i]):.2f} " + t_str + f" {float(self.times[i + 1]):.2f}: "
            )
            wf_strings.append(interval_str + wf.__repr_content__())
        return "\n".join(wf_strings)

    def __repr__(self) -> str:
        return self.__repr_header__() + self.__repr_content__()

    def _to_pulser(
        self, duration: int
    ) -> ParamObj | pulser.waveforms.Waveform | pulser.CompositeWaveform:
        """Converts a CompositeWaveform from QoolQit to Pulser.

        Pulser only supports integer duration, so the sum of rounded
        durations of each waveform needs to add up to the rounded duration
        of the composite waveform.

        If the duration of a waveform in ns is rounded to zero, it will be ignored.

        Args:
            duration (int): the new duration fo the Pulser waveform in ns.
        """
        ratio = duration / self.duration
        new_durations = round_to_sum([ratio * wd for wd in self.durations])
        pulser_waveforms = [
            w._to_pulser(duration=duration)
            for w, duration in zip(self.waveforms, new_durations)
            if duration
        ]
        if len(pulser_waveforms) == 1:
            return pulser_waveforms[0]
        return pulser.CompositeWaveform(*pulser_waveforms)
