# Atoms as qubits

On this page, you will learn about:

- How a neutral atom encodes a qubit and how a laser manipulates it
- The Rydberg blockade: why two atoms close together cannot both be excited
- How the distance between atoms and the strength of the laser decide whether a pair is blockaded

## Computing with atoms

A neutral-atom quantum processor holds individual atoms in place with optical tweezers, at positions chosen by the user.
Each atom is a qubit. Its electronic ground state $|g\rangle$ encodes $|0\rangle$, and a highly excited **Rydberg state** $|r\rangle$ encodes $|1\rangle$:

$$
|0\rangle \equiv |g\rangle, \qquad |1\rangle \equiv |r\rangle.
$$

A laser couples the two levels. Its **amplitude** $\tilde{\Omega}$ sets how fast an atom is transferred between $|0\rangle$ and $|1\rangle$, and its **detuning** $\tilde{\delta}$ sets the energy of $|1\rangle$ relative to the laser.
An isolated atom under a resonant laser ($\tilde{\delta} = 0$) oscillates between the two states, a **Rabi oscillation**, with probability of being excited

$$
P_1(\tilde{t}) = \sin^2\!\left(\frac{\tilde{\Omega}\,\tilde{t}}{2}\right).
$$

Throughout this page, quantities are written in QoolQit's dimensionless units: distances in units of the minimum spacing a device allows, and energies in units of the strongest interaction it can produce.
The next page, [Programming a neutral-atom QPU](qoolqit_model.md), explains where these units come from.

## Why two atoms are not two independent qubits

Two atoms that are both in the Rydberg state repel each other.
The interaction energy decays quickly with their distance $\tilde{r}$:

$$
\tilde{J} = \frac{1}{\tilde{r}^{\,6}}.
$$

The laser can only drive transitions whose energy lies within about $\tilde{\Omega}$ of resonance.
The first excitation of the pair is always resonant.
The second one is not: once one atom is in $|1\rangle$, exciting the other costs the extra energy $\tilde{J}$.

- If $\tilde{J} \gg \tilde{\Omega}$, the doubly excited state $|11\rangle$ is shifted out of reach. The pair can hold **at most one excitation**. The laser then drives the pair between $|00\rangle$ and the shared state $(|01\rangle + |10\rangle)/\sqrt{2}$, at the enhanced frequency $\sqrt{2}\,\tilde{\Omega}$. This is the **Rydberg blockade**.
- If $\tilde{J} \ll \tilde{\Omega}$, the interaction is too weak to matter. Each atom oscillates on its own and $|11\rangle$ is reached.

The crossover $\tilde{J} = \tilde{\Omega}$ sets a distance below which the pair is blockaded.

!!! info "Blockade radius"

    $$
    \tilde{r}_b = \tilde{\Omega}^{-1/6}
    $$

    Two atoms closer than $\tilde{r}_b$ are blockaded: they cannot both be excited.
    A stronger laser shrinks the blockade radius, a weaker one extends it.

## Blockaded or not: distance against drive

The widget below lets you run the two-atom experiment yourself.
Drag an atom, or use the sliders, to change the distance $\tilde{r}$ between the atoms and the laser amplitude $\tilde{\Omega}$.
The dashed circle around each atom has radius $\tilde{r}_b / 2$, so the two circles overlap exactly when the atoms are closer than the blockade radius.
The plot shows, as a function of time and starting from $|00\rangle$, the probability that exactly one atom is excited and the probability that both are.
Each atom glows with its excitation probability as time runs.

--8<-- "docs/extras/widgets/blockade.html"

**Inside the blockade radius** ($\tilde{J} \gg \tilde{\Omega}$, for instance $\tilde{r} = 1$ with $\tilde{\Omega} = 0.1$), the probability of exciting both atoms stays at zero.
The pair behaves as a single two-level system: the probability of exactly one excitation reaches one and oscillates faster than a single atom would, by the factor $\sqrt{2}$.

**Outside the blockade radius** ($\tilde{J} \ll \tilde{\Omega}$, for instance $\tilde{r} = 2.5$ with $\tilde{\Omega} = 0.1$), the probability of exciting both atoms reaches one.
The two atoms are independent qubits, each oscillating on its own.

**At the blockade radius** ($\tilde{J} \approx \tilde{\Omega}$) neither picture holds: the double excitation is partially suppressed and the dynamics is irregular.
Programs are designed to stay away from this crossover.

Note that the blockade radius can be crossed in two ways: moving the atoms or changing the laser.
Only the ratio $\tilde{J} / \tilde{\Omega}$ matters, which is why QoolQit expresses both in the same unit.

## What this means for a program

The blockade is the resource that QoolQit programs are built on: it is what makes atoms interact, and it is set entirely by geometry and drive.
The positions of the atoms in a register decide which pairs are blockaded for a given $\tilde{\Omega}$, and that is how a problem is mapped onto the hardware.
The drive regimes table in [Programming a neutral-atom QPU](qoolqit_model.md#drive-regimes) summarizes the trade-off, and the [Rydberg blockade example](programming_with_qoolqit.md#example-rydberg-blockade-demonstration) in Programming with QoolQit runs this two-atom experiment through the library.
