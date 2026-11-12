# Atoms as qubits

On this page, you will learn about:

- How a neutral atom encodes a qubit and how a laser manipulates it
- The Rydberg blockade: why two atoms close together cannot both be excited
- How the distance between atoms and the drive amplitude decide whether a pair is blockaded

## Computing with atoms

A neutral-atom quantum processor holds individual atoms in place with optical tweezers, at positions chosen by the user.
Each atom is a qubit. Its electronic ground state $|g\rangle$ encodes $|0\rangle$, and a highly excited **Rydberg state** $|r\rangle$ encodes $|1\rangle$:

$$
|0\rangle \equiv |g\rangle, \qquad |1\rangle \equiv |r\rangle.
$$

What makes neutral atoms useful for computing is how they interact: through the Rydberg blockade, an excited atom stops its close neighbours from being excited.
This is the building block of quantum computing with neutral atoms, and the one Pasqal's processors are built on.

Throughout this page, quantities are written in QoolQit's dimensionless units, in which no two atoms are closer than $\tilde{r} = 1$.
The next page, [Programming a neutral-atom QPU](qoolqit_model.md), explains where these units come from.

A laser couples the two levels. Its **drive amplitude** $\tilde{\Omega}$ sets how fast an atom is transferred between $|0\rangle$ and $|1\rangle$.
An isolated atom under a laser tuned to its transition oscillates between the two states, a **Rabi oscillation**: starting in $|0\rangle$, its probability of being in the Rydberg state at time $\tilde{t}$ is

$$
P_1(\tilde{t}) = \sin^2\!\left(\frac{\tilde{\Omega}\,\tilde{t}}{2}\right).
$$

## Blockaded or not: distance against drive

Two atoms that are **both** in the Rydberg state repel each other.
The interaction energy decays quickly with their distance $\tilde{r}$.

!!! info "Interaction energy"

    $$
    \tilde{J} = \frac{1}{\tilde{r}^{\,6}}
    $$

The laser is tuned to excite the atoms to the Rydberg state. Once one atom is excited, its interaction shifts the transition of its neighbour, and the laser can excite the neighbour as well only if their interaction energy is small compared with the drive amplitude. Setting $\tilde{J} = \tilde{\Omega}$ defines the distance that separates the two regimes. This distance is called the **blockade radius** $\tilde{r}_b$:

!!! info "Blockade radius"

    $$
    \tilde{r}_b = \tilde{\Omega}^{-1/6}
    $$

    Two atoms closer than $\tilde{r}_b$ are blockaded: their double excitation is suppressed.
    A larger drive amplitude shrinks the blockade radius, a smaller one extends it.

**Blockaded** ($\tilde{J} \gg \tilde{\Omega}$, for instance $\tilde{r} = 1$ with $\tilde{\Omega} = 0.1$), the probability of exciting both atoms stays close to zero.
The pair behaves as a single two-level system between $|00\rangle$ and the Bell state $\ |\Psi^+\rangle = (|01\rangle + |10\rangle)/\sqrt{2}$: the probability of exactly one excitation reaches one and oscillates faster than a single atom would, by the factor $\sqrt{2}$.

**Independent** ($\tilde{J} \ll \tilde{\Omega}$, for instance $\tilde{r} = 2.5$ with $\tilde{\Omega} = 0.1$), the probability of exciting both atoms reaches one.
The two atoms are independent qubits: their interaction is negligible and each oscillates on its own.

**At the blockade radius** ($\tilde{J} \approx \tilde{\Omega}$) the pair moves continuously from one regime to the other.
The double excitation is only partially suppressed, and the populations no longer follow a clean oscillation: the peaks change height from one cycle to the next.

Note that the blockade radius can be crossed in two ways: moving the atoms or changing the drive amplitude.
Either way, only the ratio $\tilde{J} / \tilde{\Omega}$ matters.


The widget below lets you run the two-atom experiment yourself.
Drag an atom, or use the sliders, to change the distance $\tilde{r}$ between the atoms and the drive amplitude $\tilde{\Omega}$.
The dashed circle around each atom has radius $\tilde{r}_b / 2$, so the two circles overlap exactly when the atoms are closer than the blockade radius.
The plot shows, as a function of time and starting from $|00\rangle$, the probability that exactly one atom is excited and the probability that both are.
Each atom glows with its excitation probability as time runs, and its colour goes from green when the pair is blockaded to purple when the atoms are independent, matching the plot's curves.
The buttons under the widget jump to the end of the time window for each of the three cases below.

--8<-- "docs/extras/widgets/blockade.html"

## What this means for a program

The blockade is the building block QoolQit programs rely on: it is how the interaction between atoms shows up, tying their excitations together, and it is set by geometry and drive.

The positions of the atoms in a register decide which pairs are blockaded for a given $\tilde{\Omega}$, and that is how a problem is mapped onto the hardware.

Continue with [Programming a neutral-atom QPU](qoolqit_model.md) for the units and the full Hamiltonian, see how atom positions are chosen in [Embedding](../fundamentals/embedding.md), or watch the blockade at work in [Solving a MWIS](../tutorials/Solving_a_MWIS.md), where blockaded pairs become the edges of a graph.
