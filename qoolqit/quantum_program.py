from __future__ import annotations

import numpy as np
from numpy.typing import ArrayLike
from pulser import Sequence as PulserSequence
from pulser_simulation import QutipEmulator

from qoolqit.devices import Device, MockDevice
from qoolqit.drive import Drive
from qoolqit.execution import CompilerProfile, SequenceCompiler
from qoolqit.register import Register

__all__ = ["QuantumProgram"]


class QuantumProgram:
    """A program representing a Sequence acting on a Register of qubits.

    Arguments:
        register: the Register of qubits.
        sequence: the Sequence of waveforms.
    """

    def __init__(
        self,
        register: Register,
        drive: Drive,
    ) -> None:

        self._register = register
        self._drive = drive
        self._compiled_sequence: PulserSequence | None = None
        self._device: Device | None = None

    @property
    def register(self) -> Register:
        """The register of qubits."""
        return self._register

    @property
    def drive(self) -> Drive:
        """The driving waveforms."""
        return self._drive

    @property
    def is_compiled(self) -> bool:
        """Check if the program has been compiled."""
        return False if self._compiled_sequence is None else True

    @property
    def compiled_sequence(self) -> PulserSequence:
        """The Pulser sequence compiled to a specific device."""
        if not self.is_compiled:
            raise ValueError(
                "Program has not been compiled. Please call program.compile_to(device)."
            )
        else:
            return self._compiled_sequence

    def __repr__(self) -> str:
        header = "Quantum Program:\n"
        register = f"| {self._register.__repr__()}\n"
        drive = f"| Drive(duration = {self._drive.duration:.3g})\n"
        if self.is_compiled:
            compiled = f"| Compiled: {self.is_compiled}\n"
            device = f"| Device: {self._device.__repr__()}"
        else:
            compiled = f"| Compiled: {self.is_compiled}"
            device = ""
        return header + register + drive + compiled + device

    def compile_to(
        self, device: Device, profile: CompilerProfile = CompilerProfile.DEFAULT
    ) -> None:
        """Compiles the given program to a device.

        Arguments:
            device: the Device to compile to.
            profile: the compiler profile to use during compilation.
        """
        compiler = SequenceCompiler(self.register, self.drive, device)
        compiler.profile = profile
        self._device = device
        self._compiled_sequence = compiler.compile_sequence()

    def run(self) -> ArrayLike:
        """Temporary method to run a simulation on QuTip."""
        if self._compiled_sequence is None:
            raise ValueError(
                "Program has not been compiled. Please call program.compile_to(device)."
            )
        elif self._device is not None:
            with_modulation = not isinstance(self._device, MockDevice)
            simulator = QutipEmulator.from_sequence(
                self._compiled_sequence, with_modulation=with_modulation
            )
            result = simulator.run()
            return np.array([np.flip(result[i].state[:].flatten()) for i in range(len(result))])
