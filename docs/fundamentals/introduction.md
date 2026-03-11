This section introduces the core concepts and abstractions used throughout QoolQit. It follows the typical workflow of working with the Rydberg analog model: first defining a problem in a structured form, then embedding it into a geometry compatible with neutral-atom hardware, and finally building, compiling, and executing a quantum program.

The first part of this section focuses on **problem representation and embedding**. In QoolQit, graphs provide the standard representation for many problems of interest, particularly in optimization and machine learning. The [`DataGraph`](graphs.md) class extends the standard NetworkX graph interface with functionality tailored to the Rydberg analog model, including node coordinates, distance-based methods, unit-disk graph logic, and support for node and edge weights.

Once a problem has been defined, it can be mapped into a hardware-compatible object through the **embedding** interface. The [embedding pages](available_embedders.md) introduce the basic embedding workflow in QoolQit and the pre-defined embedders currently available in the library. For more advanced use cases, QoolQit also supports the definition of [custom embedders](custom_embedders.md), allowing users to implement new embedding strategies with their own input types, output types, and configuration parameters.

The second part of this section presents the **building blocks of quantum programs** in QoolQit. A program is constructed by combining:
- a [`Register`](registers.md), which defines the qubit positions;
- a set of [`Waveforms`](waveforms.md), which describe time-dependent controls;
- a [`Drive`](drives.md), which combines those controls into a drive Hamiltonian;
- a [`Device`](devices.md), which specifies the hardware constraints and unit conversion rules; and
- a [`QuantumProgram`](programs.md), which combines the register and drive into an executable program.

Finally, the [execution](execution.md) page shows how compiled programs can be run on local emulators, remote emulators, or QPUs, and how to retrieve and interpret the resulting data.

Together, these pages define the standard workflow in QoolQit, from problem specification to hardware-oriented quantum program execution.
