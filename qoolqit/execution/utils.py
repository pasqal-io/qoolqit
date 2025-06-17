from __future__ import annotations

from qoolqit.utils import StrEnum


class CompilerProfile(StrEnum):

    DEFAULT = "Default"
    MAX_AMPLITUDE = "MaxAmplitude"
    MAX_DURATION = "MaxDuration"
    MIN_DISTANCE = "MinDistance"


class BackendName(StrEnum):

    QUTIP = "QutipBackendV2"
    EMU_MPS = "EmuMPS"


class ResultType(StrEnum):

    BITSTRING = "Bitstring"
    STATE_VECTOR = "StateVector"
