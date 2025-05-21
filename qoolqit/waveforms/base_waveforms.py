from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable
from typing import Any

import matplotlib.pyplot as plt
import numpy as np


class Waveform(ABC):
    """Base class for waveforms.

    A Waveform is a function of time for t >= 0.
    """

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
    def function(self, t: float) -> float:
        """Evaluates the waveform function at a given time t."""
        pass

    def __single_call__(self, t: float) -> float:
        return 0.0 if (t < 0.0 or t > self.duration) else self.function(t)

    def __call__(self, t: float | Iterable) -> float | list:
        if isinstance(t, Iterable):
            return [self.__single_call__(ti) for ti in t]
        else:
            return self.__single_call__(t)

    def __mul__(self, other: Waveform) -> CompositeWaveform:
        if isinstance(other, Waveform):
            if isinstance(other, CompositeWaveform):
                return CompositeWaveform(self, *other._waveforms)
            return CompositeWaveform(self, other)
        else:
            raise NotImplementedError

    def _repr_header(self) -> str:
        return f"- 0 ≤ t < {float(self.duration):.3g}: "

    def _repr_content(self) -> str:
        return self.__class__.__name__ + "()"

    def __repr__(self) -> str:
        return self._repr_header() + self._repr_content()

    def draw(
        self, n_points: int = 500, return_fig: bool = False, **kwargs: Any
    ) -> plt.Figure | None:
        fig, ax = plt.subplots(1, 1, dpi=200)
        ax.grid(True)
        t_array = np.linspace(0.0, self.duration, n_points)
        ax.plot(t_array, self(t_array))
        return fig if return_fig else None


class CompositeWaveform(Waveform):
    """Base class for composite waveforms.

    Automatically handles the waveform order and calls each.
    """

    def __init__(self, *waveforms: Waveform) -> None:
        if not all(isinstance(wf, Waveform) for wf in waveforms):
            raise TypeError("All arguments must be instances of TimeFunction.")
        if not waveforms:
            raise ValueError("At least one Waveform must be provided.")

        self._waveforms = waveforms
        self._durations = [wf.duration for wf in waveforms]
        self._n_waveforms = len(self._durations)

        # Transition times between the different functions
        self._times: list[float] = np.cumsum([0.0] + self._durations).tolist()

        super().__init__(sum(self._durations))

    @property
    def durations(self) -> list[float]:
        return self._durations

    @property
    def times(self) -> list[float]:
        return self._times

    @property
    def waveforms(self) -> list[Waveform]:
        return list(self._waveforms)

    @property
    def n_waveforms(self) -> int:
        return self._n_waveforms

    def function(self, t: float) -> float:
        idx = np.searchsorted(self._times, t, side="right") - 1
        if idx == -1:
            return 0.0
        if idx == self.n_waveforms:
            if t == self._times[-1]:
                idx = idx - 1
            else:
                return 0.0

        local_t = t - self._times[idx]
        value: float = self._waveforms[idx](local_t)
        return value

    def __mul__(self, other: Waveform) -> CompositeWaveform:
        if isinstance(other, Waveform):
            if isinstance(other, CompositeWaveform):
                return CompositeWaveform(*self._waveforms, *other._waveforms)
            return CompositeWaveform(*self._waveforms, other)
        else:
            raise NotImplementedError

    def _repr_header(self) -> str:
        return "Composite waveform:\n"

    def _repr_content(self) -> str:
        wf_strings = []
        for i, wf in enumerate(self.waveforms):
            t_str = "≤ t <" if i < self.n_waveforms - 1 else "≤ t ≤"
            interval_str = (
                f"- {float(self.times[i]):.3g} " + t_str + f" {float(self.times[i + 1]):.3g}: "
            )
            wf_strings.append(interval_str + wf._repr_content())
        return "\n".join(wf_strings)

    def __repr__(self) -> str:
        return self._repr_header() + self._repr_content()
