"""QoolQit module to execute quantum programs on QPUs or local/remote emulators."""

from __future__ import annotations

import pulser.backends as BackendType
from pulser.backend import (
    BitStrings,
    CorrelationMatrix,
    EmulationConfig,
    Energy,
    EnergySecondMoment,
    EnergyVariance,
    Expectation,
    Fidelity,
    Occupation,
    Results,
    StateResult,
)
from pulser.backend.remote import RemoteResults

from qoolqit.execution.backends import QPU, LocalEmulator, RemoteEmulator
from qoolqit.execution.sequence_compiler import SequenceCompiler

__all__ = [
    "SequenceCompiler",
    "LocalEmulator",
    "RemoteEmulator",
    "QPU",
    "EmulationConfig",
    "BitStrings",
    "CorrelationMatrix",
    "Energy",
    "EnergySecondMoment",
    "EnergyVariance",
    "Expectation",
    "Fidelity",
    "Occupation",
    "StateResult",
    "Results",
    "RemoteResults",
    "BackendType",
]
