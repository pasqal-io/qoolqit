---
template: home.html
title: Home
hide:
  - navigation
  - toc
---

# QoolQit

**QoolQit** is a Python library for designing and compiling analog quantum programs for neutral-atom devices in the Rydberg Analog Model.

Instead of writing directly in hardware-dependent physical units, QoolQit lets you describe programs in a **dimensionless framework**. This makes programs easier to reason about, easier to compare across devices, and easier to compile to real hardware.

![QoolQit demo](./extras/assets/qoolqit_demo.gif)

With QoolQit you can:

- define neutral-atom registers and interaction graphs,
- build analog Hamiltonians with drives, detunings, and local controls,
- reason about programs in dimensionless units,
- compile them to hardware-compatible physical parameters,
- simulate and analyze the resulting dynamics.

QoolQit is designed for both **algorithm exploration** and **hardware-aware program design**: you can start from an abstract many-body problem, express it in a clean dimensionless form, and then map it to a concrete device realization.

## Where to start

- [The QoolQit Model](get_started/qoolqit_model.md) — the dimensionless Hamiltonian and compilation logic,
- [Fundamentals](fundamentals/introduction.md) — registers, waveforms, programs, and execution,
- [Adimensionalization — Advanced](extended_usage/adimensionalization.md) — how dimensionless programs are mapped to physical units.

## Why QoolQit?

Programming neutral-atom hardware usually requires choosing physical parameters such as distances, amplitudes, detunings, and runtimes. These depend strongly on the target device.

QoolQit separates the **program you want to implement** from the **hardware scale used to realize it**. This makes it possible to develop analog quantum algorithms in a device-agnostic way, while still compiling them consistently to realistic hardware constraints.
