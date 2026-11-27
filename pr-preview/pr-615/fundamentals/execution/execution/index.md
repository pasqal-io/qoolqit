In this page, you will learn how to:

- run a `QuantumProgram` on local/remote emulators and QPUs.
- inspect and extract the execution results
- choose between different emulator backends and configuration options.
- use a `connection` to run programs remotely through your provider.
- submit remote jobs, query their status and retrieve results

As anticipated, a `QuantumProgram` can be run on multiple backends provided by [Pasqal](<https://docs.pasqal.com/>): - locally installed emulators - remote cloud emulators - QPUs

Remote emulators and QPUs **require** credentials to submit a job. More information on how to access a QPU through your favorite cloud provider is available at [Pasqal's website](<https://www.pasqal.com/solutions/cloud/>). Later, we will briefly show how to authenticate and send a remote job.

---

Let us revisit the quantum program definition described before in the [Defining a quantum program](<https://pasqal-io.github.io/qoolqit/fundamentals/quantum_program/index.md#defining-a-quantum-program>) page.

```
from qoolqit import AnalogDevice, ConstantWaveform, Drive, QuantumProgram, RampWaveform, Register

# Create the register
register = Register.from_coordinates([(0,1), (0,-1), (2,0)])

# Defining the drive parameters
omega = 0.8
delta_i = -2.0 * omega
delta_f = -delta_i
T = 25.0

# Defining the drive
wf_amp = ConstantWaveform(T, omega)
wf_det = RampWaveform(T, delta_i, delta_f)
drive = Drive(amplitude = wf_amp, detuning = wf_det)

# Creating the program
program = QuantumProgram(register, drive)

# Compiling the program to a device
program.compile_to(device=AnalogDevice(), profile="max_energy")
```

In the following sections we will provide more details about local/remote emulation and QPU execution of your program.

## Local Emulator

Local emulators run quantum simulations directly on your machine. They are ideal for development, testing, and small-scale quantum programs. QoolQit provides easy access to local emulation through the `LocalEmulator` class, which allows you to `run` quantum programs locally.

For all emulators, a job handler is returned, from which you can query the results. Emulating locally will only return completed jobs, as opposed to remote emulators, which we will discuss later.

```
from qoolqit.execution import LocalEmulator

emulator = LocalEmulator()
job = emulator.run(program)
results = job.results()
```

While the snippet above provides the basic way to run a quantum program, we will now discuss how to: - select different emulator backends. - get the results. - configure emulation backends.

### Backend Types

The `LocalEmulator` allows you to emulate the program run on different backends provided by Pasqal:

- `QutipBackendV2`: Based on Qutip, runs programs with up to \~12 qubits and returns qutip objects in the results (default).
- `SVBackend`: PyTorch based state vectors and sparse matrices emulator. Runs programs with up to \~25 qubits and returns torch objects in the results. Requires installing the `emu-sv` package (see the [emu-sv documentation](<https://docs.pasqal.com/emulationtools/emusv/>))
- `MPSBackend`: PyTorch based emulator using Matrix Product States (MPS). Runs programs with up to \~80 qubits and returns torch objects in the results. Requires installing the `emu-mps` package (see the [emu-mps documentation](<https://docs.pasqal.com/emulationtools/emumps/>)).

To use a particular backend it is sufficient to specify it through the `backend_type` argument:

```
from qoolqit.execution import BackendType, LocalEmulator

emulator = LocalEmulator(backend_type=BackendType.QutipBackendV2)
```

### Handling local results

The call `emulator.run(program)` will return a `Job` object type. All execution methods (`LocalEmulator.run()`, `RemoteEmulator.run()`, and `QPU.run()`) return a `Job` object that serves as a handler for managing the execution lifecycle and to fetch the results once the computation is completed. More about this in the remote emulator [section](<#handling-remote-results-job-and-status-management>) of this page.

As an example, let us inspect the results we got in the previous run:

```
# single result in the sequence
results.get_result_tags()
```

```
['bitstrings']
```

Then the bitstrings can be extracted simply as:

```
# single result in the sequence
final_bitstrings = results.final_bitstrings
final_bitstrings
```

```
Counter({'111': 822,
         '101': 67,
         '110': 49,
         '011': 47,
         '100': 8,
         '001': 4,
         '010': 3})
```

### Emulation configuration

Here we discuss how to fully configure emulator backends to exploit all their possibilities. Notable examples include asking for specific observables, modifying the default evaluation times, emulating real hardware modulation effects, defining the initial state, setting noise models, etc. This is done through the `EmulationConfig` object, which can be used to configure all emulators. Once instantiated, the configuration can be then passed to the emulator at instantiation:

```
from qoolqit.execution import BitStrings, EmulationConfig, LocalEmulator, Occupation

# observables to compute, occupation of the Rydberg state and bitstrings sample
observables = (Occupation(evaluation_times=[0.1, 0.5, 1.0]), BitStrings(num_shots=100))
emulation_config = EmulationConfig(
    observables=observables,
    with_modulation=True
    )

# emulator with a custom configuration
emulator = LocalEmulator(emulation_config=emulation_config)
# run the program with the new config
job = emulator.run(program)
```

As before, results can be inspected and queried for a specific observable result:

```
# get the results
results = job.results()

# get the result tags (this will include the observable names)
print(results.get_result_tags())

# get the result for the occupation observable at time 1.0 (final time)
results.get_result("occupation", time=1.0)
```

```
['occupation', 'bitstrings']





[0.9475510886446437, 0.9475510886446437, 0.9473207271173786]
```

The key parameters of `EmulationConfig` are:

| Parameter | Description |
| --- | --- |
| `observables` | Sequence of observables to compute during emulation. The list of available observables is available [here](<https://docs.pasqal.com/pulser/apidoc/_autosummary/pulser.backend/>). |
| `default_evaluation_times` | Default relative times (between 0 and 1) at which observables are evaluated, or `"Full"` for every emulation step. Defaults to `(1.0,)` (end of simulation only). |
| `with_modulation` | Whether to emulate finite-bandwidth hardware modulation of the drive. |
| `initial_state` | Custom initial state (defaults to all qubits in the ground state). |
| `noise_model` | Optional noise model to apply during emulation. |

For a more detailed description of all configuration options, please refer to the API documentation of `EmulationConfig` [here](<https://pasqal-io.github.io/qoolqit/reference/execution/index.md#qoolqit.execution.EmulationConfig>) or directly from the [Pulser documentation](<https://docs.pasqal.com/pulser/apidoc/_autosummary/pulser.backend.EmulationConfig/>).

The `EmulationConfig` object is designed to be easily extensible, allowing for the addition of new configuration parameters or specific backend-specific configurations, respectively `QutipConfig`, `SVConfig` and `MPSConfig`. They should be used by pairing them with the corresponding backend type and imported from their respective packages, namely `pulser-simulation`, `emu-sv` and `emu-mps`.

As we will see in the next section, `EmulationConfig` can also be used to configure the remote emulators.

## Remote Emulator

Remote emulators run on cloud infrastructure, potentially allowing you to simulate larger quantum systems. As anticipated, for remote workflows **credentials to create a connection are required**. Here we will show how to create the specific handler of Pasqal Cloud services. Again, for more information about Pasqal Cloud and other providers, please refer to the [Pasqal Cloud website](<https://www.pasqal.com/solutions/cloud/>).

Let's first initialize a connection. Without providing actual credentials, we can only create an empty object, for displaying purposes only:

```
from pasqal_cloud import PasqalCloudConnection

# connection = PasqalCloudConnection(
#     username=USERNAME,  # Your username or email address for the Pasqal Cloud Platform
#     password=PASSWORD,  # The password for your Pasqal Cloud Platform account
#     project_id=PROJECT_ID,  # The ID of the project associated to your account
# )
connection = PasqalCloudConnection()
```

To use such connection to submit jobs, we first need to initialize a remote emulator:

```
from qoolqit.execution import RemoteEmulator

remote_emulator = RemoteEmulator(connection=connection)
```

The `RemoteEmulator` supports the equivalent remote version of the above-mentioned backends, respectively `RemoteEmuFreeBackend` (default), `RemoteSVBackend` and `RemoteMPSBackend`. Depending on your provider, however, some emulator backends might not be available to use.

As before, also `RemoteEmulator` can be instantiated with: - `backend_type`: remote counterpart of local backends, namely `RemoteEmuFreeBackend` (default), `RemoteSVBackend`, `RemoteMPSBackend`. - `emulation_config`: same as local emulators. See [Emulation configuration](<#emulation-configuration>). - `num_shots`: same as local emulators.

As an example, below, we specify to emulate the program with the `RemoteEmuFreeBackend` and a custom `EmulationConfig`:

```
from qoolqit.execution import (
    BackendType,
    EmulationConfig,
    Occupation,
    RemoteEmulator,
)

# define the observables to be evaluated at the specified times
observables = (Occupation(evaluation_times=[0.5, 1.0]),)
# emulation configuration to add observables and include hardware modulation
emulation_config = EmulationConfig(observables=observables, with_modulation=True)

# initialize the remote emulator with the custom configuration and num_shots
remote_emulator = RemoteEmulator(
    backend_type=BackendType.RemoteEmuFreeBackend,
    connection=connection,
    emulation_config=emulation_config,
    num_shots=1000,
)
```

### Handling remote results: job and status management

Remote emulators and QPUs both have a `run()` method that will return a job handler.

```
job = remote_emulator.run(program)
```

If your program requires intensive resources to be run, or if the QPU happens to be under maintenance, results might not be immediately available. For this reason, the job handler provides several key methods for monitoring and retrieving results:

**Querying Job Status:**

```
# Check the current status of the job
status = job.get_status()
print(f"Job status: {status}")  # Returns: PENDING, RUNNING, DONE, ERROR, etc.
```

**Retrieving Job Results:**

```
# Get results (blocks until completion for remote jobs)
results = job.results()

# Get results with timeout (raises TimeoutError if exceeded)
results = job.results(timeout=300)  # 5 minutes timeout
```

Please note that depending on the provider connection lifecycle, `job.results()` may not allow waiting indefinitely. It is good practice to always check the status of the job before retrieving results.

**Job Identification and Retrieval:**

```
from qoolqit.execution import get_batch_id

# Get the unique batch identifier for the job
batch_id = get_batch_id(job)

# Get the unique job identifier
job_id = job.job_id()

# For remote jobs, retrieve a job using its ID
from qoolqit.execution import retrieve_remote_job
retrieved_job = retrieve_remote_job(connection, job_id, batch_id=batch_id)
```

Note that local emulator jobs complete immediately and always return `DONE` status, while remote jobs (remote emulators and QPUs) may remain in `PENDING` or `RUNNING` states before completion.

## Executing remotely on a QPU

A connection object can also be used to run the program directly on a QPU.

Then, to see the list of available devices, run:

```
connection.fetch_available_devices()
```

```
<string>:26: DeprecationWarning: Defining the number of emulation trajectories via 'NoiseModel.runs' is deprecated since pulser v1.7. Please favour using 'EmulationConfig.n_trajectories' instead.





{'FRESNEL_CAN1': FRESNEL_CAN1, 'FRESNEL': FRESNEL}
```

A default QPU device is always available in the empty Pasqal Cloud connection, for demonstration purposes.

Now, to submit the program to the QPU, the program **must be compiled for the specific QPU device** before submission:

```
from qoolqit.devices import Device

device = Device.from_connection(connection, "FRESNEL")
program.compile_to(device=device, profile="max_energy")
```

```
<string>:26: DeprecationWarning: Defining the number of emulation trajectories via 'NoiseModel.runs' is deprecated since pulser v1.7. Please favour using 'EmulationConfig.n_trajectories' instead.
```

Finally, to set up a QPU backend, there is no configuration and, as per the properties of the quantum hardware, results will come as a bitstring counter whose counts sum to the `num_shots` parameter.

```
from qoolqit.execution import QPU

qpu = QPU(connection=connection, num_shots=500)
```

Finally, submission and results handling work the same as for remote emulators.

## Hardware Considerations

When running on QPUs, consider:

- **Limited shots**: QPU time is precious, so choose your number of shots carefully
- **Hardware constraints**: Your program must be compiled for the specific QPU device
- **Queue times**: QPU jobs may wait in queue before execution

## Summary

This notebook covered the three main execution backends in QoolQit:

1. **Local Emulators**: Fast, local simulation for development and testing
2. **Remote Emulators**: Cloud-based simulation for larger quantum systems
3. **QPUs**: Real quantum hardware execution

Each backend has its use cases, and the choice depends on your specific needs: - Use local emulators for quick prototyping and small systems - Use remote emulators for larger simulations beyond local capabilities - Use QPUs for real quantum experiments and final validation

For more detailed configuration options for emulators, see the [Emulation configuration](<#emulation-configuration>) section above.
