## drive

Drive Hamiltonian (amplitude, detuning, phase) and its Detuning Map Modulator (DMM).

Classes:

- **`DetuningMapModulator`** –

  A weighted detuning for the Detuning Map Modulator (DMM).
- **`Drive`** –

  The drive Hamiltonian acting over a duration.

### DetuningMapModulator

```
DetuningMapModulator(
    waveform: Waveform, weights: dict[Any, float]
)
```

A weighted detuning for the Detuning Map Modulator (DMM).

Parameters:

- **`waveform`** (`Waveform`) –

  The waveform for this detuning. Must be negative for all times.
- **`weights`** (`dict[Any, float]`) –

  A dictionary associating detuning weights to qubits. Each weight must be in \[0, 1\], where 0 means that the waveform is ignored for this qubit and 1 means that the waveform is fully applied to this qubit.

See [https://docs.pasqal.com/pulser/tutorials/dmm/](<https://docs.pasqal.com/pulser/tutorials/dmm/>) for details on DMM.

Methods:

- **`__post_init__`** –

  Check that the waveform is non-positive and the weights are in \[0, 1\].

#### \_\_post\_init\_\_

```
__post_init__() -> None
```

Check that the waveform is non-positive and the weights are in \[0, 1\].

### Drive

```
Drive(
    *,
    amplitude: Waveform,
    detuning: Waveform | None = None,
    dmm: DetuningMapModulator | None = None,
    phase: float = 0.0,
)
```

The drive Hamiltonian acting over a duration.

The Drive specifies the control parameters for the time-dependent drive Hamiltonian in the Rydberg model (see [https://docs.pasqal.com/qoolqit/get\_started/qoolqit\_model/](<https://docs.pasqal.com/qoolqit/get_started/qoolqit_model/>) for details),

H\_drive(t) = Σᵢ \[Ω(t)/2 (cos φ(t) σˣᵢ - sin φ(t) σʸᵢ)\] - Σᵢ \[δ(t) + εᵢ Δ(t)\] nᵢ

representing: - Amplitude Ω(t): Controls the Rabi frequency that drives qubits. - Detuning δ(t): Controls the energy offset of the Rydberg state. - dmm εᵢ, Δ(t): Detuning Map Modulator (DMM) for additional qubit-specific detunings. - Phase φ: Global phase applied to the amplitude term.

Parameters:

- **`amplitude`** (`Waveform`) –

  Time-dependent amplitude waveform Ω(t) representing the Rabi frequency. Controls the strength of the coupling between ground and Rydberg states. Must be positive for all times.
- **`detuning`** (`Waveform | None`, default: `None` ) –

  Time-dependent detuning waveform δ(t) representing the energy offset of the Rydberg state relative to resonance. If None, defaults to zero detuning (Delay waveform) for the duration of the amplitude.
- **`dmm`** (`DetuningMapModulator | None`, default: `None` ) –

  DetuningMapModulator instance for additional negative detuning waveform Δ(t) ≤ 0 applied to individual qubits as specified by its `weights` attribute εᵢ.
- **`phase`** (`float`, default: `0.0` ) –

  Global phase φ applied to the amplitude term in the Hamiltonian. Defaults to 0.0 (no phase). Normalized to \[0, 2π) and stored as a ConstantWaveform spanning the full duration of the drive.

Raises:

- `TypeError` –

  If amplitude or detuning are not Waveform instances.
- `ValueError` –

  If the amplitude waveform has negative values, or if the phase is not finite.

> [!NOTE]
>
> - All arguments must be passed as keyword arguments.
> - If amplitude and detuning have different durations, the shorter one is automatically extended with a Delay to match the longer duration.
> - DetuningMapModulator waveform must be negative for all times (≤ 0) as it represents energy shifts below the resonance.

> [!NOTE]
>
> **Example**
>
> > > > from qoolqit import Drive from qoolqit.waveforms import ConstantWaveform, RampWaveform
> > > >
> > > > #### Simple constant drive
> > > >
> > > > drive = Drive(amplitude=ConstantWaveform(10.0, 1.5))
> > > >
> > > > #### Drive with time-varying amplitude and detuning
> > > >
> > > > amp = RampWaveform(5.0, 0.0, 2.0) det = ConstantWaveform(5.0, -1.0) drive = Drive(amplitude=amp, detuning=det, phase=0.5)

Methods:

- **`__repr__`** –

  Return a multi-line summary of the drive waveforms.
- **`__rshift__`** –

  Concatenate two drives in time: `self` followed by `other`.
- **`draw`** –

  Draw the amplitude, detuning, phase and DMM of the Drive.

Attributes:

- **`amplitude`** (`Waveform`) –

  The amplitude waveform in the drive.
- **`detuning`** (`Waveform`) –

  The detuning waveform in the drive.
- **`dmm`** (`DetuningMapModulator | None`) –

  Detuning Map Modulator (DMM) applied to individual qubits.
- **`duration`** (`float`) –

  The total duration of the drive.
- **`phase`** (`ConstantWaveform`) –

  The phase waveform in the drive.

#### amplitude

```
amplitude: Waveform
```

The amplitude waveform in the drive.

#### detuning

```
detuning: Waveform
```

The detuning waveform in the drive.

#### dmm

```
dmm: DetuningMapModulator | None
```

Detuning Map Modulator (DMM) applied to individual qubits.

#### duration

```
duration: float
```

The total duration of the drive.

#### phase

```
phase: ConstantWaveform
```

The phase waveform in the drive.

#### \_\_repr\_\_

```
__repr__() -> str
```

Return a multi-line summary of the drive waveforms.

#### \_\_rshift\_\_

```
__rshift__(other: Drive) -> Drive
```

Concatenate two drives in time: `self` followed by `other`.

Not supported for drives with a DMM or with different phases.

#### draw

```
draw(fig: FigureBase | None = None) -> None
```

Draw the amplitude, detuning, phase and DMM of the Drive.

The phase is drawn only if it is non-zero, and the DMM only if one is set.

Parameters:

- **`fig`** (`FigureBase | None`, default: `None` ) –

  The figure or subfigure to draw into. If None, a new pyplot figure is created.
