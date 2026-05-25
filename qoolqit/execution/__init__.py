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
from pulser.backend.remote import RemoteResults

from qoolqit.execution.backends import QPU, LocalEmulator, RemoteEmulator
from qoolqit.execution.job import Job, JobStatus, get_batch_id, retrieve_remote_job

__all__ = [
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
    "Job",
    "JobStatus",
    "get_batch_id",
    "retrieve_remote_job",
]
