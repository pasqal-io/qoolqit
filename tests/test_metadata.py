import json
from pulser import __version__ as pulser_version
from packaging.version import Version
from qoolqit import __version__ as qoolqit_version
from qoolqit.program import QuantumProgram
from qoolqit.devices import MockDevice
from typing import Callable


def test_compiled_sequence_metadata(random_program: Callable[[], QuantumProgram]) -> None:
    # metadata are stored only from pulser 1.6.3
    if Version(pulser_version) >= Version("1.6.3"):
        program = random_program()
        program.compile_to(MockDevice())
        compiled_seq_repr = json.loads(program.compiled_sequence.to_abstract_repr())

        compiled_seq_metadata = compiled_seq_repr["metadata"]
        expected_metadata = {"package_versions": {"qoolqit": qoolqit_version}, "extra": {}}
        assert compiled_seq_metadata == expected_metadata
