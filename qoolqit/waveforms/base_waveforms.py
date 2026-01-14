from __future__ import annotations

from abc import ABC, abstractmethod
from itertools import accumulate
from typing import Any, cast

import matplotlib.pyplot as plt
import numpy as np
import pulser
import torch
from matplotlib.figure import Figure
from pulser.parametrized import ParamObj
from pulser.waveforms import Waveform as PulserWaveform

from qoolqit.waveforms.utils import round_to_sum

# Default number of points used to resolve the full waveform duration
N_POINTS = 500


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
        *args: float,
        **kwargs: float | np.ndarray | torch.Tensor,
    ) -> None:
        """Initializes the Waveform.

        Arguments:
            duration: the total duration of the waveform.
        """

        if duration <= 0:
            raise ValueError("Duration needs to be a positive non-zero value.")

        if len(args) > 0:
            raise ValueError(
                f"Extra arguments in {type(self).__name__} need to be passed as keyword arguments"
            )

        self._duration = duration
        self._params_dict = kwargs

        self._max: float | torch.Tensor | None = None
        self._min: float | torch.Tensor | None = None

        for key, value in kwargs.items():
            setattr(self, key, value)

    @abstractmethod
    def function(self, t: float) -> float | torch.Tensor:
        """Evaluates the waveform function at a given time t."""
        ...

    @property
    def duration(self) -> float:
        """Returns the duration of the waveform."""
        return self._duration

    @property
    def params(self) -> dict[str, float | np.ndarray | torch.Tensor]:
        """Dictionary of parameters used by the waveform."""
        return self._params_dict

    def __call__(self, t: float) -> float | torch.Tensor:
        if t < 0.0 or t > self.duration:
            raise ValueError(f"Waveform called at time {t} outside [0.0, {self.duration}]")
        return self.function(t)

    def _approximate_min_max(self) -> None:
        # TOFIX: rewrite this using scipy.optimize or similar
        times = np.linspace(0.0, self.duration, N_POINTS)
        values = [self.function(t) for t in times]
        self._max = max(values)
        self._min = min(values)

    def max(self) -> float | torch.Tensor:
        """Get the approximate maximum value of the waveform.

        This is a brute-force method that samples the waveform over a
        pre-defined number of points to find the maximum value in the
        duration. Custom waveforms that have an easy to compute
        maximum value should override this method.
        """
        if self._max is None:
            self._approximate_min_max()
        return cast(float, self._max)

    def min(self) -> float | torch.Tensor:
        """Get the approximate minimum value of the waveform.

        This is a brute-force method that samples the waveform over a
        pre-defined number of points to find the minimum value in the
        duration. Custom waveforms that have an easy to compute
        maximum value should override this method.
        """
        if self._min is None:
            self._approximate_min_max()
        return cast(float, self._min)

    def _sample(self, num_points: int) -> np.ndarray:
        times = np.linspace(0.0, self.duration, num_points)
        values = [self.function(t) for t in times]
        for val in values:
            if isinstance(val, torch.Tensor):
                val = val.clone().detach()
        return np.array(values)

    def __rshift__(self, other: Waveform) -> CompositeWaveform:
        return self.__rrshift__(other)

    def __rrshift__(self, other: Waveform) -> CompositeWaveform:
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

    def _to_pulser(self, duration: int) -> ParamObj | PulserWaveform:
        """Convert an arbitrary Qoolqit waveform to a `pulser.InterpolatedWaveform`.

        To keep a compact representation the maximum number of samples to interpolate is set to 100.
        """
        n_samples = min(100, duration)
        times = np.linspace(0.0, self.duration, n_samples)
        samples = [self.function(t) for t in times]
        return pulser.InterpolatedWaveform(duration, samples)

    def draw(
        self, num_points: int = N_POINTS, return_fig: bool = False, **kwargs: Any
    ) -> Figure | None:
        times = np.linspace(0.0, self.duration, num_points)
        samples = self._sample(num_points)
        fig, ax = plt.subplots(1, 1, figsize=(8, 4), dpi=150)
        ax.grid(True, linewidth=0.5)
        ax.plot(times, samples)
        ax.fill_between(times, samples, color="skyblue", alpha=0.4)
        ax.set_xlabel("Time t")
        ax.set_ylabel("Waveform")
        if return_fig:
            plt.close()
            return fig
        else:
            return None


class CompositeWaveform(Waveform):
    """Base class for composite waveforms.

    A CompositeWaveform stores a sequence of waveforms occurring one after the other
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
        return [0.0] + list(accumulate(self.durations))

    @property
    def waveforms(self) -> list[Waveform]:
        """Returns a list of the individual waveforms."""
        return list(self._waveforms)

    @property
    def n_waveforms(self) -> int:
        """Returns the number of waveforms."""
        return len(self.waveforms)

    def function(self, t: float) -> float | torch.Tensor:
        """Identifies the right waveform in the composition and evaluates it at time t."""
        idx = np.searchsorted(self.times, t, side="right") - 1
        if t == self.duration:
            idx -= 1
        if idx < 0 or idx > self.n_waveforms:
            raise ValueError(f"CompositeWaveform called at time {t} outside [0.0, {self.duration}]")
        local_t = np.clip(t - self.times[idx], 0.0, self.waveforms[idx].duration)
        value = self.waveforms[idx](local_t)
        return value

    def max(self) -> float | torch.Tensor:
        """Get the maximum value of the composite waveform."""
        return max([wf.max() for wf in self.waveforms])

    def min(self) -> float | torch.Tensor:
        """Get the minimum value of the composite waveform."""
        return min([wf.min() for wf in self.waveforms])

    def __rshift__(self, other: Waveform) -> CompositeWaveform:
        return self.__rrshift__(other)

    def __rrshift__(self, other: Waveform) -> CompositeWaveform:
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

    def _to_pulser(self, duration: int) -> ParamObj | pulser.CompositeWaveform:
        """Converts a CompositeWaveform from QoolQit to Pulser.

        Pulser only supports integer duration, so the sum of rounded
        durations of each waveform needs to add up to the rounded duration
        of the composite waveform.
        """
        ratio = duration / self.duration
        new_durations = round_to_sum([ratio * wd for wd in self.durations])
        pulser_waveforms = (
            w._to_pulser(duration=duration) for w, duration in zip(self.waveforms, new_durations)
        )
        return pulser.CompositeWaveform(*pulser_waveforms)
