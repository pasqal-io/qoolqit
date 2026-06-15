from __future__ import annotations

import json

from qoolqit import ConstantWaveform, Drive, MockDevice, QuantumProgram, Register
from qoolqit import __version__ as qoolqit_version


def test_compiled_sequence_metadata() -> None:
    register = Register({"q0": (0.0, 0.0), "q1": (1.0, 0.0)})
    drive = Drive(amplitude=ConstantWaveform(10.0, 1.0))
    program = QuantumProgram(register, drive)

    # check if the metadata is correctly stored in the compiled sequence
    program.compile_to(MockDevice())
    compiled_seq_repr = json.loads(program.compiled_sequence.to_abstract_repr())

    compiled_seq_metadata = compiled_seq_repr["metadata"]
    expected_metadata = {"package_versions": {"qoolqit": qoolqit_version}, "extra": {}}
    assert compiled_seq_metadata == expected_metadata
