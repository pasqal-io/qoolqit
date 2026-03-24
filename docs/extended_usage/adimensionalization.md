# Adimensionalization

This section describes how QoolQit’s dimensionless formulation connects to real physical quantities, and how compilation maps an abstract programs onto actual hardware.

The [QoolQit Model](../get_started/qoolqit_model.md) page introduces the main idea of compilation at a high level: the compiler keeps the same dimensionless program while setting the reference physical scale used to realize it on hardware. Here, we make that idea precise by defining the reference interaction \(J_0\), the corresponding reference distance \(r_0\), and the mapping between dimensionless and physical quantities.

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

## Introducing the reference energy $J_0$

Because the interaction between Rydberg atoms depends on their separation, QoolQit introduces a reference distance \(r_0\) and the corresponding reference interaction in order to make programs device-agnostic.

$$
r_0 \;\text{(reference distance)},
\qquad
J_0 = \frac{C_6}{r_0^6} \;\text{(reference interaction)}.
$$

Concretely, \\(r_0\\) is the physical separation that corresponds to a dimensionless distance of \\(1\\): any pair of atoms that sit at distance \\(\tilde r_{ij}=1\\) in the adimensional model will be placed at distance \\(r_0\\) on the actual device. This value is not fixed in advance — it is determined by compilation — and, through the relation above, every choice of \\(r_0\\) implies a definite value of \\(J_0\\).

This quantity sets the energy scale for the program. All Hamiltonian parameters are then expressed relative to it:

$$
\tilde{r}_{ij} = \frac{r_{ij}}{r_0},
\qquad
\tilde{J}_{ij} = \frac{1}{\tilde{r}_{ij}^6} = \frac{C_6/r_{ij}^6}{J_0},
$$

$$
\tilde{\Omega} = \frac{\Omega}{J_0},
\qquad
\tilde{\delta} = \frac{\delta}{J_0},
\qquad
\tilde{\Delta} = \frac{\Delta}{J_0}.
$$

Dividing the physical Hamiltonian by \(J_0\) yields the dimensionless QoolQit Hamiltonian:

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

!!! note "Key convention"
    In QoolQit, the minimum dimensionless distance is fixed so that \(\min(\tilde r_{ij})=1\). Equivalently, the maximum dimensionless interaction is normalized to \(1\):
    $$
    \max(\tilde J_{ij}) = 1.
    $$

This is the convention used throughout the documentation: the user specifies a dimensionless program, and compilation later chooses which physical scale \(J_0\) will be used to realize it.

---

## From dimensionless programs to physical hardware

A QoolQit program is specified in terms of dimensionless quantities such as \(\tilde{J}_{ij}\), \(\tilde{\Omega}(t)\), \(\tilde{\delta}(t)\), and \(\tilde t\). These quantities describe the structure of the program independently of any particular device.

To run the program on actual hardware, one must choose a concrete value of \(J_0\). Once \(J_0\) is fixed, all dimensionless quantities are converted back into physical ones:

$$
\Omega(t) = J_0\,\tilde{\Omega}(t),
\qquad
\delta(t) = J_0\,\tilde{\delta}(t),
\qquad
\Delta(t) = J_0\,\tilde{\Delta}(t),
$$

and the physical distances are obtained from

$$
r_0 = \left(\frac{C_6}{J_0}\right)^{1/6},
\qquad
r_{ij} = r_0\,\tilde r_{ij}.
$$

So choosing a compilation is equivalent to choosing the physical reference scale \(J_0\), and therefore also the physical distance scale \(r_0\).

---

## Compilation

The geometric picture of compilation in dimensionless units — where fixing the ratio \(\tilde{\Omega}/\tilde{J}\) defines a ray in the \((\tilde{J},\tilde{\Omega})\) plane and compilation moves the program along that ray until it fits inside the allowed region — is introduced in [The QoolQit Model](../get_started/qoolqit_model.md). Here we translate that picture into physical units.

For a fixed dimensionless program, changing the reference scale \(J_0\) rescales all physical Hamiltonian parameters simultaneously:

$$
\Omega\,[\mathrm{rad/s}] = J_0\,\tilde{\Omega},
\qquad
\delta\,[\mathrm{rad/s}] = J_0\,\tilde{\delta},
\qquad
J_{ij}\,[\mathrm{rad/s}] = J_0\,\tilde{J}_{ij},
\qquad
r_{ij}\,[\mu\mathrm{m}] = r_0\,\tilde{r}_{ij},
$$

where \(r_0 = (C_6/J_0)^{1/6}\,\mu\mathrm{m}\). All physical realizations of the same dimensionless program therefore lie on a ray in the \((J,\Omega)\,[\mathrm{rad/s}]\) plane parameterized by \(J_0\).

The figure below illustrates this picture. Each straight line corresponds to a different fixed ratio \(\tilde{\Omega}/\tilde{J}\), and therefore to a different dimensionless program. The shaded green region represents the set of parameters allowed by the device, bounded by the maximum interaction strength \(J_{\max}\,[\mathrm{rad/s}]\) and the maximum drive amplitude \(\Omega_{\max}\,[\mathrm{rad/s}]\).

![Compilation diagram](../extras/assets/compilation.svg)

Compilation consists of selecting, along the ray defined by the program, the largest \(J_0\) whose corresponding physical parameters lie inside the allowed region. A larger \(J_0\) realizes the same dimensionless program with a higher physical amplitude and a shorter physical runtime \(t = \tilde{t}/J_0\,[\mathrm{s}]\), making it the most efficient choice.

Which hardware constraint becomes binding first determines the compilation strategy.

### Drive-limited compilation

When the drive amplitude bound \(\Omega_{\max}\,[\mathrm{rad/s}]\) is reached before the minimum-spacing constraint, the largest valid \(J_0\) is obtained by saturating the drive limit:

$$
\Omega_{\max}\,[\mathrm{rad/s}] = J_0\,\tilde{\Omega}_{\max}
\qquad\Longrightarrow\qquad
J_0\,[\mathrm{rad/s}] = \frac{\Omega_{\max}}{\tilde{\Omega}_{\max}}.
$$

The corresponding reference distance is then

$$
r_0\,[\mu\mathrm{m}] = \left(\frac{C_6\,[\mathrm{rad/s}\cdot\mu\mathrm{m}^6]}{J_0\,[\mathrm{rad/s}]}\right)^{1/6}.
$$

### Interaction-limited compilation

When the minimum atom spacing \(r_{\min}\,[\mu\mathrm{m}]\) is reached before the drive limit, the largest valid \(J_0\) is obtained by saturating the distance constraint. Since \(r_0 = (C_6/J_0)^{1/6}\) and the closest pair has dimensionless distance \(\tilde{r}_{\min} = 1\), setting \(r_0 = r_{\min}\) gives

$$
J_0\,[\mathrm{rad/s}] = \frac{C_6\,[\mathrm{rad/s}\cdot\mu\mathrm{m}^6]}{r_{\min}^6\,[\mu\mathrm{m}^6]}.
$$

This corresponds to placing the closest pair of atoms at the smallest physical spacing the device allows.

!!! note
    Compilation succeeds only if there exists at least one value of \(J_0\) that satisfies all hardware constraints. If multiple valid values exist, QoolQit selects the largest one so as to maximize the physical scale of the implementation.

---

## Time scaling

The [QoolQit Model](../get_started/qoolqit_model.md) page explains geometrically that if compilation changes the overall energy scale while preserving the same dimensionless Hamiltonian, then the physical runtime must change as well. Here we derive that statement explicitly.

Because QoolQit uses a dimensionless Hamiltonian defined relative to a reference energy scale \(J_0\), time must be rescaled by the same quantity. This follows directly from the Schrödinger equation.

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

Using

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

Assuming \(\hbar=1\), this is written simply as

$$
\tilde t = J_0 t.
$$

This shows that the dimensionless evolution depends only on \(\tilde H\) and \(\tilde t\). Therefore, if compilation changes the reference scale \(J_0\), the corresponding physical runtime must change accordingly in order to preserve the same dimensionless evolution.

---

## Compiling time back to physical units

Once compilation chooses a concrete value of \(J_0\), dimensionless times are mapped back to physical durations through

$$
t = \frac{\tilde t}{J_0}.
$$

This means that choosing a larger \(J_0\) produces a faster physical implementation of the same dimensionless program.

Equivalently, if compilation changes the reference scale from \(J_0\) to

$$
J_0' = \alpha J_0,
$$

then a fixed dimensionless duration \(\tilde T\) is realized physically in a time

$$
T' = \frac{\tilde T}{J_0'} = \frac{1}{\alpha}\frac{\tilde T}{J_0}.
$$

So reducing the energy scale by a factor \(\alpha\) increases the physical runtime by a factor \(1/\alpha\).

This is consistent with the compilation strategy described above: whenever possible, QoolQit selects the largest feasible \(J_0\) compatible with device constraints, so that programs run with the highest available amplitudes and shortest physical durations.

---

## Physical interpretation of dimensionless time

The meaning of \(\tilde t\) is tied to the fact that \(J_0\) is the interaction energy scale used to realize the program. Dimensionless time therefore measures how long the system evolves relative to its intrinsic interaction timescale.

In an interacting many-body system, this gives \(\tilde t\) a natural physical interpretation in terms of the buildup and propagation of correlations. Following the Lieb--Robinson picture, correlations spread at a finite speed set by the interaction scale. Roughly speaking:

- \(\tilde t \ll 1\) corresponds to evolution that is too short for interactions to significantly affect the dynamics;
- \(\tilde t \sim 1\) corresponds to the timescale on which nearest-neighbor correlations can begin to emerge;
- \(\tilde t \sim n\) can be interpreted as the timescale on which correlations may have propagated across a distance of order \(n\) lattice spacings, assuming approximately ballistic spreading.

This interpretation is useful because it is independent of the particular hardware realization: the same dimensionless time corresponds to the same interaction-relative evolution, even though the physical runtime after compilation may differ from one device to another.

---

## Special case: a single atom

The interpretation above relies on interactions being physically present. For a single atom, however, there are no pairwise interaction terms, so \(J_0\) is no longer an intrinsic dynamical scale of the problem.

Mathematically, the dimensionless convention still works exactly as before: one may still define

$$
\tilde t = \frac{J_0}{\hbar}t
$$

and rewrite the Hamiltonian in dimensionless form. But in this case, \(J_0\) is only a reference scale introduced by convention. It is not a scale that the dynamics can directly probe, because there is no interaction-driven process in the system.

As a result, saying that time is measured "in units of the interaction" remains mathematically valid, but it is not especially informative physically in the one-atom limit.

For a single atom, time should instead be interpreted through the local dynamics generated by the drive and detuning, namely through quantities such as \(\tilde\Omega\) and \(\tilde\delta\). For example, when detuning is absent, the natural timescale is the Rabi period set by the drive amplitude. In that regime, the relevant physical question is not how long it takes correlations to spread, but how long it takes the atom to undergo coherent single-particle evolution.

!!! note "Single-atom programs"
    For one-atom programs, the dimensionless formulation remains fully consistent and compilable, but the physical interpretation of time is different from the many-body case. Dimensionless time should be understood as a convenient normalized parameterization of the pulse sequence, rather than as an interaction-driven clock.
