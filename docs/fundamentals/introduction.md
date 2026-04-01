This section introduces the core concepts used throughout QoolQit, following the typical workflow: define a problem, embed it into hardware, then build, compile, and execute a quantum program.

---

## Problem definition and embedding

The first part focuses on **problem definition and embedding**.

- **Problem definition**  
  Problems are represented using graphs.  
  The [`DataGraph`](./problems/graphs.md) class extends NetworkX with features for the Rydberg analog model, including:
  - node coordinates  
  - distance-based methods  
  - unit-disk graph logic  
  - node and edge weights  

- **Embedding**  
  Once defined, a problem is mapped to hardware via the embedding interface.  

  See the [embedding pages](./problems/embedding.md) for:
  - the standard embedding workflow  
  - available built-in embedders  

  Advanced users can define [custom embedders](../extended_usage/custom_embedders.md) with custom inputs, outputs, and parameters.

---

## Quantum programs, compilation, and execution

The second part covers program construction, compilation, and execution.

A quantum program is built from:

- a [`Register`](./quantum_program/registers/index.md) — qubit positions  
- [`Waveforms`](./quantum_program/drives/waveforms.md) — time-dependent controls  
- a [`Drive`](./quantum_program/drives/index.md) — drive Hamiltonian  
- a [`Device`](./compilation/devices.md) — hardware constraints and units  
- a [`QuantumProgram`](./quantum_program/index.md) — executable program  

Finally, see the [execution](./execution/index.md) page to:

- run programs on emulators or QPUs  
- retrieve and interpret results  

---

Together, these pages define the full QoolQit workflow, from hardware-agnostic problem definition to compiled execution.