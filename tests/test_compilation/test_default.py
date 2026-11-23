"""Test the DEFAULT compilation profile."""

from __future__ import annotations

from collections.abc import Callable

import numpy as np
import pytest
from pulser.sequence import Sequence as PulserSequence

from qoolqit import (
    AnalogDevice,
    Device,
    DigitalAnalogDevice,
    Drive,
    MockDevice,
    QuantumProgram,
    Register,
)
from qoolqit.exceptions import CompilationError
from qoolqit.execution.compilation_functions import CompilerProfile
from qoolqit.waveforms import ConstantWaveform


class TestWorkingPointCompilerProfile:
    profile = CompilerProfile.DEFAULT

    @pytest.fixture(autouse=True)
    def program_factory(
        self,
        random_waveform_factory: Callable,
        random_linear_register_factory: Callable,
    ) -> Callable[[Device, int | np.random.Generator], QuantumProgram]:
        def _generate_program(
            device: Device,
            seed: int | np.random.Generator | None = None,
        ) -> QuantumProgram:
            rng = np.random.default_rng(seed)
            specs = device.specs
            min_distance = specs["min_distance"] or 1.0
            max_amp = specs["max_amplitude"] or 0.226
            max_abs_det = specs["max_abs_detuning"] or 2.26
            max_duration = specs["max_duration"] or 330

            register = random_linear_register_factory(min_distance, seed=rng)
            amplitude = random_waveform_factory(0.0, max_amp, max_duration, seed=rng)
            detuning = random_waveform_factory(-max_abs_det, max_abs_det, max_duration, seed=rng)
            drive = Drive(amplitude=amplitude, detuning=detuning)
            program = QuantumProgram(register, drive)
            return program

        return _generate_program

    @pytest.mark.parametrize("device", [AnalogDevice(), DigitalAnalogDevice(), MockDevice()])
    def test_program_init_and_compilation(self, program_factory: Callable, device: Device) -> None:

        program = program_factory(device)
        assert not program.is_compiled

        with pytest.raises(ValueError):
            _ = program.compiled_sequence

        program.compile_to(device, profile=self.profile)
        assert program.is_compiled
        assert isinstance(program.compiled_sequence, PulserSequence)

    def test_catch_compilation_error_max_amp(self) -> None:
        register = Register({"q0": (0.0, 0.0), "q1": (1.0, 0.0)})
        drive = Drive(amplitude=ConstantWaveform(50, value=0.5))
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
        drive = Drive(amplitude=ConstantWaveform(50, value=0.2))
        program = QuantumProgram(register, drive)

        with pytest.raises(
            CompilationError,
            match=(
                f"The register minimum distance between two qubits {0.78} goes below the "
                "minimum allowed for the chosen device"
            ),
        ):
            program.compile_to(device=AnalogDevice(), profile=self.profile)

    def test_catch_compilation_error_min_dist_round_off(self) -> None:
        # just outside the round-off tolerance: rejected by QoolQit, value printed in full
        register = Register({"q0": (0.0, 0.0), "q1": (1 - 2e-9, 0.0)})
        drive = Drive(amplitude=ConstantWaveform(50, value=0.2))
        program = QuantumProgram(register, drive)

        with pytest.raises(CompilationError, match="between two qubits 0.999999998 goes below"):
            program.compile_to(device=AnalogDevice(), profile=self.profile)

    @pytest.mark.parametrize(
        "register",
        [Register.circle(8), Register.circle(32), Register.triangular(rows=8, atoms_per_row=8)],
    )
    def test_compile_min_distance_round_off(self, register: Register) -> None:
        drive = Drive(amplitude=ConstantWaveform(5.0, 0.2))
        QuantumProgram(register, drive).compile_to(device=AnalogDevice(), profile=self.profile)

    def test_compile_max_radial_distance_round_off(self) -> None:
        # radial distance at the device limit 7.6, computed as 7.6000000000000005
        register = Register(
            {"a": (0.0, 0.0), "b": (1.0, 0.0), "c": (7.6 * np.cos(0.1), 7.6 * np.sin(0.1))}
        )
        drive = Drive(amplitude=ConstantWaveform(5.0, 0.2))
        QuantumProgram(register, drive).compile_to(device=AnalogDevice(), profile=self.profile)

    def test_catch_compilation_error_max_det(self) -> None:
        register = Register({"q0": (0.0, 0.0), "q1": (1.0, 1.0)})
        drive = Drive(
            amplitude=ConstantWaveform(50, value=0.2), detuning=ConstantWaveform(50, value=100)
        )
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
        drive = Drive(amplitude=ConstantWaveform(351.2, value=0.1))
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
        drive = Drive(amplitude=ConstantWaveform(13.0, 0.2))
        program = QuantumProgram(register, drive)

        with pytest.raises(
            CompilationError,
            match=(
                f"The register maximum radial distance {9.0} goes over "
                "the maximum allowed for the chosen device"
            ),
        ):
            program.compile_to(device=AnalogDevice(), profile=self.profile)
