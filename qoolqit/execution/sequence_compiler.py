from __future__ import annotations

from typing import Callable

from pulser import Sequence as PulserSequence

from qoolqit.devices import AvailableDevices, Device
from qoolqit.register import Register
from qoolqit.sequence import Sequence

from .compilation_functions import basic_compilation
from .utils import CompilerProfile

COMPILATION_FUNCTIONS = {
    AvailableDevices.MOCK.value: basic_compilation,
    AvailableDevices.ANALOG.value: basic_compilation,
    AvailableDevices.TEST_ANALOG.value: basic_compilation,
}

ALL_COMPILER_PROFILES: set = set(CompilerProfile.list())

SUPPORTED_PROFILES = {
    AvailableDevices.MOCK.value: ALL_COMPILER_PROFILES,
    AvailableDevices.ANALOG.value: ALL_COMPILER_PROFILES,
    AvailableDevices.TEST_ANALOG.value: ALL_COMPILER_PROFILES,
}


class SequenceCompiler:
    """Compiles a QoolQit Register and Sequence to a Device."""

    def __init__(self, register: Register, sequence: Sequence, device: Device):
        """Initializes the compiler.

        Arguments:
            register: the QoolQit Register.
            sequence: the QoolQit Sequence.
            device: the QoolQit Device.
        """

        self._register = register
        self._sequence = sequence
        self._device = device

        self._target_device = device._device

        self._compilation_function: Callable | None = COMPILATION_FUNCTIONS.get(device.name, None)
        self._profile = CompilerProfile.DEFAULT

    @property
    def register(self) -> Register:
        return self._register

    @property
    def sequence(self) -> Sequence:
        return self._sequence

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
            return self._compilation_function(
                self.register,
                self.sequence,
                self.device,
                self.profile,
            )
