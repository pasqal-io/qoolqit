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

!!! note
    Dedicated and specific configuration subclasses for each backend also exist: `QutipConfig`,
    `SVConfig`, `MPSConfig`. They should be used by pairing them with the corresponding backend type
    and imported from their respective packages, namely `pulser-simulation`, `emu-sv` and `emu-mps`.
    For more information about configuration options, please refer to the
    [Pulser documentation](https://pulser.readthedocs.io/en/stable/apidoc/_autosummary/pulser.backend.EmulationConfig.html).
