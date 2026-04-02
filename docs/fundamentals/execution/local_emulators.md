# Executing locally

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
