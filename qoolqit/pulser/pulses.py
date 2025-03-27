from __future__ import annotations

from pulser.pulse import Pulse as _Pulse
from pulser.waveforms import Waveform

from .waveforms import ConstantWaveform


class Pulse(_Pulse):
    def __init__(
        self,
        amplitude: Waveform | None = None,
        detuning: Waveform | None = None,
        phase: float = 0.0,
        post_phase_shift: float = 0.0,
    ) -> None:

        if amplitude is None and detuning is None:
            raise TypeError("'amplitude' and 'detuning' cannot both be empty.")

        if not isinstance(amplitude, Waveform):
            raise TypeError("'amplitude' has to be a waveform.")

        if detuning is None:
            detuning = ConstantWaveform(amplitude.duration, 0.0)

        if not isinstance(detuning, Waveform):
            raise TypeError("'detuning' has to be a waveform.")

        if amplitude is None:
            amplitude = ConstantWaveform(detuning.duration, 0.0)

        super().__init__(amplitude, detuning, phase, post_phase_shift)
