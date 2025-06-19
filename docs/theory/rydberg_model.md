---
hide:
  - navigation
---

# **Quantum computing with Rydberg atoms**

Manipulating Rydberg atomic systems for quantum computing is a complex topic, and in this page we will not cover all aspects of it. The aim of this page is to introduce the underlying computational model when writing analog algorithms with Rydberg atoms, and to abstract away as much as possible the hardware details on how these algorithms are implemented. For a more detailed description on the physics and hardware implementation of quantum computing with Rydberg atoms, [check out the **Pulser** library](https://pulser.readthedocs.io/en/stable/index.html).

## The Rydberg Analog Model

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

    where $r_ij=\sqrt{(x_i-x_j)^2+(y_i-y_j)^2}$ is the distance between qubits $q_i$ and $q_j$, and $\hat{n}=\frac12(1-\hat{\sigma}^z)$ is the number operator.

### **Drive**

A program in the Rydberg analog model is defined as a time-dependent *drive* Hamiltonian that is imposed on the qubits (in addition to the interaction Hamiltonian).

!!! info "Definition: Drive Hamiltonian"
    The drive Hamiltonian is defined as

    $$
    H^\text{d}(t)=\sum_{i=0}^{N-1}\frac{\Omega_i(t)}{2}\left(\cos\phi_i(t)\hat{\sigma}^x_i-\sin\phi_i(t)\hat{\sigma}^y_i\right)-\delta_i(t)\hat{n}_i
    $$

    where $\Omega_i(t)$, $\delta_i(t)$ and $\phi_i(t)$ are time-dependent functions that encode the program sequence corresponding, respectively, to the amplitude, detuning and phase of the drive on each qubit.
