# Executing a quantum program

Let us revisit the quantum program described in the [Quantum program](./programs.md) page.

```python exec="on" source="material-block" result="json" session="drives"
from qoolqit import PiecewiseLinear
from qoolqit import Register, Drive, QuantumProgram
from qoolqit import MockDevice

# Defining the Drive
wf0 = PiecewiseLinear([1.0, 2.0, 1.0], [0.0, 0.5, 0.5, 0.0])
wf1 = PiecewiseLinear([1.0, 2.0, 1.0], [-1.0, -1.0, 1.0, 1.0])
drive = Drive(amplitude = wf0, detuning = wf1)

# Defining the Register
coords = [(0.0, 0.0), (0.0, 1.0), (1.0, 0.0), (1.0, 1.0)]
register = Register.from_coordinates(coords)

# Creating the Program
program = QuantumProgram(register, drive)

# Compiling the Program
device = MockDevice()
program.compile_to(device)
```

The compiled program is ready to be executed using its `run()` method. The signature of this method is the following:
```
def run(
    self,
    backend_name: BackendName = BackendName.QUTIP,
    result_type: ResultType = ResultType.STATEVECTOR,
    runs: int = 100,
    evaluation_times: list[float] = [1.0],
    **backend_params: Any,
) -> OutputType:
    ...
```

The execution process is primarily controlled by two arguments: `backend_name` and `result_type`.

The `backend_name` parameter expects a value from the `BackendName` enumeration, which specifies the computational backend responsible for simulating the underlying Pulser sequence. Supported values include `QUTIP` and `EMUMPS`, corresponding to the [QuTiP](https://qutip.readthedocs.io/en/qutip-5.2.x/) backend for Pulser and the [emu-mps](https://pasqal-io.github.io/emulators/latest/emu_mps/) quantum emulator, respectively.

The `result_type` argument determines the format of the output returned by the `run()` method. It accepts values from the `ResultType` enumeration: `STATEVECTOR` and `BITSTRINGS`.

- `STATEVECTOR` returns a NumPy array of shape $T \times 2^N$, representing the quantum state vectors of an $N$-qubit system at $T$ time points.

- `BITSTRINGS` returns a list of length $T$, where each element is a `Counter` object containing the counts of the sampled bitstrings of the system’s output state at the corresponding time point. The total number of samples is given by the `runs` argument of the `run()` method.

The collection of $T$ time points where the output states are returned are controlled by the `evaluation_time` argument. It accepts a list of floats between 0.0 and 1.0 that are mapped internally to the whole duration of the underlying sequence of the quantum program.

Finally, the user can pass keyword arguments for the backend's internal configuration. The corresponding documentation on the underlying configuration object is available [here](https://pulser.readthedocs.io/en/stable/apidoc/_autosummary/pulser.backend.EmulationConfig.html#emulationconfig).

Let us run the quantum program defined previously and request the state vectors as output.

```python exec="on" source="material-block" result="json" session="drives"
# Define the evaluation times list
T = 101
evaluation_times = np.linspace(0, 1, T).tolist()

# Simulate with QUTIP backend and output state vectors
qutip_state_vecs = program.run(
    backend_name=BackendName.QUTIP,
    result_type=ResultType.STATEVECTOR,
    evaluationtimes=evaluation_times)

print("Shape of the output for state vectors:")
print(qutip_state_vecs.shape)

print("Final state vector:")
print(qutip_state_vecs[-1])
```

We can run similar simulation and output bitstrings instead.

```python exec="on" source="material-block" result="json" session="drives"
# Number of samples
runs = 1000

# Simulate with EMUMPS backend and output bitstring counts
emumps_bitstrings = program.run(
    backend_name=BackendName.EMUMPS,
    result_type=ResultType.BITSTRINGS,
    evaluation_times=evaluation_times,
    runs=runs)

print("Length of the output list:")
print(len(emumps_bitstrings))

print("Final state bitstrings:")
print(emumps_bitstrings[-1])
```
