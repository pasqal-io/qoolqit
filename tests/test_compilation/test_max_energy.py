"""Test the MAX_ENERGY compilation profile."""

from __future__ import annotations

from typing import Callable

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
)
from qoolqit.execution.compilation_functions import CompilerProfile


class TestWorkingPointCompilerProfile:
    profile = CompilerProfile.MAX_ENERGY

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
