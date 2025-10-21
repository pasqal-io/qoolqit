from __future__ import annotations

from typing import Callable

import pytest
from emu_mps import MPSBackend
from emu_sv import SVBackend
from pulser.backend.abc import EmulatorBackend
from pulser_simulation import QutipBackendV2

from qoolqit.devices import ALL_DEVICES
from qoolqit.execution import CompilerProfile, LocalEmulator
from qoolqit.program import QuantumProgram


@pytest.mark.parametrize("device_class", ALL_DEVICES)
@pytest.mark.parametrize("profile", CompilerProfile.list())
@pytest.mark.parametrize(
    "backend_type",
    [
        QutipBackendV2,
        SVBackend,
        MPSBackend,
    ],
)
@pytest.mark.parametrize("runs", [500, 100])
def test_local_backend_run(
    device_class: Callable,
    profile: CompilerProfile,
    random_program: Callable[[], QuantumProgram],
    backend_type: type[EmulatorBackend],
    runs: int,
) -> None:

    # FIXME: Reactivate the min_distance profile once we implement safe-mode compilation
    # Currently trying to set the atoms at the min distance will very often cause the
    # amplitude to go over the limit allowed for the channel, which will fail the compilation.
    if profile != CompilerProfile.MIN_DISTANCE:
        program = random_program()
        device = device_class()
        program.compile_to(device, profile=profile)

        local_emulator = LocalEmulator(backend_type=backend_type, runs=runs)
        results = local_emulator.run(program)
        assert results
        bitstrings = results[-1].final_bitstrings
        assert sum(bitstrings.values()) == runs
