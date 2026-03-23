# Executing a quantum program

In this page, you will learn how to:

- run a `QuantumProgram` on local emulators,
- choose between different emulator backends,
- configure emulator runs and observables,
- inspect and extract local execution results,
- connect to Pasqal Cloud and run programs remotely,
- submit remote jobs and retrieve their results,
- execute compiled programs on a QPU.

A `QuantumProgram` can be easily run on multiple backends provided by Pasqal:
- locally installed emulators
- remote cloud emulators
- QPUs

Remote emulators and QPU **require** credentials to submit a job.
More information on how to access a QPU through your favorite cloud provider, is available at [Pasqal's website](https://www.pasqal.com/solutions/cloud/).
Later, we will briefly show how to authenticate and send a remote job.

## A simple quantum program

Let us revisit the quantum program definition described before in the [Quantum programs](./programs.md) page.

```python exec="on" source="material-block" session="execution"

from qoolqit import Drive, Ramp, Register, Constant
from qoolqit import QuantumProgram
from qoolqit import MockDevice

# Create the register
register = Register.from_coordinates([(0,1), (0,-1), (2,0)])

# Defining the drive parameters
omega = 0.8
delta_i = -2.0 * omega
delta_f = -delta_i
T = 25.0

# Defining the drive
wf_amp = Constant(T, omega)
wf_det = Ramp(T, delta_i, delta_f)
drive = Drive(amplitude = wf_amp, detuning = wf_det)

# Creating the program
program = QuantumProgram(register, drive)

# Compiling the Program
device = MockDevice()
program.compile_to(device)
```

## Executing locally

Executing your program locally is as simple as importing the local emulator and just run your program on it
```python exec="on" source="material-block" session="execution"
from qoolqit.execution import LocalEmulator

emulator = LocalEmulator()
results = emulator.run(program)
```

The `LocalEmulator` allows to emulate the program run on different backends provided by Pasqal:

- `QutipBackendV2`: Based on Qutip, runs programs with up to ~12 qubits and return qutip objects in the results (default).
- `SVBackend`: PyTorch based state vectors and sparse matrices emulator. Runs programs with up to ~25 qubits and return torch objects in the results. Requires installing the `emu-sv` package.
- `MPSBackend`: PyTorch based emulator using Matrix Product States (MPS). Runs programs with up to ~80 qubits and return torch objects in the results. Requires installing the `emu-mps` package.

To use a particular backend it is sufficient to specify it through the `backend_type` argument:

```python exec="on" source="material-block" session="execution"
from qoolqit.execution import LocalEmulator, BackendType

emulator = LocalEmulator(backend_type=BackendType.QutipBackendV2)
```

### Handling local results

The call `emulator.run(program)` will return a `Sequence[Results]` object type. This is where the results of the computation are stored.
For more info about this specific object, please, have a look at [Pulser documentation](https://pulser.readthedocs.io/en/stable/apidoc/_autosummary/pulser.backend.Results.html#results).
As an example, lets inspect the results we got in the previous run:
```python exec="on" source="material-block" session="execution"
# single result in the sequence
results[0].get_result_tags()
print(results[0].get_result_tags())  # markdown-exec: hide
```
Then the bitstrings can be extracted simply as:
```python exec="on" source="material-block" session="execution"
# single result in the sequence
final_bitstrings = results[0].final_bitstrings
print(final_bitstrings)  # markdown-exec: hide
```


## Configuring the emulator

More experienced users might want to fully configure an emulator to exploit all its possibilities,
such as defining which observables to measure during the emulation, or emulating real hardware modulation effects.
This is done through the `EmulationConfig` object.

```python exec="on" source="material-block" session="execution"
from qoolqit.execution import EmulationConfig, Occupation

observables = (Occupation(evaluation_times=[0.1, 0.5, 1.0]),)
emulation_config = EmulationConfig(
    observables=observables,
    with_modulation=True
    )
```

The configuration is then passed to the emulator at instantiation:

```python exec="on" source="material-block" session="execution"
emulator = LocalEmulator(emulation_config=emulation_config)
```

The key parameters of `EmulationConfig` are:

| Parameter | Description |
|---|---|
| `observables` | Sequence of observables to compute during emulation. |
| `default_evaluation_times` | Default relative times (between 0 and 1) at which observables are evaluated, or `"Full"` for every emulation step. Defaults to `(1.0,)` (end of simulation only). |
| `with_modulation` | Whether to emulate finite-bandwidth hardware modulation of the drive. |
| `initial_state` | Custom initial state (defaults to all qubits in the ground state). |
| `noise_model` | Optional noise model to apply during emulation. |

### Available observables

All observables accept an optional `evaluation_times` argument — a sequence of relative times between
`0.0` (start) and `1.0` (end of the sequence) — and an optional `tag_suffix` to disambiguate
multiple instances of the same observable in the same config.
All observables can be imported directly from `qoolqit.execution`.

#### `BitStrings`

Samples bitstrings from the quantum state at the given evaluation times.
By default added automatically by QoolQit with the `runs` count set on the emulator.

```python exec="on" source="material-block" session="execution"
from qoolqit.execution import BitStrings, EmulationConfig

# sample 500 bitstrings at the end of the sequence
observables = (BitStrings(num_shots=500),)
emulation_config = EmulationConfig(observables=observables)
```

!!! note
    If `BitStrings` is included in a custom `EmulationConfig`, the `runs` parameter of the emulator
    is ignored in favour of the `num_shots` set on the observable.

#### `Occupation`

For each qubit `i`, computes the expectation value of the occupation operator `⟨n_i⟩ = ⟨ψ(t)|n_i|ψ(t)⟩`.
This gives the probability of finding each qubit in the excited (`|r⟩`) state.

```python exec="on" source="material-block" session="execution"
from qoolqit.execution import EmulationConfig, Occupation

# measure occupation at 25%, 50%, 75% and 100% of the evolution
observables = (Occupation(evaluation_times=[0.25, 0.5, 0.75, 1.0]),)
emulation_config = EmulationConfig(observables=observables)
```

#### `CorrelationMatrix`

Computes the two-body correlation matrix `C[i,j] = ⟨n_i n_j⟩` at the given evaluation times.
This reveals spatial correlations between qubits.

```python exec="on" source="material-block" session="execution"
from qoolqit.execution import CorrelationMatrix, EmulationConfig

# measure correlations at the mid-point and at the end
observables = (CorrelationMatrix(evaluation_times=[0.5, 1.0]),)
emulation_config = EmulationConfig(observables=observables)
```

#### `Energy`, `EnergyVariance`, and `EnergySecondMoment`

These observables track the energy landscape of the system throughout the evolution:

- `Energy`: the expectation value of the Hamiltonian `⟨H(t)⟩`.
- `EnergyVariance`: the variance `⟨H(t)²⟩ − ⟨H(t)⟩²`.
- `EnergySecondMoment`: the raw second moment `⟨H(t)²⟩`, useful to compute the variance when averaging over many runs.

```python exec="on" source="material-block" session="execution"
from qoolqit.execution import EmulationConfig, Energy, EnergyVariance

# track the full energy profile at 10 equally-spaced points in time
evaluation_times = [i / 10 for i in range(1, 11)]
observables = (
    Energy(evaluation_times=evaluation_times),
    EnergyVariance(evaluation_times=evaluation_times),
)
emulation_config = EmulationConfig(observables=observables)
```

#### `StateResult`

Stores the full quantum state vector at the given evaluation times.
Useful for post-processing or computing custom quantities not covered by other observables.

```python exec="on" source="material-block" session="execution"
from qoolqit.execution import EmulationConfig, StateResult

# store the state at the beginning, middle, and end of the evolution
observables = (StateResult(evaluation_times=[0.0, 0.5, 1.0]),)
emulation_config = EmulationConfig(observables=observables)
```

#### `Expectation`

Computes the expectation value of a custom operator `⟨ψ(t)|O|ψ(t)⟩`.
The operator type must be compatible with the chosen backend (e.g. a `qutip.Qobj` for `QutipBackendV2`).

```python
from qoolqit.execution import EmulationConfig, Expectation

# `operator` must match the type expected by the chosen backend
observables = (Expectation(operator=my_operator, evaluation_times=[1.0]),)
emulation_config = EmulationConfig(observables=observables)
```

#### `Fidelity`

Computes the fidelity `|⟨ψ|φ(t)⟩|²` between the evolving state `|φ(t)⟩` and a reference pure state `|ψ⟩`.

```python
from qoolqit.execution import EmulationConfig, Fidelity

# `target_state` must match the type expected by the chosen backend
observables = (Fidelity(state=target_state, evaluation_times=[1.0]),)
emulation_config = EmulationConfig(observables=observables)
```

### Combining multiple observables

Any combination of observables can be passed together in a single `EmulationConfig`.
When including multiple instances of the same observable class, use `tag_suffix` to distinguish them
in the results:

```python exec="on" source="material-block" session="execution"
from qoolqit.execution import (
    BitStrings,
    CorrelationMatrix,
    EmulationConfig,
    Energy,
    Occupation,
)

observables = (
    BitStrings(num_shots=1000),
    Occupation(evaluation_times=[0.5, 1.0]),
    CorrelationMatrix(evaluation_times=[1.0]),
    Energy(evaluation_times=[0.25, 0.5, 0.75, 1.0]),
)
emulation_config = EmulationConfig(
    observables=observables,
    with_modulation=True,
)
emulator = LocalEmulator(emulation_config=emulation_config)
```

!!! note
    Dedicated and specific configuration subclasses for each backend also exist: `QutipConfig`,
    `SVConfig`, `MPSConfig`. They should be used by pairing them with the corresponding backend type
    and imported from their respective packages, namely `pulser-simulation`, `emu-sv` and `emu-mps`.
    For more information about configuration options, please refer to the
    [Pulser documentation](https://pulser.readthedocs.io/en/stable/apidoc/_autosummary/pulser.backend.EmulationConfig.html).


## Executing remotely

As anticipated, credentials to create a connection is required for most remote workflows.
Here we will show how to create the specific handler of Pasqal Cloud services.
Again, for more information about Pasqal Cloud and other providers, please refer to the [Pasqal Cloud website](https://www.pasqal.com/solutions/cloud/).

Let's first initialize a connection as:

```python exec="on" source="material-block" session="execution"
from pulser_pasqal import PasqalCloud
```

```python
connection = PasqalCloud(
    username=USERNAME,  # Your username or email address for the Pasqal Cloud Platform
    password=PASSWORD,  # The password for your Pasqal Cloud Platform account
    project_id=PROJECT_ID,  # The ID of the project associated to your account
)
```

To use such connection, and to send jobs to the cloud, we first need to initialize a remote emulator:

```python exec="on" source="material-block" session="execution"
from qoolqit.execution import RemoteEmulator

connection = PasqalCloud()  # markdown-exec: hide
emulator = RemoteEmulator(connection=connection)
```

As before, also `RemoteEmulator` can be instantiated with:
- `backend_type`: remote counterpart of local backends, namely `EmuFreeBackendV2` (default), `EmuSVBackend` (not available yet), `EmuMPSBackend`.
- `emulation_config`: same as before.
- `runs`: same as before.

As an example, below, we specify to emulate the program with the `EmuMPSBackend` and a custom `EmulationConfig`:

```python
from qoolqit.execution import (
    BackendType,
    EmulationConfig,
    Occupation,
    RemoteEmulator,
)

observables = (Occupation(evaluation_times=[0.5, 1.0]),)
emulation_config = EmulationConfig(observables=observables, with_modulation=True)

remote_emulator = RemoteEmulator(
    backend_type=BackendType.EmuMPSBackend,
    connection=connection,
    emulation_config=emulation_config,
    runs=1000,
)
results = remote_emulator.run(program)
```

### Handling remote results

Remote emulators and QPU both have a `run()` method that will return a `Sequence[Results]` object type.
However, if your program requires intensive resources to be run, or if QPU happens to be on maintenance, the use of this method is discouraged since it might leave your script hanging.
In these situations prefer the use of the `submit(program) -> RemoteResults` instead:

```python
remote_emulator = RemoteEmulator(.., connection=connection, ...)
remote_results = remote_emulator.submit(program)
```

Here, the remote results can act as a job handler:
- Query the batch status: PENDING, RUNNING, DONE, etc.:
    ```python
    batch_status = remote_results.get_batch_status()
    ```
- Query the batch id, to be saved for later retrieval of results:
    ```python
    batch_id = remote_results.get_batch_id()
    ```
- Retrieve the remote results from `batch_id` and a `connection`:
    ```python
    from qoolqit.execution import RemoteResults

    remote_results = RemoteResults(batch_id, connection)
    ```

Once the batch has been completed (`batch_status` returns DONE), the complete results can be finally fetched as:
```python
results = remote_results.results
```

## Executing remotely on a QPU

A connection object can also be used to run the program directly on a QPU.
To see the list of available devices, run:

```python exec="on" source="material-block" session="execution"
connection = PasqalCloud()
connection.fetch_available_devices()
print(connection.fetch_available_devices())   # markdown-exec: hide
```

Finally, on a QPU there is no configuration and, as per the properties of the quantum hardware, results will come as a bitstrings counter of length specified by the `runs` parameter.

```python exec="on" source="material-block" session="execution"
from qoolqit.execution import QPU

qpu = QPU(connection=connection, runs=500)
```
