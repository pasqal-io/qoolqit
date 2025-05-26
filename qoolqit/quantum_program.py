from __future__ import annotations

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
