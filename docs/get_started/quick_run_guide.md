# Quick Run Guide

!!! info "Onboarding"
    You are currently on the onboarding page for QoolQit. This page is designed to get you up and running as quickly as possible, covering installation, running a job locally, and submitting to remote backends. It is intentionally focused and does not replace the full QoolQit documentation. For an in-depth understanding of the library we recommend following the complete documentation in order.

## Installation

QoolQit requires Python 3.10 or later. We recommend creating a virtual environment before installing to isolate your project dependencies.

### 1. Create a virtual environment

```sh
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

### 2. Install from PyPI

QoolQit can be installed from PyPI with your favorite pyproject-compatible Python manager. Using `pip`, for example:

```sh
pip install qoolqit
```

For usage within a project with a `pyproject.toml` file, add `qoolqit` to your list of dependencies:

```toml
[project]
dependencies = [
  "qoolqit"
]
```

For more installation options, including installing from source, see the [Install](install.md) page.

## Local Execution

Run your first experiment on a local emulator. No account or credentials are needed.

### 1. Define a quantum program

Create a register, define the drive, and compile the program to a device. This example uses `MockDevice` for local testing.

```python
from qoolqit import ConstantWaveform, Drive, MockDevice, QuantumProgram, RampWaveform, Register

# Create the register
register = Register.from_coordinates([(0, 1), (0, -1), (2, 0)])

# Define the drive parameters
omega = 0.8
delta_i = -2.0 * omega
delta_f = -delta_i
T = 25.0

# Define the drive
drive = Drive(amplitude=ConstantWaveform(T, omega), detuning=RampWaveform(T, delta_i, delta_f))

# Create and compile the program
program = QuantumProgram(register, drive)
program.compile_to(MockDevice())
```

### 2. Run on the local emulator

QoolQit provides access to local emulation through the `LocalEmulator` class. `run()` returns a `Job`, from which you can fetch the results.

```python
from qoolqit.execution import LocalEmulator

emulator = LocalEmulator()
job = emulator.run(program)
results = job.results()
```

### 3. Choose a backend

The `LocalEmulator` can emulate the program on different backends provided by Pasqal:

- `QutipBackendV2`: based on Qutip, runs programs with up to ~12 qubits (default).
- `SVBackend`: PyTorch-based state-vector emulator, runs programs with up to ~25 qubits. Requires the `emu-sv` package.
- `MPSBackend`: PyTorch-based Matrix Product State emulator, runs programs with up to ~80 qubits. Requires the `emu-mps` package.

`emu-sv` and `emu-mps` can be installed together with `pip install "qoolqit[extras]"`. Select a backend with the `backend_type` argument:

```python
from qoolqit.execution import BackendType, LocalEmulator

emulator = LocalEmulator(backend_type=BackendType.QutipBackendV2)
```

### 4. Inspect results

`job.results()` returns a `Results` object. Use `get_result_tags()` to see what is available, then extract the sampled bitstrings with `final_bitstrings`:

```python
results.get_result_tags()   # ['bitstrings']
results.final_bitstrings    # Counter({'111': 807, '101': 68, '110': 60, ...})
```

## Remote Execution

### Connection

!!! note "Create a connection"
    Remote execution, whether on emulators or QPUs, requires a connection to submit a job. You can connect either through Pasqal Cloud or through one of our third-party cloud providers. If you haven't set up a connection yet, see [Pasqal Cloud](https://www.pasqal.com/solutions/cloud/) before continuing.

### Remote execution to Cloud Emulators

#### 1. Create a connection

Initialize a `PasqalCloudConnection` with your username, password, and project ID from the portal, or use the third-party connection you set up above.

```python
from pasqal_cloud import PasqalCloudConnection

connection = PasqalCloudConnection(
    username=USERNAME,      # your email for the Pasqal Cloud Platform
    password=PASSWORD,      # your Pasqal Cloud Platform password
    project_id=PROJECT_ID,  # the ID of the project associated to your account
)
```

#### 2. Initialize a remote emulator and submit

Use `RemoteEmulator` with your connection. By default it uses `RemoteEmuFreeBackend`, which is free for all Pasqal Cloud accounts and requires no credits. `run()` submits the program and returns a `Job` immediately, without waiting for the results.

```python
from qoolqit.execution import BackendType, RemoteEmulator

remote_emulator = RemoteEmulator(
    backend_type=BackendType.RemoteEmuFreeBackend,
    connection=connection,
    num_shots=1000,
)
job = remote_emulator.run(program)
```

`RemoteEmulator` accepts the following arguments:

- `backend_type`: `RemoteEmuFreeBackend` (default), or `RemoteSVBackend` / `RemoteMPSBackend` as alternatives. Availability depends on your provider.
- `emulation_config`: same as for local emulators. See [Emulation configuration](../fundamentals/execution/execution.ipynb#emulation-configuration).
- `num_shots`: number of bitstring samples to collect.

#### 3. Check status and retrieve results

Remote jobs may take time to run. Check the job status, then fetch the results once the job is done. Save the job and batch IDs to retrieve the job later, for example from a new session.

```python
from qoolqit.execution import get_batch_id, retrieve_remote_job

# query status: PENDING, RUNNING, DONE, etc.
status = job.get_status()

# fetch the results (blocks until the job is done)
results = job.results()
results.final_bitstrings

# save the identifiers for later retrieval
job_id = job.job_id()
batch_id = get_batch_id(job)

# reconnect to the job later
job = retrieve_remote_job(connection, job_id, batch_id=batch_id)
```

### Remote Execution to a QPU

A connection object can also be used to run the program directly on a QPU.

#### 1. List available devices and compile to the QPU

Fetch the available devices from your connection, then compile your program to the target device. Compiling to the specific QPU device is required before submission.

```python
from qoolqit.devices import Device

# list available devices
connection.fetch_available_devices()
# {'FRESNEL': FRESNEL, ...}

# compile the program to the FRESNEL device
device = Device.from_connection(connection, "FRESNEL")
program.compile_to(device=device, profile="max_energy")
```

#### 2. Submit to the QPU

Initialize a `QPU` backend with your connection and number of shots, then submit. Checking the status and retrieving the results work the same as for remote emulators.

```python
from qoolqit.execution import QPU, get_batch_id

qpu = QPU(connection=connection, num_shots=500)
job = qpu.run(program)

# save the batch ID for later result retrieval
print(f"Batch ID: {get_batch_id(job)}")
```
