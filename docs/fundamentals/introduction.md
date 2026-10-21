This section introduces the core concepts used throughout QoolQit, following the typical workflow: define a problem, embed it into a quantum program, compile, and execute.

---

## Problem definition and embedding

The first part focuses on **problem definition and embedding**.

- **Problem definition**:
  Problems are represented using graphs.
  The [`DataGraph`](./graphs.md) class extends NetworkX with features for the Rydberg analog model, including:
      - node coordinates
      - distance-based methods
      - unit-disk graph logic
      - node and edge weights

- **Embedding**:
  Once defined, a problem is mapped to hardware via the embedding interface. See the [embedding pages](./embedding.md) for:
      - the standard embedding workflow
      - available built-in embedders

  Advanced users can define [custom embedders](../extended_usage/custom_embedders.md) with custom inputs, outputs, and parameters.

---

## Quantum programs, compilation, and execution

The second part covers program construction, compilation, and execution.

The [quantum program](./quantum_program.md#defining-a-quantum-program) page details how to create a quantum program from its basic components:

- a [`Register`](./quantum_program.md#registers) — qubit positions
- a [`Drive`](./quantum_program.md#drives) — drive Hamiltonian, as composed of [`Waveforms`](./quantum_program.md#waveforms) to specify the time-dependent qubit controls

Once defined, a quantum program **must** be compiled to a QoolQit `Device`, as described in the [`device and compilation`](./compilation/device_and_compilation.md) page. This step will encode hardware constraints and units and generate an executable program.

Finally, see the [execution](./execution/execution.md) page to:

- run compiled programs on local/remote emulators or QPUs
- retrieve and interpret results

---

Together, these pages define the full QoolQit workflow, from hardware-agnostic problem definition to compiled execution.
