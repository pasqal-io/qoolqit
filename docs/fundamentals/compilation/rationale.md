# Compiling a quantum program

## What compilation does

A QoolQit program is written entirely in dimensionless units: qubit positions are expressed as
dimensionless coordinates, waveforms carry dimensionless amplitudes and detunings, and time is
measured in units of a reference interaction energy, that we call $J_0$. This device-agnostic formulation
means that the same program can be compiled and run on any compatible hardware.

Compilation is the step that converts these dimensionless quantities into concrete physical values
that a real Pulser device can execute. Concretely, it:

1. Selects a physical reference scale $J_0$ that is consistent with the device's hardware constraints.
2. Converts all dimensionless times, energies, and distances into their physical counterparts.
3. Builds and returns a Pulser `Sequence` ready for emulation or execution on a QPU.

The conversion rules are derived from the requirement that the dimensionless Hamiltonian
$\tilde{H}(\tilde{t})$ and the physical Hamiltonian $H(t)$ generate the same unitary evolution.
A full derivation is given in the [Adimensionalization](../../extended_usage/adimensionalization.md)
page. The key identities are:

$$
r_{ij} = \left(\frac{C_6}{J_0}\right)^{1/6}	\tilde{r}_{ij},
\qqad
\Omega(t) = J_0\,	\tilde{\Omega}(	\tilde{t}),
\qquad
\delta(t) = J_0\,	\tilde{\delta}(	\tilde{t}),
\qquad
t = \frac{	\tilde{t}}{J_0}.
$$

Choosing $J_0$ therefore simultaneously sets the physical amplitude scale, the detuning scale,
the physical runtime, and the physical atom spacings.

---

## The two compilation strategies

A device imposes hardware constraints on the compiled program. The two most important ones for
compilation are:

- a **maximum drive amplitude** $\Omega_{\max}$, which defines $J_0$ through
  the relation $J_0 = \Omega / 	\tilde{\Omega} \le \Omega_{\max} / 	\tilde{\Omega}_{\max}$;
- a **minimum atom spacing** $r_{\min}$, which defines $J_0$ through the distance
  relation $r_{ij} = (C_6/J_0)^{1/6}	\tilde{r}_{ij} \ge r_{\min}$, i.e.
  $J_0 \le C_6 / (r_{\min}/	\tilde{r}_{\min})^6$.

QoolQit always picks the **largest $J_0$ consistent with all hardware constraints**, because a
larger reference scale realizes the same dimensionless program with a higher physical amplitude and a
shorter physical runtime — the most efficient use of the hardware.

Which constraint becomes binding first depends on the dimensionless ratio

$$
\frac{\tilde{\Omega}_{\max}}{\tilde{J}_{\max}} = \tilde{\Omega}_{\max} \cdot \tilde{r}_{\min}^6
$$

which characterizes the program, compared with the corresponding device ratio

$$
\frac{\Omega_{\max}}{J_{\max}} = \frac{\Omega_{\max} \cdot r_{\min}^6}{C_6}.
$$

### Compilation at maximum amplitude

When the program's energy ratio exceeds the device's energy ratio,

$$
	\tilde{\Omega}_{\max} \cdot \tilde{r}_{\min}^6 > \frac{\Omega_{\max} \cdot r_{\min}^6}{C_6},
$$

the drive amplitude bound is reached first. The largest valid $J_0$ is then obtained by
**saturating the amplitude limit**:

$$
\Omega_{\max} = J_0\,	ilde{\Omega}_{\max}
\qquad\Longrightarrow\qquad
J_0 = \frac{\Omega_{\max}}{	ilde{\Omega}_{\max}}.
$$

In this regime the compiled program runs at **maximum device amplitude** $\Omega = \Omega_{\max}$,
and the physical atom spacings are larger than the device minimum.

### Compilation at minimum spacing

When the program's energy ratio is within the device budget,

$$
	\tilde{\Omega}_{\max} \cdot \tilde{r}_{\min}^6 \le \frac{\Omega_{\max} \cdot r_{\min}^6}{C_6},
$$

the minimum-spacing constraint is reached first. The largest valid $J_0$ is obtained by
**saturating the distance limit**:

$$
r_{\min} = \left(\frac{C_6}{J_0}
\right)^{1/6}	\tilde{r}_{\min}
\qquad\Longrightarrow\qquad
J_0 = \frac{C_6}{(r_{\min}/	\tilde{r}_{\min})^6}.
$$

In this regime the compiled register uses the smallest physical spacing the device allows, and the
resulting amplitude $\Omega = J_0\,	\tilde{\Omega}_{\max}$ is below $\Omega_{\max}$.

!!! note "QoolQit always maximizes the physical energy scale"
    In both cases, QoolQit selects the largest feasible reference scale $J_0$. When the drive
    bound is the binding constraint, this means the compilation always produces a pulse that
    **saturates $\Omega_{\max}$** — the maximum amplitude available on the device. Doing so
    gives the fastest possible physical runtime for the program, since $t = \tilde{t}/J_0$
    decreases as $J_0$ increases.
