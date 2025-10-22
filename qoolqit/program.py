from __future__ import annotations

from typing import Any, Union
from warnings import warn

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from pulser.sequence.sequence import Sequence as PulserSequence

from qoolqit.devices import Device, MockDevice
from qoolqit.drive import Drive
from qoolqit.execution.backend import EmuMPSBackend, OutputType, QutipBackend
from qoolqit.execution.sequence_compiler import SequenceCompiler
from qoolqit.execution.utils import BackendName, CompilerProfile, ResultType
from qoolqit.register import Register

__all__ = ["QuantumProgram"]

BackendType = Union[QutipBackend, EmuMPSBackend]


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
        for detuning in drive.weighted_detunings:
            for key in detuning.weights.keys():
                if key not in register.qubits:
                    raise ValueError(
                        "In this QuantumProgram, the drive and the register "
                        f"do not match: qubit {key} appears in the drive but "
                        f"is not defined in the register."
                    )

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

    def run(
        self,
        backend_name: BackendName = BackendName.QUTIP,
        result_type: ResultType = ResultType.STATEVECTOR,
        runs: int = 100,
        evaluation_times: list[float] = [1.0],
        **backend_params: Any,
    ) -> OutputType:
        """Run the compiled sequence on selected backend.

        `run()` method of a QuantumProgram is deprecated starting from qoolqit v0.1.3.

        Please, instantiate a backend from `qoolqit.execution.backends` and run the program
        through its submit/run method, as discussed in the [documentation](https://pasqal-io.github.io/qoolqit/latest/contents/execution/).
        """  # noqa
        warn(
            """`run()` method of a QuantumProgram is deprecated starting from qoolqit v0.1.3.

                Please, instantiate a backend from `qoolqit.execution.backends` and run the program
                through its submit/run method, as discussed in the [documentation](https://pasqal-io.github.io/qoolqit/latest/contents/execution/).""",
            DeprecationWarning,
        )
        if self._compiled_sequence is None:
            raise ValueError(
                "Program has not been compiled. Please call program.compile_to(device)."
            )
        elif self._device is not None:
            # initialize the backend
            backend_params["with_modulation"] = not isinstance(self._device, MockDevice)
            backend: BackendType
            if backend_name == BackendName.QUTIP:
                backend = QutipBackend(self._compiled_sequence, result_type, **backend_params)
                return backend.run(runs, evaluation_times)
            elif backend_name == BackendName.EMUMPS:
                backend = EmuMPSBackend(self._compiled_sequence, result_type, **backend_params)
                return backend.run(runs, evaluation_times)

            else:
                raise ValueError(f"Invalid backend {backend_name}")
        else:
            raise ValueError("Missing device")
