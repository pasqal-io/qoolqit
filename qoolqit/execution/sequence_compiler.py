from __future__ import annotations

from typing import Callable

from pulser.sequence.sequence import Sequence as PulserSequence

from qoolqit.devices import Device
from qoolqit.drive import Drive
from qoolqit.exceptions import CompilationError
from qoolqit.register import Register

from .compilation_functions import CompilerProfile, basic_compilation


class SequenceCompiler:
    """Compiles a QoolQit Register and Drive to a Device."""

    def __init__(self, register: Register, drive: Drive, device: Device, profile: CompilerProfile):
        """Initializes the compiler.

        Arguments:
            register: the QoolQit Register.
            drive: the QoolQit Drive.
            device: the QoolQit Device.
        """

        self._register = register
        self._drive = drive
        self._device = device
        self._target_device = device._device
        self._profile = profile
        self._compilation_function: Callable = basic_compilation

    @property
    def register(self) -> Register:
        return self._register

    @property
    def drive(self) -> Drive:
        return self._drive

    @property
    def device(self) -> Device:
        return self._device

    @property
    def profile(self) -> CompilerProfile:
        return self._profile

    def compile_sequence(self) -> PulserSequence:
        try:
            return self._compilation_function(
                self.register,
                self.drive,
                self.device,
                self.profile,
            )
        except CompilationError as error:
            raise error
        except Exception as error:
            raise CompilationError(f"Failed to compile the sequence due to:\n\n{error}")
