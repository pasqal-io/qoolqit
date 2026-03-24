"""Test the WORKING_POINT compilation profile."""

from __future__ import annotations

from typing import Callable

import numpy as np
import pytest
from pulser.sequence import Sequence as PulserSequence

from qoolqit import (
    AnalogDevice,
    Constant,
    Device,
    DigitalAnalogDevice,
    Drive,
    MockDevice,
    QuantumProgram,
    Register,
)
from qoolqit.exceptions import CompilationError
from qoolqit.execution.compilation_functions import CompilerProfile


class TestWorkingPointCompilerProfile:
    profile = CompilerProfile.WORKING_POINT

    @pytest.fixture(autouse=True)
    def program_factory(
        self,
        random_amplitude_factory: Callable,
        random_linear_register_factory: Callable,
    ) -> Callable[[Device, int | np.random.Generator], QuantumProgram]:
        def _generate_program(
            device: Device,
            seed: int | np.random.Generator = np.random.default_rng(),
        ) -> QuantumProgram:
            rng = np.random.default_rng(seed)
            specs = device.specs
            min_distance = specs["min_distance"] or 1.0
            max_amp = specs["max_amplitude"] or 0.226
            max_abs_det = specs["max_abs_detuning"] or 2.26
            max_duration = specs["max_duration"] or 330

            register = random_linear_register_factory(min_distance, seed=rng)
            amplitude = random_amplitude_factory(0.0, max_amp, max_duration, seed=rng)
            detuning = random_amplitude_factory(-max_abs_det, max_abs_det, max_duration, seed=rng)
            drive = Drive(amplitude=amplitude, detuning=detuning)
            program = QuantumProgram(register, drive)
            return program

        return _generate_program

    @pytest.mark.parametrize("device", [AnalogDevice(), DigitalAnalogDevice(), MockDevice()])
    def test_program_init_and_compilation(self, program_factory: Callable, device: Device) -> None:

        program = program_factory(device)
        assert not program.is_compiled

        with pytest.raises(ValueError):
            program.compiled_sequence

        program.compile_to(device, profile=self.profile)
        assert program.is_compiled
        assert isinstance(program.compiled_sequence, PulserSequence)

    def test_catch_compilation_error_max_amp(self) -> None:
        register = Register({"q0": (0.0, 0.0), "q1": (1.0, 0.0)})
        drive = Drive(amplitude=Constant(50, value=0.5))
        program = QuantumProgram(register, drive)

        with pytest.raises(
            CompilationError,
            match=(
                f"The drive's maximum amplitude {0.5:.4f} goes over "
                "the maximum value allowed for the chosen device"
            ),
        ):
            program.compile_to(device=AnalogDevice(), profile=self.profile)

    def test_catch_compilation_error_min_dist(self) -> None:
        register = Register({"q0": (0.0, 0.0), "q1": (0.78, 0.0)})
        drive = Drive(amplitude=Constant(50, value=0.2))
        program = QuantumProgram(register, drive)

        with pytest.raises(
            CompilationError,
            match=(
                f"The register minimum distance between two qubits {0.78:.4f} goes below the "
                "minimum allowed for the chosen device"
            ),
        ):
            program.compile_to(device=AnalogDevice(), profile=self.profile)

    def test_catch_compilation_error_max_det(self) -> None:
        register = Register({"q0": (0.0, 0.0), "q1": (1.0, 1.0)})
        drive = Drive(amplitude=Constant(50, value=0.2), detuning=Constant(50, value=100))
        program = QuantumProgram(register, drive)

        with pytest.raises(
            CompilationError,
            match=(
                f"The drive's maximum absolute detuning {100:.4f} goes over "
                "the maximum value allowed for the chosen device"
            ),
        ):
            program.compile_to(device=AnalogDevice(), profile=self.profile)

    def test_catch_compilation_error_max_duration(self) -> None:
        register = Register({"q0": (0.0, 0.0), "q1": (1.0, 1.0)})
        drive = Drive(amplitude=Constant(351.2, value=0.1))
        program = QuantumProgram(register, drive)

        with pytest.raises(
            CompilationError,
            match=(
                f"The drive's duration {351.2:.4f} "
                "goes over the maximum value allowed for the chosen device"
            ),
        ):
            program.compile_to(device=AnalogDevice(), profile=self.profile)

    def test_catch_compilation_error_max_dist(self) -> None:
        register = Register({"q0": (0.0, 0.0), "q1": (9.0, 0.0)})
        drive = Drive(amplitude=Constant(13.0, 0.2))
        program = QuantumProgram(register, drive)

        with pytest.raises(
            CompilationError,
            match=(
                f"The register maximum radial distance {9.0:.4f} goes over "
                "the maximum allowed for the chosen device"
            ),
        ):
            program.compile_to(device=AnalogDevice(), profile=self.profile)
