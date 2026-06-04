In this page, you will learn:

- Meaning of the compilation step,
- Role of adimensional units in QoolQit,
- Compilation strategies: default and working point (in progress),
- Hardware effects,


## Compiling a quantum program

A QoolQit program is written in dimensionless units.
Qubit positions are expressed as dimensionless coordinates, waveforms carry dimensionless amplitudes and detunings, and time is measured in units of a reference interaction energy, that we call $J_{max}$.
This device-agnostic formulation means that the same program can be compiled and run on any compatible hardware.

Compilation is then the step that converts these dimensionless quantities into concrete physical values, and where a QoolQit program is translated into a lower-level code that can be executed on real QPU. Concretely, it:

1. Converts all dimensionless times, energies, and distances into their physical counterparts.
2. Rescale the program to met device's hardware constraints.
3. Builds a Pulser `Sequence`, i.e. a lower level of instructions to execute on the QPU.

The conversion rules are derived from the requirement that the dimensionless Hamiltonian
$\tilde{H}(\tilde{t})$ and the physical Hamiltonian $H(t)$ generate the same unitary evolution.
A full derivation is given in the [Adimensionalization and Compilation](../../extended_usage/adimensionalization.md)
page. The key identities are:

$$
r_{ij} = \left(\frac{C_6}{J_{max}}\right)^{1/6}	\tilde{r}_{ij},
\qquad
\Omega(t) = J_{max}\,	\tilde{\Omega}(	\tilde{t}),
\qquad
\delta(t) = J_0\,	\tilde{\delta}(	\tilde{t}),
\qquad
t = \frac{	\tilde{t}}{J_{max}}.
$$

Choosing $J_{max}$ therefore simultaneously sets the physical amplitude scale, the detuning scale,
the physical runtime, and the physical atom spacings.

Finally, the compilation will internally store the set of instructions needed for QPU execution as a Pulser `Sequence`.
Pulser is an open-source library that provides tools to design and run pulse sequences that act on programmable arrays of neutral atoms.
More information about the scope of the library are available at the [Pasqal's documentation portal](https://docs.pasqal.com/pulser/).

### Default compilation

A device imposes hardware constraints on the compiled program. The two most important ones for
compilation are:

- a **maximum drive amplitude** $\Omega_{\max}$, which defines $J_0$ through
  the relation $J_0 = \Omega / 	\tilde{\Omega} \le \Omega_{\max} / 	\tilde{\Omega}_{\max}$;
- a **minimum atom spacing** $r_{\min}$, which defines $J_0$ through the distance
  relation $r_{ij} = (C_6/J_0)^{1/6}	\tilde{r}_{ij} \ge r_{\min}$, i.e.
  $J_0 \le C_6 / (r_{\min}/	\tilde{r}_{\min})^6$.

QoolQit always picks the **largest $J_0$ consistent with these hardware constraints**, because a
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

These two example are shown in the following figure

![Compilation diagram](../../extras/assets/compilation_rationale.svg)

The users works by default at $\tilde{J}=1.0$. When the program's energy ratio exceeds the device's energy ratio, the drive amplitude bound is reached first (blue line). The largest valid $J_0$ is then obtained by **rescaling the amplitude limit** to the maximum allowed value (as denoted by the arrow).

In this regime the compiled program runs at **maximum device amplitude**, and the physical atom spacings are larger than the device minimum.

When the program's energy ratio is within the device budget, the minimum-spacing constraint is reached first (red line). The largest valid $J_0$ is obtained by **saturating the distance limit**.

In this regime the compiled register uses the smallest physical spacing the device allows, and the resulting amplitude is below $\Omega_{\max}$.

!!! note "QoolQit always maximizes the physical energy scale"
    In both cases, QoolQit selects the largest feasible reference scale $J_0$. Doing so
    gives the fastest possible physical runtime for the program, since $t = \tilde{t}/J_0$
    decreases as $J_0$ increases.


### Working point compilation
In progress...
