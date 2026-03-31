# Compiling a quantum program

In this page, you will learn how to:

- understand what compilation does in QoolQit,
- understand the two compilation strategies: drive-limited and interaction-limited,
- understand why QoolQit always uses the maximum available amplitude $\Omega_{\max}$ whenever possible,
- inspect the compiled Pulser `Sequence` that results from compilation.

---

## What compilation does

A QoolQit program is written entirely in dimensionless units: qubit positions are expressed as
dimensionless coordinates, waveforms carry dimensionless amplitudes and detunings, and time is
measured in units of a reference interaction energy $J_0$. This device-agnostic formulation
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
\Omega(t) = J_0\,	\tilde{\Omega}(	\tilde{t}),
\qquad
\delta(t) = J_0\,	\tilde{\delta}(	\tilde{t}),
\qquad
t = \frac{	\tilde{t}}{J_0},
\qquad
r_{ij} = \left(\frac{C_6}{J_0}\right)^{1/6}	\tilde{r}_{ij}.
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

In this regime the compiled program runs at **full device amplitude** $\Omega = \Omega_{\max}$,
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

---

## Compilation in practice

Compilation is triggered by calling `compile_to` on a `QuantumProgram`:

```python exec="on" source="material-block" result="json" session="compilation"
from qoolqit import Drive, Ramp, Constant, Register, QuantumProgram, AnalogDevice

# Define a simple register and drive
register = Register.from_coordinates([(0, 0), (0, 1), (1, 0)])

T = 20.0
omega = 1.0
wf_amp = Constant(T, omega)
wf_det = Ramp(T, -2.0, 2.0)
drive = Drive(amplitude=wf_amp, detuning=wf_det)

program = QuantumProgram(register, drive)
print(program)  # markdown-exec: hide
```

Before compilation the program has no associated device:

```python exec="on" source="material-block" result="json" session="compilation"
program.is_compiled
print(program.is_compiled)  # markdown-exec: hide
```

Compiling to a `Device` triggers the strategy selection described above (here we employ the `AnalogDevice`):

```python exec="on" source="material-block" result="json" session="compilation"
device = AnalogDevice()
program.compile_to(device)
print(program)  # markdown-exec: hide
```

The compiled Pulser `Sequence` can then be inspected directly:

```python exec="on" source="material-block" html="1" session="compilation"
pulser_sequence = program.compiled_sequence
```

And both the original dimensionless program and its compiled counterpart can be drawn
side by side for a visual check:

```python exec="on" source="material-block" html="1" session="compilation"
import matplotlib.pyplot as plt  # markdown-exec: hide
from docs.utils import fig_to_html  # markdown-exec: hide
program.draw()
fig_original = program.draw(return_fig=True)  # markdown-exec: hide
print(fig_to_html(fig_original))  # markdown-exec: hide
```

```python exec="on" source="material-block" html="1" session="compilation"
program.draw(compiled=True)
fig_compiled = program.draw(compiled=True, return_fig=True)  # markdown-exec: hide
print(fig_to_html(fig_compiled))  # markdown-exec: hide
```

---

## Validation

After selecting $J_0$ and computing the physical parameters, the compiler validates that the
compiled program satisfies **all** device constraints:

| Drive amplitude bounds |
| Drive detuning bounds |
| Sequence duration|
| Minimum atom spacing |
| Maximum radial distance |

If any constraint is violated, a `CompilationError` is raised with a descriptive message
indicating which bound was exceeded and the device specifications that must be satisfied.

!!! note "MockDevice"
    `MockDevice` has no hardware constraints, so compilation always succeeds and uses the
    default unit converter (energy unit $= 4\pi$). It is designed for rapid prototyping
    without worrying about physical bounds.
