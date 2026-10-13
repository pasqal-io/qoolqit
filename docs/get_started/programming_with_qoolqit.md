# Tutorial: Programming with QoolQit

This page explains how QoolQit can be used to build quantum programs by employing the dimensionless Hamiltonian framework described in [Programming a neutral atom QPU](qoolqit_model.md).

Programming with QoolQit is based on five core steps:

1. Defining a **Register** — where qubits live (their geometry).
2. Defining a **Drive** — how you control the system over time (waveforms).
3. Building a **QuantumProgram** — the pairing of *Register + Drive*.
4. **Compiling** the **QuantumProgram** — mapping the abstract program onto a specific device model.
5. **Executing** the compiled program— running the compiled sequence and collecting results.

---
### 1. Register

A **register** defines the **positions** of qubits in your program. In neutral-atom / Rydberg analog models, geometry directly determines how strongly qubits interact.

> **Tip — use unit spacing**: the closest pair of qubits should be at distance **1**. This convention normalises interaction strengths and keeps drive parameters interpretable across different layouts.

```python exec="on" source="above" html="1" session="programming"
from qoolqit import Register

# Create a register from coordinates (dimensionless units)
register = Register.from_coordinates([
    (0, 0),
    (1, 0),
    (0.5, 0.866)
])

# Or use built-in graph patterns
from qoolqit.graphs import DataGraph

graph = DataGraph.square(m=2, n=2)
register = Register.from_graph(graph)  # 2x2 square lattice
register.draw()
from qoolqit.visualization import fig_to_html; print(fig_to_html())  # markdown-exec: hide
```

For problem embedding, QoolQit also provides layout embedders that map graph structure onto qubit positions:

```python exec="on" source="above" html="1" session="programming"
from qoolqit import Register
from qoolqit.embedding import SpringLayoutEmbedder
from qoolqit.graphs import DataGraph

graph = DataGraph.random_er(n=5, p=0.3, seed=3)
embedded_graph = SpringLayoutEmbedder().embed(graph)
register = Register.from_graph(embedded_graph)
register.draw()
from qoolqit.visualization import fig_to_html; print(fig_to_html())  # markdown-exec: hide
```

> 📖 See [Registers](../fundamentals/quantum_program.ipynb#registers) for all available register creation methods and options.
>
> 📖 See [Problem Embedding](../fundamentals/embedding.ipynb) for embedding data and problems into the Rydberg analog model.

---
### 2. Waveforms and Drives

A **drive** is the time-dependent control applied to the system, built from one or more **waveforms** — for example, amplitude $\tilde{\Omega}$ and detuning $\tilde{\delta}$ as functions of time $\tilde{t}$.

Waveform durations are dimensionless: $\tilde{t}$ measures duration relative to an interaction timescale. In an interacting many-body system, this gives $\tilde t$ a natural physical interpretation in terms of the buildup and propagation of correlations.

| Regime | Condition | Physical meaning |
|--------|-----------|------------------|
| Short time | $\tilde{t} \ll 1$ | Too short for interactions to strongly reshape the state |
| Long time | $\tilde{t} \sim n$ | Correlations may have propagated across a distance of order $n$ lattice spacings |

```python exec="on" source="above" html="1" session="programming"
from qoolqit import Drive
from qoolqit.waveforms import ConstantWaveform, InterpolatedWaveform, RampWaveform

# Interpolated waveform: smooth curve through specified values
omega_wf = InterpolatedWaveform(duration=10, values=[0, 1, 0])

# Constant waveform
delta_wf = ConstantWaveform(duration=10, value=-2)

# Ramp waveform
delta_wf = RampWaveform(duration=10, initial_value=-2, final_value=2)

# Combine into a Drive
drive = Drive(
    amplitude=omega_wf,
    detuning=delta_wf
)

drive.draw()
from qoolqit.visualization import fig_to_html; print(fig_to_html())  # markdown-exec: hide
```

> 📖 See [Waveforms](../fundamentals/quantum_program.ipynb#waveforms) for all waveform types and options.
>
> 📖 See [Drive Hamiltonian](../fundamentals/quantum_program.ipynb#drives) for details on combining waveforms into drives.

---
### 3. QuantumProgram

A `QuantumProgram` pairs a **register** (layout and interactions) with a **drive** (time-dependent controls). The initial state is always $|0\rangle^{\otimes N}$, so every program describes how the drive and interactions evolve this fixed initial state.

```python exec="on" source="above" session="programming"
from qoolqit import QuantumProgram

program = QuantumProgram(
    register=register,
    drive=drive
)
```

> 📖 See [Quantum Programs](../fundamentals/quantum_program.ipynb#defining-a-quantum-program) for more details.

---
### 4. Compilation

Compilation translates your abstract program into something a given device (or emulator) can actually run, applying device-specific constraints such as maximum duration, amplitude and detuning bounds, discretization rules, and other hardware limits.

```python exec="on" source="above" session="programming"
from qoolqit import AnalogDevice

device = AnalogDevice()
program.compile_to(device, profile="max_energy")
```

---
### 5. Execution

Once compiled, run the sequence and retrieve results. The three stages map cleanly onto three concepts:

- **Program** — what you *want* to run (abstract physics).
- **Sequence** — what you *will* run (device-compatible instructions).
- **Result** — what you *observed* (samples, probabilities, observables, etc.).

```python exec="on" source="above" session="programming"
from qoolqit.execution import JobStatus, LocalEmulator

emulator = LocalEmulator()
job = emulator.run(program)
assert job.get_status() == JobStatus.DONE
results = job.results()
```

> 📖 See [Devices](../fundamentals/compilation/device_and_compilation.ipynb) for available devices and their specifications.
>
> 📖 See [Execution](../fundamentals/execution/execution.ipynb) for running programs and handling job results.

---
### Example: Rydberg Blockade Demonstration

The **blockade regime** occurs when interactions prevent nearby atoms from being simultaneously excited. In the dimensionless framework this is straightforward to set up:

- Place two qubits at unit distance $\Rightarrow \tilde{J} = 1$.
- Blockade condition: $\tilde{\Omega} \ll 1$ (drive is weak compared to interactions).

We will compare two programs:

| Case | $\tilde{\Omega}$ | Regime | Expected behaviour |
|------|-----------------|--------|--------------------|
| Blockade | $0.3$ | $\tilde{\Omega} \ll \tilde{J}$ | Double excitation $\|11\rangle $ suppressed |
| Non-blockade | $2.0$ | $\tilde{\Omega} \gg \tilde{J}$ | Qubits behave more independently; $\|11\rangle $ accessible |

```python exec="on" source="above" session="programming"
import numpy as np

from qoolqit import Drive, QuantumProgram, Register
from qoolqit.devices import AnalogDevice
from qoolqit.execution import BitStrings, EmulationConfig, LocalEmulator
from qoolqit.waveforms import ConstantWaveform

# Two qubits at unit distance => maximum interaction J = 1
register = Register.from_coordinates([(0, 0), (1, 0)])

duration = 10

# Blockade regime: Omega << J => double excitation is suppressed
drive_blockade = Drive(
    amplitude=ConstantWaveform(duration, 0.3),  # Omega = 0.3 << 1
    detuning=ConstantWaveform(duration, 0.0)
)

# Non-blockade regime: Omega >> J => drive dominates, both atoms can be excited
drive_no_blockade = Drive(
    amplitude=ConstantWaveform(duration, 2.0),  # Omega = 2.0 >> 1
    detuning=ConstantWaveform(duration, 0.0)
)
```

```python exec="on" source="above" session="programming"
# Build and compile programs
program_blockade = QuantumProgram(register, drive_blockade)
program_no_blockade = QuantumProgram(register, drive_no_blockade)

device = AnalogDevice()
program_blockade.compile_to(device, profile="max_energy")
program_no_blockade.compile_to(device, profile="max_energy")
```

```python exec="on" source="above" session="programming"
# Configure emulation: sample bitstrings at 81 evaluation times
eval_times = np.linspace(0.0, 1.0, 81)
bitstrings = BitStrings(evaluation_times=list(eval_times), num_shots=1000)
configuration = EmulationConfig(observables=[bitstrings])

emulator = LocalEmulator(emulation_config=configuration)

job_blockade = emulator.run(program_blockade)
assert job_blockade.get_status() == JobStatus.DONE
result_blockade = job_blockade.results()
job_no_blockade = emulator.run(program_no_blockade)
assert job_no_blockade.get_status() == JobStatus.DONE
result_no_blockade = job_no_blockade.results()
```

```python exec="on" source="above" html="1" session="programming"
import matplotlib.pyplot as plt

times=result_blockade.get_result_times(bitstrings)
occupation=[result_blockade.get_result(bitstrings.tag,time=t)["11"]/1000
             for k,t in enumerate(times)]
plt.plot(times,occupation,
         label="Blockade",
         color="navy")
times=result_no_blockade.get_result_times(bitstrings)
occupation=[result_no_blockade.get_result(bitstrings.tag,time=t)["11"]/1000
             for k,t in enumerate(times)]
plt.plot(times,occupation,
         label="No Blockade",
         color="crimson")
plt.xlabel(r"$t$",fontsize=22)
plt.ylabel(r"$P_{rr}$",fontsize=22)
plt.xticks(fontsize=18)
plt.yticks(fontsize=18)
plt.legend(fontsize=16)
from qoolqit.visualization import fig_to_html; print(fig_to_html())  # markdown-exec: hide
```

#### What to expect

- **Blockade case** ($\tilde{\Omega} = 0.3$): the strong interaction heavily penalises the $|11\rangle$ state. You should observe a suppressed probability of both qubits being excited simultaneously.
- **Non-blockade case** ($\tilde{\Omega} = 2.0$): the drive dominates and interactions are comparatively weak, so the two qubits behave more independently and $|11\rangle$ becomes much more accessible.

> 📖 See [Solving a Basic QUBO Problem](../tutorials/solving_a_qubo.ipynb) for another application example.
