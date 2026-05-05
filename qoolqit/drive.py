from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure

from qoolqit.waveforms import CompositeWaveform, Delay, Waveform

__all__ = ["DetuningMapModulator", "Drive"]


@dataclass(frozen=True)
class DetuningMapModulator:
    """A weighted detuning for the Detuning Map Modulator (DMM).

    Args:
        waveform: The waveform for this detuning. Must be negative for all times.
        weights: A dictionary associating detuning weights to qubits.
            Each weight must be in [0, 1], where 0 means that the waveform is ignored for
            this qubit and 1 means that the waveform is fully applied to this qubit.

    See https://docs.pasqal.com/pulser/tutorials/dmm/ for details on DMM.
    """

    waveform: Waveform
    weights: dict[Any, float]

    def __post_init__(self) -> None:
        if self.waveform.max() > 0:
            raise ValueError("`waveform` must be negative for all times.")
        if any(weight < 0 or weight > 1 for weight in self.weights.values()):
            raise ValueError("`weights` must be a dictionary of values in [0, 1].")


class Drive:
    """The drive Hamiltonian acting over a duration."""

    def __init__(
        self,
        *,
        amplitude: Waveform,
        detuning: Waveform | None = None,
        dmm: DetuningMapModulator | None = None,
        phase: float = 0.0,
    ) -> None:
        """Initialize a Drive.

        The Drive specifies the control parameters for the time-dependent drive Hamiltonian
        in the Rydberg model
        (see https://docs.pasqal.com/qoolqit/get_started/qoolqit_model/ for details),

        H_drive(t) = Σᵢ [Ω(t)/2 (cos φ(t) σˣᵢ - sin φ(t) σʸᵢ)] - Σᵢ [δ(t) + εᵢ Δ(t)] nᵢ

        representing:
        - Amplitude Ω(t): Controls the Rabi frequency that drives qubits.
        - Detuning δ(t): Controls the energy offset of the Rydberg state.
        - dmm εᵢ, Δ(t): Detuning Map Modulator (DMM) for additional qubit-specific detunings.
        - Phase φ: Global phase applied to the amplitude term.

        Args:
            amplitude: Time-dependent amplitude waveform Ω(t) representing the Rabi frequency.
                Controls the strength of the coupling between ground and Rydberg states.
                Must be positive for all times.
            detuning: Time-dependent detuning waveform δ(t) representing the energy offset
                of the Rydberg state relative to resonance. If None, defaults to zero
                detuning (Delay waveform) for the duration of the amplitude.
            dmm: DetuningMapModulator instance for additional negative detuning waveform Δ(t) ≤ 0
                applied to individual qubits as specified by its `weights` attribute εᵢ.
            phase: Global phase φ applied to the amplitude term in the Hamiltonian.
                Defaults to 0.0 (no phase).

        Raises:
            TypeError: If amplitude or detuning are not Waveform instances.
            ValueError: If the amplitude waveform has negative values.

        Note:
            - All arguments must be passed as keyword arguments.
            - If amplitude and detuning have different durations, the shorter one is
              automatically extended with a Delay to match the longer duration.
            - DetuningMapModulator waveform must be negative for all times
                (≤ 0) as it represents energy shifts below the resonance.

        Example:
            >>> from qoolqit import Drive
            >>> from qoolqit.waveforms import Constant, Ramp
            >>>
            >>> # Simple constant drive
            >>> drive = Drive(amplitude=Constant(10.0, 1.5))
            >>>
            >>> # Drive with time-varying amplitude and detuning
            >>> amp = Ramp(5.0, 0.0, 2.0)
            >>> det = Constant(5.0, -1.0)
            >>> drive = Drive(amplitude=amp, detuning=det, phase=0.5)
        """

        for arg in [amplitude, detuning]:
            if arg is not None and not isinstance(arg, Waveform):
                raise TypeError("'amplitude' and 'detuning' must be of type Waveform.")

        if amplitude.min() < 0.0:
            raise ValueError("'amplitude' must be positive.")

        self._amplitude = amplitude
        self._detuning = detuning if detuning is not None else Delay(amplitude.duration)

        self._amplitude_orig = self._amplitude
        self._detuning_orig = self._detuning

        # adjust amplitude and detuning waveforms to match the duration
        if self._amplitude.duration > self._detuning.duration:
            extra_duration = self._amplitude.duration - self._detuning.duration
            self._detuning = CompositeWaveform(self._detuning, Delay(extra_duration))
        elif self._detuning.duration > self._amplitude.duration:
            extra_duration = self._detuning.duration - self._amplitude.duration
            self._amplitude = CompositeWaveform(self._amplitude, Delay(extra_duration))

        self._duration = self._amplitude.duration
        if dmm is not None and not isinstance(dmm, DetuningMapModulator):
            raise TypeError("'dmm' must be of type DetuningMapModulator.")
        self._dmm = dmm
        self._phase = phase

    @property
    def amplitude(self) -> Waveform:
        """The amplitude waveform in the drive."""
        return self._amplitude_orig

    @property
    def detuning(self) -> Waveform:
        """The detuning waveform in the drive."""
        return self._detuning_orig

    @property
    def dmm(self) -> DetuningMapModulator | None:
        """Detuning Map Modulator (DMM) applied to individual qubits."""
        return self._dmm

    @property
    def phase(self) -> float:
        """The phase value in the drive."""
        return self._phase

    @property
    def duration(self) -> float:
        return self._duration

    def __rshift__(self, other: Drive) -> Drive:
        return self.__rrshift__(other)

    def __rrshift__(self, other: Drive) -> Drive:
        if isinstance(other, Drive):
            if self.phase != other.phase:
                raise NotImplementedError("Composing drives with different phase not supported.")
            return Drive(
                amplitude=CompositeWaveform(self._amplitude, other._amplitude),
                detuning=CompositeWaveform(self._detuning, other._detuning),
                phase=self._phase,
            )
        else:
            raise NotImplementedError(f"Composing with object of type {type(other)} not supported.")

    def __amp_header__(self) -> str:
        return "Amplitude: \n"

    def __det_header__(self) -> str:
        return "Detuning: \n"

    def __repr__(self) -> str:
        if isinstance(self.amplitude, CompositeWaveform):
            amp_repr = self.__amp_header__() + self.amplitude.__repr_content__()
        else:
            amp_repr = (
                self.__amp_header__()
                + self.amplitude.__repr_header__()
                + self.amplitude.__repr_content__()
            )
        if isinstance(self.detuning, CompositeWaveform):
            det_repr = self.__det_header__() + self.detuning.__repr_content__()
        else:
            det_repr = (
                self.__det_header__()
                + self.detuning.__repr_header__()
                + self.detuning.__repr_content__()
            )
        return amp_repr + "\n\n" + det_repr

    def draw(self, n_points: int = 500, return_fig: bool = False) -> Figure | None:
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

        if return_fig:
            plt.close()
            return fig
        else:
            return None
