"""Test the MAX_ENERGY compilation profile."""

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
    profile = CompilerProfile.MAX_ENERGY

    @pytest.fixture(autouse=True)
    def program_factory(
        self,
        random_waveform_factory: Callable,
        random_linear_register_factory: Callable,
    ) -> Callable[[Device, int | np.random.Generator], QuantumProgram]:
        def _generate_program(
            device: Device,
            seed: int | np.random.Generator = np.random.default_rng(),
        ) -> QuantumProgram:
            rng = np.random.default_rng(seed)

            # set program bounds to generate a valid program
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
    def test_program_compilation(self, program_factory: Callable, device: Device) -> None:

        program = program_factory(device)
        assert not program.is_compiled

        with pytest.raises(ValueError):
            program.compiled_sequence

        program.compile_to(device, profile=self.profile)
        assert program.is_compiled
        compiled_sequence = program.compiled_sequence
        assert isinstance(compiled_sequence, PulserSequence)

    def test_catch_compilation_error_max_abs_detuning(self) -> None:
        register = Register({"q0": (0.0, 0.0), "q1": (1.0, 0.0)})
        amp_max_value = 0.5
        amplitude = Constant(50, value=amp_max_value)
        detuning = Constant(50, value=20.26)
        drive = Drive(amplitude=amplitude, detuning=detuning)
        program = QuantumProgram(register, drive)
        device = AnalogDevice()

        # maximum absolute detuning allowed for this program
        ENERGY = device._target_amp_adim / amp_max_value
        if device.specs["max_abs_detuning"]:
            max_abs_det_allowed = device.specs["max_abs_detuning"] / ENERGY
            with pytest.raises(
                CompilationError,
                match="To compile your program, set the maximum absolute"
                f" detuning below {max_abs_det_allowed}",
            ):
                program.compile_to(AnalogDevice(), profile=self.profile)

    def test_catch_compilation_error_max_duration(self) -> None:
        register = Register({"q0": (0.0, 0.0), "q1": (1.0, 0.0)})
        duration = 300
        amplitude = Constant(duration, value=0.5)
        drive = Drive(amplitude=amplitude)
        program = QuantumProgram(register, drive)
        device = AnalogDevice()

        # maximum absolute detuning allowed for this program
        ENERGY = device._target_amp_adim / amplitude.max()
        if device.specs["max_duration"]:
            max_duration_allowed = device.specs["max_duration"] * ENERGY
            msg = f"To compile your program, set the drive's duration below {max_duration_allowed}"
            with pytest.raises(CompilationError, match=msg):
                program.compile_to(AnalogDevice(), profile=self.profile)

    def test_catch_compilation_error_max_radial_distance(self) -> None:
        register = Register({"q0": (0.0, 0.0), "q1": (9.0, 0.0)})
        drive = Drive(amplitude=Constant(13.0, 0.5))
        program = QuantumProgram(register, drive)
        device = AnalogDevice()

        # maximum radial distance allowed for this program
        ENERGY = device._target_amp_adim / drive.amplitude.max()
        if device.specs["max_radial_distance"]:
            max_radial_distance_allowed = device.specs["max_radial_distance"] * ENERGY ** (1 / 6)
            msg = (
                "To compile your program, set the maximum radial"
                f" distance below {max_radial_distance_allowed}"
            )
            with pytest.raises(CompilationError, match=msg):
                program.compile_to(AnalogDevice(), profile=self.profile)
