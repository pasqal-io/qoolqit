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

## Introducing the reference interaction \(J_0\)

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

As discussed in [The QoolQit Model](../get_started/qoolqit_model.md), compilation preserves the same dimensionless program while changing the physical scale used to realize it on hardware.

The key point is that the user specifies **dimensionless ratios**, while the hardware imposes **physical bounds**. Compilation must therefore find a value of \(J_0\) such that the resulting physical parameters remain inside the device limits.

For example, if the target hardware imposes bounds such as

$$
\Omega(t) \le \Omega_{\max},
\qquad
\delta(t) \in [\delta_{\min},\delta_{\max}],
\qquad
\Delta(t) \in [\Delta_{\min},\Delta_{\max}],
$$

and if there is also a geometric constraint on the minimum physical spacing \(r_{ij}\), then only certain choices of \(J_0\) are valid.

Using \(\Omega = J_0 \tilde{\Omega}\), the drive bound becomes

$$
J_0\,\tilde{\Omega}(t) \le \Omega_{\max}.
$$

Similarly, since \(r_{ij}=r_0\tilde r_{ij}\) and \(r_0=(C_6/J_0)^{1/6}\), any lower bound on physical distances translates into an upper bound on \(J_0\).

Compilation therefore consists of finding a value of \(J_0\) that satisfies all such constraints simultaneously.

### Geometric interpretation

When describing the [QoolQit model](../get_started/qoolqit_model.md), we introduced a geometric picture of compilation in dimensionless units: fixing the ratio \(\tilde{\Omega}/\tilde{J}\) defines a line in the \((\tilde{J},\tilde{\Omega})\) plane, and compilation moves the program along that line until it reaches the allowed region.

The same idea can be translated into physical units. For a fixed dimensionless program, changing the reference scale \(J_0\) rescales both the physical interaction strength and the physical drive amplitude according to

$$
J = J_0 \tilde{J},
\qquad
\Omega = J_0 \tilde{\Omega}.
$$

As a result, all physical realizations of the same dimensionless program lie on a ray in the \((J,\Omega)\) plane. Each ray is therefore associated with a fixed value of the ratio \(\tilde{\Omega}/\tilde{J}\), while different points along the same ray correspond to different choices of the physical reference scale \(J_0\).

The figure below illustrates this picture. Each straight line corresponds to a different fixed ratio \(\tilde{\Omega}/\tilde{J}\), and therefore to a different dimensionless program. The shaded green region represents the set of parameters allowed by the device, bounded here by the maximum interaction strength \(J_{\max}\) and the maximum drive amplitude \(\Omega_{\max}\).

![Compilation diagram](../extras/assets/compilation.svg)

Compilation consists of selecting, along the ray defined by the program, a point that lies inside this allowed region. Among all such points, QoolQit chooses the largest valid one, corresponding to the largest reference scale \(J_0\) compatible with the hardware constraints. This choice is preferable because it realizes the same dimensionless program with the largest possible physical energy scale, and therefore with the shortest corresponding physical runtime.

### Drive-limited compilation

If the drive bound is reached before the interaction bound, then the largest valid implementation is obtained by saturating the drive limit:

$$
\Omega = \Omega_{\max}.
$$

Since \(\Omega = J_0 \tilde{\Omega}\), this fixes

$$
J_0 = \frac{\Omega_{\max}}{\tilde{\Omega}}.
$$

The corresponding reference distance is then

$$
r_0 = \left(\frac{C_6}{J_0}\right)^{1/6}.
$$

### Interaction-limited compilation

If the interaction bound is reached before the drive limit, then the largest valid implementation is obtained by saturating the interaction limit:

$$
J = J_{\max}.
$$

Since \(J = J_0 \tilde{J}\), this fixes

$$
J_0 = \frac{J_{\max}}{\tilde{J}}.
$$

Equivalently, this corresponds to choosing the smallest physical spacing allowed by the device for the relevant pair of atoms.

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
