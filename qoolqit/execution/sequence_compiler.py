from __future__ import annotations

from typing import Callable

from pulser.sequence.sequence import Sequence as PulserSequence

from qoolqit.devices import AvailableDevices, Device
from qoolqit.drive import Drive
from qoolqit.exceptions import CompilationError
from qoolqit.register import Register

from .compilation_functions import basic_compilation
from .utils import CompilerProfile

COMPILATION_FUNCTIONS = {device.value: basic_compilation for device in AvailableDevices}

ALL_COMPILER_PROFILES: set = set(CompilerProfile.list())

SUPPORTED_PROFILES = {device.value: ALL_COMPILER_PROFILES for device in AvailableDevices}


class SequenceCompiler:
    """Compiles a QoolQit Register and Drive to a Device."""

    def __init__(self, register: Register, drive: Drive, device: Device):
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

        self._compilation_function: Callable | None = COMPILATION_FUNCTIONS.get(device.name, None)
        self._profile = CompilerProfile.DEFAULT

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
        """The compiler profile to use."""
        return self._profile

    @profile.setter
    def profile(self, profile: CompilerProfile) -> None:
        """Set the compiler profile.

        Arguments:
            profile: the chosen compiler profile.
        """
        if profile not in CompilerProfile:
            raise TypeError(
                "Unknown profile, please pick one from the CompilerProfile enumeration."
            )
        elif profile not in SUPPORTED_PROFILES[self.device.name]:
            raise NotImplementedError(
                f"The requested profile is not implemented for device {self.device.name}"
            )
        else:
            self._profile = profile

    def compile_sequence(self) -> PulserSequence:
        if self._compilation_function is None:
            raise ValueError(f"Device {self.device.name} has an unknown compilation function.")
        else:
            try:
                return self._compilation_function(
                    self.register,
                    self.drive,
                    self.device,
                    self.profile,
                )
            except Exception as error:
                raise CompilationError(f"Failed to compile the sequence due to:\n\n{error}")
