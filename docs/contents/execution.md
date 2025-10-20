# Executing a quantum program

A `QuantumProgram` can be easily run on multiple backends provided by Pasqal:
- locally installed emulators
- remote cloud emulators
- QPUs

Remote emulators and QPU **require** credentials to submit a job.
More information on how to access a QPU through your favorite cloud provider, is available at [Pasqal's website](https://www.pasqal.com/solutions/cloud/).
Later, we will briefly show how to authenticate and send a remote job.

## A simple quantum program

Let us revisit the quantum program definition described before in the [Quantum programs](./programs.md) page.

```python exec="on" source="material-block" session="execution"

from qoolqit import Drive, Ramp, Register, Constant
from qoolqit import QuantumProgram
from qoolqit import MockDevice

# Create the register
register = Register.from_coordinates([(0,1), (0,-1), (2,0)])

# Defining the drive parameters
omega = 0.8
delta_i = -2.0 * omega
delta_f = -delta_i
T = 25.0

# Defining the drive
wf_amp = Constant(T, omega)#PiecewiseLinear([T/4, T/2, T/4], [0.0, omega, omega, 0.0])
wf_det = Ramp(T, delta_i, delta_f)
drive = Drive(amplitude = wf_amp, detuning = wf_det)

# Creating the program
program = QuantumProgram(register, drive)

# Compiling the Program
device = MockDevice()
program.compile_to(device)
```

## Executing locally

Executing your program locally is as simple as importing the local emulator and just run your program on it
```python exec="on" source="material-block" session="execution"

from qoolqit.execution import LocalEmulator
emulator = LocalEmulator()
results = emulator.run(program)
```
