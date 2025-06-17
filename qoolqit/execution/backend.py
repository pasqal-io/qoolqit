from __future__ import annotations

import logging
import string
from collections import Counter
from typing import Any, Union

import emu_mps
import numpy as np
import pulser
import torch
from emu_mps import MPSBackend, MPSConfig
from pulser import Sequence
from pulser.backend import EmulationConfig
from pulser.backends import QutipBackendV2

from qoolqit.execution.utils import BackendName, ResultType

AVAILABLE_BACKENDS = {BackendName.QUTIP: QutipBackendV2, BackendName.EMU_MPS: MPSBackend}

AVAILABLE_CONFIGS = {BackendName.QUTIP: EmulationConfig, BackendName.EMU_MPS: MPSConfig}

ResType = Union[np.ndarray, list[Counter]]


class Backend:
    """Wrapper for Pulser's backend API."""

    def __init__(
        self,
        seq: Sequence,
        name: BackendName = BackendName.QUTIP,
        result_type: ResultType = ResultType.STATE_VECTOR,
        **backend_params: Any,
    ):
        self.seq = seq
        self.name = name
        self.result_type = result_type
        self.backend_params = backend_params

        # Get the selected backend
        self.backend_cls = AVAILABLE_BACKENDS[name]

        # Get the appropriate config
        self.config_cls = AVAILABLE_CONFIGS[name]

    def build_config(self, runs: int = 100) -> None:
        # Add the necessary observables based on the expected result type
        obs = self.backend_params.get("observables", [])

        if len(obs) == 0:
            if self.result_type == ResultType.BITSTRING:
                obs.append(pulser.backend.BitStrings(num_shots=runs))
            elif self.result_type == ResultType.STATE_VECTOR:
                obs.append(pulser.backend.StateResult())

        self.backend_params["observables"] = obs

        # Set default values for the config
        self.backend_params.setdefault("log_level", logging.WARNING)

        # Build the config object
        self.config = self.config_cls(**self.backend_params)

    def build_backend(self) -> None:
        # Build the local backend
        self.backend = self.backend_cls(self.seq, config=self.config)

    def contract_mps(self, mps_state: emu_mps.MPS) -> torch.Tensor:
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

    def run(self, runs: int = 100) -> ResType:

        # Build the config and the backend
        self.build_config(runs)
        self.build_backend()

        if self.result_type == ResultType.STATE_VECTOR:
            states = self.backend.run().state
            if self.name == BackendName.EMU_MPS:
                # Get initial state vector
                initial_state = self.backend._config.initial_state
                if initial_state is None:
                    initial_state = emu_mps.MPS.from_state_amplitudes(
                        eigenstates=("r", "g"),
                        amplitudes={"g" * len(self.seq.register.qubits): 1.0},
                    )

                # Constract MPS states to get state vectors
                state_vecs = np.array(
                    [self.contract_mps(initial_state)]
                    + [self.contract_mps(state) for state in states]
                )
            else:
                state_vecs = np.array(
                    [np.flip(state.to_qobj().full().flatten()) for state in states]
                )

            return state_vecs

        elif self.result_type == ResultType.BITSTRING:
            return self.backend.run().get_tagged_results()
