"""Test compilation independently on the compilation profiles."""
from __future__ import annotations

import pytest

from qoolqit import AnalogDevice, Constant, Drive, QuantumProgram, Register
from qoolqit.execution.compilation_functions import CompilerProfile


@pytest.mark.parametrize("profile", [CompilerProfile.MAX_ENERGY, CompilerProfile.WORKING_POINT])
def test_compilation_single_qubit(profile: CompilerProfile) -> None:
    """Test compilation of a single-qubit program."""
    register = Register(qubits={"q0": (0.0, 0.0)})
    drive = Drive(amplitude=Constant(2.0, 1.0))
    program = QuantumProgram(register=register, drive=drive)

    # Test compilation on the default profile
    program.compile_to(device=AnalogDevice())
    assert program.is_compiled
