from __future__ import annotations

from typing import Any

from pulser.pulse import Pulse
from pulser.sequence import Sequence as _Sequence
from pulser.waveforms import Waveform

from .devices import Device
from .register import Register


class Sequence(_Sequence):
    """Wraps the Sequence from Pulser for a simplified interface."""

    channel_label = "global"
    dmm_label = "dmm_0"

    def __init__(self, register: Register, device: Device):
        super().__init__(register, device._device)
        self.declare_channel(self.channel_label, "rydberg_global")
        self.weights: dict | None = None

    def set_weights(self, weights: dict) -> None:
        self.weights = weights
        detuning_map = self.register.define_detuning_map(weights, self.dmm_label)
        self.config_detuning_map(detuning_map, self.dmm_label)

    def add(self, pulse: Pulse, *args: Any, **kwargs: Any) -> None:
        super().add(pulse, self.channel_label, *args, **kwargs)

    def add_weighted_detuning(self, waveform: Waveform) -> None:
        if not self.weights:
            raise ValueError(
                "Adding a weighted detuning requires setting the "
                "qubit weights with the `set_weights` method."
            )
        self.add_dmm_detuning(waveform, self.dmm_label)
