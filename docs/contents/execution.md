# Executing a quantum program

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

More experienced users, might also want to configure an emulator.
To fully exploit the potential of each emulator backend, they can be configured through the generic `EmulationConfig` object. For example, the following configuration,

```python exec="on" source="material-block" session="execution"
from qoolqit.execution import EmulationConfig, Occupation

observables = (Occupation(evaluation_times=[0.1, 0.5, 1.0]),)
emulation_config = EmulationConfig(
    observables=observables,
    with_modulation=True
    )
```

simply asks the backend to compute some observable during runtime and to emulate the hardware more closely by considering finite-bandwidth hardware modulation of the drive.

Finally, to run a program on a configured emulator (local or remote), we can simply pass the configuration as an additional argument to the emulator instance as:

```python exec="on" source="material-block" session="execution"
from qoolqit.execution import EmulationConfig

emulator = LocalEmulator(emulation_config=emulation_config)
```

Dedicated and specific configuration for each backend also exist: `QutipConfig`, `SVConfig`, `MPSConfig`. They should be used by pairing them with the corresponding backend type and imported from their respective packages, namely `pulser-simulation`, `emu-sv` and `emu-mps`.
For more information about how the configuration options, please, refer to [Pulser documentation](https://pulser.readthedocs.io/en/stable/apidoc/_autosummary/pulser.backend.EmulationConfig.html).


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

As an example, below, we specify to emulate the program with the `EmuMPSBackend`:

```python
from qoolqit.execution import RemoteEmulator, BackendType

remote_emulator = RemoteEmulator(
        backend_type=BackendType.EmuMPSBackend,
        connection=connection,
        emulation_config = emulation_config
        runs=200
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
