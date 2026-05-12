# QoolQit model

In Rydberg neutral-atom systems, atoms interact through a combination of **distance-dependent interactions** and **laser-driven controls**. The interaction strength between two atoms decreases rapidly with their separation $r$ (as $1/r^6$), while the laser beams determine how strongly each atom is driven.

As a result, the behavior of the system is not set by absolute values alone, but by the **interplay between geometry (distances) and control strength (laser power)**. Different combinations of these quantities can lead to equivalent physical behavior, as long as their relative scales are preserved.

!!! info "Take-home message 1"
    QoolQit introduces a **dimensionless reference frame** where all quantities are expressed in function of an **interaction reference**.

The quantum system is thus described by the sum of two energetic contributions, the interaction and the driving one, as described by the following Hamiltonian:

$$
\tilde{H}(t) =
\underbrace{\sum_{i<j} \tilde{J}_{ij}\,\hat{n}_i \hat{n}_j}_{\text{interactions}}
+
\underbrace{\sum_i \frac{\tilde{\Omega}(t)}{2}
\left(
\cos\phi(t)\,\hat{\sigma}^x_i - \sin\phi(t)\,\hat{\sigma}^y_i
\right)}_{\text{global drive}}
-
\underbrace{\sum_i \left( \tilde{\delta}(t) + \epsilon_i\,\tilde{\Delta}(t) \right) \hat{n}_i}_{\text{detuning}}.
$$

Here, $\hat{n}_i = \frac{1}{2}(1 + \hat{\sigma}^z_i)$ is the Rydberg occupation operator of atom $i$, and the $\hat{\sigma}^{x,y,z}_i$ are the Pauli operators:

$$
\sigma^x=\begin{pmatrix} 0 & 1 \\ 1 & 0\end{pmatrix},
\qquad
\sigma^y=\begin{pmatrix} 0 & -i \\ i & 0\end{pmatrix},
\qquad
\sigma^z=\begin{pmatrix} 1 & 0 \\ 0 & -1\end{pmatrix}.
$$

- The interaction $\tilde{J}_{ij}$ follows the $1/r^6$ Rydberg scaling, normalized so that the maximum can at most be equal to $1$: $\tilde{J}_{ij} = \tilde{r}_{ij}^{-6}$ and $\max(\tilde{J}_{ij}) = 1$.
- $\tilde{\Omega}(t)$ and $\tilde{\delta}(t)$ are laser parameters (amplitude and detuning) and are measured relative to the maximum interaction strength, which is equal to $1$.
- Times $\tilde{t}$ are measured relative to the interaction timescale.

This means that programs are **hardware-independent until compilation**: drive strengths are naturally expressed as multiples of the interaction strength, and the same program can be compiled to different devices without modification.

!!! info "Take-home message 2"
    The actual physical scale, such as the precise distances or laser amplitudes, is determined later during the **compilation step**, when targeting a specific device.

More details about the connection to physical units are provided in the section [Adimensionalization](../extended_usage/adimensionalization.md).
The following table summarizes the parameters appearing in the Hamiltonian and their allowed ranges.

| Symbol | Description | Range |
|--------|-------------|-------|
| $\tilde{J}_{ij}$ | Dimensionless coupling between sites $i$ and $j$ | $[0,\,1]$ |
| $\tilde{\Omega}(t)$ | Global drive amplitude, affecting all sites equally | $\geq 0$ |
| $\tilde{\delta}(t)$ | Global detuning, affecting all sites equally | any real value |
| $\tilde{\Delta}(t)$ | Local detuning amplitude | $\leq 0$ |
| $\phi(t)$ | Global phase | $[0,\,2\pi]$ |
| $\epsilon_i$ | Local detuning weight for site $i$ | $[0,\,1]$ |
| $\tilde{t}$ | Dimensionless time | $> 0$ |

The introduced many-body Hamiltonian has rich dynamics, resulting from the interplay between the driving and interaction terms over time.
To help users understand how to define a concrete program, we briefly describe below the expected physical regimes for particular choices of driving strength (amplitude) and program duration. We will see that their values relative to the program's maximum interaction strength,

$$
\tilde J_{\text{max}} \;=\; \max_{i<j}\tilde J_{ij} \;\leq\; 1,
$$

is what matters.

## Drive regimes

Because $\tilde{\Omega}$ is expressed relative to the maximum interaction strength, strong and weak drive regimes are defined independently of the specific geometry:

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

Next we will discuss the compilation, the crucial step to translate a QoolQit dimensionless program to a sequence of operations that can be realized on a real neutral-atom-based QPU.

## Compilation

As described above, a QoolQit program is written in **dimensionless units**. This means that the user specifies the problem in terms of dimensionless quantities, independently of any particular device.

However, the values that can actually be implemented are constrained by the **hardware**. Real devices only allow certain ranges of interaction strengths, drive amplitudes, detunings, and evolution times. Therefore, an important task of QoolQit is to take the dimensionless program specified by the user and map it to a set of parameters that can be realized on the chosen hardware. We refer to this step as **compilation**.


!!! info
    Compilation is the step where QoolQit takes a dimensionless program and rescales it into hardware-realizable parameters, while preserving physical invariants.


A convenient way to understand this is to first work entirely in dimensionless units. As mentioned above, the key idea is that the program is defined by **ratios**, not by absolute scales. For example, fixing the ratio $\frac{\max_{\tilde{t}}\tilde{\Omega}}{\tilde{J}}$ defines a line in the $(\tilde{J},\tilde{\Omega})$ plane. Moving along this line changes the overall scale of the program, but preserves its dimensionless structure (here $\max_{\tilde{t}}$ stands for the maximum over time).

This means that compilation does **not** change the dimensionless physics of the program. Instead, it rescales the program so that it lies inside the region that can be implemented on a given device.


### Example

Consider the figure below:

![Compilation diagram](../extras/assets/compilation.svg)

The valid compilation region of a device is constrained by $\tilde{J} \leq 1, \;\tilde{\Omega} \leq 0.2,$. The bound $\tilde{J} \leq 1$ is compatible with a minimum spacing $a$ allowed in the register distance equal to $a_{\text{min}}=1$.

We define two programs by specifying the maximum adimensional amplitude in time $\max_{\tilde{t}}\tilde{\Omega}$ and the adimensional interaction between nearest neighbor atoms in the register $\tilde{J}=\frac{1}{\tilde{a^6}}$.  We define the following tuples:

1. $(\tilde{J},\max_{\tilde{t}}\tilde{\Omega}) = (1,0.4)$,
2. $(\tilde{J},\max_{\tilde{t}}\tilde{\Omega}) = (0.7,0.1)$


The lines correspond to the programs with fixed ratio $\tilde{\Omega}/\tilde{J}=2/5$ and $\tilde{\Omega}/\tilde{J}=1/7$.
At compilation Qoolqit checks the energy ratio and the valid region of compilation and maximizes the $\tilde{\Omega}$.

1. The point $(1,0.4)$ is outside the valid region, because the drive amplitude is too large. To compile the program, QoolQit rescales it while preserving the ratio $\max_{\tilde{t}}\tilde{\Omega}/\tilde{J} = 2/5$.
2. The point $(0.7,0.1)$ is inside, but the drive amplitude can be larger.QoolQit rescales it to the maximum possible $\tilde{\Omega}$ while preserving the ratio $\max_{\tilde{t}}\tilde{\Omega}/\tilde{J} = 1/7$.

The dimensionless content is unchanged: the ratio between drive and interaction is the same, and therefore the underlying dimensionless problem is the same.

### What changes under compilation?

What is preserved by compilation is the ratio $\max_{\tilde t}\tilde\Omega/\tilde J$ — that is, the relative balance between drive and interactions, which defines the line on which the program lives and encodes the physics of the problem.

What changes are the **dimensionless values themselves**: compilation slides the program along its line, multiplying $\tilde J$, $\tilde\Omega$, and $\tilde\delta$ by a common factor $\alpha$ chosen as large as possible while keeping the program inside the device's feasible region.

For instance, compiling the program $(\tilde J, \max_{\tilde t}\tilde\Omega) = (1, 0.4)$ to $(0.5, 0.2)$ corresponds to a rescaling factor $\alpha = 0.5$. The ratio $2/5$ is preserved, but the dimensionless interaction is halved, meaning the closest pair of atoms is placed further apart and the dimensionless drive is halved so that it saturates the device maximum.

Finally, compilation also rescales time: if the dimensionless Hamiltonian is multiplied by $\alpha$, dimensionless time must be divided by $\alpha$ in order to preserve the unitary evolution. A full derivation and concrete numerical examples are given in [Adimensionalization](../extended_usage/adimensionalization.md).
