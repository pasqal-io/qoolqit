# QoolQit Workflow Overview

This page explains how QoolQit can be used to build quantum programs by employing the dimensionless Hamiltonian framework described in [Programming a neutral atom QPU](../get_started/rydberg_model.md).

Let us recall that QoolQit uses a **dimensionless reference frame** where all quantities are expressed relative to a reference interaction strength. This makes programs device-agnostic at definition time and portable across hardware configurations:

- Programs remain hardware-independent until compilation.
- Drive strengths are naturally expressed as multiples of interactions.
- The same program compiles to different devices without modification.

---

## The QoolQit Hamiltonian

Your system evolves under the following Hamiltonian:

$$
\tilde{H}(t) = \underbrace{\sum_{i<j} \tilde{J}_{ij}\,\hat{n}_i \hat{n}_j}_{\text{interactions}}
+ \underbrace{\sum_i \frac{\tilde{\Omega}(t)}{2} \left( \cos\phi(t)\,\hat{\sigma}^x_i - \sin\phi(t)\,\hat{\sigma}^y_i \right)}_{\text{global drive}}
- \underbrace{\sum_i \left( \tilde{\delta}(t) + \epsilon_i\,\tilde{\Delta}(t) \right) \hat{n}_i}_{\text{detuning}}
$$

where $\hat{n} = \frac{1}{2}(1 + \hat{\sigma}^z)$ is the Rydberg occupation operator.

| Symbol | Description | Range |
|--------|-------------|-------|
| $\tilde{J}_{ij}$ | Dimensionless coupling between qubits $i$ and $j$ | $(0, 1]$ |
| $\tilde{\Omega}(t)$ | Global Rabi frequency (drive amplitude) | $\geq 0$ |
| $\tilde{\delta}(t)$ | Global detuning | any |
| $\tilde{\Delta}(t)$ | Local detuning amplitude | $\leq 0$ |
| $\phi(t)$ | Drive phase | $[0, 2\pi)$ |
| $\epsilon_i$ | Local detuning weight for qubit $i$ | $[0, 1]$ |

---

## Building Blocks of a Quantum Program

A QoolQit program is built from five core pieces:

1. **Register** — where qubits live (their geometry).
2. **Drive** — how you control the system over time (waveforms).
3. **QuantumProgram** — the pairing of *Register + Drive*.
4. **Compilation** — mapping the abstract program onto a specific device model.
5. **Execution** — running the compiled sequence and collecting results.

---

## 1. Register

A **register** defines the **positions** of qubits in your program. In neutral-atom / Rydberg analog models, geometry directly determines how strongly qubits interact.

```python
from qoolqit import Register

# Create a register from coordinates (dimensionless units)
register = Register.from_coordinates([
    (0, 0),
    (1, 0),
    (0.5, 0.866)
])

# Or use built-in patterns
from qoolqit import DataGraph

graph = DataGraph.square(m=2, n=2)
register = Register.from_graph(graph)  # 2x2 square lattice
```

!!! tip "Use unit spacing"
    The closest pair of qubits should be at distance **1**. This convention normalises interaction strengths and keeps drive parameters interpretable across different layouts.

For problem embedding, QoolQit also provides layout embedders:

```python
from qoolqit import SpringLayoutEmbedder, DataGraph, Register

graph = DataGraph.random_er(n=7, p=0.3, seed=3)
embedded_graph = SpringLayoutEmbedder().embed(graph)
register = Register.from_graph(embedded_graph)
```

> 📖 See [Programming a neutral atom QPU](registers.md). for all available register creation methods and options.
>
> 📖 See [Problem embedding](../fundamentals/problem_embedding.md) for embedding data and problems into the Rydberg analog model.

---

## 2. Waveforms and Drives

A **drive** is the time-dependent control applied to the system, built from one or more **waveforms** — for example, amplitude $\tilde{\Omega}$ and detuning $\tilde{\delta}$ as functions of time $\tilde{t}$.

### Waveforms

QoolQit supports several waveform types:

```python
from qoolqit.waveforms import Interpolated, Constant, Ramp
from qoolqit import Drive

# Interpolated waveform: smooth curve through specified values
omega_wf = Interpolated(duration=10, values=[0, 1, 0])

# Constant waveform
delta_wf = Constant(duration=10, value=-2)

# Ramp waveform
delta_wf = Ramp(duration=10, start=-2, stop=2)

# Combine into a Drive
drive = Drive(
    amplitude=omega_wf,
    detuning=delta_wf
)
```

Waveform durations are dimensionless: $\tilde{t}$ measures duration relative to an interaction timescale, telling you how many interaction cycles the system is allowed to undergo.

| Regime | Condition | Physical meaning |
|--------|-----------|-----------------|
| Short time | $\tilde{t} \ll 1$ | Too short for interactions to strongly reshape the state |
| Long time | $\tilde{t} \gg 1$ | Many interaction cycles; rich correlated dynamics can develop |

> 📖 See [Waveforms](waveforms.md) for all waveform types and options.
>
> 📖 See [Drive Hamiltonian](drives.md) for details on combining waveforms into drives.

---

## 3. QuantumProgram

A `QuantumProgram` pairs a **register** (layout and interactions) with a **drive** (time-dependent controls):

```python
from qoolqit import QuantumProgram

program = QuantumProgram(
    register=register,
    drive=drive
)
```

The initial state is always $|0\rangle^{\otimes N}$, so every program describes how the drive and interactions evolve this fixed initial state.

> 📖 See [Quantum programs](fundamentals/programs.md) for more details.

---

## 4. Compilation

Compilation translates your abstract program into something a given device (or emulator) can actually run, applying device-specific constraints such as maximum duration, amplitude and detuning bounds, discretization rules, and other hardware limits.

```python
from qoolqit import AnalogDevice

device = AnalogDevice()
program.compile_to(device)
```

### Optional: Time reference

You can also define a reference time at compilation with the `t_ref` parameter:

```python
sequence = program.compile(device, t_ref=kappa * device.max_duration)
```

When `t_ref` is set, waveform durations are interpreted as fractions of `t_ref` rather than absolute dimensionless units. For example, given three waveforms with durations 10, 10, and 20 and `t_ref=40`:

| Original duration | Interpreted as |
|-------------------|----------------|
| 10 | $0.25 \times t_{\text{ref}}$ |
| 10 | $0.25 \times t_{\text{ref}}$ |
| 20 | $0.50 \times t_{\text{ref}}$ |

This is useful when you want to define a waveform shape once, then scale it to match a device's time budget.

---

## 5. Execution

Once compiled, run the sequence and retrieve results:

```python
from qoolqit.execution import LocalEmulator

emulator = LocalEmulator()
results = emulator.run(program)
```

The three stages map cleanly onto three concepts:

- **Program** — what you *want* to run (abstract physics).
- **Sequence** — what you *will* run (device-compatible instructions).
- **Result** — what you *observed* (samples, probabilities, observables, etc.).

> 📖 See [Devices](../fundamentals/devices.md) for available devices and their specifications.
>
> 📖 See [Execution](fundamentals/execution.md) for running programs and handling different result types.
