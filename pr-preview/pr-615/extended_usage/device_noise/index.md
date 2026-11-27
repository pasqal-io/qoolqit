# Emulating device noise

In this notebook, you will learn how to:

- fetch a device from a connection and use its noise model,
- emulate a program with the device noise model,
- compare ideal and noisy results, through occupations and bitstrings.

## Fetching a device with a noise model

Here, we fetch a device from PasqalCloudConnection which has a noise model.

```
from pasqal_cloud import PasqalCloudConnection

from qoolqit import Device

device = Device.from_connection(connection=PasqalCloudConnection(), name="FRESNEL_CAN1")
```

```
<string>:26: DeprecationWarning: Defining the number of emulation trajectories via 'NoiseModel.runs' is deprecated since pulser v1.7. Please favour using 'EmulationConfig.n_trajectories' instead.
```

## Rabi oscillations of a blockaded pair

We drive two qubits placed at the minimum distance of the device, where their interaction energy is \\(J = 1\\) in dimensionless units, with a constant amplitude \\(\\Omega = 0.1\\).

Since \\(J \\gg \\Omega\\), the pair is in the blockade regime: the doubly excited state \\(|11\\rangle\\) is strongly suppressed. Neglecting it, the global drive couples \\(|00\\rangle\\) only to the symmetric state \\(|\\Psi^+\\rangle = (|01\\rangle + |10\\rangle)/\\sqrt{2}\\).

In this approximation, the pair behaves as a two-level system oscillating at the collective Rabi frequency \\(\\sqrt{2}\\,\\Omega\\):

\\\[ P\_{\\Psi^+}(t) \\simeq \\sin^2\\left(\\frac{\\sqrt{2}\\,\\Omega\\, t}{2}\\right), \\\]

and the occupation of each qubit, \\(P\_{\\Psi^+}/2\\), oscillates between \\(0\\) and \\(1/2\\) with period \\(T\_\\text{Rabi} \\simeq 2\\pi / (\\sqrt{2}\\,\\Omega)\\).

This is the leading order in \\(\\Omega / J\\): the residual coupling to \\(|11\\rangle\\) shifts the frequency by corrections of order \\(\\Omega^2 / J\\), so over many periods the exact dynamics slowly drifts from this estimate.

We choose the drive duration as a number of Rabi periods, long enough for the noise to build up.

```
import numpy as np

from qoolqit import ConstantWaveform, Drive, QuantumProgram, Register

omega = 0.1 # much smaller than the interaction energy (1.0 at distance 1): blockade regime
n_oscillations = 7
# approximate duration of n_oscillations Rabi periods, valid in the blockade regime
duration = n_oscillations * 2 * np.pi / (np.sqrt(2) * omega)

register = Register.from_coordinates([(0.0, 0.0), (1.0, 0.0)])
drive = Drive(amplitude=ConstantWaveform(duration, omega))
program = QuantumProgram(register, drive)

program.compile_to(device)
print(program)
```

```
Quantum Program:
| Register(n_qubits = 2)
| Drive(duration = 311.002)
| Compiled: True
| Device: FRESNEL_CAN1
```

## Switching on the device noise

We ask the emulator for the Rydberg `Occupation` of each qubit along the pulse. Starting from an ideal configuration, the noisy one is obtained by setting `prefer_device_noise_model=True`.

Since the device noise is stochastic, the emulation averages over `n_trajectories` random realizations of the noise.

```
from qoolqit.execution import EmulationConfig, LocalEmulator, Occupation

rel_times = np.linspace(0, 1, 201)  # relative evaluation times, between 0 and 1
observables = (Occupation(evaluation_times=rel_times),)

ideal_config = EmulationConfig(observables=observables)
# same configuration, with the device noise switched on
noisy_config = EmulationConfig(
    observables=observables, prefer_device_noise_model=True, n_trajectories=64
)

ideal_results = LocalEmulator(emulation_config=ideal_config).run(program).results()
noisy_results = LocalEmulator(emulation_config=noisy_config).run(program).results()
```

```
/home/runner/work/qoolqit/qoolqit/.venv/lib/python3.14/site-packages/pulser_simulation/qutip_backend.py:149: UserWarning: 'sequence.device.noise_model.runs=1' is being ignored; 'config.n_trajectories=64' will be used instead.
  super().__init__(sequence, config=config, mimic_qpu=mimic_qpu)
```

```
import matplotlib.pyplot as plt

# evaluation times are relative to the drive duration
times = rel_times * duration

fig, axes = plt.subplots(1, 2, figsize=(10, 4), sharey=True)
for qubit, ax in enumerate(axes):
    ax.plot(times, [occ[qubit] for occ in ideal_results.occupation], label="ideal")
    ax.plot(
        times,
        [occ[qubit] for occ in noisy_results.occupation],
        "-o",
        ms=4,
        markevery=4,
        label="noisy",
    )
    ax.set_title(f"qubit {qubit}")
    ax.set_xlabel("$t$")
    ax.legend(loc="upper right")
axes[0].set_ylabel("Rydberg occupation")
plt.show()
```

png

Without noise, the two qubits oscillate in phase with full contrast, between \\(0\\) and \\(1/2\\). With noise, the oscillation damps: the maxima decrease and the minima lift from zero.

Noise also shows up in the bitstrings sampled at the end of the pulse: the noisy counts deviate from the ideal ones, partly because of state preparation and measurement (SPAM) errors. Note that the noisy counter collects the shots of every trajectory.

```
print("Ideal:", ideal_results.final_bitstrings)
print("Noisy:", noisy_results.final_bitstrings)

print("Number of ideal results (n_shots):", sum(ideal_results.final_bitstrings.values()))
print(
    "Number of noisy results (n_trajectories x n_shots):",
    sum(noisy_results.final_bitstrings.values()),
)
```

```
Ideal: Counter({'00': 998, '01': 2})
Noisy: Counter({'00': 51981, '01': 7524, '10': 4277, '11': 218})
Number of ideal results (n_shots): 1000
Number of noisy results (n_trajectories x n_shots): 64000
```
