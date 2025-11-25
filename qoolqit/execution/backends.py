from __future__ import annotations

import copy
import logging
import inspect
from functools import lru_cache
from typing import Optional, Sequence, Type

from pulser.backend import BitStrings, Results
from pulser.backend.abc import EmulatorBackend
from pulser.backend.config import EmulationConfig
from pulser.backend.qpu import QPUBackend
from pulser.backend.remote import JobParams, RemoteConnection, RemoteResults
from pulser_pasqal.backends import EmuFreeBackendV2, RemoteEmulatorBackend
from pulser_simulation import QutipBackendV2

from qoolqit.program import QuantumProgram

class PulserIntrospectionBase:
    """PulserIntrospectionBase class.
    It is providing cached signature inspection utilities shared across all QoolQit-Pulser backend wrappers.
    """
    _INTROSPECTION_CACHE_SIZE = 128  # Max cached backend types
    @staticmethod
    @lru_cache(maxsize=_INTROSPECTION_CACHE_SIZE)
    def _backend_accepts_mimic_qpu(backend_type: Type[object]) -> bool:
        """ Check whether a backend class supports the mimic_qpu keyword. 
   
        This inspects the Method Resolution Order (MRO) of backend_type and looks at each class' __init__ signature to see if it declares a
        parameter named mimic_qpu. If any __init__ in the MRO accepts this parameter, the backend is considered compatible and it is safe to
        forward the mimic_qpu= keyword argument when instantiating it.

        Results are cached to avoid repeated introspection of the same backend classes.

        Args:
            backend_type: The backend class to inspect.

        Returns:
            bool: True if any __init__ in the backend's MRO defines a mimic_qpu parameter, False otherwise.
        """
        for cls in backend_type.mro():
            try:
                sig = inspect.signature(cls.__init__)
            except (TypeError, ValueError):
                continue

            if "mimic_qpu" in sig.parameters:
                return True

        return False


class PulserEmulatorBackend(PulserIntrospectionBase):
    """Base Emulator class.

    Args:
        runs (int): run the program `runs` times to collect bitstrings statistics.
            On QPU backends this represents the actual number of runs of the program.
            On emulators, instead the bitstring are sampled from the quantum state `runs` times.
    """

    def __init__(self, runs: int = 100, mimic_qpu: bool = False) -> None:
        self._runs = runs
        self._mimic_qpu = bool(mimic_qpu)

    def validate_emulation_config(
        self, emulation_config: Optional[EmulationConfig]
    ) -> EmulationConfig:
        """Returns a valid config for emulator backends, if needed.

        Args:
            emulation_config (EmulationConfig): base configuration class for all emulators backends.
                If no config is provided to an emulator backend, a default will be provided instead.
        Note:
            Emulators backend (local/remote) can be configured through the generic
            `EmulationConfig` object. Early validation makes the error easier to understand.
        """
        if emulation_config is None:
            return self.default_emulation_config()
        
        emulation_config = copy.deepcopy(emulation_config)
        has_bitstrings = any(
            isinstance(obs, BitStrings) for obs in emulation_config.observables
        )
        if has_bitstrings:
            # if the provided config has already a biststring obs, ignore nruns
            logging.warning(
                f"""The number of runs is specified both in {self.__class__.__name__}
                    and in `EmulationConfig`, ignoring the former"""
            )
        else:
            # else append a bitstring observable with nruns specified by the user
            emulation_config.observables = (*emulation_config.observables, BitStrings(num_shots=self._runs))
        # TODO: validate config when bump to pulser==1.6 (uncomment below)
        # config = backend_type.validate_config(config)
        return emulation_config

    def default_emulation_config(self) -> EmulationConfig:
        """Return a unique emulation config for all emulators.

        Defaults to a configuration that asks for the final bitstring, sampled `runs` times.
        """
        return EmulationConfig(observables=(BitStrings(num_shots=self._runs),))


class PulserRemoteBackend(PulserIntrospectionBase):

    @staticmethod
    def validate_connection(connection: RemoteConnection) -> RemoteConnection:
        """Validate the required connection to instantiate a RemoteBackend.

        Remote emulators and QPUs require a `pulser.backend.remote.RemoteConnection` or derived
        to send jobs. Validation also happens inside the backend. Early validation just makes the
        error easier to understand.
        """
        if not isinstance(connection, RemoteConnection):
            raise TypeError(
                f"""Error in `PulserRemoteBackend`:
                `connection` must be of type {RemoteConnection}."""
            )
        return connection


class LocalEmulator(PulserEmulatorBackend):
    """
    Run QoolQit `QuantumProgram`s on a Pasqal local emulator backends.

    This class serves as a primary interface between tools written using QoolQit (including solvers)
    and local emulator backends.

    Args:
        backend_type (type): backend type. Must be a subtype of `pulser.backend.EmulatorBackend`.
        emulation_config (EmulationConfig): optional configuration object emulators.
        runs (int): number of bitstring samples to collect from the final quantum state.
            It emulates running the program `runs` times to collect bitstrings statistics.

    Examples:
        ```python
        from qoolqit.execution import Emulator, SVBackend
        backend = Emulator(backend_type=SVBackend)
        result = backend.run(program)
        ```
    """

    def __init__(
        self,
        *,
        backend_type: type[EmulatorBackend] = QutipBackendV2,
        emulation_config: Optional[EmulationConfig] = None,
        runs: int = 100,
        mimic_qpu: bool = False,
    ) -> None:
        super().__init__(runs=runs, mimic_qpu=mimic_qpu)
        if not issubclass(backend_type, EmulatorBackend):
            raise TypeError(
                "Error in `LocalEmulator`: `backend_type` must be a EmulatorBackend type."
            )
        if issubclass(backend_type, RemoteEmulatorBackend):
            raise TypeError(
                """Error in `LocalEmulator`: `backend_type` cannot be a RemoteBackend type.
                If you wish to run your program on a remote emulator backend, please, use the
                RemoteEmulator class."""
            )
        self._backend_type = backend_type
        self._emulation_config = self.validate_emulation_config(emulation_config)

    def run(self, program: QuantumProgram) -> Sequence[Results]:
        """Run a compiled QuantumProgram and return the results."""
        
        backend_kwargs = {"config": self._emulation_config}
        if self._backend_accepts_mimic_qpu(self._backend_type):
            backend_kwargs["mimic_qpu"] = self._mimic_qpu

        self._backend = self._backend_type(program.compiled_sequence, **backend_kwargs)
        results = self._backend.run()
        return (results,) if isinstance(results, Results) else tuple(results)
        


class RemoteEmulator(PulserEmulatorBackend, PulserRemoteBackend):
    """
    Run QoolQit `QuantumProgram`s on a Pasqal remote emulator backends.

    This class serves as a primary interface between tools written using QoolQit (including solvers)
    and remote emulator backends.
    The behavior is similar to `LocalEmulator`, but here, requires credentials through
    a `connection` to submit/run a program.
    To get your credentials and to create a connection object, please refer to the [Pasqal Cloud
    interface documentation](https://docs.pasqal.com/cloud).

    Args:
        backend_type (type): backend type. Must be a subtype of
            `pulser_pasqal.backends.RemoteEmulatorBackend`.
        connection (RemoteConnection): connection to execute the program on remote backends.
        emulation_config (EmulationConfig): optional configuration object emulators.
        runs (int): number of bitstring samples to collect from the final quantum state.
            It emulates running the program `runs` times to collect bitstrings statistics.

    Examples:
        ```python
        from pulser_pasqal import PasqalCloud
        from qoolqit.execution import RemoteEmulator, EmuFreeBackendV2
        connection = PasqalCloud(username=..., password=..., project_id=...)
        backend = RemoteEmulator(backend_type=EmuFreeBackendV2, connection=connection)
        ```
        then
        ```python
        remote_results = backend.submit(program)
        ```
        or
        ```python
        results = backend.run(program)
        ```
    """

    def __init__(
        self,
        *,
        backend_type: type[RemoteEmulatorBackend] = EmuFreeBackendV2,
        connection: RemoteConnection,
        emulation_config: Optional[EmulationConfig] = None,
        runs: int = 100,
        mimic_qpu: bool = False,
    ) -> None:
        super().__init__(runs=runs, mimic_qpu=mimic_qpu)
        if not issubclass(backend_type, RemoteEmulatorBackend):
            raise TypeError(
                "Error in `RemoteEmulator`: `backend_type` must be a RemoteEmulatorBackend type."
            )
        self._backend_type = backend_type
        self._emulation_config = self.validate_emulation_config(emulation_config)
        self._connection = self.validate_connection(connection)
        # JobParams is ignored in remote emulators and `runs`
        # is set instead in `default_emulation_config()`.
        # TODO: after pulser 1.6 & pasqal-cloud 0.20.6 assess if job_params is still needed
        self._job_params = [JobParams(runs=self._runs)]

    def submit(self, program: QuantumProgram, wait: bool = False) -> RemoteResults:
        """Submit a compiled QuantumProgram and return a remote handler of the results.

        The returned handler `RemoteResults` can be used to:
        - query the job status with `remote_results.get_batch_status()`
        - when DONE, retrieve results with `remote_results.results`

        Args:
            program (QuantumProgram): the compiled quantum program to run.
            wait (bool): Wait for remote backend to complete the job.
        """
        backend_kwargs = {
            "connection": self._connection,
            "config": self._emulation_config,
        }
        if self._backend_accepts_mimic_qpu(self._backend_type):
            backend_kwargs["mimic_qpu"] = self._mimic_qpu

        # Instantiate backend
        self._backend = self._backend_type(
            program.compiled_sequence,
            **backend_kwargs,
        )
        return self._backend.run(job_params=self._job_params, wait=wait)
        

    def run(self, program: QuantumProgram) -> Sequence[Results]:
        """Run a compiled QuantumProgram remotely and return the results."""
        remote_results = self.submit(program, wait=True)
        res_seq: Sequence[Results] = remote_results.results
        return res_seq


class QPU(PulserRemoteBackend):
    """
    Run QoolQit `QuantumProgram`s on a Pasqal QPU.

    This class serves as a primary interface between tools written using QoolQit (including solvers)
    and QPU backend. It requires credentials through a `connection` to submit/run a program.
    Please, contact your provider to get your credentials and get help on how create a
    connection object:
    - [Pasqal Cloud interface documentation](https://docs.pasqal.com/cloud)
    - [Atos MyQML framework](https://github.com/pasqal-io/Pulser-myQLM/blob/main/tutorials/Submitting%20AFM%20state%20prep%20to%20QPU.ipynb)

    Args:
        connection (RemoteConnection): connection to execute the program on remote backends.
        runs (int): run the program `runs` times to collect bitstrings statistics.

    Examples:
        ```python
        from pulser_pasqal import PasqalCloud
        from qoolqit.execution import QPU
        connection = PasqalCloud(username=..., password=..., project_id=...)
        backend = QPU(connection=connection)
        remote_results = backend.submit(program)
        ```
    """  # noqa

    def __init__(
        self,
        *,
        connection: RemoteConnection,
        runs: int = 100,
    ) -> None:

        self._backend_type = QPUBackend
        self._runs = runs
        self._connection = self.validate_connection(connection)
        # in QPU backends `runs` is specified in a JobParams object
        self._job_params = [JobParams(runs=self._runs)]

    def submit(self, program: QuantumProgram, wait: bool = False) -> RemoteResults:
        """Submit a compiled QuantumProgram and return a remote handler of the results.

        The returned handler `RemoteResults` can be used to:
        - query the job status with `remote_results.get_batch_status()`
        - when DONE, retrieve results with `remote_results.results`

        Args:
            program (QuantumProgram): the compiled quantum program to run.
            wait (bool): Wait for remote backend to complete the job.
        """
        self._backend = self._backend_type(program.compiled_sequence, connection=self._connection)
        return self._backend.run(job_params=self._job_params, wait=wait)
        

    def run(self, program: QuantumProgram) -> Sequence[Results]:
        """Run a compiled QuantumProgram remotely and return the results."""
        remote_results = self.submit(program, wait=True)
        res_seq: Sequence[Results] = remote_results.results
        return res_seq
