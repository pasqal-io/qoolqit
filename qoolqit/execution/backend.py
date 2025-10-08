from __future__ import annotations

import logging
import string
from abc import ABC, abstractmethod
from collections import Counter
from typing import Any, Union

import numpy as np
import pulser
import torch
from emu_mps import MPS, MPSBackend, MPSConfig
from pulser.backend import EmulationConfig
from pulser.backends import QutipBackendV2 as PulserQutipBackend
from pulser.sequence.sequence import Sequence as PulserSequence

from qoolqit.execution.utils import BackendName, ResultType

AVAILABLE_BACKENDS = {BackendName.QUTIP: PulserQutipBackend, BackendName.EMUMPS: MPSBackend}
AVAILABLE_CONFIGS = {BackendName.QUTIP: EmulationConfig, BackendName.EMUMPS: MPSConfig}

OutputType = Union[np.ndarray, list[Counter]]


class BaseBackend(ABC):
    def __init__(
        self,
        seq: PulserSequence,
        name: BackendName = BackendName.QUTIP,
        result_type: ResultType = ResultType.STATEVECTOR,
        **backend_params: Any,
    ) -> None:

        self.seq = seq
        self.name = name
        self.result_type = result_type
        self.backend_params = backend_params

        # Get the selected backend
        self.backend_cls = AVAILABLE_BACKENDS[name]

        # Get the appropriate config
        self.config_cls = AVAILABLE_CONFIGS[name]

    def build_config(self, runs: int = 100, evaluation_times: list[float] = [1.0]) -> None:
        # Add the necessary observables based on the expected result type
        obs = self.backend_params.get("observables", [])

        if len(obs) == 0:
            if self.result_type == ResultType.BITSTRINGS:
                obs.append(
                    pulser.backend.BitStrings(evaluation_times=evaluation_times, num_shots=runs)
                )
            elif self.result_type == ResultType.STATEVECTOR:
                obs.append(pulser.backend.StateResult(evaluation_times=evaluation_times))

        self.backend_params["observables"] = obs

        # Set default values for the config
        self.backend_params.setdefault("log_level", logging.WARNING)

        # Build the config object
        self.config = self.config_cls(**self.backend_params)

    def build_backend(self) -> None:
        # Build the local backend
        self.backend = self.backend_cls(self.seq, config=self.config)

    @abstractmethod
    def run(self) -> Any:
        pass


class EmuMPSBackend(BaseBackend):
    """Emu-MPS backend."""

    def __init__(
        self,
        seq: PulserSequence,
        result_type: ResultType = ResultType.STATEVECTOR,
        **backend_params: Any,
    ):
        super().__init__(seq, BackendName.EMUMPS, result_type, **backend_params)

    def contract_mps(self, mps_state: MPS) -> torch.Tensor:
        """
        Contract a MPS state into a full state vector.

        Args:
            mps_state (MPS): MPS state to contract

        Returns:
            A flattened torch.Tensor representing the state vector.
        """
        n = len(mps_state.factors)

        # Use ascii letters to build einsum subscripts
        letters = list(string.ascii_lowercase)
        einsum_subs = []
        for i in range(n):
            left = letters[i]
            phys = letters[n + i]
            right = letters[i + 1]
            einsum_subs.append(f"{left}{phys}{right}")

        einsum_str = ",".join(einsum_subs) + "->" + "".join(letters[n : 2 * n])
        result = torch.einsum(einsum_str, *mps_state.factors)
        return result.flatten().cpu()

    def run(self, runs: int = 100, evaluation_times: list[float] = [1.0]) -> OutputType:

        # Build the config and the backend
        self.build_config(runs, evaluation_times)
        self.build_backend()

        # run the simulation
        result = self.backend.run()

        # Get initial state vector
        initial_state = self.backend._config.initial_state
        if initial_state is None:
            initial_state = MPS.from_state_amplitudes(
                eigenstates=("r", "g"),
                amplitudes={"g" * len(self.seq.register.qubits): 1.0},
            )

        if self.result_type == ResultType.STATEVECTOR:
            # Constract MPS states to get state vectors
            if len(evaluation_times) == 1:
                state_vecs = [self.contract_mps(state) for state in result.state]
            else:
                state_vecs = [self.contract_mps(initial_state)] + [
                    self.contract_mps(state) for state in result.state
                ]
            state_vecs = np.array(state_vecs)
            return state_vecs

        elif self.result_type == ResultType.BITSTRINGS:
            if len(evaluation_times) == 1:
                bitstrings = result.get_tagged_results()["bitstrings"]
            else:
                bitstrings = [initial_state.sample(num_shots=runs)] + result.get_tagged_results()[
                    "bitstrings"
                ]
            return bitstrings


class QutipBackend(BaseBackend):
    """Qutip backend."""

    def __init__(
        self,
        seq: PulserSequence,
        result_type: ResultType = ResultType.STATEVECTOR,
        **backend_params: Any,
    ):
        super().__init__(seq, BackendName.QUTIP, result_type, **backend_params)

    def run(self, runs: int = 100, evaluation_times: list[float] = [1.0]) -> OutputType:

        # Build the config and the backend
        self.build_config(runs, evaluation_times)
        self.build_backend()

        # run the simulation
        result = self.backend.run()

        if self.result_type == ResultType.STATEVECTOR:
            state_vecs = np.array(
                [np.flip(state.to_qobj().full().flatten()) for state in result.state]
            )
            return state_vecs

        elif self.result_type == ResultType.BITSTRINGS:
            return result.get_tagged_results()["bitstrings"]
