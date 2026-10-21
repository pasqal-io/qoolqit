# Programming with QoolQit

This page explains how QoolQit can be used to build quantum programs by employing the dimensionless Hamiltonian framework described in [Programming a neutral-atom QPU](qoolqit_model.md).

Programming with QoolQit is based on five core steps:

1. Defining a **Register**: where qubits live (their geometry).
2. Defining a **Drive**: how you control the system over time (waveforms).
3. Building a **QuantumProgram**: the pairing of *Register + Drive*.
4. **Compiling** the **QuantumProgram**: mapping the abstract program onto a specific device model.
5. **Executing** the compiled program: running the compiled sequence and collecting results.

## 1. Register

A **register** defines the **positions** of qubits in your program. In neutral-atom / Rydberg analog models, geometry directly determines how strongly qubits interact.

!!! tip "Use unit spacing"

    The closest pair of qubits should be at distance **1**. This convention normalizes interaction strengths and keeps drive parameters interpretable across different layouts.

```python exec="on" source="above" html="true" session="programming"
from qoolqit import Register

# Create a register from coordinates (dimensionless units)
register = Register.from_coordinates([(0, 0), (1, 0), (0.5, 0.866)])

# Or use built-in graph patterns
from qoolqit.graphs import DataGraph

graph = DataGraph.square(m=2, n=2)
register = Register.from_graph(graph)  # 2x2 square lattice
register.draw()
from qoolqit.visualization import fig_to_html; print(fig_to_html())  # markdown-exec: hide
```

For problem embedding, QoolQit also provides layout embedders that map graph structure onto qubit positions:

```python exec="on" source="above" html="true" session="programming"
from qoolqit import Register
from qoolqit.embedding import SpringLayoutEmbedder
from qoolqit.graphs import DataGraph

graph = DataGraph.random_er(n=5, p=0.3, seed=3)
embedded_graph = SpringLayoutEmbedder().embed(graph)
register = Register.from_graph(embedded_graph)
register.draw()
from qoolqit.visualization import fig_to_html; print(fig_to_html())  # markdown-exec: hide
```

!!! info "Go further"

    See [Registers](../fundamentals/quantum_program.md#registers) for all available register creation methods and options.

    See [Problem Embedding](../fundamentals/embedding.md) for embedding data and problems into the Rydberg analog model.

## 2. Waveforms and Drives

A **drive** is the time-dependent control applied to the system, built from one or more **waveforms**, for example amplitude $\tilde{\Omega}$ and detuning $\tilde{\delta}$ as functions of time $\tilde{t}$.

Waveform durations are dimensionless: $\tilde{t}$ measures duration relative to an interaction timescale. In an interacting many-body system, this gives $\tilde t$ a natural physical interpretation in terms of the buildup and propagation of correlations.

| Regime | Condition | Physical meaning |
|--------|-----------|------------------|
| Short time | $\tilde{t} \ll 1$ | Too short for interactions to strongly reshape the state |
| Long time | $\tilde{t} \sim n$ | Correlations may have propagated across a distance of order $n$ lattice spacings |

```python exec="on" source="above" html="true" session="programming"
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
from qoolqit.visualization import fig_to_html; print(fig_to_html())  # markdown-exec: hide
```

!!! info "Go further"

    See [Waveforms](../fundamentals/quantum_program.md#waveforms) for all waveform types and options.

    See [Drive Hamiltonian](../fundamentals/quantum_program.md#drives) for details on combining waveforms into drives.

## 3. QuantumProgram

A `QuantumProgram` pairs a **register** (layout and interactions) with a **drive** (time-dependent controls). The initial state is always $|0\rangle^{\otimes N}$, so every program describes how the drive and interactions evolve this fixed initial state.

```python exec="on" source="above" html="true" session="programming"
from qoolqit import QuantumProgram

program = QuantumProgram(register=register, drive=drive)
```

!!! info "Go further"

    See [Quantum Programs](../fundamentals/quantum_program.md#defining-a-quantum-program) for more details.

## 4. Compilation

Compilation translates your abstract program into something a given device (or emulator) can actually run, applying device-specific constraints such as maximum duration, amplitude and detuning bounds, discretization rules, and other hardware limits.

```python exec="on" source="above" html="true" session="programming"
from qoolqit import AnalogDevice

device = AnalogDevice()
program.compile_to(device, profile="max_energy")
```

!!! info "Go further"

    See [Compiling a Quantum Program](../fundamentals/compilation/rationale.md) for how compilation works.

    See [Devices](../fundamentals/compilation/device_and_compilation.md) for available devices and their specifications.

## 5. Execution

Once compiled, run the sequence and retrieve results. The three stages map cleanly onto three concepts:

- **Program**: what you *want* to run (abstract physics).
- **Sequence**: what you *will* run (device-compatible instructions).
- **Result**: what you *observed* (samples, probabilities, observables, etc.).

```python exec="on" source="above" html="true" session="programming"
from qoolqit.execution import LocalEmulator

emulator = LocalEmulator()
job = emulator.run(program)
results = job.results()
```

!!! info "Go further"

    See [Execution](../fundamentals/execution/execution.md) for running programs and handling job results:

    - [Local emulation](../fundamentals/execution/execution.md#local-emulator)
    - [Remote emulation](../fundamentals/execution/execution.md#remote-emulator)
    - [QPU execution](../fundamentals/execution/execution.md#executing-remotely-on-a-qpu)

## Example: Rydberg Blockade Demonstration

The **blockade regime** occurs when interactions prevent nearby atoms from being simultaneously excited. In the dimensionless framework this is straightforward to set up:

- Place two qubits at unit distance $\Rightarrow \tilde{J} = 1$.
- Blockade condition: $\tilde{\Omega} \ll 1$ (drive is weak compared to interactions).

We will compare two programs:

| Case | $\tilde{\Omega}$ | Regime | Expected behavior |
|------|-----------------|--------|--------------------|
| Blockade | $0.3$ | $\tilde{\Omega} \ll \tilde{J}$ | Double excitation $\vert 11\rangle$ suppressed |
| Non-blockade | $2.0$ | $\tilde{\Omega} \gg \tilde{J}$ | Qubits behave more independently; $\vert 11\rangle$ accessible |

```python exec="on" source="above" html="true" session="programming"
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

```python exec="on" source="above" html="true" session="programming"
# Build and compile programs
program_blockade = QuantumProgram(register, drive_blockade)
program_no_blockade = QuantumProgram(register, drive_no_blockade)

device = AnalogDevice()
program_blockade.compile_to(device, profile="max_energy")
program_no_blockade.compile_to(device, profile="max_energy")
```

```python exec="on" source="above" html="true" session="programming"
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

```python exec="on" source="above" html="true" session="programming"
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
from qoolqit.visualization import fig_to_html; print(fig_to_html())  # markdown-exec: hide
```

### What to expect

- **Blockade case** ($\tilde{\Omega} = 0.3$): the strong interaction heavily penalizes the $|11\rangle$ state. You should observe a suppressed probability of both qubits being excited simultaneously.
- **Non-blockade case** ($\tilde{\Omega} = 2.0$): the drive dominates and interactions are comparatively weak, so the two qubits behave more independently and $|11\rangle$ becomes much more accessible.

!!! info "Go further"

    See [Solving a Basic QUBO Problem](../tutorials/solving_a_qubo.md) for another application example.
