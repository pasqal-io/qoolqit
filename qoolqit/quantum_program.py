from __future__ import annotations

from pulser import Sequence as PulserSequence

from qoolqit.devices import Device
from qoolqit.execution import SequenceCompiler
from qoolqit.register import Register
from qoolqit.sequence import Sequence

__all__ = ["QuantumProgram"]


class QuantumProgram:
    def __init__(
        self,
        register: Register,
        sequence: Sequence,
    ) -> None:

        self._register = register
        self._sequence = sequence
        self._compiled_sequence: Sequence | None = None

    @property
    def register(self) -> Register:
        return self._register

    @property
    def sequence(self) -> Sequence:
        return self._sequence

    @property
    def compiled_sequence(self) -> PulserSequence:
        if self._compiled_sequence is None:
            raise ValueError(
                "Program has not been compiled. Please call program.compile_to(device)."
            )
        else:
            return self._compiled_sequence

    def compile_to(self, device: Device) -> None:
        compiler = SequenceCompiler(self.register, self.sequence, device)
        self._compiled_sequence = compiler.compile_sequence()
