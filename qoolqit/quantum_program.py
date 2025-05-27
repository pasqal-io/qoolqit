from __future__ import annotations

from pulser import Sequence as PulserSequence

from qoolqit.devices import Device
from qoolqit.execution import CompilerProfile, SequenceCompiler
from qoolqit.register import Register
from qoolqit.sequence import Sequence

__all__ = ["QuantumProgram"]


class QuantumProgram:
    """A program applying a continuous Sequence on a Register of qubits.

    Arguments:
        register: the Register of qubits.
        sequence: the Sequence of waveforms.
    """

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
        """The register of qubits."""
        return self._register

    @property
    def sequence(self) -> Sequence:
        """The sequence of waveforms."""
        return self._sequence

    @property
    def compiled_sequence(self) -> PulserSequence:
        """The Pulser sequence compiled to a specific device."""
        if self._compiled_sequence is None:
            raise ValueError(
                "Program has not been compiled. Please call program.compile_to(device)."
            )
        else:
            return self._compiled_sequence

    def compile_to(
        self, device: Device, profile: CompilerProfile = CompilerProfile.DEFAULT
    ) -> None:
        """Compiles the given program to a device.

        Arguments:
            device: the Device to compile to.
            profile: the compiler profile to use during compilation.
        """
        compiler = SequenceCompiler(self.register, self.sequence, device)
        compiler.profile = profile
        self._compiled_sequence = compiler.compile_sequence()
