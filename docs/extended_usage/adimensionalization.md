# Adimensionalization

This section explains how QoolQit's dimensionless formulation relates to physical quantities, and how compilation maps abstract programs back to real hardware.

---

## Physical Hamiltonian

In physical units, the Rydberg Hamiltonian is:

$$
H(t) = \underbrace{\sum_{i<j} \frac{C_6}{r_{ij}^{6}} \hat{n}_i \hat{n}_j}_{\text{interactions}}
+ \underbrace{\sum_i \frac{\Omega(t)}{2}\left(\cos\phi(t)\,\hat{\sigma}_i^x - \sin\phi(t)\,\hat{\sigma}_i^y\right)}_{\text{global drive}}
- \underbrace{\sum_i \left(\delta(t) + \epsilon_i\Delta(t)\right)\hat{n}_i}_{\text{detuning}}
$$

where $\hat{n}=\frac{1}{2}\left(1+\hat{\sigma}^z\right)$ is the Rydberg occupation operator.

| Symbol | Description | Typical units |
|--------|-------------|---------------|
| $C_6(n)$ | Interaction coefficient (Rydberg level $n$) | $\text{rad/s} \times \mu\text{m}^6$ |
| $\Omega(t)$ | Global Rabi frequency (drive amplitude) | rad/s |
| $\delta(t)$ | Global detuning | rad/s |
| $\Delta(t)$ | Local detuning amplitude | rad/s |
| $\phi(t)$ | Drive phase | $[0, 2\pi)$ |
| $\epsilon_i$ | Local detuning weight | $[0, 1]$ |

---

## Introducing the Reference Interaction $J_0$

To make programs device-agnostic, QoolQit defines an arbitrary reference distance $r_0$ and a corresponding reference interaction:

$$
J_0 = \frac{C_6}{r_0^6}
$$

This $J_0$ sets the energy scale for the problem. All quantities are then expressed relative to it:

$$
\tilde{r}_{ij} = \frac{r_{ij}}{r_0}, \qquad \tilde{J}_{ij} = \frac{1}{\tilde{r}_{ij}^6}, \qquad \tilde{\Omega} = \frac{\Omega}{J_0}, \qquad \tilde{\delta} = \frac{\delta}{J_0}
$$

Dividing the full Hamiltonian by $J_0$ yields the dimensionless QoolQit Hamiltonian:

$$
\tilde{H}(t) = \sum_{i<j} \tilde{J}_{ij}\,\hat{n}_i \hat{n}_j
+ \sum_i \frac{\tilde{\Omega}(t)}{2}\left(\cos\phi(t)\,\hat{\sigma}^x_i - \sin\phi(t)\,\hat{\sigma}^y_i\right)
- \sum_i \left(\tilde{\delta}(t) + \epsilon_i\tilde{\Delta}(t)\right)\hat{n}_i
$$

!!! note "Key convention"
    In QoolQit, the minimum dimensionless distance is fixed such that $\min(\tilde{r}_{ij}) = 1$, which means the maximum interaction strength is also 1.

---

## Compilation

When you write a QoolQit program, you specify dimensionless ratios like $\tilde{\Omega}/\tilde{J}$. Compilation chooses a concrete value for $J_0$ that maps these ratios to physical values within a given device's capabilities.

The key insight is:

- A **program** defines a ratio $\tilde{\Omega}/\tilde{J}$, which corresponds to a line through the origin in $(\Omega, J)$ space.
- A **device** defines a box of allowed physical values: $[0,\,\Omega_{\max}] \times [0,\,J_{\max}]$.

All points on the program line that fall within the device box are valid compilations. Choosing $J_0$ is equivalent to selecting which point on that line to use. In practice, programs running at higher amplitude perform better on hardware, so QoolQit automatically selects the point that maximises amplitude while staying within device constraints.

![Compilation diagram](../extras/assets/compilation.svg)

### Case 1: Drive-limited compilation

When the program line hits the maximum amplitude $\Omega_{\max}$ before reaching $J_{\max}$, the compiler sets:

$$J_0 = \Omega_{\max}$$

and calculates the corresponding reference distance, which will fit within device specs.

### Case 2: Interaction-limited compilation

When the program line hits the maximum interaction $J_{\max}$ before reaching $\Omega_{\max}$, the compiler sets:

$$J_0 = J_{\max}$$

This is equivalent to placing the closest pair of atoms at the minimum allowed distance. The compiler then derives the corresponding $\Omega$ value.

!!! note
    This strategy guarantees that compiled programs fit within device specs (if compilation succeeds) and use the maximum amplitude possible for the user-defined program.

If compilation fails, the program simply cannot fit the device under any valid assignment of $J_0$.


## Time scaling

Because QoolQit uses a dimensionless Hamiltonian defined relative to a reference energy scale $J_0$, time must be rescaled by the same quantity. This follows directly from the Schrödinger equation.

In physical units, the dynamics are governed by

$$
i\hbar \frac{d}{dt}|\psi(t)\rangle = H(t)|\psi(t)\rangle.
$$

We want the physical and dimensionless descriptions to generate the same unitary evolution:

$$
U(t)\equiv \mathcal{T}\exp\left(-\frac{i}{\hbar}\int_0^t H(t')\,dt'\right)
=
\tilde U(\tilde t)\equiv \mathcal{T}\exp\left(-i\int_0^{\tilde t}\tilde H(\tilde t')\,d\tilde t'\right).
$$

Using the definition of the dimensionless Hamiltonian,

$$
H(t)=J_0\,\tilde H(\tilde t),
$$

this equivalence is possible only if the integration variables satisfy

$$
\frac{J_0}{\hbar}\,dt = d\tilde t,
\qquad\Longrightarrow\qquad
\tilde t = \frac{J_0}{\hbar}t.
$$

With this choice, the Schrödinger equation becomes

$$
i\frac{d}{d\tilde t}|\psi(\tilde t)\rangle = \tilde H(\tilde t)|\psi(\tilde t)\rangle.
$$

Assuming $\hbar=1$, so this is written simply as

$$
\tilde t = J_0 t.
$$

---

## Physical interpretation of dimensionless time

The meaning of $\tilde t$ is tied to the fact that $J_0$ is the interaction energy at the working point. Dimensionless time therefore measures how long the system evolves relative to its intrinsic interaction timescale.

In an interacting many-body system, this gives $\tilde t$ a natural physical interpretation in terms of the buildup and propagation of correlations. Following the Lieb--Robinson picture, correlations spread at a finite speed set by the interaction scale. Roughly speaking:

- $\tilde t \ll 1$ corresponds to evolution that is too short for interactions to significantly affect the dynamics,
- $\tilde t \sim 1$ corresponds to the timescale on which nearest-neighbor correlations can begin to emerge,
- $\tilde t \sim n$ can be interpreted as the timescale on which correlations may have propagated across a distance of order $n$ lattice spacings, assuming approximately ballistic spreading.

This interpretation is particularly useful because it is independent of the specific hardware realization: the same dimensionless time corresponds to the same interaction-relative evolution, even though the physical runtime after compilation may differ from one device to another.

---

## Compiling time back to physical units

Once compilation chooses a concrete value of $J_0$, dimensionless times are mapped back to physical durations through

$$
t = \frac{\tilde t}{J_0}.
$$

This means that choosing a larger $J_0$ produces a faster physical implementation of the same dimensionless program. This is consistent with the compilation strategy described above: whenever possible, QoolQit selects the largest feasible scale compatible with device constraints, so that programs run with the highest available amplitudes and shortest physical durations.

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