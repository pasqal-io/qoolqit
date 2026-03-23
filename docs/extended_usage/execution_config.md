# Emulation configuration

More experienced users might want to fully configure an emulator to exploit all its possibilities,
such as defining which observables to measure during the emulation, or emulating real hardware modulation effects.
This is done through the `EmulationConfig` object.

```python exec="on" source="material-block" session="execution_config"
from qoolqit import Drive, Ramp, Register, Constant
from qoolqit import QuantumProgram
from qoolqit import MockDevice

register = Register.from_coordinates([(0,1), (0,-1), (2,0)])
omega = 0.8
delta_i = -2.0 * omega
delta_f = -delta_i
T = 25.0
wf_amp = Constant(T, omega)
wf_det = Ramp(T, delta_i, delta_f)
drive = Drive(amplitude = wf_amp, detuning = wf_det)
program = QuantumProgram(register, drive)
device = MockDevice()
program.compile_to(device)
```

```python exec="on" source="material-block" session="execution_config"
from qoolqit.execution import EmulationConfig, LocalEmulator, Occupation

observables = (Occupation(evaluation_times=[0.1, 0.5, 1.0]),)
emulation_config = EmulationConfig(
    observables=observables,
    with_modulation=True
    )
```

The configuration is then passed to the emulator at instantiation:

```python exec="on" source="material-block" session="execution_config"
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

## Available observables

All observables accept an optional `evaluation_times` argument — a sequence of relative times between
`0.0` (start) and `1.0` (end of the sequence) — and an optional `tag_suffix` to disambiguate
multiple instances of the same observable in the same config.
All observables can be imported directly from `qoolqit.execution`.

### `BitStrings`

Samples bitstrings from the quantum state at the given evaluation times.
By default added automatically by QoolQit with the `runs` count set on the emulator.

```python exec="on" source="material-block" session="execution_config"
from qoolqit.execution import BitStrings, EmulationConfig

# sample 500 bitstrings at the end of the sequence
observables = (BitStrings(num_shots=500),)
emulation_config = EmulationConfig(observables=observables)
```

!!! note
    If `BitStrings` is included in a custom `EmulationConfig`, the `runs` parameter of the emulator
    is ignored in favour of the `num_shots` set on the observable.

### `Occupation`

For each qubit `i`, computes the expectation value of the occupation operator `⟨n_i⟩ = ⟨ψ(t)|n_i|ψ(t)⟩`.
This gives the probability of finding each qubit in the excited (`|r⟩`) state.

```python exec="on" source="material-block" session="execution_config"
from qoolqit.execution import EmulationConfig, Occupation

# measure occupation at 25%, 50%, 75% and 100% of the evolution
observables = (Occupation(evaluation_times=[0.25, 0.5, 0.75, 1.0]),)
emulation_config = EmulationConfig(observables=observables)
```

### `CorrelationMatrix`

Computes the two-body correlation matrix `C[i,j] = ⟨n_i n_j⟩` at the given evaluation times.
This reveals spatial correlations between qubits.

```python exec="on" source="material-block" session="execution_config"
from qoolqit.execution import CorrelationMatrix, EmulationConfig

# measure correlations at the mid-point and at the end
observables = (CorrelationMatrix(evaluation_times=[0.5, 1.0]),)
emulation_config = EmulationConfig(observables=observables)
```

### `Energy`, `EnergyVariance`, and `EnergySecondMoment`

These observables track the energy landscape of the system throughout the evolution:

- `Energy`: the expectation value of the Hamiltonian `⟨H(t)⟩`.
- `EnergyVariance`: the variance `⟨H(t)²⟩ − ⟨H(t)⟩²`.
- `EnergySecondMoment`: the raw second moment `⟨H(t)²⟩`, useful to compute the variance when averaging over many runs.

```python exec="on" source="material-block" session="execution_config"
from qoolqit.execution import EmulationConfig, Energy, EnergyVariance

# track the full energy profile at 10 equally-spaced points in time
evaluation_times = [i / 10 for i in range(1, 11)]
observables = (
    Energy(evaluation_times=evaluation_times),
    EnergyVariance(evaluation_times=evaluation_times),
)
emulation_config = EmulationConfig(observables=observables)
```

### `StateResult`

Stores the full quantum state vector at the given evaluation times.
Useful for post-processing or computing custom quantities not covered by other observables.

```python exec="on" source="material-block" session="execution_config"
from qoolqit.execution import EmulationConfig, StateResult

# store the state at the beginning, middle, and end of the evolution
observables = (StateResult(evaluation_times=[0.0, 0.5, 1.0]),)
emulation_config = EmulationConfig(observables=observables)
```

### `Expectation`

Computes the expectation value of a custom operator `⟨ψ(t)|O|ψ(t)⟩`.
The operator type must be compatible with the chosen backend (e.g. a `qutip.Qobj` for `QutipBackendV2`).

```python
from qoolqit.execution import EmulationConfig, Expectation

# `operator` must match the type expected by the chosen backend
observables = (Expectation(operator=my_operator, evaluation_times=[1.0]),)
emulation_config = EmulationConfig(observables=observables)
```

### `Fidelity`

Computes the fidelity `|⟨ψ|φ(t)⟩|²` between the evolving state `|φ(t)⟩` and a reference pure state `|ψ⟩`.

```python
from qoolqit.execution import EmulationConfig, Fidelity

# `target_state` must match the type expected by the chosen backend
observables = (Fidelity(state=target_state, evaluation_times=[1.0]),)
emulation_config = EmulationConfig(observables=observables)
```

## Combining multiple observables

Any combination of observables can be passed together in a single `EmulationConfig`.
When including multiple instances of the same observable class, use `tag_suffix` to distinguish them
in the results:

```python exec="on" source="material-block" session="execution_config"
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
