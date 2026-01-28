# From Physical Units to QoolQit

This section explains how QoolQit's dimensionless formulation relates to physical quantities and how compilation maps abstract programs back to real hardware.

## The Physical Hamiltonian

In physical units, the Rydberg Hamiltonian is:

$$
H(t) =
\underbrace{\sum_{i<j} \frac{C_6}{r_{ij}} \hat{n}_i \hat{n}_j}_{\text{interactions}}+
\underbrace{\sum_i \frac{\Omega(t)}{2}\left(\cos\phi(t)\,\hat{\sigma}_i^x - \sin\phi(t)\hat{\sigma}_i^y\right)}_{\text{global drive}}-\underbrace{\sum_i \left(\delta(t) + \epsilon_i\Delta(t)\right)\hat{n}_i}_{\text{detuning}}
$$

where $\hat{n}=\frac{1}{2}\left(1-\hat{\sigma}^z\right)$ is the Rydberg occupation operator.

#### Components

| Symbol | Description | Typical units |
|--------|-------------|---------------|
| $C_6(n)$ | Interaction coefficient (Rydberg level $n$) | rad/$\mu s$ (or MHz) $\times \mu m^6$ |
| $\Omega(t)$ | Global Rabi frequency (drive amplitude) | rad/$\mu s$ (or MHz) |
| $\delta(t)$ | Global detuning | rad/$\mu s$ (or MHz) |
| $\Delta(t)$ | Local detuning amplitude | rad/$\mu s$ (or MHz) |
| $\phi(t)$ | Drive phase | $[0,2\pi)$ |
| $\epsilon_i$ | Local detuning weight | $[0,1]$ |

## Introducing the Reference Interaction $J_0$

To make programs device-agnostic, we define an arbitrary **reference distance** $r_0$ and a corresponding **reference interaction**:

$$
J_0 = \frac{C_6}{r_0^6}
$$

This $J_0$ sets the energy scale for the problem. We then express all quantities relative to it:

$$\tilde{r}_{ij} = \frac{r_{ij}}{r_0}, \qquad \tilde{J}_{ij} = \frac{1}{\tilde{r}_{ij}^6}, \qquad \tilde{\Omega} = \frac{\Omega}{J_0}, \qquad \tilde{\delta} = \frac{\delta}{J_0}$$

Dividing the full Hamiltonian by $J_0$ gives the **dimensionless QoolQit Hamiltonian**:

$$
\tilde{H}(t) =
\sum_{i<j} \tilde{J}_{ij} \hat{n}_i \hat{n}_j + \sum_i \frac{\tilde{\Omega}(t)}{2}\left(\cos\phi(t)\hat{\sigma}^x_i - \sin\phi(t)\hat{\sigma}^y_i\right) - \sum_i \left(\tilde{\delta}(t) + \epsilon_i\tilde{\Delta}(t)\right)\hat{n}_i
$$

**Key convention:** In QoolQit, the minimum dimensionless distance is $\min(\tilde{r}_{ij}) = 1$, which means the maximum interaction is 1 as well.

## What Compilation Does

When you write a QoolQit program, you specify dimensionless ratios like $\tilde{\Omega}/\tilde{J}$. Compilation chooses a concrete value for $J_0$ that maps these ratios to physical values within the device's capabilities.

The key insight is:

- A **program** defines a ratio $\tilde{\Omega}/\tilde{J}$, which corresponds to a **line** through the origin in $(\Omega, J)$ space
- A **device** defines a box of allowed physical values: $[0, \Omega_{\max}] \times [0, J_{\max}]$

![Compilation strategy](../extras/assets/figures/compilation.png)

All points on the program line that fall within the device box are valid compilations. Choosing $J_0$ is equivalent to selecting which point on the line to use.

In practice, **programs with higher amplitude perform better on hardware**, so QoolQit automatically selects the point that maximizes amplitude while staying within device constraints.

### Case 1: Drive-limited compilation

When the user chooses $\tilde{\Omega}/\tilde{J} = 1$ (blue line in the plot):

The program line hits the maximum amplitude $\Omega_{\max}$ before reaching $J_{\max}$. The compiler sets:

$$J_0 = \Omega_{\max}$$

and calculates the corresponding reference distance, which will fit within device specs.

### Case 2: Interaction-limited compilation

When the user chooses $\tilde{\Omega}/\tilde{J} = 0.05$ (green line in the plot):

The program line hits the maximum interaction $J_{\max}$ before reaching $\Omega_{\max}$. The compiler sets:

$$J_0 = J_{\max}$$

This is equivalent to placing the closest pair of atoms at the minimum allowed distance. The compiler then calculates the corresponding $\Omega$ value.

!!! note "Previous behavior"
    In earlier versions of QoolQit, setting $J_0 = \Omega_{\max}$ for low-$\Omega$ programs would fail because atoms ended up below the minimum distance. The current strategy automatically handles this case.

This approach guarantees that compiled programs:

- **Fit within device specs** (if compilation succeeds)
- **Use the maximum amplitude possible** for the user-defined program

If compilation fails, the program simply cannot fit the device under any valid assignment of $J_0$.

!!! tip "Future extensions"
    - QoolQit can suggest **approximations** of incompatible programs that would compile
    - A "force compilation" strategy may be added in future versions


## Time scaling

Since QoolQit used an adimensional Hamiltonian defined with respect to a reference **energy scale** $J_0$, time must also be measured relative to that same scale. The reason is simply the Schrödinger equation that describes the dynamics of the quantum system.

$$
i\hbar \frac{d}{dt}|\psi(t)\rangle = H(t)|\psi(t)\rangle
$$

We require the physical and dimensionless descriptions to generate the **same unitary evolution**:

$$ U(t)  = \tilde U(\tilde t)\doublearrow \int_0^{t} H(t')dt'=\int_0^{\tilde{t}} \tilde{H}(\tilde{t}')d\tilde{t}'$$

Therefore

$$\int_0^{t} H(t')dt' = \int_0^{t} J_0 \tilde{H}(t') t_0 d\tilde{t}' = \int_0^{t} J_0 t_0 \tilde{H}(\tilde{t}')  d\tilde{t}' \doublearrow J_0 t_0=1$$

where we defined the adimensional time $\tilde{t}=\frac{t}{t_0}.

!!! note "Pulser behavior"
    In Pulser, energies are measured in rad/$\mu s$ (or MHz) but times are measured in $ns$ creating an artificial discrepancy of $10^3$ for convenience in terms of rounding and displaying. To keep track of this, also the invariant written before has to be rescaled according to $J_0 t_0=100$ and this is the value used in QoolQit.
