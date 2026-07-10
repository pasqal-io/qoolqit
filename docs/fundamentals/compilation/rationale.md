Before reading this page, we suggest starting with the [Get Started: Programming a Neutral Atom QPU](../../get_started/qoolqit_model.md) guide, which introduces the QoolQit dimensionless model and provides a first insight into compilation.

In this page, you will learn about:

- Compilation profiles: default and working point
- Hardware modulation and noise emulation


## Compiling a quantum program

QoolQit programs are written in dimensionless units, allowing the same program to be compiled and executed on any compatible quantum hardware.

As a reminder, the compilation process:

- Converts all dimensionless program's parameters, times, energies, and distances into their physical equivalents.
- Generates a Pulser `Sequence` containing the low-level instructions for QPU execution.

The conversion rules ensure that the dimensionless Hamiltonian $\tilde{H}(\tilde{t})$ and the physical Hamiltonian $H(t)$ produce identical unitary evolution.
For a complete mathematical derivation, see the [Get Started: Programming a Neutral Atom QPU](../../get_started/qoolqit_model.md#derivation) page.

The essential conversion relationships are:

$$
r_{ij} = \left(\frac{C_6}{J_{max}^{d}}\right)^{1/6}	\tilde{r}_{ij},
\qquad
\Omega(t) = J_{max}^{d}\tilde{\Omega}(\tilde{t}),
\qquad
\delta(t) = J_{max}^{d}\tilde{\delta}(\tilde{t}),
\qquad
t = \tilde{t}/J_{max}^{d}.
$$

Compiling a QoolQit program to a particular device, will set the conversion factor, $J_{max}^{d}=C_6/(r_{\text{min}}^{d})^6$, for amplitude, detuning, runtime, and atom spacings scales all at once.
It is important to remind that such constant **depends on the particular hardware** of choice, being $C_6$ an interaction coefficient that depends on the specific Rydberg level of a specific atomic species used in the QPU, while $r_{\text{min}}^{d}$ is the minimum pairwise distance that can be realized.

Finally, when a program is compiled, the compilation output is stored internally as a Pulser `Sequence`, which contains the instructions for QPU execution.
Pulser is an open-source library that provides tools for designing and running pulse sequences on programmable neutral atom arrays.
For more details about Pulser's scope and capabilities, visit [Pulser documentation](https://docs.pasqal.com/pulser/).

## Compilation profiles
Besides dimensionalization, every rescaling $\left(t, H\right) \rightarrow \left(t/\alpha, \alpha H\right)$ will produce in theory a physically equivalent program.
At the moment, QoolQit provides a single simple compilation strategy, which seeks maximizing the energy scale of the input program.

### Maximum energy (default)
A device imposes hardware constraints and limits the range of parameters in a program.
The two most important ones for compilation are the maximum drive amplitude $\Omega_{\max}^{d}$ and the minimum atom spacing $r_{\min}^{d}$.

The maximum energy strategy always picks the **largest energy scale** that satisfies these hardware constraints, which guarantees the most efficient use of the hardware.
Indeed, a larger reference scale realizes the same dimensionless program with a higher drive's amplitude (higher signal to noise ratio), a shorter physical runtime (less noise) and shorter distances between atoms (more compact registers can fit more atoms/qubits).

The following figure illustrates two key scenarios:

![Compilation diagram](../../extras/assets/compilation.svg)

The green box highlights the valid parameter region for the interaction energy $\tilde{J}_{ij}$ and the driving amplitude $\tilde{\Omega}$.
As described in the [QoolQit model](../../get_started/qoolqit_model.md) page, the interaction energy is bounded by 1 by construction: QoolQit's adimensionalization enforces $\tilde{J}_{ij} = J_{ij}/J_{max}^{d} \leq 1$ across all devices.
The driving amplitude (more precisely, its maximum over time) is instead constrained to a device-dependent upper bound. In this example, we take $\Omega_{max}^{d}/J_{max}^{d} = 0.2$, so that $\tilde{\Omega} = \Omega/J_{max}^{d} \lesssim 0.2$.

The key idea is that the program is defined by **ratios**, not by absolute scales. For example, fixing the ratio $\frac{\max_{\tilde{t}}\tilde{\Omega}}{\tilde{J}}$ defines a line in the $(\tilde{J},\tilde{\Omega})$ plane.
Moving along this line changes the overall scale of the program, but preserves its dimensionless structure (here $\max_{\tilde{t}}$ stands for the maximum over time).

We define two programs by specifying the maximum amplitude in time $\max_{\tilde{t}}\tilde{\Omega}$ and the interaction between nearest neighbor atoms in the register $\tilde{J}=\frac{1}{\tilde{a^6}}$. We define the following tuples:

1. $(\tilde{J},\max_{\tilde{t}}\tilde{\Omega}) = (1,0.4)$,
2. $(\tilde{J},\max_{\tilde{t}}\tilde{\Omega}) = (0.7,0.1)$

The lines correspond to the programs with fixed ratio $\tilde{\Omega}/\tilde{J}=2/5$ and $\tilde{\Omega}/\tilde{J}=1/7$.
At compilation, QoolQit checks the energy ratio against the device's valid region and rescales the program to maximize $\tilde{\Omega}$ within that region.

1. The point $(1,0.4)$ is outside the valid region, because the drive amplitude is too large. To compile the program, QoolQit rescales it while preserving the ratio $\max_{\tilde{t}}\tilde{\Omega}/\tilde{J} = 2/5$.
    In this regime the compiled program runs at **maximum device amplitude**, and the physical atom spacings are larger than the device minimum.

2. The point $(0.7,0.1)$ is inside, but the drive amplitude can be larger. QoolQit rescales it to the maximum possible $\tilde{\Omega}$ while preserving the ratio $\max_{\tilde{t}}\tilde{\Omega}/\tilde{J} = 1/7$.
    In this regime the compiled register uses the smallest physical spacing the device allows, and the resulting amplitude is below $\Omega_{\max}$.


The dimensionless content is unchanged: the ratio between drive and interaction is the same, and therefore the underlying dimensionless problem is the same.

### Working point
The working point does not apply any rescaling on top of the dimensionalization of the quantum program.
It is designed for users that really want to control the precise physical values of drive's amplitude and detuning, distances and time, and opt-out from the default compilation profile.

## Hardware effects
Real quantum hardware introduces deviations between the ideal compiled program and its actual execution.
These effects can be categorized into two main classes: hardware modulation and noise sources.
Importantly, in both cases, these effects can be included by configuring emulators, as detailed in the [Execution](../execution/execution.ipynb) page of this documentation.

### Hardware modulation
**Hardware modulation** arises from the finite bandwidth limitations of optical channels, such as the lasers that drive qubits in neutral atom QPUs. When waveforms contain sharp features (like steps or rapid transitions) the hardware's bandwidth constraints will smooth out these abrupt changes during actual laser pulse execution. This smoothing can alter the intended pulse shape and timing, potentially affecting the quantum operation's fidelity.
The net effect on the drive is always visible when inspecting the compiled sequence in a program, as shown in [Devices and Compilation](./device_and_compilation.ipynb). Moreover, to account for hardware modulation during the emulation of a program, emulators must be configured with the flag `with_hardware_modulation=true`, as described in [Execution](../execution/execution.ipynb).

### Noise
**Noise sources** encompass various forms of environmental and systematic errors that introduce unwanted fluctuations or systematic shifts in the quantum system parameters during execution.
As before, to include noise sources in the emulation of a program, emulators must be configured with the flag `noise_model`, as described in [Execution](../execution/execution.ipynb).

Finally, for more detailed information on [hardware modulation](https://docs.pasqal.com/pulser/tutorials/output_mod_eom/) and [noise sources](https://docs.pasqal.com/pulser/noise_model/), consult the comprehensive discussions available in the Pulser documentation.
