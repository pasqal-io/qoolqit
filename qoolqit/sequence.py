from __future__ import annotations

from typing import Any

import matplotlib.pyplot as plt
import numpy as np

from qoolqit.waveforms import CompositeWaveform, Delay, Waveform

__all__ = ["Sequence"]


class Sequence:
    """A Sequence representing the drive Hamiltonian acting over a duration."""

    def __init__(
        self,
        *args: Any,
        amplitude: Waveform | None = None,
        detuning: Waveform | None = None,
        phase: float = 0.0,
    ) -> None:
        """Default constructor for the Sequence.

        Must be instantiated with keyword arguments. Accepts either an amplitude waveform,
        a detuning waveform, or both. A phase value can also be passed.

        Arguments:
            amplitude: waveform representing Ω(t) in the drive Hamiltonian.
            detuning: waveform representing δ(t) in the drive Hamiltonian.
            phase: phase value ɸ for the amplitude term.
        """

        if len(args) > 0:
            raise TypeError("Please pass the `amplitude` and / or `detuning` as keyword arguments.")

        if amplitude is None and detuning is None:
            raise ValueError("Amplitude and detuning cannot both be empty.")

        for arg in [amplitude, detuning]:
            if arg is not None and not isinstance(arg, Waveform):
                raise TypeError("Amplitude and detuning must be of type Waveform.")

        # Ok let's try to please mypy...

        self._amplitude: Waveform
        self._detuning: Waveform
        self._amplitude_orig: Waveform
        self._detuning_orig: Waveform

        if amplitude is None and isinstance(detuning, Waveform):
            self._amplitude = Delay(detuning.duration)
            self._detuning = detuning
        elif detuning is None and isinstance(amplitude, Waveform):
            self._amplitude = amplitude
            self._detuning = Delay(amplitude.duration)
        elif isinstance(detuning, Waveform) and isinstance(amplitude, Waveform):
            self._amplitude = amplitude
            self._detuning = detuning

        self._amplitude_orig = self._amplitude
        self._detuning_orig = self._detuning

        if self._amplitude.duration > self._detuning.duration:
            extra_duration = self._amplitude.duration - self._detuning.duration
            self._detuning = self._detuning * Delay(extra_duration)
        elif self._detuning.duration > self._amplitude.duration:
            extra_duration = self._detuning.duration - self._amplitude.duration
            self._amplitude = self._amplitude * Delay(extra_duration)

        self._duration = self._amplitude.duration
        self._phase = phase

    @property
    def amplitude(self) -> Waveform:
        """The amplitude waveform in the sequence."""
        return self._amplitude_orig

    @property
    def detuning(self) -> Waveform:
        """The detuning waveform in the sequence."""
        return self._detuning_orig

    @property
    def phase(self) -> float:
        """The phase value in the sequence."""
        return self._phase

    @property
    def duration(self) -> float:
        return self._duration

    def __mul__(self, other: Sequence) -> Sequence:
        if isinstance(other, Sequence):
            if self.phase != other.phase:
                raise NotImplementedError("Composing sequences with different phase not supported.")
            return Sequence(
                amplitude=self._amplitude * other._amplitude,
                detuning=self._detuning * other._detuning,
                phase=self._phase,
            )
        else:
            raise NotImplementedError(f"Composing with object of type {type(other)} not supported.")

    def _amplitude_header(self) -> str:
        return "Amplitude: \n"

    def _detuning_header(self) -> str:
        return "Detuning: \n"

    def __repr__(self) -> str:
        if isinstance(self.amplitude, CompositeWaveform):
            amp_repr = self._amplitude_header() + self.amplitude._repr_content()
        else:
            amp_repr = (
                self._amplitude_header()
                + self.amplitude._repr_header()
                + self.amplitude._repr_content()
            )
        if isinstance(self.detuning, CompositeWaveform):
            det_repr = self._detuning_header() + self.detuning._repr_content()
        else:
            det_repr = (
                self._detuning_header()
                + self.detuning._repr_header()
                + self.detuning._repr_content()
            )
        return amp_repr + "\n\n" + det_repr

    def draw(self, n_points: int = 500, return_fig: bool = False) -> plt.Figure | None:
        fig, ax = plt.subplots(2, 1, sharex=True, figsize=(16, 4), dpi=200)

        ax[0].grid(True, color="lightgray", linestyle="--", linewidth=0.7)
        ax[0].set_axisbelow(True)
        ax[0].set_ylabel("Amplitude")
        ax[1].grid(True, color="lightgray", linestyle="--", linewidth=0.7)
        ax[1].set_axisbelow(True)
        ax[1].set_ylabel("Detuning")
        ax[1].set_xlabel("Time t")

        t_array = np.linspace(0.0, self.duration, n_points)
        y_amp = self.amplitude(t_array)
        y_det = self.detuning(t_array)

        ax[0].plot(t_array, y_amp, color="darkgreen")
        ax[1].plot(t_array, y_det, color="darkmagenta")

        ax[0].fill_between(t_array, y_amp, color="darkgreen", alpha=0.4)
        ax[1].fill_between(t_array, y_det, color="darkmagenta", alpha=0.4)

        return fig if return_fig else None
