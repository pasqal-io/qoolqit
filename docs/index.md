---
template: home.html
title: Home
hide:
  - navigation
  - toc
---

# QoolQit

**QoolQit** is a Python library for designing and compiling analog quantum programs for neutral-atom devices in the Rydberg Analog Model.

QoolQit works in a **dimensionless framework**. This solves a key challenge in programming neutral-atom quantum computers, that is specifying physical parameters such as atom positions in micrometers, laser amplitudes in MHz, and pulse durations in nanoseconds. Sicne these values depend strongly on the particular hardware platform and differ of different devices.

QoolQit separates the **program you want to implement** from the **hardware scale used to realize it**. This makes it possible to develop analog quantum algorithms in a device-agnostic way, while still compiling them consistently to realistic hardware constraints.

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
