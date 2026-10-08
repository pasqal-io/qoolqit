# Quick Run Guide

!!! info "Onboarding"

    You are currently on the onboarding page for QoolQit. This page is designed to get you up and running as quickly as possible, covering installation, running a job locally, and submitting to remote backends. It is intentionally focused and does not replace the full QoolQit documentation. For an in-depth understanding of the library, we recommend following the complete documentation in order.

## Installation

QoolQit requires Python 3.10 or later. Install it from [PyPI](https://pypi.org/project/qoolqit/) in a virtual environment:

``` sh
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install qoolqit
```

## Local Execution

Run your first experiment on a local emulator. No account or credentials are needed.

### 1. Define a quantum program

Create a register and a drive, then compile the program to a device. `MockDevice` is a test device for local runs.

``` python
from qoolqit import (
    ConstantWaveform,
    Drive,
    MockDevice,
    QuantumProgram,
    RampWaveform,
    Register,
)

# Create the register
register = Register.from_coordinates([(0, 1), (0, -1), (2, 0)])

# Define the drive parameters
omega = 0.8
delta_i = -2.0 * omega
delta_f = -delta_i
T = 25.0

# Define the drive
drive = Drive(
    amplitude=ConstantWaveform(T, omega),
    detuning=RampWaveform(T, delta_i, delta_f),
)

# Create and compile the program
program = QuantumProgram(register, drive)
program.compile_to(MockDevice())
```

### 2. Run on the local emulator

`LocalEmulator` runs the program on your machine. `run()` returns a `Job`, and `job.results()` gives you the results.

``` python
from qoolqit.execution import LocalEmulator

emulator = LocalEmulator()
job = emulator.run(program)
results = job.results()
```

### 3. Choose a backend

`LocalEmulator` supports several [Pasqal emulators](https://docs.pasqal.com/qpu-emulators/emulators/):

- `QutipBackendV2` (default): based on QuTiP, best for up to ~15 qubits.
- `SVBackend`: PyTorch-based state-vector emulator, best for up to ~25 qubits. Requires the [`emu-sv`](https://docs.pasqal.com/qpu-emulators/emusv/) package.
- `MPSBackend`: PyTorch-based Matrix Product State emulator, best for 25 to ~80 qubits. Requires the [`emu-mps`](https://docs.pasqal.com/qpu-emulators/emumps/) package.

Install `emu-sv` and `emu-mps` with `pip install "qoolqit[extras]"`, then pick a backend with `backend_type`:

``` python
from qoolqit.execution import BackendType, LocalEmulator

emulator = LocalEmulator(backend_type=BackendType.QutipBackendV2)
```

### 4. Inspect results

`job.results()` returns a `Results` object. `get_result_tags()` lists what it contains, and `final_bitstrings` gives the sampled bitstrings:

``` python
results.get_result_tags()   # ['bitstrings']
results.final_bitstrings    # Counter({'111': 807, '101': 68, '110': 60, ...})
```

## Remote Execution

### Connection

!!! note "Create a Connection"

    Remote execution, whether it's on Emulators or QPUs, requires a connection to submit a job. You can connect either through Pasqal Cloud or through one of our Third-Party Cloud providers. If you haven't set up a connection yet, do so before continuing.

    <div style="text-align: center">
      <a href="https://docs.pasqal.com/cloud/set-up" class="md-button md-button--primary">Pasqal Cloud</a>
      <a class="md-button" title="Coming soon">Third-Party Providers (coming soon)</a>
    </div>

### Remote Execution on Cloud Emulators

#### 1. Create a connection

Create a `PasqalCloudConnection` with your username, password and project ID from the portal, or use your third-party connection.

``` python
from pasqal_cloud import PasqalCloudConnection

connection = PasqalCloudConnection(
    username=USERNAME,      # your user/email for the Pasqal Cloud Platform
    password=PASSWORD,      # your Pasqal Cloud Platform password
    project_id=PROJECT_ID,  # the ID of the project associated with your account
)
```

#### 2. Initialize a remote emulator and submit

`RemoteEmulator` uses `RemoteEmuFreeBackend` by default, which is free for all Pasqal Cloud accounts and needs no credits. `run()` submits the program and returns a `Job` without waiting for the results.

``` python
from qoolqit.execution import BackendType, RemoteEmulator

remote_emulator = RemoteEmulator(
    backend_type=BackendType.RemoteEmuFreeBackend,
    connection=connection,
    num_shots=1000,
)
job = remote_emulator.run(program)
```

`RemoteEmulator` accepts the following arguments:

- `backend_type`: `RemoteEmuFreeBackend` (default), `RemoteSVBackend` or `RemoteMPSBackend`. Availability depends on your provider.
- `emulation_config`: same as for local emulators. See [Emulation configuration](../fundamentals/execution/execution.ipynb#emulation-configuration).
- `num_shots`: number of bitstring samples to collect.

#### 3. Check status and retrieve results

Remote jobs run asynchronously, so you can check their status and fetch the results once they are done. Save the job and batch IDs to retrieve the job later, for example from a new session.

``` python
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

### Remote Execution on a QPU

The same connection lets you run the program on a QPU.

#### 1. List available devices and compile to the QPU

List the devices available through your connection, then compile the program to the target QPU. You must compile to the QPU device before submitting.

``` python
from qoolqit.devices import Device

# list available devices
connection.fetch_available_devices()
# {'FRESNEL': FRESNEL, ...}

# compile the program to the FRESNEL device
device = Device.from_connection(connection, "FRESNEL")
program.compile_to(device=device, profile="max_energy")
```

#### 2. Submit to the QPU

Create a `QPU` backend with your connection and number of shots, then submit. Status checks and result retrieval work the same as for remote emulators.

``` python
from qoolqit.execution import QPU, get_batch_id

qpu = QPU(connection=connection, num_shots=500)
job = qpu.run(program)

# save the identifiers for later retrieval
job_id = job.job_id()
batch_id = get_batch_id(job)
```
