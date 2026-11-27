# Solving a MWIS problem

In this tutorial, we solve a small **Maximum-Weight Independent Set (MWIS)** instance end-to-end with **QoolQit**, mapping it onto an array of **Rydberg atoms** and solving it with the **Quantum Adiabatic Algorithm (QAA)**. We will:

1. Define the problem and its graph, and write down its mathematical formulation.
2. Map it onto the weighted Rydberg Hamiltonian, term by term.
3. **Embed** the graph into a register of atoms, so that interactions reproduce the graph's edges.
4. Encode the node weights with a **Detuning Map Modulator (DMM)**.
5. Design an **adiabatic schedule** that drives the atoms into the MWIS solution.
6. Compile, run on a local emulator, and read out the answer.

## The Maximum-Weight Independent Set problem

The **Maximum-Weight Independent Set (MWIS)** problem is a classic combinatorial optimization task with applications including resource allocation, scheduling and staffing problems, error-correcting coding, complex system analysis and optimization, logistics and transportation, and communication networks.

Given a graph whose nodes carry positive weights, the goal is to select a subset of nodes such that

- **no two selected nodes are connected by an edge** (the set is *independent*), and
- **the total weight of the selected nodes is as large as possible**.

When all weights are equal, this reduces to the well-known Maximum Independent Set (MIS) problem.

What makes MWIS a natural fit for neutral-atom quantum hardware is its close correspondence with the physics of an array of **Rydberg atoms**: the *Rydberg blockade* prevents two nearby atoms from being simultaneously excited, which is exactly the independence constraint, while a per-atom energy offset can encode the node weights.

## 1\. The problem and its graph

We define the following weighted graph.

- The graph has four nodes \\(\\{0, 1, 2, 3\\}\\),
- The edges are between the pairs \\(0\\!-\\!1\\), \\(0\\!-\\!2\\), \\(0\\!-\\!3\\) and \\(2\\!-\\!3\\),
- The node weights are \\(w\_0 = 0,\\ w\_1 = 2,\\ w\_2 = 2,\\ w\_3 = 0\\).

In **QoolQit** a graph lives in a `DataGraph`. We build the graph from its edge list and attach a weight to every node.

```
import numpy as np

from qoolqit.graphs import DataGraph

# Build the graph from its edges, then attach a weight to each node.
graph = DataGraph([(0, 1), (0, 2), (0, 3), (2, 3)])
graph.node_weights = {0: 0.0, 1: 2.0, 2: 2.0, 3: 0.0}

# Color and size each node by its weight to make the structure visible.
weights = graph.node_weights
node_color = ["tab:green" if weights[n] > 0 else "tab:blue" for n in graph.nodes]
node_size = [600 + 600 * weights[n] for n in graph.nodes]

graph.draw(node_color=node_color, node_size=node_size, font_weight="bold")
```

png

Let's reason about the solution by hand. The **independent sets** of this graph (subsets with no internal edge) that are maximal are:

- \\(\\{1, 2\\}\\), nodes \\(1\\) and \\(2\\) are not directly connected; total weight \\(= 2 + 2 = 4\\).
- \\(\\{1, 3\\}\\), nodes \\(1\\) and \\(3\\) are not directly connected; total weight \\(= 2 + 0 = 2\\).

The set with the largest total weight is \\(\\{1, 2\\}\\), so the **MWIS of this graph is \\(\\{1, 2\\}\\)**.

We can encode the solution of the problem as a length-4 bitstring \\(x = x\_0 x\_1 x\_2 x\_3\\), where \\(x\_i = 1\\) if node \\(i\\) is selected. The answer we are looking for is `0110`.

## 2\. Mathematical formulation

### 2.1 The MWIS problem

Let \\(G = (V, E)\\) be an undirected graph, where \\(V\\) is the set of vertices and \\(E\\) is the set of edges, and let every vertex \\(i \\in V\\) carry a positive weight \\(w\_i\\).

A subset \\(S \\subseteq V\\) is an **independent set** if no two of its vertices are adjacent:

\\\[ (i, j) \\in E \\implies i \\notin S \\ \\text{ or }\\ j \\notin S . \\\]

The **Maximum-Weight Independent Set** is the independent set of *largest total weight*. Introducing a binary variable \\(x\_i \\in \\{0, 1\\}\\) for each vertex, with \\(x\_i = 1\\) if and only if \\(i \\in S\\), the problem is the constrained maximization

\\\[ \\max\_{x \\in \\{0,1\\}^{|V|}} \\ \\sum\_{i \\in V} w\_i\\, x\_i \\qquad \\text{subject to} \\qquad x\_i + x\_j \\le 1 \\quad \\forall\\, (i, j) \\in E . \\\]

The constraint \\(x\_i + x\_j \\le 1\\) simply forbids selecting both endpoints of an edge, which is exactly the independence condition. We denote by \\(x^\\star\\) the optimal assignment. When all weights are equal (\\(w\_i \\equiv 1\\)) this reduces to the ordinary (unweighted) **Maximum Independent Set (MIS)**.

### 2.2 MWIS as a QUBO problem

Rather than imposing the independence constraints explicitly, we can fold them into the objective as a **penalty**: every edge whose two endpoints are both selected (i.e. \\(x\_i x\_j = 1\\)) is charged a cost \\(\\alpha \> 0\\). This turns the constrained problem into an *unconstrained* one,

\\\[ \\max\_{x \\in \\{0,1\\}^{|V|}} \\ \\sum\_{i \\in V} w\_i\\, x\_i \\;-\\; \\alpha \\sum\_{(i,j) \\in E} x\_i\\, x\_j , \\\]

which is a **Quadratic Unconstrained Binary Optimization (QUBO)** problem. If the penalty \\(\\alpha\\) is large enough (larger than any weight it could "buy back"), violating an edge is never profitable, so the QUBO optimum coincides with the MWIS solution \\(x^\\star\\). Since QUBO is conventionally written as a minimization, an equivalent form is

\\\[ \\min\_{x \\in \\{0,1\\}^{|V|}} \\ \\alpha \\sum\_{(i,j) \\in E} x\_i\\, x\_j \\;-\\; \\sum\_{i \\in V} w\_i\\, x\_i . \\\]

This is the key observation for the rest of the tutorial, **an MWIS instance is fully specified by two ingredients:** 1. the graph's edges 2. the vertex weights both will have to be encoded on the Rydberg hardware.

It is convenient to pack them into a single symmetric matrix \\(Q\\) of size \\(N \\times N\\):

- the **off-diagonal** \\(Q\_{ij} = Q\_{ji}\\) is the adjacency matrix (\\(1\\) on an edge, \\(0\\) otherwise), it collects the independence constraints (the penalty terms);
- the **diagonal** \\(Q\_{ii} = w\_i\\) holds the vertex weights.

For our graph the matrix \\(Q\\) reads:

```
Q = np.diag([ graph.node_weights[n] for n in graph.nodes ])

for i, j in graph.edges():
    Q[i, j] = 1
    Q[j, i] = 1
```

Note that on any *feasible* (independent) assignment all cross terms vanish, since \\(Q\_{ij} \\neq 0\\) forces \\(x\_i x\_j = 0\\); the quadratic form \\(x^\\top Q x\\) then collapses onto the plain weight sum \\(\\sum\_i Q\_{ii}\\, x\_i = \\sum\_i w\_i\\, x\_i\\). In the rest of the tutorial we never build the QUBO cost matrix explicitly: we read the **two ingredients** off \\(Q\\) separately — the off-diagonal (edges) becomes the atom geometry via the *Rydberg blockade*, and the diagonal (weights) becomes a per-atom detuning.

## 3\. From MWIS to a Rydberg atom array

**QoolQit** programs a *weighted analog Ising Hamiltonian*, the natural model of an array of Rydberg atoms driven by a global laser plus a per-atom detuning channel (in dimensionless units):

\\\[ H(t) = \\sum\_{i} \\left\[ \\frac{\\Omega(t)}{2}\\,\\sigma^x\_i \\;-\\; \\big(\\delta(t) + \\epsilon\_i\\,\\Delta(t)\\big)\\, n\_i \\right\] \\;+\\; \\sum\_{i\<j} J\_{ij}\\, n\_i n\_j , \\\]

where \\(n\_i = |r\\rangle\\langle r|\_i\\) is the Rydberg occupation of atom \\(i\\), \\(\\Omega(t)\\) is the Rabi drive, \\(\\delta(t)\\) a global detuning, and \\(\\Delta(t)\\) a second detuning channel weighted per atom by \\(\\epsilon\_i \\in \[0, 1\]\\), \\(J\_{ij} \\propto r^{-6}\_{ij}\\) is the van der Waals interaction between atoms \\(i\\) and \\(j\\) at distance \\(r\_{ij}\\).

Each term of \\(Q\\) maps onto one ingredient of this Hamiltonian:

| MWIS quantity | Rydberg ingredient | QoolQit object |
| --- | --- | --- |
| off-diagonal \\(Q\_{ij}\\) (edges) | pairwise interaction \\(J\_{ij}\\) | `Register` (atom positions) |
| diagonal \\(Q\_{ii}\\) (weights) | per-atom detuning weights \\(\\epsilon\_i\\) | `DetuningMapModulator` |
| the optimum \\(x^\\star\\) | ground state of \\(H\\) | prepared by the QAA `Drive` |

The three ideas are:

1. **Edges → interactions.** The interaction \\(r\_{ij}^{-6}\\) decays steeply with distance, so placing connected nodes *close together* makes them strongly interacting: exciting both to \\(|r\\rangle\\) costs a large energy, which enforces the independence constraint (this is the *Rydberg blockade*). We find atom positions that reproduce the off-diagonal pattern of \\(Q\\): the **embedding** step.
2. **Weights → detuning.** The diagonal \\(Q\_{ii}\\) is encoded through a per-atom detuning, so that heavier nodes are energetically *favored* to be excited to \\(|r\\rangle\\).
3. **Optimum → ground state.** The MWIS solution is the ground state of \\(H\\) at the end of the schedule. We reach it with the **Quantum Adiabatic Algorithm**: start in an easy-to-prepare ground state and deform the Hamiltonian slowly enough to stay in the instantaneous ground state throughout.

## 4\. Embedding the graph into a register

The first task is purely geometric: find atom coordinates such that the interaction matrix \\(J\_{ij}\\) matches the off-diagonal part of \\(Q\\).

QoolQit's `InteractionEmbedder` does exactly this: it runs a numerical optimization over the atom positions to minimize the mismatch between \\(J\_{ij}\\) and the target off-diagonal entries.

We pass it the matrix \\(Q\\) (the embedder only looks at the off-diagonal entries) and obtain a `DataGraph` *with coordinates*, from which we build a `Register`.

```
from qoolqit import Register
from qoolqit.embedding import InteractionEmbedder, InteractionEmbedderConfig

config = InteractionEmbedderConfig(seed=1)
embedder = InteractionEmbedder(config)
embedded_graph = embedder.embed(Q)          # DataGraph with optimized coordinates
embedded_graph.draw(node_color=node_color, node_size=node_size, font_weight="bold")

register = Register.from_graph(embedded_graph)
```

png

Connected nodes (\\(0\\!-\\!1\\), \\(0\\!-\\!2\\), \\(0\\!-\\!3\\), \\(2\\!-\\!3\\)) end up at unit distance while the non-adjacent pairs (\\(1\\!-\\!2\\), \\(1\\!-\\!3\\)) are pushed roughly twice as far apart.

We can check the embedding quality directly: `register.interactions()` returns \\(J\_{ij}\\) for every pair, which should be \\(\\approx 1\\) on edges and \\(\\approx 0\\) elsewhere, reproducing the off-diagonal of \\(Q\\).

```
for (i, j), value in register.interactions().items():
    edge = "edge    " if Q[i, j] == 1 else "non-edge"
    print(f"pair (i={i}, j={j}):  is {edge}   Jij = {value:5.2f}   (target Q_ij = {Q[i, j]:.0f})")
```

```
pair (i=0, j=1):  is edge       Jij =  1.00   (target Q_ij = 1)
pair (i=1, j=2):  is non-edge   Jij =  0.02   (target Q_ij = 0)
pair (i=0, j=3):  is edge       Jij =  1.00   (target Q_ij = 1)
pair (i=2, j=3):  is edge       Jij =  1.00   (target Q_ij = 1)
pair (i=0, j=2):  is edge       Jij =  1.00   (target Q_ij = 1)
pair (i=1, j=3):  is non-edge   Jij =  0.02   (target Q_ij = 0)
```

## 5\. Encoding the weights with a Detuning Map Modulator

The register takes care of the edges; the node weights are encoded with the **Detuning Map Modulator (DMM)**, a channel that adds a per-atom detuning \\(-\\,\\epsilon\_i\\,\\Delta(t)\\,n\_i\\) on top of the global detuning.

A `DetuningMapModulator` bundles together:

- a **waveform** \\(\\Delta(t)\\), shared by all atoms and required to be **non-positive** (\\(\\Delta(t) \\le 0\\)), and
- a dictionary of **weights** \\(\\epsilon\_i \\in \[0, 1\]\\), one per atom: \\(\\epsilon\_i = 0\\) means the atom ignores the DMM entirely, \\(\\epsilon\_i = 1\\) means it feels its full effect.

We want the heaviest nodes to be the *easiest* to excite (most likely to be selected), so we give them **no extra detuning** (\\(\\epsilon\_i = 0\\)), and progressively penalize the lighter nodes.

A natural choice normalizes by the largest weight:

\\\[ \\epsilon\_i = 1 - \\frac{w\_i}{\\max\_k w\_k}. \\\]

Nodes carrying the maximum weight get \\(\\epsilon\_i = 0\\); a node with zero weight gets \\(\\epsilon\_i = 1\\), i.e. the strongest penalty.

```
node_weights = np.diag(Q)
dmm_weights = 1.0 - node_weights / node_weights.max()

# Map each weight to its atom (the register's qubit ids follow Q's row order).
det_map = {qubit: float(dmm_weights[i]) for i, qubit in enumerate(register.qubits.keys())}
print("DMM weights (epsilon_i):", det_map)
```

```
DMM weights (epsilon_i): {0: 1.0, 1: 0.0, 2: 0.0, 3: 1.0}
```

As expected, the heavy nodes \\(1\\) and \\(2\\) get \\(\\epsilon = 0\\) (no penalty) while the zero-weight nodes \\(0\\) and \\(3\\) get \\(\\epsilon = 1\\) (full penalty).

We will turn these weights into an actual `DetuningMapModulator` once we have fixed the schedule's energy scale in the next section.

## 6\. Designing the adiabatic schedule

The **Quantum Adiabatic Algorithm** prepares the ground state of \\(H\\) by slowly interpolating from a trivial Hamiltonian to the target one. The adiabatic theorem guarantees that a system started in the ground state stays there, provided the change is slow compared to the inverse square of the energy gap.

> Concretely, we vary the two global drive parameters in time:
>
> - The **Rabi amplitude** \\(\\Omega(t)\\) starts at \\(0\\), is ramped up, and brought back to \\(0\\) at the end. This supplies the quantum fluctuations that let the system explore configurations during the sweep.
> - The **global detuning** \\(\\delta(t)\\) is swept from a **negative** value \\(\\delta\_0 \< 0\\) to a **positive** value \\(\\delta\_f \> 0\\).
>
> At the start, \\(\\Omega(0) = 0\\) and \\(\\delta\_0 \< 0\\) make the trivial state \\(|g g g g\\rangle\\) (no atom excited) the ground state — easy to prepare exactly. At the end, the positive detuning \\(\\delta\_f \> 0\\) rewards exciting atoms to \\(|r\\rangle\\), while the blockade forbids exciting connected pairs: the ground state is then the independent set of largest weight, i.e. the MWIS.
>
> Alongside the global sweep, the DMM applies a constant negative detuning \\(\\Delta(t) = -\\delta\_f\\), weighted per atom by the \\(\\epsilon\_i\\) above. This tilts the energy landscape *against* the low-weight nodes, steering the adiabatic path toward the correctly-weighted solution.

**Choosing the energy scales.** We tie every scale to the interaction strength between atoms:

- \\(\\Omega\_{\\max}\\) is set an order of magnitude above the strongest pairwise interaction \\(J\_{ij}^{\\max} = 1/r\_{\\min}^6\\). Keeping the drive well above the interaction scale keeps the adiabatic path smooth and avoids getting stuck in the many small gaps of the blockaded subspace.
- \\(\\delta\_0 = -\\Omega\_{\\max}\\) guarantees the trivial ground state at \\(t=0\\).
- \\(\\delta\_f = -\\delta\_0\\) (just has to be positive) rewards excitations at the end.
- \\(T\\) is the total (dimensionless) evolution time, the *speed* knob of the adiabatic sweep.

```
# Strongest interaction in the register sets the reference energy scale.
distances = np.array(list(register.distances().values()))
max_interaction = 1.0 / distances.min() ** 6

Omega = 10.0 * max_interaction   # drive amplitude, safely above the interaction scale
delta_0 = -Omega                 # negative: trivial |gggg> ground state at t = 0
delta_f = -delta_0               # positive: excitations rewarded at t = T
T = 200.0                        # total (dimensionless) evolution time

print(f"Omega = {Omega:.2f}   delta_0 = {delta_0:.2f}   delta_f = {delta_f:.2f}   T = {T:.0f}")
```

```
Omega = 10.00   delta_0 = -10.00   delta_f = 10.00   T = 200
```

We now assemble the `Drive`, QoolQit's container for the time-dependent control fields. Its `amplitude` and `detuning` are **waveforms**; we use `InterpolatedWaveform`, which smoothly interpolates through a list of values across the total duration \\(T\\):

- amplitude: `[0, Omega, 0]` — the ramp up and down;
- detuning: `[delta_0, 0, delta_f]` — the sweep from negative to positive.

The DMM waveform is a `ConstantWaveform` holding at \\(-\\delta\_f\\) for the whole duration. Passing the `DetuningMapModulator` to the `Drive` via its `dmm` argument attaches the per-atom weights to the global schedule.

```
from qoolqit import ConstantWaveform, Drive, InterpolatedWaveform
from qoolqit.drive import DetuningMapModulator

dmm = DetuningMapModulator(ConstantWaveform(T, -delta_f), det_map)

drive = Drive(
    amplitude=InterpolatedWaveform(T, [0.0, Omega, 0.0]),
    detuning=InterpolatedWaveform(T, [delta_0, 0.0, delta_f]),
    dmm=dmm,
)
```

## 7\. Assembling and compiling the program

A `QuantumProgram` binds the *where* (the `register`) to the *how* (the `drive`). Everything so far has been in **dimensionless units**; `compile_to` maps the program onto a concrete device, rescaling positions and pulses to its physical constraints.

Because our schedule uses a DMM channel, we compile to a device that provides one. `MockDevice` is an idealized, constraint-free device that supports the DMM and is perfect for prototyping. Calling `draw()` shows the three control fields the backend will run: the amplitude bump, the global detuning sweep, and the constant DMM waveform.

```
from qoolqit import MockDevice, QuantumProgram

program = QuantumProgram(register, drive)
program.compile_to(device=MockDevice(), profile="max_energy")
program.draw()
```

png

## 8\. Running the algorithm and reading the solution

We run the compiled program on a local emulator. `LocalEmulator` propagates the state under the schedule and, at the end, samples the atoms in the \\(\\{|g\\rangle, |r\\rangle\\}\\) basis. The `final_bitstrings` field of the results is a dictionary mapping each measured bitstring to its number of occurrences, where bit \\(i\\) is `1` when atom \\(i\\) was found in \\(|r\\rangle\\) — that is, when node \\(i\\) is **selected**.

```
from qoolqit.execution import LocalEmulator

emulator = LocalEmulator()
job = emulator.run(program)
results = job.results()

counts = results.final_bitstrings
print("Most frequent bitstring:", max(counts, key=counts.get))
```

```
Most frequent bitstring: 0110
```

Finally we plot the full distribution of measured bitstrings, highlighting the exact MWIS solution `0110`. An adiabatic run that stayed in the ground state should return `0110` with overwhelming probability.

```
from qoolqit.visualization import COLORS, plot_bitstrings

SOLUTION = "0110"

plot_bitstrings(counts, highlight={SOLUTION: COLORS["mintgreen"]})
```

png

## 9\. Running on a realistic device

So far we compiled to `MockDevice`, an idealized, constraint-free device that let us pick a long, comfortably adiabatic schedule (\\(T = 200\\)). A real neutral-atom machine imposes **physical limits**: a maximum laser amplitude, a maximum detuning, a minimum atom spacing and, crucially here, a **maximum pulse duration**.

`AnalogDeviceWithDMM` is a realistic device model, the constraints of the analog device, plus a DMM channel so we can still encode the weights. Its amplitude ceiling fixes the physical energy scale, and once that scale is set the device's finite pulse duration translates into a *much shorter* admissible sweep time than the one we used: for this instance the longest schedule that compiles is about \\(T \\approx 7.5\\), more than an order of magnitude below \\(T = 200\\). Compiling the original program unchanged would raise a `CompilationError` stating exactly by how much the duration must shrink.

We therefore rebuild the drive with a shorter duration `T_analog` that respects the device limit, keeping every other quantity identical. Because the adiabatic theorem rewards *slow* sweeps, this faster schedule is less adiabatic, so we expect the success probability to drop somewhat.

```
from qoolqit import AnalogDeviceWithDMM

# Shorter schedule that fits the device's maximum pulse duration.
T_analog = 7.5

drive_analog = Drive(
    amplitude=InterpolatedWaveform(T_analog, [0.0, Omega, 0.0]),
    detuning=InterpolatedWaveform(T_analog, [delta_0, 0.0, delta_f]),
    dmm=DetuningMapModulator(ConstantWaveform(T_analog, -delta_f), det_map),
)

program_analog = QuantumProgram(register, drive_analog)
program_analog.compile_to(device=AnalogDeviceWithDMM(), profile="max_energy")

results_analog = emulator.run(program_analog).results()
counts_analog = results_analog.final_bitstrings

total = sum(counts_analog.values())
p_solution = counts_analog.get(SOLUTION, 0) / total
print("Most frequent bitstring:", max(counts_analog, key=counts_analog.get))
print(f"P({SOLUTION}) = {p_solution:.2%}")

plot_bitstrings(counts, highlight={SOLUTION: COLORS["mintgreen"]})
```

```
Most frequent bitstring: 0110
P(0110) = 79.20%
```

png

The realistic device still identifies `0110` as the most frequent outcome, so the algorithm finds the correct MWIS. As anticipated, though, the success probability is noticeably lower than on `MockDevice` (roughly \\(80\\%\\) versus \\(\\sim 98\\%\\)): the device-imposed cap on the pulse duration forces a faster, less adiabatic sweep, which leaves more weight on nearby sub-optimal bitstrings.

## 10\. Conclusion

We solved a Maximum-Weight Independent Set problem end-to-end on a Rydberg atom array with **QoolQit**. The recipe generalizes to any MWIS instance:

1. Encode the graph and its weights in a symmetric matrix \\(Q\\).
2. **Embed** the off-diagonal of \\(Q\\) into atom positions with an `InteractionEmbedder`, turning edges into blockade constraints.
3. Encode the diagonal (node weights) into per-atom detuning weights carried by a `DetuningMapModulator`.
4. Drive the system with an **adiabatic schedule** — an amplitude bump plus a detuning sweep from negative to positive — so that the final ground state is the MWIS.
5. Compile to a DMM-capable device, run on an emulator, and read the answer from `final_bitstrings`.

We first prototyped on the unconstrained `MockDevice`, where a long schedule (\\(T = 200\\)) made the sweep essentially adiabatic and returned `0110` with overwhelming probability. Moving to the realistic `AnalogDeviceWithDMM` we hit the device's physical limits: the maximum pulse duration caps the sweep time to \\(T \\approx 7.5\\), and the faster, less adiabatic evolution still identifies `0110` but with a lower success probability.
