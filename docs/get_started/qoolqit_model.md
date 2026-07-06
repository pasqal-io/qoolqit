# QoolQit model

On this page, you will learn about:

- The QoolQit dimensionless model for Rydberg neutral-atom systems
- Drive strength and time regimes in the dynamics
- The meaning of compilation

## Dimensionless Hamiltonian

In Rydberg neutral-atom systems, atoms interact through a combination of **distance-dependent interactions** and **laser-driven controls**, as described by the following dimensionless Hamiltonian:

$$
\tilde{H}(\tilde{t}) =
\underbrace{\sum_{i<j} \tilde{J}_{ij}\,\hat{n}_i \hat{n}_j}_{\text{interactions}}
+
\underbrace{\sum_i \frac{\tilde{\Omega}(\tilde{t})}{2}
\left(
\cos(\phi) \hat{\sigma}^x_i - \sin(\phi)\hat{\sigma}^y_i
\right)}_{\text{global drive}}
-
\underbrace{\sum_i \left( \tilde{\delta}(\tilde{t}) + \epsilon_i\,\tilde{\Delta}(\tilde{t}) \right) \hat{n}_i}_{\text{detuning}}.
$$

Here, $\hat{n}_i = \frac{1}{2}(1 + \hat{\sigma}^z_i)$ is the Rydberg occupation operator of atom $i$, and the $\hat{\sigma}^{x,y,z}_i$ are the Pauli operators:

$$
\sigma^x=\begin{pmatrix} 0 & 1 \\ 1 & 0\end{pmatrix},
\qquad
\sigma^y=\begin{pmatrix} 0 & -i \\ i & 0\end{pmatrix},
\qquad
\sigma^z=\begin{pmatrix} 1 & 0 \\ 0 & -1\end{pmatrix}.
$$

The following table summarizes the dimensionless parameters defining the Hamiltonian and their allowed ranges. Collectively, these parameters define a **quantum program**, which fully specifies the time-dependent Hamiltonian introduced above.

| Symbol | Description | Range |
|--------|-------------|-------|
| $\tilde{r}_{ij}$ | Distance between atom $i$ and $j$ | $\geq 1$ |
| $\tilde{J}_{ij}=1/\tilde{r}_{ij}^6$ | Distance-dependent coupling between sites $i$ and $j$. Sets how strongly excited atoms interact. | $[0,\,1]$ |
| $\tilde{\Omega}(\tilde{t})$ | Global time-dependent drive's amplitude. Sets how strongly the atoms are driven. | $\geq 0$ |
| $\tilde{\delta}(\tilde{t})$ | Global time-dependent drive's detuning | any real value |
| $\phi$ | Global drive's phase | $[0,\,2\pi]$ |
| $\tilde{\Delta}(\tilde{t})$ | Additional global time-dependent drive's detuning | $\leq 0$ |
| $\epsilon_i$ | Local detuning weight for site $i$ to locally modulate $\tilde{\Delta}$ | $[0,\,1]$ |
| $\tilde{t}$ | Dimensionless time | $> 0$ |

## Interaction reference

In QoolQit, the dimensionless Hamiltonian is obtained by rescaling the interaction and the drive terms such that, equivalently:

- The minimum pairwise distance between atoms is $1$:

$$\tilde{r}_{ij}\geq 1$$

- The maximum interaction energy (since $\tilde{J}_{ij}=1/\tilde{r}_{ij}^{6}$) is 1:

$$\tilde{J}_{ij}\leq 1$$

!!! info "Take-home message 1"
    QoolQit introduces a **dimensionless model** where all quantities are expressed relative to an **interaction reference**.

Such reference makes the program definition hardware independent and provides several advantages:

* **Removal of hardware-specific constants:** By defining a new unit of energy, all device-dependent constants are factored out.
* **Dimensionless parameters:** Expressing drive and interaction strengths as dimensionless quantities makes it easier to explore different physical regimes.
* **Portability:** Programs can be transferred across different devices and hardware generations with minimal modifications, improving reproducibility and reducing platform-specific code.
* **Hardware-agnostic algorithm development:** Developers can design algorithms that focus on the underlying physics and computational logic rather than hardware-specific implementation details.

To help users understand how to define a concrete program, we briefly describe below the expected physical regimes for particular choices of driving strength (amplitude) and program duration. We will see that their values relative to the program's maximum interaction strength is what matters.

## Drive regimes

Since the drive's amplitude $\tilde{\Omega}$ is expressed relative to the maximum interaction strength, strong and weak drive regimes are defined independently of the specific geometry:

| Regime | Condition | Intuition |
|--------|-----------|-----------|
| Strong drive | $\tilde{\Omega} \gg \tilde J_{\text{max}}$ | Controls dominate; interactions are a perturbation |
| Balanced | $\tilde{\Omega} \sim \tilde J_{\text{max}}$ | Controls and interactions compete |
| Weak drive | $\tilde{\Omega} \ll \tilde J_{\text{max}}$ | Interactions dominate; blockade and correlation effects are strong |

## Time regimes

In an interacting many-body system, time can be naturally measured relative to the timescale on which interactions generate correlations. Roughly speaking, a time $\tilde{t} \sim 1/\tilde J_{\text{max}}$ is enough for nearest-neighbor sites to begin developing correlations. More generally, $\tilde{t} \sim n/\tilde J_{\text{max}}$ can be interpreted as the timescale on which correlations may have propagated over a distance of order $n$ lattice spacings.

| Regime | Condition | Intuition |
|--------|-----------|-----------|
| Short time | $\tilde{t} \ll 1/\tilde J_{\text{max}}$ | Evolution is too brief for interactions to significantly build up correlations |
| Intermediate time | $\tilde{t} \sim 1/\tilde J_{\text{max}}$ | Interactions begin to visibly affect the dynamics; nearest-neighbor correlations can emerge |
| Long time | $\tilde{t} \gg 1/\tilde J_{\text{max}}$ | Correlations and many-body interaction effects have had time to spread across the system |

Since all physical regimes are characterized by parameters relative to the maximum interaction strength, QoolQit's choice of dimensionless units is natural: interactions are always of order unity, providing an intuitive reference scale for all other quantities.

## Derivation

This section describes how QoolQit’s dimensionless formulation connects to real physical quantities, precisely defining the reference interaction energy. In physical units, the Rydberg Hamiltonian reads:

$$
H(t) =
\underbrace{\sum_{i<j} \frac{C_6}{r_{ij}^{6}} \hat{n}_{i} \hat{n}_{j}}_{\text{interactions}}
+
\underbrace{\sum_i \frac{\Omega(t)}{2}\left(\cos(\phi)\,\hat{\sigma}_{i}^{x} - \sin(\phi)\,\hat{\sigma}_{i}^{y}\right)}_{\text{global drive}}
-
\underbrace{\sum_i \left(\delta(t) + \epsilon_i\Delta(t)\right)\hat{n}_{i}}_{\text{detuning}}.
$$

| Symbol | Description | units |
|--------|-------------|-------|
| $C_6(n)$ | Interaction coefficient for Rydberg level $n$. Also depends on the atomic species. | $\mathrm{rad/\mu s}\times\mu\mathrm{m}^6$ |
| $r_{ij}$ | Physical distance between atom $i$ and $j$ | $\mu\mathrm{m}$ |
| $\Omega(t)$, $\delta(t)$, $\Delta(t)$ | Physical drive parameters | $\mathrm{rad/\mu s}$ |

Every neutral-atom device is characterized by a minimum allowed atom separation $r_{\text{min}}^{d}$, determined by hardware constraints. This minimum spacing corresponds to the largest pairwise interaction the device can produce:

!!! info "Maximum interaction energy"

    $$
    J_{\text{max}}^{d} = \frac{C_6}{(r_{\text{min}}^{d})^{6}}.
    $$

    Both $r_{\text{min}}^{d}$ and $J_{\text{max}}^{d}$ are **device constants**. They are determined by the particular hardware on which the program is executed.

QoolQit takes this $J_{\text{max}}^{d}$ as the **reference energy scale** for adimensionalization, and the corresponding minimum spacing as the reference distance.


All Hamiltonian parameters are expressed relative to this fixed scale:

$$
\tilde{r}_{ij} = \frac{r_{ij}}{r_{\text{min}}},
\qquad
\tilde{J}_{ij} = \frac{1}{\tilde{r}_{ij}^6} = \frac{C_6/r_{ij}^6}{J_{\text{max}}},
$$

$$
\tilde{\Omega} = \frac{\Omega}{J_{\text{max}}},
\qquad
\tilde{\delta} = \frac{\delta}{J_{\text{max}}},
\qquad
\tilde{\Delta} = \frac{\Delta}{J_{\text{max}}}.
$$

Most programs are built starting from the definition of a set of coordinates for the atoms (register), or equivalently an interaction matrix. For this reason renormalization provides a natural constraint for program feasibility. Since, $J_{\text{max}}^{d}$ is the largest interaction the device can produce, every physically realizable register satisfies $\tilde r_{ij} \geq 1$ or equivalently $\tilde J_{ij} \leq 1$.

Next we will discuss the compilation, the crucial step to translate a QoolQit dimensionless program to a sequence of operations that can be realized on a real neutral-atom-based QPU.

## Compilation

As described above, a QoolQit program is expressed in dimensionless units, allowing users to define problems independently of any specific hardware platform.

In contrast, hardware specifications are given in physical units and and can only realize a limited range of parameter values. As a result, the dimensionless program parameters must be translated into physical interaction strengths, drive amplitudes, detunings, and evolution times that lie within the capabilities of the target device (if possible).
We refer to this step as **compilation**.

!!! info "Compilation"
    Compilation is the step where QoolQit takes a dimensionless program and rescales it into hardware-realizable parameters, while preserving physical invariants.

Practically, as anticipated in the previous section, a device choice will set the interaction energy reference.

!!! info "Take-home message 2"
    The actual physical scale $J_{\text{max}}^{d}$, such as the precise distances or laser amplitudes, is determined during the **compilation step**, when targeting a specific device.

### Example

As mentioned above, compilation does **not** change the physics of the program. Instead, it rescales the program so that it lies inside the region that can be implemented on a given device.

Consider the figure below:

![Compilation diagram](../extras/assets/compilation.svg)

The valid parameters region (green box) of a device is constrained by $\tilde{J} \leq 1, \;\tilde{\Omega} \leq 0.2$. The bound $\tilde{J} \leq 1$ is compatible with a minimum spacing $a$ allowed in the register distance equal to $a_{\text{min}}=1$.

The key idea is that the program is defined by **ratios**, not by absolute scales. For example, fixing the ratio $\frac{\max_{\tilde{t}}\tilde{\Omega}}{\tilde{J}}$ defines a line in the $(\tilde{J},\tilde{\Omega})$ plane. Moving along this line changes the overall scale of the program, but preserves its dimensionless structure (here $\max_{\tilde{t}}$ stands for the maximum over time).

We define two programs by specifying the maximum amplitude in time $\max_{\tilde{t}}\tilde{\Omega}$ and the interaction between nearest neighbor atoms in the register $\tilde{J}=\frac{1}{\tilde{a^6}}$. We define the following tuples:

1. $(\tilde{J},\max_{\tilde{t}}\tilde{\Omega}) = (1,0.4)$,
2. $(\tilde{J},\max_{\tilde{t}}\tilde{\Omega}) = (0.7,0.1)$

The lines correspond to the programs with fixed ratio $\tilde{\Omega}/\tilde{J}=2/5$ and $\tilde{\Omega}/\tilde{J}=1/7$.
At compilation QoolQit checks the energy ratio and the valid region of compilation and maximizes the $\tilde{\Omega}$.

1. The point $(1,0.4)$ is outside the valid region, because the drive amplitude is too large. To compile the program, QoolQit rescales it while preserving the ratio $\max_{\tilde{t}}\tilde{\Omega}/\tilde{J} = 2/5$.
2. The point $(0.7,0.1)$ is inside, but the drive amplitude can be larger. QoolQit rescales it to the maximum possible $\tilde{\Omega}$ while preserving the ratio $\max_{\tilde{t}}\tilde{\Omega}/\tilde{J} = 1/7$.

The dimensionless content is unchanged: the ratio between drive and interaction is the same, and therefore the underlying dimensionless problem is the same.

### What changes under compilation?

What is preserved by compilation is the ratio $\max_{\tilde t}\tilde\Omega/\tilde J$ — that is, the relative balance between drive and interactions, which defines the line on which the program lives and encodes the physics of the problem.

What changes are the **dimensionless values themselves**: compilation slides the program along its line, multiplying $\tilde J$, $\tilde\Omega$, and $\tilde\delta$ by a common factor $\alpha$ chosen as large as possible while keeping the program inside the device's feasible region.

For instance, compiling the program $(\tilde J, \max_{\tilde t}\tilde\Omega) = (1, 0.4)$ to $(0.5, 0.2)$ corresponds to a rescaling factor $\alpha = 0.5$. The ratio $2/5$ is preserved, but the dimensionless interaction is halved, meaning the closest pair of atoms is placed further apart and the dimensionless drive is halved so that it saturates the device maximum.

Finally, compilation also rescales time: if the dimensionless Hamiltonian is multiplied by $\alpha$, dimensionless time must be divided by $\alpha$ in order to preserve the unitary evolution. A full derivation and concrete numerical examples are given in [Adimensionalization and Compilation](../extended_usage/adimensionalization.md).
