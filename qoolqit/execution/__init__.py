"""Execute quantum programs on QPUs or local/remote emulators."""

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

from qoolqit.execution.backends import QPU, LocalEmulator, RemoteEmulator
from qoolqit.execution.job import Job, JobStatus, get_batch_id, retrieve_remote_job

__all__ = [
    "QPU",
    "BackendType",
    "BitStrings",
    "CorrelationMatrix",
    "EmulationConfig",
    "Energy",
    "EnergySecondMoment",
    "EnergyVariance",
    "Expectation",
    "Fidelity",
    "Job",
    "JobStatus",
    "LocalEmulator",
    "Occupation",
    "RemoteEmulator",
    "Results",
    "StateResult",
    "get_batch_id",
    "retrieve_remote_job",
]
