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

The `LocalEmulator` is a flexible object which allows to emulate the program run on different backends:
```python exec="on" source="material-block" session="execution"
from qoolqit.execution import LocalEmulator
from qoolqit.execution import QutipBackendV2, SVBackend, MPSBackend

emulator = LocalEmulator(backend_type=SVBackend)
```

- `QutipBackendV2`: Based on Qutip, runs programs with up to ~12 qubits and return qutip objects in the results.
- `SVBackend`: PyTorch based state vectors and sparse matrices emulator. Runs programs with up to ~25 qubits and return torch objects in the results.
- `MPSBackend`: PyTorch based emulator using Matrix Product States (MPS). Runs programs with up to ~100 qubits and return torch objects in the results.

More experienced users, might also want to configure an emulator through the generic `EmulationConfig` or the specific `QutipConfig`, `SVConfig`, `MPSConfig`.
For more information about how the configuration options, please, refer to [Pulser documentation](https://pulser.readthedocs.io/en/stable/apidoc/_autosummary/pulser.backend.EmulationConfig.html).

To run a program on a configured emulator (local or remote), we can simply pass the configuration as an additional argument to the emulator instance as:

```python exec="on" source="material-block" session="execution"
from qoolqit.execution import EmulationConfig

emulation_config = EmulationConfig()
emulator = LocalEmulator(emulation_config=emulation_config)
```

### Handling local results

## Executing remotely

As anticipated, credentials to create a connection is required for most remote workflows.
Here we will show how to create the specific handler of Pasqal Cloud services.
Again, for more information about Pasqal Cloud and other providers, please refer to the [Pasqal Cloud website](https://www.pasqal.com/solutions/cloud/).

Let's first initialize a connection as:

```python exec="on" source="material-block" session="execution"
from pulser_pasqal import PasqalCloud
```

```python source="material-block"
connection = PasqalCloud(
    username=USERNAME,  # Your username or email address for the Pasqal Cloud Platform
    password=PASSWORD,  # The password for your Pasqal Cloud Platform account
    project_id=PROJECT_ID,  # The ID of the project associated to your account
)
```

```python exec="on" source="material-block" session="execution"
from qoolqit.execution import RemoteEmulator

emulator = RemoteEmulator(connection=connection)
```

### Handling remote results


## Executing remotely on a QPU

A connection object can also be used to run the program directly on a QPU.
To see the list of available devices, run:

```python exec="on" source="material-block" result="json" session="execution"
connection=PasqalCloud()
connection.fetch_available_devices()
```

Finally, on a QPU there is no configuration and, as per the properties of the quantum hardware, results will come as a bitstrings counter of length specified by the `runs` parameter.

```python exec="on" source="material-block" session="execution"
from qoolqit.execution import QPU

qpu = QPU(connection=connection, runs=100)
```
