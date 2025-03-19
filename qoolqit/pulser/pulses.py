from __future__ import annotations

from dataclasses import dataclass

from pulser.pulse import Pulse as _Pulse
from pulser.waveforms import Waveform


@dataclass(init=False, repr=False, frozen=True)
class Pulse(_Pulse):
    def __init__(
        amplitude: Waveform, detuning: Waveform, phase: float = 0.0, post_phase_shift: float = 0.0
    ) -> None:
        super().__init__(amplitude, detuning, phase, post_phase_shift)
