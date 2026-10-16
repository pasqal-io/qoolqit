"""Drive Hamiltonian (amplitude, detuning, phase) and its Detuning Map Modulator (DMM)."""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import FigureBase

from qoolqit.waveforms import CompositeWaveform, ConstantWaveform, DelayWaveform, Waveform

__all__ = ["DetuningMapModulator", "Drive"]


def _mod_2pi(x: float) -> float:
    """Reduce x modulo 2π to [0, 2π).

    Float rounding can make tiny negative values wrap to exactly 2π, so those are
    mapped to 0.

    Args:
        x: The value to reduce.
    """
    x = float(x) % math.tau
    return 0.0 if x >= math.tau else x


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
        dmm: DetuningMapModulator | Sequence[DetuningMapModulator] | None = None,
        phase: float = 0.0,
    ) -> None:
        """Initialize a Drive.

        The Drive specifies the control parameters for the time-dependent drive Hamiltonian
        in the Rydberg model
        (see https://docs.pasqal.com/qoolqit/get_started/qoolqit_model/ for details),

        H_drive(t) = Σᵢ [Ω(t)/2 (cos φ(t) σˣᵢ - sin φ(t) σʸᵢ)] - Σᵢ [δ(t) + Σₖ εᵢₖ Δₖ(t)] nᵢ

        representing:
        - Amplitude Ω(t): Controls the Rabi frequency that drives qubits.
        - Detuning δ(t): Controls the energy offset of the Rydberg state.
        - dmm εᵢₖ, Δₖ(t): Detuning Map Modulators (DMM) for additional qubit-specific detunings.
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
                Also accepts a sequence of them, each one a detuning map εᵢₖ, Δₖ(t): a single
                map scales one time profile per qubit, several maps let qubits follow time
                profiles that are not proportional. Compiling several maps requires a device
                that can reuse its DMM channel, such as `MockDevice`.
            phase: Global phase φ applied to the amplitude term in the Hamiltonian.
                Defaults to 0.0 (no phase). Normalized to [0, 2π) and stored as a
                ConstantWaveform spanning the full duration of the drive.

        Raises:
            TypeError: If amplitude or detuning are not Waveform instances, or if dmm is not
                a DetuningMapModulator or a sequence of them.
            ValueError: If the amplitude waveform has negative values, or if the phase
                is not finite.

        Note:
            - All arguments must be passed as keyword arguments.
            - If amplitude and detuning have different durations, the shorter one is
              automatically extended with a Delay to match the longer duration.
            - DetuningMapModulator waveform must be negative for all times
                (≤ 0) as it represents energy shifts below the resonance.

        Example:
            >>> from qoolqit import Drive
            >>> from qoolqit.waveforms import ConstantWaveform, RampWaveform
            >>>
            >>> # Simple constant drive
            >>> drive = Drive(amplitude=ConstantWaveform(10.0, 1.5))
            >>>
            >>> # Drive with time-varying amplitude and detuning
            >>> amp = RampWaveform(5.0, 0.0, 2.0)
            >>> det = ConstantWaveform(5.0, -1.0)
            >>> drive = Drive(amplitude=amp, detuning=det, phase=0.5)
        """
        for arg in [amplitude, detuning]:
            if arg is not None and not isinstance(arg, Waveform):
                raise TypeError("'amplitude' and 'detuning' must be of type Waveform.")

        if amplitude.min() < 0.0:
            raise ValueError("'amplitude' must be positive.")

        if not math.isfinite(phase):
            raise ValueError("'phase' must be finite.")

        self._amplitude = amplitude
        self._detuning = detuning if detuning is not None else DelayWaveform(amplitude.duration)

        self._amplitude_orig = self._amplitude
        self._detuning_orig = self._detuning

        # adjust amplitude and detuning waveforms to match the duration
        if self._amplitude.duration > self._detuning.duration:
            extra_duration = self._amplitude.duration - self._detuning.duration
            self._detuning = CompositeWaveform(self._detuning, DelayWaveform(extra_duration))
        elif self._detuning.duration > self._amplitude.duration:
            extra_duration = self._detuning.duration - self._amplitude.duration
            self._amplitude = CompositeWaveform(self._amplitude, DelayWaveform(extra_duration))

        self._duration = self._amplitude.duration
        # a single DMM is kept as given, a sequence as a tuple, an empty one as None
        self._dmm = (tuple(dmm) or None) if isinstance(dmm, Sequence) else dmm
        if not all(isinstance(d, DetuningMapModulator) for d in self._dmms):
            raise TypeError(
                "'dmm' must be of type DetuningMapModulator or a sequence of DetuningMapModulator."
            )
        self._phase = ConstantWaveform(self.duration, _mod_2pi(phase))

    @property
    def amplitude(self) -> Waveform:
        """The amplitude waveform in the drive."""
        return self._amplitude_orig

    @property
    def detuning(self) -> Waveform:
        """The detuning waveform in the drive."""
        return self._detuning_orig

    @property
    def dmm(self) -> DetuningMapModulator | tuple[DetuningMapModulator, ...] | None:
        """Detuning Map Modulator (DMM) applied to individual qubits.

        A tuple when the drive was given a sequence of them.
        """
        return self._dmm

    @property
    def _dmms(self) -> tuple[DetuningMapModulator, ...]:
        """The DMMs of the drive as a tuple, empty if there is none."""
        if self._dmm is None:
            return ()
        return self._dmm if isinstance(self._dmm, tuple) else (self._dmm,)

    @property
    def phase(self) -> ConstantWaveform:
        """The phase waveform in the drive."""
        return self._phase

    @property
    def duration(self) -> float:
        return self._duration

    def __rshift__(self, other: Drive) -> Drive:
        if not isinstance(other, Drive):
            return NotImplemented
        if self.dmm is not None or other.dmm is not None:
            raise NotImplementedError("Composing drives with a dmm is not supported.")
        if self.phase.value != other.phase.value:
            raise NotImplementedError("Composing drives with different phase not supported.")
        return Drive(
            amplitude=CompositeWaveform(self._amplitude, other._amplitude),
            detuning=CompositeWaveform(self._detuning, other._detuning),
            phase=self.phase.value,
        )

    def __amp_header__(self) -> str:
        return "amplitude: \n"

    def __det_header__(self) -> str:
        return "detuning: \n"

    def __phase_header__(self) -> str:
        return "phase: \n"

    def __dmm_header__(self) -> str:
        return "dmm: \n"

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

        repr = amp_repr + "\n" + det_repr

        if self.phase.value != 0:
            phase_repr = (
                self.__phase_header__()
                + self.phase.__repr_header__()
                + self.phase.__repr_content__()
            )
            repr += "\n" + phase_repr

        if self.dmm is not None:
            dmm_repr = self.__dmm_header__() + "\n".join(dmm.__repr__() for dmm in self._dmms)
            repr += "\n" + dmm_repr

        return repr

    def draw(self, fig: FigureBase | None = None) -> None:
        """Draw the amplitude, detuning, phase and DMM of the Drive.

        The phase is drawn only if it is non-zero, and the DMM only if one is set.

        Args:
            fig: The figure or subfigure to draw into. If None, a new pyplot figure is
                created.
        """
        if fig is None:
            fig = plt.figure()

        # setup subplots
        nrows = 2
        if self.dmm is not None:
            nrows += 1
        has_phase = self.phase.value != 0
        if has_phase:
            nrows += 1

        axs = fig.subplots(nrows, 1, sharex=True)

        # samples
        times = np.linspace(0.0, self.duration, 250)
        amplitude = self.amplitude(times)
        detuning = self.detuning(times)

        # draw amplitude
        axs[0].set_ylabel("Amplitude")
        axs[0].plot(times, amplitude, color="darkgreen")
        axs[0].fill_between(times, amplitude, color="darkgreen", alpha=0.4)

        # draw detuning
        axs[1].set_axisbelow(True)
        axs[1].set_ylabel("Detuning")
        axs[1].plot(times, detuning, color="darkmagenta")
        axs[1].fill_between(times, detuning, color="darkmagenta", alpha=0.4)

        # draw phase if present
        if has_phase:
            phase = self.phase(times) / (2 * np.pi)
            axs[2].set_ylabel(r"Phase $/ \ 2\pi$")
            axs[2].plot(times, phase, color="darkorange")
            axs[2].fill_between(times, phase, color="darkorange", alpha=0.4)

        # draw DMM if present
        if self.dmm is not None:
            axs[-1].set_ylabel("DMM")
        for dmm in self._dmms:
            y_dmm = dmm.waveform(times)
            axs[-1].plot(times, y_dmm, color="darkblue")
            axs[-1].fill_between(times, y_dmm, color="darkblue", alpha=0.4)

        axs[-1].set_xlabel("Time t")

        # add grids
        for ax in axs:
            ax.grid(True, color="lightgray", linestyle="--", linewidth=0.7)
