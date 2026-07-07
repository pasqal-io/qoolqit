# Programming a neutral-atom QPU

On this page, you will learn about:

- The QoolQit dimensionless model for Rydberg neutral-atom systems
- Drive strength and time regimes in the dynamics
- The meaning of compilation

## QoolQit dimensionless model

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

Here, $\hat{n}_i = \frac{1}{2}(1 + \hat{\sigma}^z_i)$ is the Rydberg occupation operator of atom $i$ (measuring how much of the Rydberg state is excited), and the $\hat{\sigma}^{x,y,z}_i$ are the Pauli operators:

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
| $\tilde{r}_{ij}$ | Distance between atom sites $i$ and $j$ | $\geq 1$ |
| $\tilde{J}_{ij}=1/\tilde{r}_{ij}^6$ | Distance-dependent coupling between atom sites $i$ and $j$. Sets how strongly excited atoms interact. | $[0,\,1]$ |
| $\tilde{\Omega}(\tilde{t})$ | Global time-dependent drive's amplitude. Sets how strongly the atoms are driven. | $\geq 0$ |
| $\tilde{\delta}(\tilde{t})$ | Global time-dependent drive's detuning | any real value |
| $\phi$ | Global drive's phase | $[0,\,2\pi]$ |
| $\tilde{\Delta}(\tilde{t})$ | Additional global time-dependent drive's detuning | $\leq 0$ |
| $\epsilon_i$ | Local detuning weight for atom $i$ to locally modulate $\tilde{\Delta}$ | $[0,\,1]$ |
| $\tilde{t}$ | Dimensionless time | $> 0$ |

### Interaction reference

In QoolQit, the dimensionless Hamiltonian is obtained from the physical Hamiltonian (see [Derivation](#derivation)) by rescaling the interaction and the drive terms such that, equivalently:

- The minimum pairwise distance between atoms is $1$:

$$\tilde{r}_{ij}\geq 1$$

- The maximum interaction energy (since $\tilde{J}_{ij}=1/\tilde{r}_{ij}^{6}$) is 1:

$$\tilde{J}_{ij}\leq 1$$

!!! info "QoolQit Model"
    QoolQit introduces a **dimensionless model** where all quantities are expressed relative to an **interaction reference**, such that $\tilde{r}_{ij}\geq 1$ and $\tilde{J}_{ij}\leq 1$.

Such reference makes the program definition hardware independent and provides several advantages:

* **Removal of hardware-specific constants:** By defining a new unit of energy, all device-dependent constants are factored out.
* **Dimensionless parameters:** Expressing drive and interaction strengths as dimensionless quantities makes it easier to explore different physical regimes.
* **Portability:** Programs can be transferred across different devices and hardware generations with minimal modifications, improving reproducibility and reducing platform-specific code.
* **Hardware-agnostic algorithm development:** Developers can design algorithms that focus on the underlying physics and computational logic rather than hardware-specific implementation details.

To help users understand how to define a program, we briefly describe below the expected physical regimes for particular choices of driving strength (amplitude) and program duration. We will see that their values relative to the program's maximum interaction strength is what matters. Thus QoolQit's choice of dimensionless units is natural: interactions are always of order unity, providing an intuitive reference scale for all other quantities.

### Drive regimes

Since the drive's amplitude $\tilde{\Omega}$ is expressed relative to the maximum interaction strength, strong and weak drive regimes are defined independently of the specific geometry:

| Regime | Condition | Intuition |
|--------|-----------|-----------|
| Strong drive | $\tilde{\Omega} \gg \tilde J_{\text{max}}$ | Controls dominate; interactions are a perturbation |
| Balanced | $\tilde{\Omega} \sim \tilde J_{\text{max}}$ | Controls and interactions compete |
| Weak drive | $\tilde{\Omega} \ll \tilde J_{\text{max}}$ | Interactions dominate; blockade and correlation effects are strong |

### Time regimes

In an interacting many-body system, time can be naturally measured relative to the timescale on which interactions generate correlations. Roughly speaking, a time $\tilde{t} \sim 1/\tilde J_{\text{max}}$ is enough for nearest-neighbor sites to begin developing correlations. More generally, $\tilde{t} \sim n/\tilde J_{\text{max}}$ can be interpreted as the timescale on which correlations may have propagated over a distance of order $n$ lattice spacings.

| Regime | Condition | Intuition |
|--------|-----------|-----------|
| Short time | $\tilde{t} \ll 1/\tilde J_{\text{max}}$ | Evolution is too brief for interactions to significantly build up correlations |
| Intermediate time | $\tilde{t} \sim 1/\tilde J_{\text{max}}$ | Interactions begin to visibly affect the dynamics; nearest-neighbor correlations can emerge |
| Long time | $\tilde{t} \gg 1/\tilde J_{\text{max}}$ | Correlations and many-body interaction effects have had time to spread across the system |

Next we will discuss the compilation, the crucial step to translate a QoolQit dimensionless program to a sequence of operations that can be realized on a real neutral-atom-based QPU.

## Compilation

A QoolQit program is expressed in dimensionless units, allowing users to define problems independently of any specific hardware platform.
In contrast, hardware specifications are given in physical units and and can only realize a limited range of parameter values.
Thus, before executing it on real hardware, a program must be compiled in two steps:

- **Dimensionalization**: Conversion of dimensionless parameters into physical units of energy, distances and times, to fall within the capabilities of the target device (if possible).

- **Translation**: Conversion into a lower-level representation that can directly instruct the target hardware (e.g., a [Pulser sequence](https://docs.pasqal.com/pulser/)).

We refer to this overall two-step process as **compilation**.

!!! info "Compilation in QoolQit"

    Translating a program to physical units and a set of hardware executable instructions.

Practically, as anticipated in the previous section, a device choice will set the interaction energy reference.

!!! note "Take-home message 2"
    The actual physical scale $J_{\text{max}}^{d}$, such as the precise distances or laser amplitudes, is determined during the **compilation step**, when targeting a specific device.


### Derivation

This section describes how QoolQit's dimensionless formulation connects to real physical quantities, precisely defining the reference interaction energy.
In physical units, the Rydberg Hamiltonian reads:

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
| $r_{ij}$ | Physical distance between atoms site $i$ and $j$. | $\mu\mathrm{m}$ |
| $\Omega(t)$, $\delta(t)$, $\Delta(t)$ | Physical drive parameters. | $\mathrm{rad/\mu s}$ |
| $t$ | Physical time. | $\mathrm{ns}$ |

Every neutral-atom device is characterized by a minimum allowed atom separation $r_{\text{min}}^{d}$, determined by hardware constraints. This minimum spacing corresponds to the largest pairwise interaction the device can produce:

!!! info "Maximum interaction energy"

    $$
    J_{\text{max}}^{d} = \frac{C_6}{(r_{\text{min}}^{d})^{6}}.
    $$

    Both $r_{\text{min}}^{d}$ and $J_{\text{max}}^{d}$ are **device constants**. They are determined by the particular hardware on which the program is executed.

QoolQit takes this $J_{\text{max}}^{d}$ as the **reference energy scale** for adimensionalization, and the corresponding minimum spacing as the reference distance.


All Hamiltonian parameters are expressed relative to this fixed scale:

$$
\tilde{r}_{ij} = \frac{r_{ij}}{r_{\text{min}}^{d}},
\qquad
\tilde{J}_{ij} = \frac{1}{\tilde{r}_{ij}^6} = \frac{C_6/r_{ij}^6}{J_{\text{max}}^{d}},
$$

$$
\tilde{\Omega} = \frac{\Omega}{J_{\text{max}}^{d}},
\qquad
\tilde{\delta} = \frac{\delta}{J_{\text{max}}^{d}},
\qquad
\tilde{\Delta} = \frac{\Delta}{J_{\text{max}}^{d}}.
$$

Most programs are built starting from the definition of a set of coordinates for the atoms (register), or equivalently an interaction matrix.
For this reason renormalization provides a natural constraint for program feasibility.
Since, $J_{\text{max}}^{d}$ is the largest interaction the device can produce, every physically realizable register satisfies $\tilde r_{ij} \geq 1$ or equivalently $\tilde J_{ij} \leq 1$.
