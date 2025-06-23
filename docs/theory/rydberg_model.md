---
hide:
  - navigation
---

# **Quantum computing with Rydberg atoms**

Manipulating Rydberg atomic systems for quantum computing is a complex topic, and in this page we will not cover all aspects of it. The aim of this page is to introduce the underlying computational model when writing analog algorithms with Rydberg atoms, and to abstract away as much as possible the hardware details on how these algorithms are implemented. For a more detailed description on the physics and hardware implementation of quantum computing with Rydberg atoms, [check out the **Pulser** library](https://pulser.readthedocs.io/en/stable/index.html).

## **The Rydberg Analog Model**

The **Rydberg Analog Model** is a computational model following the Ising-mode operation of Rydberg atoms. Similarly to the circuit-model, it adopts the *qubit* as the basic unit of information. Two characteristics of the Rydberg analog model make it inherently different from the circuit-model:

- It is a **continuous-time** model, meaning all operations are defined as time-evolving processes that continuously alter the state of the qubits.

- The spatial arrangement of the qubits has a direct influence on the operations due to the **always-on physical interaction** of the atoms.

### **Register**

The register defines the qubit resources available to perform the computation.

!!! info "Definition: Register"
    A register $R$ is a set of qubits, each identified by an index $q_i$ and a position $p_i = (x_i, y_i)$, $R=\{(q_i, p_i)\}$, with size $|R|=N$. A register is assumed to have an initial state $|\psi_R(t=0)\rangle = |0\rangle^{\otimes N}$

### **Interaction**

Once a register is initialized, the physics of Rydberg atoms dictate that the state of the qubits evolves with an always-on interaction Hamiltonian. This background interaction is constant in time, and present during the whole program.

!!! info "Definition: Interaction Hamiltonian"
    The interaction Hamiltonian is defined as

    $$H^\text{int}=\sum_{i=0}^{N-1}\sum_{j=0}^{i-1}\frac{1}{r^6_{ij}}\hat{n}_i\hat{n}_j,$$

    where $r_{ij}=\sqrt{(x_i-x_j)^2+(y_i-y_j)^2}$ is the distance between qubits $q_i$ and $q_j$, and $\hat{n}=\frac12(1-\hat{\sigma}^z)$ is the number operator.

### **Drive**

A program in the Rydberg analog model is defined as a time-dependent *drive* Hamiltonian that is imposed on the qubits (in addition to the interaction Hamiltonian).

!!! info "Definition: Drive Hamiltonian"
    The drive Hamiltonian is defined as

    $$
    H^\text{d}(t)=\sum_{i=0}^{N-1}\frac{\Omega_i(t)}{2}\left(\cos\phi_i(t)\hat{\sigma}^x_i-\sin\phi_i(t)\hat{\sigma}^y_i\right)-\delta_i(t)\hat{n}_i
    $$

    where $\Omega_i(t)$, $\delta_i(t)$ and $\phi_i(t)$ are time-dependent functions, or waveforms, that encode the program corresponding, respectively, to the amplitude, detuning and phase of the drive on each qubit.

    The drive $D_i(t)$ is the set of functions $D_i(t) = \{\Omega_i(t), \delta_i(t), \phi_i(t)\}$ defined for $t\geq0$ that define the time-dependent Hamiltonian $H^\text{d}_i(t)$ driving qubit $q_i$.

    The drive is global if it is the same for all qubits in the register, $D_i(t)=D(t)~\forall~q_i\in R$.

#### Weighted detuning

In the Rydberg analog model drives are global. However, an extra local detuning term can be added when a weight map is passed $\{q_i: \epsilon_i\}$, where $\epsilon_i\in[0, 1]$ is the weight for each qubit $q_i$. Then, the detuning term changes to

$$
H^\text{d}(t)=\sum_{i=0}^{N-1}\frac{\Omega(t)}{2}\left(\cos\phi(t)\hat{\sigma}^x_i-\sin\phi(t)\hat{\sigma}^y_i\right)-\delta_\text{max}(\delta(t)+\epsilon_i\Delta(t))\hat{n}_i
$$

with the condition that the waveform $\Delta(t)$ must be negative.

### **The full model**

!!! info "Definition: Rydberg Analog Model"
    A register of qubits $R$ is initialized, where each qubit $q_i$ has a position $p_i = (x_i, y_i)$.

    The local detuning weights are programmed, $\{q_i: \epsilon_i\}$.

    The drive waveforms are programmed, $D(t) = \{\Omega(t), \delta(t), \Delta(t), \phi(t)\}$.

    The system evolves with the Hamiltonian:

    $$
    H(t)=\sum_{i=0}^{N-1}\frac{\Omega(t)}{2}\left(\cos\phi(t)\hat{\sigma}^x_i-\sin\phi(t)\hat{\sigma}^y_i\right)-(\delta(t)+\epsilon_i\Delta(t))\hat{n}_i + \sum_{i=0}^{N-1}\sum_{j=0}^{i-1}\frac{1}{r^6_{ij}}\hat{n}_i\hat{n}_j
    $$

    The system is measured in the computational basis at some time $t^* > 0$.

## **Model units**

The **Rydberg Analog Model** as implemented in QoolQit is **adimensional**, which is not the case in [Pulser](https://pulser.readthedocs.io/en/stable/). Below we go over some details on how this works.

### Pulser units

Pulser sets $\hbar=1$ and then uses the following units:

$$\text{Time:}~[\text{ns}],\qquad\text{Energy:}~[\text{rad}.\mu\text{s}^{-1}],\qquad\text{Distance:}~[\mu\text{m}]$$

Furthermore, Pulser writes the interaction term using a physical coefficient related to the energy level where the qubit is encoded:

$$H^\text{int}_\text{Pulser}=\sum_{i=0}^{N-1}\sum_{j=0}^{i-1}\frac{C_6}{r^6_{ij}}\hat{n}_i\hat{n}_j.$$

The interaction coefficient $C_6$ has units of $[\text{rad}.\mu\text{s}^{-1}.\mu\text{m}^{6}].$

This seemingly small difference has an important implication: a Pulser sequence is fundamentally device-specific. Pulser has a safety-first design, and does extensive validation when each sequence is created to guarantee it is compatible with the device it is created for, which is very important.

### Unit conversion

QoolQit handles the unit conversion automatically through a compilation layer, and also includes a number of features for more advanced users to customize it. This is done by defining a set of conversion factors for time, energy and distance, $\{\Delta_T$, $\Delta_E$, $\Delta_D\}$, such that:

$$\text{Time[P]}=\Delta_T \times \text{Time[Q]},\quad\text{Energy[P]}=\Delta_E \times \text{Energy[Q]},\quad\text{Distance[P]}=\Delta_D \times \text{Distance[Q]},$$

where $\text{P}$ and $\text{Q}$ refer to the Pulser and QoolQit units, respectively. Defining a valid set of conversion factors between QoolQit and Pulser can be done arbitrarily, as long as the **both the time-energy invariant and the energy-distance invariant are respected**:

$$\Delta_T\,\times\,\Delta_E = 1000,\qquad \Delta_D^6\,\times\,\Delta_E = C_6.$$

This means that it is possible to pick an arbitrary value for **one** of the conversion factors, and the two remaining ones can be automatically calculated from the invariants. As seen from the dependence of the invariants on the interaction coefficient $C_6$, these are calculated specifically for each device, and this is what guarantees that QoolQit programs can be device agnostic.

For details on how to customize the unit conversion in QoolQit check the contents pages on [devices](../contents/devices.md) and [quantum programs](../contents/programs.md). For further examples on understanding the unit conversion check the [unit conversion tutorial](../tutorials/unit_conversion.md).

#### Advantages & disadvantages

Working with an adimensional model has a few advantages:

- Programs are **more abstract and device agnostic**, and the rules to compile to different devices are clearly defined.
- Algorithm descriptions are **more unified and consistent**, focusing more on the logic of the algorithm and less on the implementation details.
- Increases **code portability** between experimental setups, different hardware configurations, and even different hardware calibrations.
- Program descriptions are **more future-proof**, as the same description today can be valid for future hardware generations.

However, while the above conversion is exact in theory, **in practice real device execution will have sources of errors and discrepancies** that are not accounted for in a simple unit conversion. Abstracting away the finer control over such errors can be seen as a disadvantage, but it is also an opportunity for improvement. The advanced user who understands such discrepancies can work on developing more robust protocols for compilation and noise mitigation and integrating them in the stack.
