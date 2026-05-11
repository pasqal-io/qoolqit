# Adimensionalization

In this section, you will learn how to:

- relate the physical Rydberg Hamiltonian to QoolQit’s dimensionless Hamiltonian,
- define the reference interaction $J_0$ and reference distance $r_0$,
- understand how compilation chooses the physical scale of an implementation,
- distinguish drive-limited and interaction-limited compilation,
- see why time must be rescaled together with the Hamiltonian

---

This section describes how QoolQit’s dimensionless formulation connects to real physical quantities, and how compilation maps an abstract programs onto actual hardware.

The [QoolQit Model](../get_started/qoolqit_model.ipynb) page introduces the main idea of compilation at a high level: the compiler translates a program, defined in dimensionless units, to the physical scale used to realize it on hardware. Here, we make that idea precise by defining a reference interaction, the corresponding reference distance, and the mapping between dimensionless and physical quantities.

---

## Physical Hamiltonian

In physical units, the Rydberg Hamiltonian is

$$
H(t) =
\underbrace{\sum_{i<j} \frac{C_6}{r_{ij}^{6}} \hat{n}_i \hat{n}_j}_{\text{interactions}}
+
\underbrace{\sum_i \frac{\Omega(t)}{2}\left(\cos\phi(t)\,\hat{\sigma}_i^x - \sin\phi(t)\,\hat{\sigma}_i^y\right)}_{\text{global drive}}
-
\underbrace{\sum_i \left(\delta(t) + \epsilon_i\Delta(t)\right)\hat{n}_i}_{\text{detuning}}.
$$

Here $\hat{n}=\frac{1}{2}\left(1+\hat{\sigma}^z\right)$ is the Rydberg occupation operator.

| Symbol | Description | Typical units |
|--------|-------------|---------------|
| $C_6(n)$ | Interaction coefficient for Rydberg level $n$ | $\mathrm{rad/s}\times\mu\mathrm{m}^6$ |
| $\Omega(t)$ | Global Rabi frequency (drive amplitude) | $\mathrm{rad/s}$ |
| $\delta(t)$ | Global detuning | $\mathrm{rad/s}$ |
| $\Delta(t)$ | Local detuning amplitude | $\mathrm{rad/s}$ |
| $\phi(t)$ | Drive phase | $[0,2\pi)$ |
| $\epsilon_i$ | Local detuning weight | $[0,1]$ |

---

## Reference energy and dimensionless Hamiltonian

Every neutral-atom device is characterized by a minimum allowed atom separation $r_{\min}$, set by hardware. This minimum spacing corresponds to the largest pairwise interaction the device can ever produce:

$$
J_{\text{max}} \;=\; \frac{C_6}{r_{\min}^{6}}.
$$

QoolQit takes this $J_{\text{max}}$ as the **reference energy scale** for adimensionalization, and the corresponding minimum spacing as the reference distance.

!!! note "Key point"
    Both $r_{\text{min}}$ and $J_{\text{max}}$ are **device constants**. They are fixed by the hardware specification and do not depend on the user's program. They are not chosen by compilation.

All Hamiltonian parameters are expressed relative to this fixed scale:

$$
\tilde{r}_{ij} = \frac{r_{ij}}{r_{\text{min}},
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

Dividing the physical Hamiltonian by $J_{\text{max}}$ yields the dimensionless QoolQit Hamiltonian:

$$
\tilde{H}(t) =
\sum_{i<j} \tilde{J}_{ij}\,\hat{n}_i \hat{n}_j
+
\sum_i \frac{\tilde{\Omega}(t)}{2}
\left(
\cos\phi(t)\,\hat{\sigma}^x_i - \sin\phi(t)\,\hat{\sigma}^y_i
\right)
-
\sum_i \left(\tilde{\delta}(t) + \epsilon_i\tilde{\Delta}(t)\right)\hat{n}_i.
$$

Since $J_0$ is the largest interaction the device can produce, every physically realizable register satisfies

$$
\min_{i<j}\tilde r_{ij} \geq 1,
\qquad\text{equivalently}\qquad
\max_{i<j}\tilde J_{ij} \leq 1,
$$

---

## From dimensionless programs to physical hardware

A QoolQit program is specified in terms of dimensionless quantities ($\tilde{J}_{ij}$, $\tilde{\Omega}(t)$, $\tilde{\delta}(t)$, $\tilde t$). Once the device, and therefore $J_{\text{max}}$ and $r_{\text{min}}$ — is fixed, the conversion to physical units is **completely determined**:

$$
\Omega(t) = J_{\text{max}}\,\tilde{\Omega}(t),
\qquad
\delta(t) = J_{\text{max}}\,\tilde{\delta}(t),
\qquad
\Delta(t) = J_{\text{max}}\,\tilde{\Delta}(t),
\qquad
r_{ij} = r_{\text{min}}\,\tilde r_{ij}.
$$

A given dimensionless program corresponds to one and only one set of physical parameters on a given device.

In the following step, QoolQit adjusts the **dimensionless program** so that the resulting physical parameters satisfy the device's operational constraints.

---

## Compilation

TThe user specifies a dimensionless program by providing a register (which determines the values $\tilde J_{ij}$) and a drive (which determines $\max_{\tilde t} \tilde \Omega(t)$, $\tilde\delta(t)$, etc.). Together these correspond to a point in the $(\tilde J, \tilde\Omega)$ plane — more precisely, to a value of the ratio

$$
\frac{\max_{\tilde t}\tilde\Omega}{\max_{i<j}\tilde J_{ij}},
$$

which defines a line through the origin in that plane.

In addition to the upper bound $\tilde J_{ij} \leq 1$ inherent to the adimensionalization, the device imposes a maximum drive amplitude $\tilde\Omega_{\text{max}} = \Omega_{\max}/J_{\text{max}}$. Together these define a **device allowed region** represented as a shaded green rectangle in the figure below:

![Compilation diagram](../extras/assets/compilation.svg)

If the user's point lies outside this region, the program cannot be implemented as specified. If it lies strictly inside, the program is feasible but does not exploit the full capability of the device. Compilation resolves both situations by sliding the program point along the line until it sits exactly on the boundary of the feasible region, maximizing $\tilde\Omega$.

Concretely, compilation multiplies all dimensionless parameters along the ray by a common factor $\alpha$:

$$
\tilde J_{ij}\;\to\;\alpha\,\tilde J_{ij},
\qquad
\tilde\Omega\;\to\;\alpha\,\tilde\Omega,
\qquad
\tilde\delta\;\to\;\alpha\,\tilde\delta,
$$

with $\alpha$ chosen as large as possible while keeping the program inside the feasible region. The ratio $\tilde\Omega/\tilde J$ is preserved by construction, so the dimensionless content of the program — the relative balance between drive and interactions — is unchanged.

### Drive-limited compilation

When the ratio $\tilde\Omega/\tilde J$ is large, the ray hits the line $\tilde\Omega = \tilde\Omega_{\max}$ before reaching $\tilde J = 1$. The compiled program saturates the drive maximum:

$$
\alpha \,\max_{\tilde t}\tilde\Omega \;=\; \tilde\Omega_{\max}
\qquad\Longrightarrow\qquad
\alpha \;=\; \frac{\tilde\Omega_{\max}}{\max_{\tilde t}\tilde\Omega}.
$$

Atoms are placed further apart than the device minimum: the closest pair sits at a dimensionless distance $\tilde r > 1$, equivalently at a physical distance $r > r_{\min}$.

### Interaction-limited compilation

When the ratio $\tilde\Omega/\tilde J$ is small, the ray hits $\tilde J = 1$ before reaching $\tilde\Omega_{\max}$. The compiled program saturates the interaction bound:

$$
\alpha \,\max_{i<j}\tilde J_{ij} \;=\; 1
\qquad\Longrightarrow\qquad
\alpha \;=\; \frac{1}{\max_{i<j}\tilde J_{ij}}.
$$

In this case, the closest pair of atoms is placed exactly at the device's minimum spacing $r_{\min}$, and the drive amplitude remains strictly below the device maximum.

!!! note
    Compilation succeeds whenever such an $\alpha$ exists. If multiple values of $\alpha$ would keep the program inside the feasible region, QoolQit chooses the largest one, in order to maximize the physical drive amplitude and minimize the physical runtime.

---

## Time scaling

The same rescaling argument that adjusts $\tilde\Omega$ and $\tilde J$ also forces a rescaling of dimensionless time. This follows directly from the Schrödinger equation.

In physical units,

$$
i\hbar \frac{d}{dt}|\psi(t)\rangle = H(t)|\psi(t)\rangle.
$$

Because $J_{\text{max}}$ is a fixed device constant, the change of variable $\tilde t = J_{\text{max}}t$ rewrites this exactly as

$$
i\frac{d}{d\tilde t}|\psi(\tilde t) \rangle = \tilde H(\tilde t)|\psi(\tilde t) \rangle,
$$

where $\tilde H = H/J_{\text{max}}$. The conversion $\tilde t = J_{\text{max}} t$ between physical and dimensionless time is therefore **fixed by the device**, exactly like $\tilde \Omega = \Omega/J_{\text{max}}$.

Now consider what happens during compilation. Compilation multiplies the dimensionless Hamiltonian by a factor $\alpha$:

$$
\tilde H(\tilde t)\;\longrightarrow\;\alpha\,\tilde H(\tilde t).
$$

For two programs along the same line to represent the **same physics**,i.e. to generate the same unitary evolution, the dimensionless time variable must be rescaled by the inverse factor:

$$
\tilde t\;\longrightarrow\;\tilde t/\alpha.
$$

Indeed, with this rescaling,

$$
\mathcal{T}\exp\left(-i\int_0^{\tilde t/\alpha}\alpha\,\tilde H(\tilde t')\,d\tilde t'\right)
=
\mathcal{T}\exp\left(-i\int_0^{\tilde t}\tilde H(s)\,ds\right),
$$

so the unitary generated by the rescaled program over a rescaled dimensionless duration is identical to the unitary generated by the original program.

---

## Compiling time back to physical units

Combining the fixed device conversion $t = \tilde t/J_{\text{max}}$ with the compilation rescaling $\tilde t \to \tilde t/\alpha$, a dimensionless duration $\tilde T$ specified by the user is realized physically in a time

$$
T \;=\; \frac{\tilde T/\alpha}{J_{\text{max}}} \;=\; \frac{\tilde T}{\alpha\,J_{\text{max}}}.
$$

A larger $\alpha$, that is a program with larger amplitude and interaction, yields a shorter physical runtime. This is consistent with the compilation strategy: by maximizing $\alpha$, QoolQit produces the fastest physical implementation compatible with the device constraints.

---

## Physical interpretation of dimensionless time

Let us definethe strongest interaction **present in the register** as
$$
\tilde J_{\text{max}} \;=\; \max_{i<j}\tilde J_{ij} \;\leq\; 1.
$$

In an interacting many-body system, the product $\tilde J_{\text{max}}\tilde t$ (and so the time $\tilde $) has a natural physical interpretation in terms of the buildup and propagation of correlations. Following the Lieb-Robinson picture, correlations spread at a finite speed set by the interaction scale. Roughly speaking:

- $\tilde \tilde t \ll 1/J_{\text{max}}$ corresponds to evolution that is too short for interactions to significantly affect the dynamics;
- $\tilde \tilde t \sim 1/J_{\text{max}}$ corresponds to the timescale on which nearest-neighbor correlations can begin to emerge;
- $\tilde \tilde t \sim n/J_{\text{max}}$ can be interpreted as the timescale on which correlations may have propagated across a distance of order $n$ lattice spacings, assuming approximately ballistic spreading.


---

## Special case: a single atom

The interpretation above relies on interactions being physically present. For a single atom, however, there are no pairwise interaction terms, so $J_0$ is no longer an intrinsic dynamical scale of the problem.

Mathematically, the dimensionless convention still works exactly as before: one may still define

$$
\tilde t = \frac{J_0}{\hbar}t
$$

and rewrite the Hamiltonian in dimensionless form. But in this case, $J_0$ is only a reference scale introduced by convention. It is not a scale that the dynamics can directly probe, because there is no interaction-driven process in the system.

As a result, saying that time is measured "in units of the interaction" remains mathematically valid, but it is not especially informative physically in the one-atom limit.

For a single atom, time should instead be interpreted through the local dynamics generated by the drive and detuning, namely through quantities such as $\tilde\Omega$ and $\tilde\delta$. For example, when detuning is absent, the natural timescale is the Rabi period set by the drive amplitude. In that regime, the relevant physical question is not how long it takes correlations to spread, but how long it takes the atom to undergo coherent single-particle evolution.

!!! note "Single-atom programs"
    For one-atom programs, the dimensionless formulation remains fully consistent and compilable, but the physical interpretation of time is different from the many-body case. Dimensionless time should be understood as a convenient normalized parameterization of the pulse sequence, rather than as an interaction-driven clock.
