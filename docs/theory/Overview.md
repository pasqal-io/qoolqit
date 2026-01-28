## Overview

This page explains how QoolQit represents quantum programs using a dimensionless Hamiltonian framework built on Rydberg atom physics.

QoolQit uses a **dimensionless reference frame** where all quantities are expressed relative to a reference interaction strength. This makes your programs device-agnostic at definition time and portable across different hardware configurations.

**Key benefits:**

- Programs are hardware-independent until compilation
- Drive strengths are naturally expressed as "multiples of interactions"
- The same program can be compiled to different devices without modification

## The QoolQit Hamiltonian

Your system evolves under the following Hamiltonian:

$$
\tilde{H}(t) = \underbrace{\sum_{i<j} \tilde{J}_{ij}  \hat{n}_i \hat{n}_j}_{\text{interactions}} + \underbrace{\sum_i \frac{\tilde{\Omega}(t)}{2} \left( \cos\phi(t) \, \hat{\sigma}^x_i - \sin\phi(t) \hat{\sigma}^y_i \right)}_{\text{global drive}} - \underbrace{\sum_i \left( \tilde{\delta}(t) + \epsilon_i  \tilde{\Delta}(t) \right) \hat{n}_i}_{\text{detuning}}
$$

where $\hat{n} = \frac{1}{2}(1 - \hat{\sigma}^z)$ is the Rydberg occupation operator.

### Components

| Symbol | Description | Range |
|--------|-------------|-------|
| $\tilde{J}_{ij}$ | Dimensionless coupling between qubits $i$ and $j$ | $(0, 1]$ |
| $\tilde{\Omega}(t)$ | Global Rabi frequency (drive amplitude) | $\geq 0$ |
| $\tilde{\delta}(t)$ | Global detuning | any |
| $\tilde{\Delta}(t)$ | Local detuning amplitude | $\leq 0$ |
| $\phi(t)$ | Drive phase | $[0, 2\pi)$ |
| $\epsilon_i$ | Local detuning weight for qubit $i$ | $[0, 1]$ |

## Register

A register defines the qubit positions in your program. QoolQit provides several ways to create registers.

```python
from qoolqit import Register

# Create a register from coordinates (dimensionless units)
register = Register.from_coordinates([
    (0, 0),
    (1, 0),
    (0.5, 0.866)
])

# Or use built-in patterns
register = Register.square(2)      # 2x2 square lattice
register = Register.triangular(3)  # triangular lattice
```

**Convention:** Use unit spacing—the closest pair of qubits should be at distance 1.

> 📖 Check [Registers](registers.md) for all available register creation methods and options.

> 📖 Check [Problem embedding](available_embedder.md) for embedding data and problems into the Rydberg analog model.

Qubit interactions follow the positions of the atoms according to the Rydberg $1/\tilde{r}^6$ scaling:

$$
\tilde{J}_{ij} = \frac{1}{\tilde{r}_{ij}^6}
$$

where $\tilde{r}_{ij}$ is the dimensionless distance between qubits $i$ and $j$.

## Waveforms and Drives

Drives are time-dependent waveforms that control the system evolution. QoolQit supports several waveform types.

```python
from qoolqit.waveforms import InterpolatedWaveform, ConstantWaveform, RampWaveform
from qoolqit import Drive

# Interpolated waveform: smooth curve through specified values
omega_wf = InterpolatedWaveform(duration=10, values=[0, 1, 0])

# Constant waveform
delta_wf = ConstantWaveform(duration=10, value=-2)

# Ramp waveform
delta_wf = RampWaveform(duration=10, start=-2, stop=2)

# Combine into a Drive
drive = Drive(
    amplitude=omega_wf,
    detuning=delta_wf
)
```

> 📖 See [Waveforms](waveforms.md) for all waveform types and options.

> 📖 See [Drive Hamiltonian](drives.md) for details on combining waveforms into drives.

The dimensionless drive $\tilde{\Omega}$ is expressed relative to the maximum interaction $\max{\tilde{J}_{ij}}$:

| Regime | Condition | Physical Meaning |
|--------|-----------|------------------|
| Strong drive | $\tilde{\Omega} \gg 1$ | Drive dominates interactions |
| Balanced | $\tilde{\Omega} \sim 1$ | Comparable energy scales |
| Weak drive | $\tilde{\Omega} \ll 1$ | Interactions dominate |

## Building a Program

A complete QoolQit program combines register and drive specifications.

```python
from qoolqit import Program

program = Program(
    register=register,
    drive=drive
)
```

The initial state of the system is always $|0\rangle^{\otimes N}$.

> 📖 See [Quantum Programs](programs.md) for more details.

## Compilation and Execution

To run on hardware or emulators, QoolQit compiles your abstract program to device-specific parameters.

```python
from qoolqit.devices import MockDevice, AnalogDevice

# Use MockDevice for ideal simulations
device = MockDevice()

# Or AnalogDevice for realistic hardware constraints
device = AnalogDevice()

# Compile and run
sequence = program.compile(device)
result = sequence.run()
```

> 📖 See [Devices](devices.md) for available devices and their specifications.
> 📖 See [Execution](execution.md) for running programs and handling results.

## Time Handling

Time in QoolQit is also dimensionless. The dimensionless time $\tilde{t}$ measures duration relative to the interaction timescale.

The value of $\tilde{t}$ tells you how many "interaction cycles" your program runs:

| Regime | Condition | Physical Meaning |
|--------|-----------|------------------|
| Short time | $\tilde{t} \ll 1$ | Evolution time is short compared to interaction timescale; interactions have little effect |
| Long time | $\tilde{t} \gg 1$ | Many interaction cycles; dynamics fully explore the interacting Hilbert space |

For adiabatic algorithms, you typically need $\tilde{t} \gg 1$ to allow the system to follow the ground state.

With specific applications in mind, a user can optionally define a reference time at compilation stage.

```python
# Durations are interpreted as fractions of t_ref
sequence = program.compile(device, t_ref=kappa * device.max_duration)
```

### Example

Suppose you define three waveforms with dimensionless durations:

```python
from qoolqit.waveforms import InterpolatedWaveform

wf1 = InterpolatedWaveform(10, [0, omega, 0])
wf2 = InterpolatedWaveform(10, [0, omega, 0])
wf3 = InterpolatedWaveform(20, [0, omega, 0])
```

With `compile(device)`, these durations are used directly.

With `compile(device, t_ref=40)`, the durations are interpreted as fractions of `t_ref`:

| Original duration | Interpreted as |
|-------------------|----------------|
| 10 | 0.25 × t_ref |
| 10 | 0.25 × t_ref |
| 20 | 0.50 × t_ref |

This allows you to define programs in relative terms and scale them, e.g., to the device's maximum duration at compile time.

## Example: Rydberg Blockade Demonstration

In the dimensionless framework, the blockade regime is controlled by the drive amplitude $\tilde{\Omega}$ relative to the interaction strength. With qubits at unit distance ($\tilde{J} = 1$), the blockade condition is $\tilde{\Omega} \ll 1$.

```python
from qoolqit import Register, Drive, Program
from qoolqit.waveforms import InterpolatedWaveform
from qoolqit.devices import MockDevice

# Two qubits at unit distance (maximum interaction J = 1)
register = Register.from_coordinates([(0, 0), (1, 0)])

duration = 10

# Blockade regime: Omega << J, drive is weak compared to interaction
# Double excitation is suppressed
drive_blockade = Drive(
    amplitude=InterpolatedWaveform(duration, [0, 0.3, 0.3, 0]),  # Omega = 0.3 << 1
    detuning=InterpolatedWaveform(duration, [0, 0, 0, 0])
)

# Non-blockade regime: Omega >> J, drive dominates interaction
# Both atoms can be excited independently
drive_no_blockade = Drive(
    amplitude=InterpolatedWaveform(duration, [0, 3.0, 3.0, 0]),  # Omega = 3.0 >> 1
    detuning=InterpolatedWaveform(duration, [0, 0, 0, 0])
)

# Create and run programs
program_blockade = Program(register, drive_blockade)
program_no_blockade = Program(register, drive_no_blockade)

device = MockDevice()
result_blockade = program_blockade.compile(device).run()
result_no_blockade = program_no_blockade.compile(device).run()
```

> 📖 See [Solving a Basic QUBO Problem](../tutorials/basic_qubo.md) for a complete application example.

---

## Advanced: From Physical Units to QoolQit

This section explains how QoolQit's dimensionless formulation relates to physical quantities and how compilation maps abstract programs back to real hardware.

### The Physical Hamiltonian

In physical units, the Rydberg Hamiltonian is:

$$
H = \sum_{i<j} \frac{C_6}{r_{ij}^6} \hat{n}_i \hat{n}_j + \frac{\Omega(t)}{2} \sum_i \hat{\sigma}^x_i - \delta(t) \sum_i \hat{n}_i
$$

where:

- $C_6$ is a device-dependent coefficient (set by the Rydberg level)
- $r_{ij}$ is the physical distance between atoms (in µm)
- $\Omega(t)$ is the Rabi frequency (in rad/µs or MHz)
- $\delta(t)$ is the detuning (in rad/µs or MHz)

### Introducing the Reference Interaction $J_0$

To make programs device-agnostic, we define an arbitrary **reference distance** $r_0$ and a corresponding **reference interaction**:

$$
J_0 = \frac{C_6}{r_0^6}
$$

This $J_0$ sets the energy scale for the problem. We then express all quantities relative to it:

$$
\tilde{r}_{ij} = \frac{r_{ij}}{r_0}, \qquad \tilde{J}_{ij} = \frac{1}{\tilde{r}_{ij}^6}, \qquad \tilde{\Omega} = \frac{\Omega}{J_0}, \qquad \tilde{\delta} = \frac{\delta}{J_0}
$$

Dividing the full Hamiltonian by $J_0$ gives the **dimensionless QoolQit Hamiltonian**:

$$
\tilde{H} = \frac{H}{J_0} = \sum_{i<j} \tilde{J}_{ij} \hat{n}_i \hat{n}_j + \frac{\tilde{\Omega}(t)}{2} \sum_i \hat{\sigma}^x_i - \tilde{\delta}(t) \sum_i \hat{n}_i
$$

**Key convention:** In QoolQit, the minimum dimensionless distance is $\min(\tilde{r}_{ij}) = 1$, which means the maximum interaction is $\max(\tilde{J}_{ij}) = 1$.

### What Compilation Does

When you write a QoolQit program, you specify dimensionless ratios like $\tilde{\Omega}/\tilde{J}$. Compilation chooses a concrete value for $J_0$ that maps these ratios to physical values within the device's capabilities.

The key insight is:

- A **program** defines a ratio $\tilde{\Omega}/\tilde{J}$, which corresponds to a **line** through the origin in $(\Omega, J)$ space
- A **device** defines a box of allowed physical values: $[0, \Omega_{\max}] \times [0, J_{\max}]$

![Compilation strategy](./compilation.png)

All points on the program line that fall within the device box are valid compilations. Choosing $J_0$ is equivalent to selecting which point on the line to use.

In practice, **programs with higher amplitude perform better on hardware**, so QoolQit automatically selects the point that maximizes amplitude while staying within device constraints.

### Case 1: Drive-limited compilation

When the user chooses $\tilde{\Omega}/\tilde{J} = 1$ (blue line in the plot):

The program line hits the maximum amplitude $\Omega_{\max}$ before reaching $J_{\max}$. The compiler sets:

$$J_0 = \Omega_{\max}$$

and calculates the corresponding reference distance, which will fit within device specs.

### Case 2: Interaction-limited compilation

When the user chooses $\tilde{\Omega}/\tilde{J} = 0.05$ (green line in the plot):

The program line hits the maximum interaction $J_{\max}$ before reaching $\Omega_{\max}$. The compiler sets:

$$J_0 = J_{\max}$$

This is equivalent to placing the closest pair of atoms at the minimum allowed distance. The compiler then calculates the corresponding $\Omega$ value.

!!! note "Previous behavior"
    In earlier versions of QoolQit, setting $J_0 = \Omega_{\max}$ for low-$\Omega$ programs would fail because atoms ended up below the minimum distance. The current strategy automatically handles this case.

This approach guarantees that compiled programs:

- **Fit within device specs** (if compilation succeeds)
- **Use the maximum amplitude possible** for the user-defined program

If compilation fails, the program simply cannot fit the device under any valid assignment of $J_0$.

!!! tip "Future extensions"
    - QoolQit can suggest **approximations** of incompatible programs that would compile
    - A "force compilation" strategy may be added in future versions
