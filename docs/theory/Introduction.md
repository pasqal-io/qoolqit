# Introduction

## Why QoolQit?

Programming neutral-atom quantum computers requires specifying physical parameters: atom positions in micrometers, laser amplitudes in MHz, pulse durations in nanoseconds. These values depend heavily on the specific hardware—different devices have different Rydberg levels, laser power limits, and trap geometries.

**QoolQit solves this problem** by letting you write quantum programs in a **dimensionless framework**. Instead of working with device-specific physical units, you express your program in terms of ratios and relative scales. The same program can then be compiled to any compatible device.

!!! tip "Dimensionless reference frame"

    QoolQit introduces a **dimensionless reference frame** where:
    - Distances are measured relative to the closest atom pair (minimum distance = 1)
    - Energies are measured relative to the maximum interaction strength
    - Times are measured relative to the interaction timescale

    **Key benefits:**

    - Programs are hardware-independent until compilation
    - Drive strengths are naturally expressed as "multiples of interactions"
    - The same program can be compiled to different devices without modification

This means you can write the quantum evolution you want your system to follow (your QuantumProgram) and a compilation routine will automatically map your dimensionless program to physical values that fit the target device.

!!! definition "The Dimensionless Hamiltonian"

    At the heart of QoolQit is a dimensionless formulation of the Rydberg Hamiltonian. Your system evolves under:

    $$
    \tilde{H}(t) = \sum_{i<j} \tilde{J}_{ij} \hat{n}_i \hat{n}_j + \sum_i \frac{\tilde{\Omega}(t)}{2} \left( \cos\phi(t) \, \hat{\sigma}^x_i - \sin\phi(t) \, \hat{\sigma}^y_i \right) - \sum_i \left( \tilde{\delta}(t) + \epsilon_i \tilde{\Delta}(t) \right) \hat{n}_i
    $$

    where all quantities with tildes ($\tilde{\phantom{x}}$) are dimensionless.

**Interactions** ($\tilde{J}_{ij}$): Follow the $1/r^6$ Rydberg scaling, normalized so the maximum is 1:

$$
\tilde{J}_{ij} = \frac{1}{\tilde{r}_{ij}^6}, \qquad \max(\tilde{J}_{ij}) = 1
$$

**Drive amplitude** ($\tilde{\Omega}$): Expressed relative to the interaction scale:

- $\tilde{\Omega} \ll 1$: Interactions dominate
- $\tilde{\Omega} \sim 1$: Drive and interactions compete
- $\tilde{\Omega} \gg 1$: Drive dominates

**Time** ($\tilde{t}$): Measured in "interaction cycles":

- $\tilde{t} \ll 1$: Too fast for interactions to matter
- $\tilde{t} \gg 1$: Many interaction cycles

### Components Reference

| Symbol | Description | Range |
|--------|-------------|-------|
| $\tilde{J}_{ij}$ | Dimensionless coupling between qubits $i$ and $j$ | $(0, 1]$ |
| $\tilde{\Omega}(t)$ | Dimensionless Rabi frequency (drive amplitude) | $\geq 0$ |
| $\tilde{\delta}(t)$ | Dimensionless global detuning | any |
| $\tilde{\Delta}(t)$ | Dimensionless local detuning amplitude | $\leq 0$ |
| $\phi(t)$ | Drive phase | $[0, 2\pi)$ |
| $\epsilon_i$ | Local detuning weight for qubit $i$ | $[0, 1]$ |
| $\hat{n}_i$ | Rydberg occupation operator: $\frac{1}{2}(1 - \hat{\sigma}^z_i)$ | — |

## What's Next

- **[Overview](overview.md)**: Learn how to build programs with QoolQit—registers, waveforms, drives, and execution
- **[Advanced](advanced.md)**: Understand the connection to physical units and how compilation works
