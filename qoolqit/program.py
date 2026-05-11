from __future__ import annotations

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from pulser.sequence.sequence import Sequence as PulserSequence

from qoolqit.devices import Device
from qoolqit.drive import Drive
from qoolqit.exceptions import CompilationError
from qoolqit.execution.compilation_functions import CompilerProfile
from qoolqit.execution.sequence_compiler import SequenceCompiler
from qoolqit.register import Register


class QuantumProgram:
    """A program representing a Sequence acting on a Register of qubits.

    Arguments:
        register: the register of qubits, defining their positions.
        drive: the drive acting on qubits, defining amplitude, detuning and phase.
    """

    def __init__(
        self,
        register: Register,
        drive: Drive,
    ) -> None:

        if not isinstance(register, Register):
            raise TypeError("`register` must be of type Register.")
        self._register = register

        if not isinstance(drive, Drive):
            raise TypeError("`drive` must be of type Drive.")
        if drive.dmm is not None:
            dmm_weights = drive.dmm.weights
            for qid in dmm_weights.keys():
                if qid not in register.qubits:
                    raise ValueError(
                        "In this QuantumProgram, the drive's detuning modulator map (DMM) "
                        f"and the register do not match: qubit {qid} appears in the DMM "
                        "but is not defined in the register."
                    )

        self._drive = drive
        self._compiled_sequence: PulserSequence | None = None

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
        if not self._compiled_sequence:
            raise ValueError(
                "Program has not been compiled. Please call program.compile_to(device)."
            )
        return self._compiled_sequence

    def __repr__(self) -> str:
        header = "Quantum Program:\n"
        register = f"| {self._register.__repr__()}\n"
        drive = f"| Drive(duration = {self._drive.duration:.3f})\n"
        if self.is_compiled:
            compiled = f"| Compiled: {self.is_compiled}\n"
            device = f"| Device: {self._device.__repr__()}"
        else:
            compiled = f"| Compiled: {self.is_compiled}"
            device = ""
        return header + register + drive + compiled + device

    def compile_to(
        self,
        device: Device,
        profile: CompilerProfile = CompilerProfile.MAX_ENERGY,
        device_max_duration_ratio: float | None = None,
    ) -> None:
        """Compiles the quantum program for execution on a specific device.

        The compilation process adapts the program to the device's constraints while
        preserving the relative ratios of the original program parameters. Different
        compilation profiles optimize for specific objectives:

        - CompilerProfile.MAX_ENERGY (default): Scales the program to utilize the device's
            maximum capabilities. The drive amplitude and the register positions are rescaled
            to achieve respectively the maximum amplitude and the minimum pairwise distance
            compatible with the input program and the device's constraints.
        - CompilerProfile.WORKING_POINT: .

        Further options DO NOT preserve the input program, but rather adapts the program to
        the device's constraint. Programs compiled this way are not guaranteed to be portable
        across devices.

        - device_max_duration_ratio: Rescale the drive duration to a fraction of the
            device's maximum allowed duration.
            This option is useful in adiabatic protocols where one simply seek to
            minimize the time derivative of the drive's amplitude.

        Args:
            device: The target device for compilation. Must be a QoolQit Device :class:.
            profile: The compilation strategy to optimize the program.
                Defaults to CompilerProfile.MAX_ENERGY.
            device_max_duration_ratio: Whether to set the program duration to a fraction of
                the device's maximum allowed duration. Must be a number in the range (0, 1].
                Can only be set if the device has a maximum allowed duration.

        Raises:
            CompilationError: If the compilation fails due to device constraints.
        """
        if not isinstance(device, Device):
            raise TypeError("`device` must be of type `qoolqit.devices.Device`.")

        if device_max_duration_ratio is not None:
            if device._max_duration is None:
                raise ValueError(
                    "Cannot set `device_max_duration_ratio` because the target device "
                    "does not have a maximum allowed duration."
                )
            if not (0 < device_max_duration_ratio <= 1):
                raise ValueError(
                    "`device_max_duration_ratio` must be between 0 and 1, "
                    f"got {device_max_duration_ratio} instead."
                )

        # Check if device supports DMM and has a DMM channel
        if self.drive.dmm is not None:
            if not device._device.dmm_channels:
                raise CompilationError(
                    "The device does not support DMM. Please use a device that supports DMM."
                )

        compiler = SequenceCompiler(
            self.register, self.drive, device, profile, device_max_duration_ratio
        )
        self._device = device
        self._compiled_sequence = compiler.compile_sequence()

    def draw(
        self,
        n_points: int = 500,
        compiled: bool = False,
        return_fig: bool = False,
    ) -> Figure | None:
        if not compiled:
            return self.drive.draw(n_points=n_points, return_fig=return_fig)
        else:
            if not self.is_compiled:
                raise ValueError(
                    "Program has not been compiled. Please call program.compile_to(device)."
                )
            else:
                _, fig, _, _ = self.compiled_sequence._plot(
                    draw_phase_area=False,
                    draw_interp_pts=True,
                    draw_phase_shifts=False,
                    draw_register=False,
                    draw_input=True,
                    draw_modulation=True,
                    draw_phase_curve=True,
                    draw_detuning_maps=False,
                    draw_qubit_amp=False,
                    draw_qubit_det=False,
                    phase_modulated=False,
                )

                if return_fig:
                    plt.close()
                    return fig
                else:
                    return None


__all__ = ["QuantumProgram"]
