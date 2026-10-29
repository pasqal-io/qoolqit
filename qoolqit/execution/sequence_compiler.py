"""SequenceCompiler: turn a register and drive into a Pulser sequence for a device."""

from __future__ import annotations

from collections.abc import Callable

from pulser.sequence.sequence import Sequence as PulserSequence

from qoolqit.devices import Device
from qoolqit.drive import Drive
from qoolqit.exceptions import CompilationError
from qoolqit.register import Register

from .compilation_functions import CompilerProfile, basic_compilation


class SequenceCompiler:
    """Compiles a QoolQit Register and Drive to a Device."""

    def __init__(
        self,
        register: Register,
        drive: Drive,
        device: Device,
        profile: CompilerProfile,
        device_max_duration_ratio: float | None = None,
    ) -> None:
        """Initializes the compiler.

        Args:
            register: the QoolQit Register.
            drive: the QoolQit Drive.
            device: the QoolQit Device.
            profile: the CompilerProfile to use.
            device_max_duration_ratio: optionally set the program duration to a fraction
                of the device's maximum allowed duration.
        """
        self._register = register
        self._drive = drive
        self._device = device
        self._target_device = device._device
        self._profile = profile
        self._device_max_duration_ratio = device_max_duration_ratio
        self._compilation_function: Callable = basic_compilation

    @property
    def register(self) -> Register:
        """The QoolQit register to compile."""
        return self._register

    @property
    def drive(self) -> Drive:
        """The QoolQit drive to compile."""
        return self._drive

    @property
    def device(self) -> Device:
        """The target QoolQit device."""
        return self._device

    @property
    def profile(self) -> CompilerProfile:
        """The compiler profile used for compilation."""
        return self._profile

    @property
    def device_max_duration_ratio(self) -> float | None:
        """Fraction of the device's maximum duration to use, if set."""
        return self._device_max_duration_ratio

    def compile_sequence(self) -> PulserSequence:
        """Compiles the register and drive into a Pulser sequence.

        Raises:
            CompilationError: if compilation fails.
        """
        try:
            return self._compilation_function(
                self.register,
                self.drive,
                self.device,
                self.profile,
                self.device_max_duration_ratio,
            )
        except CompilationError:
            raise
        except Exception as err:
            raise CompilationError(f"Failed to compile the sequence due to:\n\n{err}") from err
