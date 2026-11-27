# Programming with QoolQit

This page explains how QoolQit can be used to build quantum programs by employing the dimensionless Hamiltonian framework described in [Programming a neutral-atom QPU](<https://pasqal-io.github.io/qoolqit/get_started/qoolqit_model/index.md>).

Programming with QoolQit is based on five core steps:

1. Defining a **Register**: where qubits live (their geometry).
2. Defining a **Drive**: how you control the system over time (waveforms).
3. Building a **QuantumProgram**: the pairing of *Register + Drive*.
4. **Compiling** the **QuantumProgram**: mapping the abstract program onto a specific device model.
5. **Executing** the compiled program: running the compiled sequence and collecting results.

## 1\. Register

A **register** defines the **positions** of qubits in your program. In neutral-atom / Rydberg analog models, geometry directly determines how strongly qubits interact.

> [!TIP]
>
> **Use unit spacing**
>
> The closest pair of qubits should be at distance **1**. This convention normalizes interaction strengths and keeps drive parameters interpretable across different layouts.

```
from qoolqit import Register

# Create a register from coordinates (dimensionless units)
register = Register.from_coordinates([(0, 0), (1, 0), (0.5, 0.866)])

# Or use built-in graph patterns
from qoolqit.graphs import DataGraph

graph = DataGraph.square(m=2, n=2)
register = Register.from_graph(graph)  # 2x2 square lattice
register.draw()
```

For problem embedding, QoolQit also provides layout embedders that map graph structure onto qubit positions:

```
from qoolqit import Register
from qoolqit.embedding import SpringLayoutEmbedder
from qoolqit.graphs import DataGraph

graph = DataGraph.random_er(n=5, p=0.3, seed=3)
embedded_graph = SpringLayoutEmbedder().embed(graph)
register = Register.from_graph(embedded_graph)
register.draw()
```

> [!NOTE]
>
> **Go further**
>
> See [Registers](<https://pasqal-io.github.io/qoolqit/fundamentals/quantum_program/index.md#registers>) for all available register creation methods and options.
>
> See [Problem Embedding](<https://pasqal-io.github.io/qoolqit/fundamentals/embedding/index.md>) for embedding data and problems into the Rydberg analog model.

## 2\. Waveforms and Drives

A **drive** is the time-dependent control applied to the system, built from one or more **waveforms**, for example amplitude \\(\\tilde{\\Omega}\\) and detuning \\(\\tilde{\\delta}\\) as functions of time \\(\\tilde{t}\\).

Waveform durations are dimensionless: \\(\\tilde{t}\\) measures duration relative to an interaction timescale. In an interacting many-body system, this gives \\(\\tilde t\\) a natural physical interpretation in terms of the buildup and propagation of correlations.

| Regime | Condition | Physical meaning |
| --- | --- | --- |
| Short time | \\(\\tilde{t} \\ll 1\\) | Too short for interactions to strongly reshape the state |
| Long time | \\(\\tilde{t} \\sim n\\) | Correlations may have propagated across a distance of order \\(n\\) lattice spacings |

```
from qoolqit import Drive
from qoolqit.waveforms import ConstantWaveform, InterpolatedWaveform, RampWaveform

# Interpolated waveform: smooth curve through specified values
omega_wf = InterpolatedWaveform(duration=10, values=[0, 1, 0])

# Constant waveform
delta_wf = ConstantWaveform(duration=10, value=-2)

# Ramp waveform
delta_wf = RampWaveform(duration=10, initial_value=-2, final_value=2)

# Combine into a Drive
drive = Drive(amplitude=omega_wf, detuning=delta_wf)

drive.draw()
```

> [!NOTE]
>
> **Go further**
>
> See [Waveforms](<https://pasqal-io.github.io/qoolqit/fundamentals/quantum_program/index.md#waveforms>) for all waveform types and options.
>
> See [Drive Hamiltonian](<https://pasqal-io.github.io/qoolqit/fundamentals/quantum_program/index.md#drives>) for details on combining waveforms into drives.

## 3\. QuantumProgram

A `QuantumProgram` pairs a **register** (layout and interactions) with a **drive** (time-dependent controls). The initial state is always \\(|0\\rangle^{\\otimes N}\\), so every program describes how the drive and interactions evolve this fixed initial state.

```
from qoolqit import QuantumProgram

program = QuantumProgram(register=register, drive=drive)
```

> [!NOTE]
>
> **Go further**
>
> See [Quantum Programs](<https://pasqal-io.github.io/qoolqit/fundamentals/quantum_program/index.md#defining-a-quantum-program>) for more details.

## 4\. Compilation

Compilation translates your abstract program into something a given device (or emulator) can actually run, applying device-specific constraints such as maximum duration, amplitude and detuning bounds, discretization rules, and other hardware limits.

```
from qoolqit import AnalogDevice

device = AnalogDevice()
program.compile_to(device, profile="max_energy")
```

> [!NOTE]
>
> **Go further**
>
> See [Compiling a Quantum Program](<https://pasqal-io.github.io/qoolqit/fundamentals/compilation/rationale/index.md>) for how compilation works.
>
> See [Devices](<https://pasqal-io.github.io/qoolqit/fundamentals/compilation/device_and_compilation/index.md>) for available devices and their specifications.

## 5\. Execution

Once compiled, run the sequence and retrieve results. The three stages map cleanly onto three concepts:

- **Program**: what you *want* to run (abstract physics).
- **Sequence**: what you *will* run (device-compatible instructions).
- **Result**: what you *observed* (samples, probabilities, observables, etc.).

```
from qoolqit.execution import LocalEmulator

emulator = LocalEmulator()
job = emulator.run(program)
results = job.results()
```

> [!NOTE]
>
> **Go further**
>
> See [Execution](<https://pasqal-io.github.io/qoolqit/fundamentals/execution/execution/index.md>) for running programs and handling job results:
>
> - [Local emulation](<https://pasqal-io.github.io/qoolqit/fundamentals/execution/execution/index.md#local-emulator>)
> - [Remote emulation](<https://pasqal-io.github.io/qoolqit/fundamentals/execution/execution/index.md#remote-emulator>)
> - [QPU execution](<https://pasqal-io.github.io/qoolqit/fundamentals/execution/execution/index.md#executing-remotely-on-a-qpu>)

## Example: Rydberg Blockade Demonstration

The **blockade regime** occurs when interactions prevent nearby atoms from being simultaneously excited. In the dimensionless framework this is straightforward to set up:

- Place two qubits at unit distance \\(\\Rightarrow \\tilde{J} = 1\\).
- Blockade condition: \\(\\tilde{\\Omega} \\ll 1\\) (drive is weak compared to interactions).

We will compare two programs:

| Case | \\(\\tilde{\\Omega}\\) | Regime | Expected behavior |
| --- | --- | --- | --- |
| Blockade | \\(0.3\\) | \\(\\tilde{\\Omega} \\ll \\tilde{J}\\) | Double excitation \\(\\vert 11\\rangle\\) suppressed |
| Non-blockade | \\(2.0\\) | \\(\\tilde{\\Omega} \\gg \\tilde{J}\\) | Qubits behave more independently; \\(\\vert 11\\rangle\\) accessible |

```
import numpy as np

from qoolqit import AnalogDevice, Drive, QuantumProgram, Register
from qoolqit.execution import BitStrings, EmulationConfig, LocalEmulator
from qoolqit.waveforms import ConstantWaveform

# Two qubits at unit distance => maximum interaction J = 1
register = Register.from_coordinates([(0, 0), (1, 0)])

duration = 10

# Blockade regime: Omega << J => double excitation is suppressed
drive_blockade = Drive(
    amplitude=ConstantWaveform(duration, 0.3),
)

# Non-blockade regime: Omega >> J => drive dominates, both atoms can be excited
drive_no_blockade = Drive(
    amplitude=ConstantWaveform(duration, 2.0),
)
```

Drawing the register with `blockade_radius` shows a disk of radius \\(\\tilde{r}\_b / 2\\) around each atom, with \\(\\tilde{r}\_b = \\tilde{\\Omega}^{-1/6}\\): the two disks overlap exactly when the atoms are blockaded.

```
import matplotlib.pyplot as plt

fig, axs = plt.subplots(1, 2, figsize=(8, 3))
for ax, omega in zip(axs, [0.3, 2.0], strict=True):
    register.draw(ax=ax, blockade_radius=omega ** (-1 / 6))
    ax.set_title(rf"$\tilde\Omega = {omega}$")
fig.tight_layout()
```

```
# Build and compile programs
program_blockade = QuantumProgram(register, drive_blockade)
program_no_blockade = QuantumProgram(register, drive_no_blockade)

device = AnalogDevice()
program_blockade.compile_to(device, profile="max_energy")
program_no_blockade.compile_to(device, profile="max_energy")
```

```
# Configure emulation: sample bitstrings at 81 evaluation times
eval_times = np.linspace(0.0, 1.0, 81)
bitstrings = BitStrings(evaluation_times=list(eval_times), num_shots=1000)
configuration = EmulationConfig(observables=[bitstrings])

emulator = LocalEmulator(emulation_config=configuration)

job_blockade = emulator.run(program_blockade)
result_blockade = job_blockade.results()

job_no_blockade = emulator.run(program_no_blockade)
result_no_blockade = job_no_blockade.results()
```

```
import matplotlib.pyplot as plt

for result, label, color in [
    (result_blockade, "Blockade", "navy"),
    (result_no_blockade, "No Blockade", "crimson"),
]:
    times = result.get_result_times(bitstrings)
    occupation = [
        result.get_result(bitstrings.tag, time=t)["11"] / bitstrings.num_shots for t in times
    ]
    plt.plot(times, occupation, label=label, color=color)

plt.xlabel(r"$t$", fontsize=20)
plt.ylabel(r"$P_{rr}$", fontsize=20)
plt.xticks(fontsize=16)
plt.yticks(fontsize=16)
plt.legend(fontsize=14)
```

### What to expect

- **Blockade case** (\\(\\tilde{\\Omega} = 0.3\\)): the strong interaction heavily penalizes the \\(|11\\rangle\\) state. You should observe a suppressed probability of both qubits being excited simultaneously.
- **Non-blockade case** (\\(\\tilde{\\Omega} = 2.0\\)): the drive dominates and interactions are comparatively weak, so the two qubits behave more independently and \\(|11\\rangle\\) becomes much more accessible.

> [!NOTE]
>
> **Go further**
>
> See [Solving a Basic QUBO Problem](<https://pasqal-io.github.io/qoolqit/tutorials/solving_a_qubo/index.md>) for another application example.
