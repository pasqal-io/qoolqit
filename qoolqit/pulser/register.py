from __future__ import annotations

from pulser.register import Register as _Register


class Register(_Register):

    @property
    def n_qubits(self) -> int:
        return len(self.qubits)

    def __repr__(self) -> str:
        return self.__class__.__name__ + f"(n_qubits = {self.n_qubits})"
