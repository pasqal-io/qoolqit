# Introduction

QoolQit lets you write analog quantum programs for neutral-atom platforms in a **dimensionless framework**. Instead of working with physical units, you express your program in terms of ratios and relative scales — the same program can then be compiled to any compatible device.

This solves a key challenge in programming neutral-atom quantum computers: typically, you must specify physical parameters like atom positions in micrometers, laser amplitudes in MHz, and pulse durations in nanoseconds. These values depend heavily on the specific hardware — different devices have different Rydberg levels, laser power limits, and trap geometries.

QoolQit introduces a **dimensionless reference frame** with the following conventions:

- Distances are rescaled so that the smallest pairwise distance equals 1.
- $\tilde{\Omega}(t)$ and $\tilde{\delta}(t)$ are measured relative to the maximum interaction strength, which is equal to one in the dimensionless program.
- Times $\tilde{t}$ are measured relative to the interaction timescale.

This means programs are **hardware-independent until compilation**: drive strengths are naturally expressed as multiples of the interaction strength, and the same program can be compiled to different devices without modification.

Once a quantum program is written, a **compilation routine** automatically maps its dimensionless parameters to physical values compatible with the target hardware. For more details, see the Overview page.

---

## The QoolQit Dimensionless Hamiltonian

Your system evolves under the following Hamiltonian:

$$
\tilde{H}(t) = \underbrace{\sum_{i<j} \tilde{J}_{ij}\,\hat{n}_i \hat{n}_j}_{\text{interactions}} + \underbrace{\sum_i \frac{\tilde{\Omega}(t)}{2} \left( \cos\phi(t)\,\hat{\sigma}^x_i - \sin\phi(t)\,\hat{\sigma}^y_i \right)}_{\text{global drive}} - \underbrace{\sum_i \left( \tilde{\delta}(t) + \epsilon_i\,\tilde{\Delta}(t) \right) \hat{n}_i}_{\text{detuning}}
$$

where $\hat{n} = \frac{1}{2}(1 + \hat{\sigma}^z)$ is the Rydberg occupation operator, and the Pauli operators are:

$$
\sigma^x=\begin{pmatrix} 0 & 1\\ 1 & 0\end{pmatrix}, \qquad
\sigma^y=\begin{pmatrix} 0 & -i\\ i & 0\end{pmatrix}, \qquad
\sigma^z=\begin{pmatrix} 1 & 0\\ 0 & -1\end{pmatrix}
$$

### Parameters

| Symbol | Description | Range | Notes |
|--------|-------------|-------|-------|
| $\tilde{J}_{ij}$ | Dimensionless coupling between sites $i$ and $j$ | $(0,\,1]$ | Follows $1/r^6$ Rydberg scaling, normalized so the maximum equals 1: $\tilde{J}_{ij} = \tilde{r}_{ij}^{-6},\quad\max(\tilde{J}_{ij})=1$ |
| $\tilde{\Omega}(t)$ | Global drive amplitude, affecting all sites equally | $\geq 0$ | Expressed relative to the maximum interaction strength in the register (see [Adimensionalization](#)) |
| $\tilde{\delta}(t)$ | Global detuning, affecting all sites equally | any | |
| $\tilde{\Delta}(t)$ | Local detuning amplitude | $\leq 0$ | |
| $\phi(t)$ | Global phase | $[0,\,2\pi)$ | |
| $\epsilon_i$ | Local detuning weight for site $i$ | $[0,\,1]$ | |
| $\tilde{t}$ | Dimensionless time | $> 0$ | Measured relative to the interaction timescale: $\tilde{t}\ll 1$ is too short for interactions to matter; $\tilde{t}\gg 1$ is long enough for interactions to influence the dynamics |

### Drive regimes

Because $\tilde{\Omega}$ is expressed relative to the maximum interaction strength, strong vs. weak drive regimes are defined independently of the specific geometry:

| Regime | Condition | Intuition |
|--------|-----------|-----------|
| Strong drive | $\tilde{\Omega} \gg 1$ | Controls dominate; interactions are a perturbation |
| Balanced | $\tilde{\Omega} \sim 1$ | Controls and interactions compete |
| Weak drive | $\tilde{\Omega} \ll 1$ | Interactions dominate; blockade and correlation effects are strong |


### Time regimes

Time is expressed in QoolQit in units of the maximum interaction energy.

In an interacting many-body system, this gives $\tilde{t}$ a natural physical interpretation: it measures evolution time relative to the timescale on which interactions generate correlations. Roughly speaking, a time $\tilde{t}\sim 1$ is enough for nearest-neighbor sites to begin developing correlations. More generally, $\tilde{t}\sim n$ can be interpreted as the timescale on which correlations may have propagated over a distance of order $n$ lattice spacings.

This makes dimensionless time a convenient, geometry-independent way to describe how long the system evolves relative to its intrinsic interaction dynamics.

| Regime | Condition | Intuition |
|--------|-----------|-----------|
| Short time | $\tilde{t} \ll 1$ | Evolution is too brief for interactions to significantly build up correlations |
| Intermediate time | $\tilde{t} \sim 1$ | Interactions begin to visibly affect the dynamics; nearest-neighbor correlations can emerge |
| Long time | $\tilde{t} \gg 1$ | Correlations and many-body interaction effects have had time to spread across the system |

---

## What's Next

- [Fundamentals](../fundamentals/introduction.md) — Learn how to build programs with QoolQit: registers, waveforms, drives, and execution.
- [Adimensionalization — Advanced](../extended_usage/adimensionalization.md) — Understand the connection to physical units and how compilation works.
