In this page, you will learn:

- What the compilation step does and why it's important
- How dimensionless units work in QoolQit
- Compilation strategies: default and working point (in progress)
- Hardware modulation and noise


## Compiling a quantum program

QoolQit programs are written using dimensionless units, making them hardware-independent.
Qubit positions use dimensionless coordinates, waveforms have dimensionless amplitudes and detunings, and time is measured in units of a reference interaction energy called $J_{max}$.
This device-agnostic approach allows the same program to be compiled and executed on any compatible quantum hardware.

Compilation transforms these dimensionless quantities into concrete physical values and translates the QoolQit program into low-level instructions for real quantum processing units (QPUs). The compilation process:

1. Converts all dimensionless times, energies, and distances into their physical equivalents.
2. Rescales the program to satisfy device-specific hardware constraints.
3. Generates a Pulser `Sequence` containing the low-level instructions for QPU execution.

The conversion rules ensure that the dimensionless Hamiltonian $\tilde{H}(\tilde{t})$ and the physical Hamiltonian $H(t)$ produce identical unitary evolution.
For a complete mathematical derivation, see the [Adimensionalization and Compilation](../../extended_usage/adimensionalization.md) page. The essential conversion relationships are:

$$
r_{ij} = \left(\frac{C_6}{J_{max}}\right)^{1/6}	\tilde{r}_{ij},
\qquad
\Omega(t) = J_{max}\,	\tilde{\Omega}(	\tilde{t}),
\qquad
\delta(t) = J_0\,	\tilde{\delta}(	\tilde{t}),
\qquad
t = \frac{	\tilde{t}}{J_{max}}.
$$

Setting $J_{max}$ determines the physical amplitude scale, detuning scale, runtime, and atom spacings all at once.

The compilation output is stored internally as a Pulser `Sequence`, which contains the instructions for QPU execution.
Pulser is an open-source library that provides tools for designing and running pulse sequences on programmable neutral atom arrays.
For more details about Pulser's scope and capabilities, visit [Pasqal's documentation portal](https://docs.pasqal.com/pulser/).

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

The determining factor is which constraint becomes active first, based on comparing the dimensionless program ratio,

$$
\frac{\tilde{\Omega}_{\max}}{\tilde{J}_{\max}} = \tilde{\Omega}_{\max} \cdot \tilde{r}_{\min}^6,
$$

which characterizes the program, compared with the corresponding device ratio

$$
\frac{\Omega_{\max}}{J_{\max}} = \frac{\Omega_{\max} \cdot r_{\min}^6}{C_6}.
$$

The following figure illustrates both scenarios:

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



## Hardware effects

Real quantum hardware introduces deviations between the ideal compiled program and its actual execution. These effects can be categorized into two main classes: hardware modulation and noise sources.

Importantly, in both cases, these effects can be included by configuring emulators, as detailed in the [Execution](../execution/execution.ipynb) page of this documentation.

### Hardware modulation
**Hardware modulation** arises from the finite bandwidth limitations of optical channels, such as the lasers that drive qubits in neutral atom QPUs. When waveforms contain sharp features (like steps or rapid transitions) the hardware's bandwidth constraints will smooth out these abrupt changes during actual laser pulse execution. This smoothing can alter the intended pulse shape and timing, potentially affecting the quantum operation's fidelity.
The net effect on the drive is always visible when inspecting the compiled sequence in a program, as shown in [Devices and Compilation](./device_and_compilation.ipynb). Moreover, to account for hardware modulation during the emulation of a program, emulators must be configured with the flag `with_hardware_modulation=true`, as described in [Execution](../execution/execution.ipynb).


### Noise
**Noise sources** encompass various forms of environmental and systematic errors that introduce unwanted fluctuations or systematic shifts in the quantum system parameters during execution. As before, to include noise sources in the emulation of a program, emulators must be configured with the flag `noise_model`, as described in [Execution](../execution/execution.ipynb).

Finally, for more detailed information on [hardware modulation](https://docs.pasqal.com/pulser/tutorials/output_mod_eom/) and [noise sources](https://docs.pasqal.com/pulser/noise_model/), consult the comprehensive discussions available in the Pulser documentation.
