"""Test the MAX_ENERGY compilation profile."""

from __future__ import annotations

import numpy as np
import pytest
from numpy.random import Generator, RandomState
from pulser.sequence import Sequence as PulserSequence

from qoolqit import (
    AnalogDevice,
    Device,
    DigitalAnalogDevice,
    Drive,
    MockDevice,
    QuantumProgram,
    Ramp,
    Register,
)
from qoolqit.execution.compilation_functions import CompilerProfile
from qoolqit.waveforms.base_waveforms import Waveform


class TestWorkingPointCompilerProfile:
    profile = CompilerProfile.MAX_ENERGY

    def random_register(
        self, min_distance: float, seed: int | RandomState | Generator = np.random.default_rng()
    ) -> Register:
        rng = np.random.default_rng(seed)
        n = rng.integers(low=2, high=5)
        start_x = -(n - 1) / 2.0
        coords = [((start_x + i) * min_distance, 0.0) for i in range(n)]
        return Register.from_coordinates(coords)

    def random_waveform(
        self,
        min_value: float,
        max_value: float,
        max_duration: float,
        seed: int | RandomState | Generator = np.random.default_rng(),
    ) -> Waveform:
        rng = np.random.default_rng(seed)
        n = rng.integers(2, 5)
        durations = rng.uniform(1.0, 2.0, size=n)
        durations *= rng.uniform(0.0, max_duration) / np.sum(durations)
        wf: Waveform = Ramp(
            durations[0],
            initial_value=rng.uniform(min_value, max_value),
            final_value=rng.uniform(min_value, max_value),
        )
        for i in range(1, n):
            wf = wf >> Ramp(
                durations[i],
                initial_value=rng.uniform(min_value, max_value),
                final_value=rng.uniform(min_value, max_value),
            )
        return wf

    def random_valid_program(
        self, device: Device, seed: int | RandomState | Generator = np.random.default_rng()
    ) -> QuantumProgram:
        rng = np.random.default_rng(seed)
        specs = device.specs
        min_distance = specs["min_distance"] or 1.0
        max_amp = specs["max_amplitude"] or 0.226
        max_abs_det = specs["max_abs_detuning"] or 2.26
        max_duration = specs["max_duration"] or 330

        register = self.random_register(min_distance, seed=rng)
        amplitude = self.random_waveform(0.0, max_amp, max_duration, seed=rng)
        detuning = self.random_waveform(-max_abs_det, max_abs_det, max_duration, seed=rng)
        drive = Drive(amplitude=amplitude, detuning=detuning)
        program = QuantumProgram(register, drive)
        return program

    @pytest.mark.parametrize("device", [AnalogDevice(), DigitalAnalogDevice(), MockDevice()])
    def test_program_init_and_compilation(self, device: Device) -> None:

        program = self.random_valid_program(device)
        assert not program.is_compiled

        with pytest.raises(ValueError):
            program.compiled_sequence

        program.compile_to(device, profile=self.profile)
        assert program.is_compiled
        assert isinstance(program.compiled_sequence, PulserSequence)
