from __future__ import annotations

from qoolqit.utils import StrEnum


class CompilerProfile(StrEnum):

    DEFAULT = "Default"
    MAX_AMPLITUDE = "MaxAmplitude"
    MAX_DURATION = "MaxDuration"
    MIN_DISTANCE = "MinDistance"


class BackendName(StrEnum):

    QUTIP = "Qutip"
    EMUMPS = "EmuMPS"


class ResultType(StrEnum):

    BITSTRINGS = "Bitstrings"
    STATEVECTOR = "StateVector"
