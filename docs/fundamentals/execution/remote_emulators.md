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
- `emulation_config`: same as before — see [Emulation configuration](../../extended_usage/execution_config.md) for details.
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
