from __future__ import annotations

from typing import Any

from pulser.sequence import Sequence as _Sequence
from pulser.waveforms import Waveform

from .devices import Device
from .pulses import Pulse
from .register import Register


class Sequence(_Sequence):
    """Wraps the Sequence from Pulser for a simplified interface."""

    channel_label = "global"
    dmm_label = "dmm_0"

    def __init__(self, register: Register, device: Device, weights: dict | None = None):
        super().__init__(register, device._device)
        self.declare_channel(self.channel_label, "rydberg_global")

        self._weights = weights

        if self._weights is not None:
            self.detuning_map = self.register.define_detuning_map(weights, self.dmm_label)
            self.config_detuning_map(self.detuning_map, self.dmm_label)

    def add(self, pulse: Pulse, *args: Any, **kwargs: Any) -> None:
        super().add(pulse, self.channel_label, *args, **kwargs)

    def add_weighted_detuning(self, waveform: Waveform) -> None:
        if not self._weights:
            raise ValueError(
                "Adding a weighted detuning requires initializing the "
                "sequence with qubit weights using the `weights` argument."
            )
        self.add_dmm_detuning(waveform, self.dmm_label)

    @property
    def weights(self) -> dict:
        weight_dict: dict = {q: 0.0 for q in self.register.qubits}
        if self._weights:
            weight_dict = self.detuning_map.get_qubit_weight_map(self.register.qubits)
        return weight_dict
