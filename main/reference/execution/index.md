## execution

Execute quantum programs on QPUs or local/remote emulators.

Modules:

- **`BackendType`** –

  A module gathering all available backends.
- **`backends`** –

  Backends to run quantum programs on local/remote emulators and QPUs.
- **`compilation_functions`** –

  Compilation of QoolQit programs into Pulser sequences, per compiler profile.
- **`example_connection`** –

  Example remote connection that runs sequences locally, without credentials, for tutorials.
- **`job`** –

  Job submission and results retrieval on local/remote emulators and QPUs.
- **`sequence_compiler`** –

  SequenceCompiler: turn a register and drive into a Pulser sequence for a device.

Classes:

- **`BitStrings`** –

  Stores bitstrings sampled from the state at the evaluation times.
- **`CorrelationMatrix`** –

  Stores the correlation matrix for the current state.
- **`EmulationConfig`** –

  Configures an emulation on a backend.
- **`Energy`** –

  Stores the energy of the system at the evaluation times.
- **`EnergySecondMoment`** –

  Stores the expectation value of `H(t)^2` at the evaluation times.
- **`EnergyVariance`** –

  Stores the variance of the Hamiltonian at the evaluation times.
- **`Expectation`** –

  Stores the expectation of the given operator on the current state.
- **`Fidelity`** –

  Stores the fidelity with a pure state at the evaluation times.
- **`Job`** –

  Abstract representation of an asynchronous job or task.
- **`LocalEmulator`** –

  Run QoolQit `QuantumProgram`s on Pasqal local emulator backends.
- **`Occupation`** –

  Stores the occupation number of an eigenstate on each qudit.
- **`QPU`** –

  Execute QoolQit QuantumPrograms on Pasqal quantum processing units.
- **`RemoteEmulator`** –

  Run QoolQit `QuantumProgram`s on Pasqal remote emulator backends.
- **`Results`** –

  A collection of results.
- **`StateResult`** –

  Stores the quantum state at the evaluation times.

Functions:

- **`get_batch_id`** –

  Return the batch ID associated with a remote job.
- **`retrieve_remote_job`** –

  Retrieve a previously submitted remote job by its identifiers.

Attributes:

- **`JobStatus`** (`TypeAlias`) –

  Alias for :class:`~pulser.backend.remote.JobStatus`.

### JobStatus

```
JobStatus: TypeAlias = remote.JobStatus
```

Alias for :class:`~pulser.backend.remote.JobStatus`.

Terminal states (where :meth:`Job.has_ended` returns `True`):

- :attr:`~remote.JobStatus.DONE`
- :attr:`~remote.JobStatus.ERROR`
- :attr:`~remote.JobStatus.CANCELED`

### BitStrings

```
BitStrings(
    *,
    evaluation_times: Sequence[float] | None = None,
    num_shots: int | None = None,
    one_state: Eigenstate | None = None,
    tag_suffix: str | None = None,
    default_aggregation_method: AggregationMethod = BAG_UNION,
)
```

Stores bitstrings sampled from the state at the evaluation times.

Error rates are taken from the NoiseModel passed to the backend via the EmulationConfig. The bitstrings are stored as a Counter\[str\].

Parameters:

- **`evaluation_times`** (`Sequence[float] | None`, default: `None` ) –

  The relative times at which to sample bitstrings. If left as `None`, uses the `default_evaluation_times` of the backend's `EmulationConfig`.
- **`num_shots`** (`int | None`, default: `None` ) –

  How many bitstrings to sample each time this observable is computed. If left as `None`, will use `default_num_shots` of the backend's `EmulationConfig`.
- **`one_state`** (`Eigenstate | None`, default: `None` ) –

  The eigenstate that measures to 1. Can be left undefined if the state's eigenstates form a known eigenbasis with a defined "one state".
- **`tag_suffix`** (`str | None`, default: `None` ) –

  An optional suffix to append to the tag. Needed if multiple instances of the same observable are given to the same EmulationConfig.
- **`default_aggregation_method`** (`AggregationMethod`, default: `BAG_UNION` ) –

  How to combine the values of this observable from multiple results.

Methods:

- **`__call__`** –

  Specifies a call to the observable at a specific time.
- **`apply`** –

  Calculates the observable to store in the Results.

Attributes:

- **`default_aggregation_method`** (`AggregationMethod`) –

  How the values from multiple results are combined.
- **`num_shots`** (`int | None`) –

  How many bitstrings to sample each time this observable is computed.
- **`tag`** (`str`) –

  Label for the observable, used to index the Results object.
- **`uuid`** (`UUID`) –

  A universal unique identifier for this instance.

#### default\_aggregation\_method

```
default_aggregation_method: AggregationMethod
```

How the values from multiple results are combined.

#### num\_shots

```
num_shots: int | None
```

How many bitstrings to sample each time this observable is computed.

> [!WARNING]
>
> The default value for this parameter was changed from 1000 to None in Pulser v1.7. When left as None, it now relies on `EmulationConfig.default_num_shots` to decide how many shots to take.

#### tag

```
tag: str
```

Label for the observable, used to index the Results object.

Within a Results instance, all computed observables must have different tags.

Returns:

- `str` –

  The tag of the observable.

#### uuid

```
uuid: UUID
```

A universal unique identifier for this instance.

#### \_\_call\_\_

```
__call__(
    config: EmulationConfig,
    t: float,
    state: State,
    hamiltonian: Operator,
    result: Results,
) -> None
```

Specifies a call to the observable at a specific time.

This is called after each time step performed by the emulator. By default it calls `apply()` to compute a result and put it in Results if t in self.evaluation\_times. It can be overloaded to define general callbacks that don't put results in the Results object.

Parameters:

- **`config`** (`EmulationConfig`) –

  The config object passed to the backend.
- **`t`** (`float`) –

  The relative time as a float between 0 and 1.
- **`state`** (`State`) –

  The current state.
- **`hamiltonian`** (`Operator`) –

  The Hamiltonian at this time.
- **`result`** (`Results`) –

  The Results object to store the result in.

#### apply

```
apply(
    *, config: EmulationConfig, state: State, **kwargs: Any
) -> Counter[str]
```

Calculates the observable to store in the Results.

### CorrelationMatrix

```
CorrelationMatrix(
    *,
    evaluation_times: Sequence[float] | None = None,
    one_state: Eigenstate | None = None,
    tag_suffix: str | None = None,
    default_aggregation_method: AggregationMethod = MEAN,
)
```

Stores the correlation matrix for the current state.

The correlation matrix is calculated as `[[<φ(t)|n_i n_j|φ(t)> for j in qubits] for i in qubits]` where `n_k = |one_state><one_state|`.

Parameters:

- **`evaluation_times`** (`Sequence[float] | None`, default: `None` ) –

  The relative times at which to compute the correlation matrix. If left as `None`, uses the `default_evaluation_times` of the backend's `EmulationConfig`.
- **`one_state`** (`Eigenstate | None`, default: `None` ) –

  The eigenstate to measure the population of in the correlation matrix. Can be left undefined if the state's eigenstates form a known eigenbasis with a defined "one state".
- **`tag_suffix`** (`str | None`, default: `None` ) –

  An optional suffix to append to the tag. Needed if multiple instances of the same observable are given to the same EmulationConfig.
- **`default_aggregation_method`** (`AggregationMethod`, default: `MEAN` ) –

  How to combine the values of this observable from multiple results.

Methods:

- **`__call__`** –

  Specifies a call to the observable at a specific time.
- **`apply`** –

  Calculates the observable to store in the Results.

Attributes:

- **`default_aggregation_method`** (`AggregationMethod`) –

  How the values from multiple results are combined.
- **`tag`** (`str`) –

  Label for the observable, used to index the Results object.
- **`uuid`** (`UUID`) –

  A universal unique identifier for this instance.

#### default\_aggregation\_method

```
default_aggregation_method: AggregationMethod
```

How the values from multiple results are combined.

#### tag

```
tag: str
```

Label for the observable, used to index the Results object.

Within a Results instance, all computed observables must have different tags.

Returns:

- `str` –

  The tag of the observable.

#### uuid

```
uuid: UUID
```

A universal unique identifier for this instance.

#### \_\_call\_\_

```
__call__(
    config: EmulationConfig,
    t: float,
    state: State,
    hamiltonian: Operator,
    result: Results,
) -> None
```

Specifies a call to the observable at a specific time.

This is called after each time step performed by the emulator. By default it calls `apply()` to compute a result and put it in Results if t in self.evaluation\_times. It can be overloaded to define general callbacks that don't put results in the Results object.

Parameters:

- **`config`** (`EmulationConfig`) –

  The config object passed to the backend.
- **`t`** (`float`) –

  The relative time as a float between 0 and 1.
- **`state`** (`State`) –

  The current state.
- **`hamiltonian`** (`Operator`) –

  The Hamiltonian at this time.
- **`result`** (`Results`) –

  The Results object to store the result in.

#### apply

```
apply(
    *, state: State, hamiltonian: Operator, **kwargs: Any
) -> list[list]
```

Calculates the observable to store in the Results.

### EmulationConfig

```
EmulationConfig(
    *,
    callbacks: Sequence[Callback] = (),
    observables: Sequence[Observable] = (),
    default_evaluation_times: Sequence[SupportsFloat]
    | Literal["Full"] = (1.0,),
    initial_state: StateType | None = None,
    with_modulation: bool = False,
    interaction_matrix: ArrayLike | None = None,
    prefer_device_noise_model: bool = False,
    noise_model: NoiseModel | None = None,
    n_trajectories: int | None = None,
    default_num_shots: int = 1000,
    **backend_options: Any,
)
```

Configures an emulation on a backend.

> [!NOTE]
>
> Additional parameters may be provided. It is up to the emulation backend that receives a configuration with extra parameters to assess whether it recognizes them and how it will use them. To know all parameters expected by an EmulatorBackend, **consult its associated EmulationConfig subclass found under** `EmulatorBackend.config_type`.

Parameters:

- **`observables`** (`Sequence[Observable]`, default: `()` ) –

  A sequence of observables to compute at specific evaluation times. The observables without specified evaluation times will use this configuration's 'default\_evaluation\_times'.
- **`callbacks`** (`Sequence[Callback]`, default: `()` ) –

  A general callback that is not an observable. Observables must be fed into the observables arg, since they all interact with the Results, and are subject to additional validation. Unlike observables, these are called at every emulation step.
- **`default_evaluation_times`** (`Sequence[SupportsFloat] | Literal['Full']`, default: `(1.0,)` ) –

  The default times at which observables are computed. Can be a sequence of unique relative times between 0 (the start of the sequence) and 1 (the end of the sequence), in ascending order. Can also be specified as "Full", in which case every step in the emulation will also be an evaluation time.
- **`initial_state`** (`StateType | None`, default: `None` ) –

  The initial state from which emulation starts. When given to an `EmulatorBackend`, it is automatically converted to `EmulatorBackend.config_type.state_type` if needed, which requires it to have been created via `State.from_state_amplitudes()`. If left undefined, defaults to starting with all qudits in the ground state.
- **`with_modulation`** (`bool`, default: `False` ) –

  Whether to emulate the sequence with the programmed input or the expected output.
- **`interaction_matrix`** (`ArrayLike | None`, default: `None` ) –

  An optional interaction matrix to replace the interaction terms in the Hamiltonian. For an N-qudit system, an interaction matrix is an NxN symmetric matrix, where entry (i, j) dictates the interaction coefficient between qudits i and j, ie it replaces the C\_n/r\_{ij}^n term. In XY, there are the two interactions C3 and C6 so the input should be a tensor of shape (2,N,N), representing the interaction matrix for the XY and the Rydberg term in that order. Otherwise the input should be a tensor of shape (N, N) or (1,N,N).
- **`prefer_device_noise_model`** (`bool`, default: `False` ) –

  If True, uses the noise model of the sequence's device (if the sequence's device has one), regardless of the noise model given with this configuration.
- **`noise_model`** (`NoiseModel | None`, default: `None` ) –

  An optional noise model to emulate the sequence with. Ignored if the sequence's device has default noise model and `prefer_device_noise_model=True`.
- **`n_trajectories`** (`int | None`, default: `None` ) –

  The number of trajectories to average over when the emulation includes stochastic noise or is using a Monte Carlo solver. When left undefined:

  (1) If 'prefer\_device\_noise\_model=False', tries to use the (now deprecated) value of `NoiseModel.runs`. If that is also not defined, defaults to 1 trajectory.

  (2) If 'prefer\_device\_noise\_model=True', **defaults to 40** trajectories.
- **`default_num_shots`** (`int`, default: `1000` ) –

  The default number of shots for `BitStrings`, used whenever the observable doesn't define its own. Defaults to 1000.

Methods:

- **`from_abstract_repr`** –

  Deserialize an EmulationConfig from an abstract JSON object.
- **`is_evaluation_time`** –

  Assesses whether a relative time is an evaluation time.
- **`is_time_in_evaluation_times`** –

  Checks if a time is within a collection of evaluation times.
- **`operator_type`** –

  The preferred operator type to use with this config class.
- **`state_type`** –

  The preferred state type to use with this config class.
- **`to_abstract_repr`** –

  Serialize `EmulationConfig` to a JSON formatted str.
- **`with_changes`** –

  Returns a copy of the config with the given changes.

Attributes:

- **`callbacks`** (`Sequence[Callback]`) –

  A sequence of callbacks that are not observables.
- **`default_evaluation_times`** (`NDArray[floating[Any]] | Literal['Full']`) –

  The default times at which observables are computed.
- **`default_num_shots`** (`int`) –

  The default number of shots for `BitStrings`.
- **`initial_state`** (`StateType | None`) –

  A custom initial state from which emulation starts.
- **`interaction_matrix`** (`AbstractArray | None`) –

  An interaction matrix to replace the Hamiltonian interaction terms.
- **`n_trajectories`** (`int`) –

  The number of trajectories to average over (when applicable).
- **`noise_model`** (`NoiseModel`) –

  A custom noise model to emulate the sequence with.
- **`observables`** (`Sequence[Observable]`) –

  A sequence of observables to compute at specific evaluation times.
- **`prefer_device_noise_model`** (`bool`) –

  Whether to use the noise model of the sequence's `Device`.
- **`with_modulation`** (`bool`) –

  Whether to emulate the sequence with output modulation effects.

#### callbacks

```
callbacks: Sequence[Callback]
```

A sequence of callbacks that are not observables.

#### default\_evaluation\_times

```
default_evaluation_times: (
    NDArray[floating[Any]] | Literal["Full"]
)
```

The default times at which observables are computed.

#### default\_num\_shots

```
default_num_shots: int
```

The default number of shots for `BitStrings`.

#### initial\_state

```
initial_state: StateType | None
```

A custom initial state from which emulation starts.

#### interaction\_matrix

```
interaction_matrix: AbstractArray | None
```

An interaction matrix to replace the Hamiltonian interaction terms.

#### n\_trajectories

```
n_trajectories: int
```

The number of trajectories to average over (when applicable).

#### noise\_model

```
noise_model: NoiseModel
```

A custom noise model to emulate the sequence with.

#### observables

```
observables: Sequence[Observable]
```

A sequence of observables to compute at specific evaluation times.

#### prefer\_device\_noise\_model

```
prefer_device_noise_model: bool
```

Whether to use the noise model of the sequence's `Device`.

#### with\_modulation

```
with_modulation: bool
```

Whether to emulate the sequence with output modulation effects.

#### from\_abstract\_repr

```
from_abstract_repr(obj_str: str) -> EmulationConfig
```

Deserialize an EmulationConfig from an abstract JSON object.

Parameters:

- **`obj_str`** (`str`) –

  The JSON string representing the config encoded in the abstract JSON format.

Returns:

- **`EmulationConfig`** ( `EmulationConfig` ) –

  The EmulationConfig instance.

#### is\_evaluation\_time

```
is_evaluation_time(t: float, tol: float = 1e-06) -> bool
```

Assesses whether a relative time is an evaluation time.

#### is\_time\_in\_evaluation\_times

```
is_time_in_evaluation_times(
    t: float,
    evaluation_times: ArrayLike,
    tol: float = 1e-06,
) -> bool
```

Checks if a time is within a collection of evaluation times.

#### operator\_type

```
operator_type() -> Type[Operator]
```

The preferred operator type to use with this config class.

#### state\_type

```
state_type() -> Type[State]
```

The preferred state type to use with this config class.

#### to\_abstract\_repr

```
to_abstract_repr(skip_validation: bool = False) -> str
```

Serialize `EmulationConfig` to a JSON formatted str.

#### with\_changes

```
with_changes(**changes: Any) -> Self
```

Returns a copy of the config with the given changes.

### Energy

```
Energy(
    *,
    evaluation_times: Sequence[float] | None = None,
    tag_suffix: str | None = None,
    default_aggregation_method: AggregationMethod = MEAN,
)
```

Stores the energy of the system at the evaluation times.

The energy is calculated as the expectation value of the Hamiltonian, i.e. `<φ(t)|H(t)|φ(t)>`.

Parameters:

- **`evaluation_times`** (`Sequence[float] | None`, default: `None` ) –

  The relative times at which to compute the energy. If left as `None`, uses the `default_evaluation_times` of the backend's `EmulationConfig`.
- **`tag_suffix`** (`str | None`, default: `None` ) –

  An optional suffix to append to the tag. Needed if multiple instances of the same observable are given to the same EmulationConfig.
- **`default_aggregation_method`** (`AggregationMethod`, default: `MEAN` ) –

  How to combine the values of this observable from multiple results.

Methods:

- **`__call__`** –

  Specifies a call to the observable at a specific time.
- **`apply`** –

  Calculates the observable to store in the Results.

Attributes:

- **`default_aggregation_method`** (`AggregationMethod`) –

  How the values from multiple results are combined.
- **`tag`** (`str`) –

  Label for the observable, used to index the Results object.
- **`uuid`** (`UUID`) –

  A universal unique identifier for this instance.

#### default\_aggregation\_method

```
default_aggregation_method: AggregationMethod
```

How the values from multiple results are combined.

#### tag

```
tag: str
```

Label for the observable, used to index the Results object.

Within a Results instance, all computed observables must have different tags.

Returns:

- `str` –

  The tag of the observable.

#### uuid

```
uuid: UUID
```

A universal unique identifier for this instance.

#### \_\_call\_\_

```
__call__(
    config: EmulationConfig,
    t: float,
    state: State,
    hamiltonian: Operator,
    result: Results,
) -> None
```

Specifies a call to the observable at a specific time.

This is called after each time step performed by the emulator. By default it calls `apply()` to compute a result and put it in Results if t in self.evaluation\_times. It can be overloaded to define general callbacks that don't put results in the Results object.

Parameters:

- **`config`** (`EmulationConfig`) –

  The config object passed to the backend.
- **`t`** (`float`) –

  The relative time as a float between 0 and 1.
- **`state`** (`State`) –

  The current state.
- **`hamiltonian`** (`Operator`) –

  The Hamiltonian at this time.
- **`result`** (`Results`) –

  The Results object to store the result in.

#### apply

```
apply(
    *, state: State, hamiltonian: Operator, **kwargs: Any
) -> Any
```

Calculates the observable to store in the Results.

### EnergySecondMoment

```
EnergySecondMoment(
    *,
    evaluation_times: Sequence[float] | None = None,
    tag_suffix: str | None = None,
    default_aggregation_method: AggregationMethod = MEAN,
)
```

Stores the expectation value of `H(t)^2` at the evaluation times.

Together with the mean, this can be used to compute the variance when averaging over many executions of the program.

Parameters:

- **`evaluation_times`** (`Sequence[float] | None`, default: `None` ) –

  The relative times at which to compute the moment. If left as `None`, uses the `default_evaluation_times` of the backend's `EmulationConfig`.
- **`tag_suffix`** (`str | None`, default: `None` ) –

  An optional suffix to append to the tag. Needed if multiple instances of the same observable are given to the same EmulationConfig.
- **`default_aggregation_method`** (`AggregationMethod`, default: `MEAN` ) –

  How to combine the values of this observable from multiple results.

Methods:

- **`__call__`** –

  Specifies a call to the observable at a specific time.
- **`apply`** –

  Calculates the observable to store in the Results.

Attributes:

- **`default_aggregation_method`** (`AggregationMethod`) –

  How the values from multiple results are combined.
- **`tag`** (`str`) –

  Label for the observable, used to index the Results object.
- **`uuid`** (`UUID`) –

  A universal unique identifier for this instance.

#### default\_aggregation\_method

```
default_aggregation_method: AggregationMethod
```

How the values from multiple results are combined.

#### tag

```
tag: str
```

Label for the observable, used to index the Results object.

Within a Results instance, all computed observables must have different tags.

Returns:

- `str` –

  The tag of the observable.

#### uuid

```
uuid: UUID
```

A universal unique identifier for this instance.

#### \_\_call\_\_

```
__call__(
    config: EmulationConfig,
    t: float,
    state: State,
    hamiltonian: Operator,
    result: Results,
) -> None
```

Specifies a call to the observable at a specific time.

This is called after each time step performed by the emulator. By default it calls `apply()` to compute a result and put it in Results if t in self.evaluation\_times. It can be overloaded to define general callbacks that don't put results in the Results object.

Parameters:

- **`config`** (`EmulationConfig`) –

  The config object passed to the backend.
- **`t`** (`float`) –

  The relative time as a float between 0 and 1.
- **`state`** (`State`) –

  The current state.
- **`hamiltonian`** (`Operator`) –

  The Hamiltonian at this time.
- **`result`** (`Results`) –

  The Results object to store the result in.

#### apply

```
apply(
    *, state: State, hamiltonian: Operator, **kwargs: Any
) -> Any
```

Calculates the observable to store in the Results.

### EnergyVariance

```
EnergyVariance(
    *,
    evaluation_times: Sequence[float] | None = None,
    tag_suffix: str | None = None,
    default_aggregation_method: AggregationMethod = SKIP_WARN,
)
```

Stores the variance of the Hamiltonian at the evaluation times.

The variance of the Hamiltonian at time `t` is calculated by `<φ(t)|H(t)^2|φ(t)> - <φ(t)|H(t)|φ(t)>^2`

Parameters:

- **`evaluation_times`** (`Sequence[float] | None`, default: `None` ) –

  The relative times at which to compute the variance. If left as `None`, uses the `default_evaluation_times` of the backend's `EmulationConfig`.
- **`tag_suffix`** (`str | None`, default: `None` ) –

  An optional suffix to append to the tag. Needed if multiple instances of the same observable are given to the same EmulationConfig.
- **`default_aggregation_method`** (`AggregationMethod`, default: `SKIP_WARN` ) –

  How to combine the values of this observable from multiple results.

Methods:

- **`__call__`** –

  Specifies a call to the observable at a specific time.
- **`apply`** –

  Calculates the observable to store in the Results.

Attributes:

- **`default_aggregation_method`** (`AggregationMethod`) –

  How the values from multiple results are combined.
- **`tag`** (`str`) –

  Label for the observable, used to index the Results object.
- **`uuid`** (`UUID`) –

  A universal unique identifier for this instance.

#### default\_aggregation\_method

```
default_aggregation_method: AggregationMethod
```

How the values from multiple results are combined.

#### tag

```
tag: str
```

Label for the observable, used to index the Results object.

Within a Results instance, all computed observables must have different tags.

Returns:

- `str` –

  The tag of the observable.

#### uuid

```
uuid: UUID
```

A universal unique identifier for this instance.

#### \_\_call\_\_

```
__call__(
    config: EmulationConfig,
    t: float,
    state: State,
    hamiltonian: Operator,
    result: Results,
) -> None
```

Specifies a call to the observable at a specific time.

This is called after each time step performed by the emulator. By default it calls `apply()` to compute a result and put it in Results if t in self.evaluation\_times. It can be overloaded to define general callbacks that don't put results in the Results object.

Parameters:

- **`config`** (`EmulationConfig`) –

  The config object passed to the backend.
- **`t`** (`float`) –

  The relative time as a float between 0 and 1.
- **`state`** (`State`) –

  The current state.
- **`hamiltonian`** (`Operator`) –

  The Hamiltonian at this time.
- **`result`** (`Results`) –

  The Results object to store the result in.

#### apply

```
apply(
    *, state: State, hamiltonian: Operator, **kwargs: Any
) -> Any
```

Calculates the observable to store in the Results.

### Expectation

```
Expectation(
    operator: Operator,
    *,
    evaluation_times: Sequence[float] | None = None,
    tag_suffix: str | None = None,
    default_aggregation_method: AggregationMethod = MEAN,
)
```

Stores the expectation of the given operator on the current state.

Parameters:

- **`evaluation_times`** (`Sequence[float] | None`, default: `None` ) –

  The relative times at which to compute the expectation value. If left as `None`, uses the `default_evaluation_times` of the backend's `EmulationConfig`.
- **`operator`** (`Operator`) –

  The operator to measure. If its type is not the backend's operator type, it is automatically converted when the config is given to the backend, provided it was created via `Operator.from_operator_repr()`.
- **`tag_suffix`** (`str | None`, default: `None` ) –

  An optional suffix to append to the tag. Needed if multiple instances of the same observable are given to the same EmulationConfig.
- **`default_aggregation_method`** (`AggregationMethod`, default: `MEAN` ) –

  How to combine the values of this observable from multiple results.

Methods:

- **`__call__`** –

  Specifies a call to the observable at a specific time.
- **`apply`** –

  Calculates the observable to store in the Results.

Attributes:

- **`default_aggregation_method`** (`AggregationMethod`) –

  How the values from multiple results are combined.
- **`tag`** (`str`) –

  Label for the observable, used to index the Results object.
- **`uuid`** (`UUID`) –

  A universal unique identifier for this instance.

#### default\_aggregation\_method

```
default_aggregation_method: AggregationMethod
```

How the values from multiple results are combined.

#### tag

```
tag: str
```

Label for the observable, used to index the Results object.

Within a Results instance, all computed observables must have different tags.

Returns:

- `str` –

  The tag of the observable.

#### uuid

```
uuid: UUID
```

A universal unique identifier for this instance.

#### \_\_call\_\_

```
__call__(
    config: EmulationConfig,
    t: float,
    state: State,
    hamiltonian: Operator,
    result: Results,
) -> None
```

Specifies a call to the observable at a specific time.

This is called after each time step performed by the emulator. By default it calls `apply()` to compute a result and put it in Results if t in self.evaluation\_times. It can be overloaded to define general callbacks that don't put results in the Results object.

Parameters:

- **`config`** (`EmulationConfig`) –

  The config object passed to the backend.
- **`t`** (`float`) –

  The relative time as a float between 0 and 1.
- **`state`** (`State`) –

  The current state.
- **`hamiltonian`** (`Operator`) –

  The Hamiltonian at this time.
- **`result`** (`Results`) –

  The Results object to store the result in.

#### apply

```
apply(*, state: State, **kwargs: Any) -> Any
```

Calculates the observable to store in the Results.

### Fidelity

```
Fidelity(
    state: State,
    *,
    evaluation_times: Sequence[float] | None = None,
    tag_suffix: str | None = None,
    default_aggregation_method: AggregationMethod = MEAN,
)
```

Stores the fidelity with a pure state at the evaluation times.

The fidelity uses the overlap between the given state and the state of the system at each evaluation time. For pure states, this corresponds to `|<ψ|φ(t)>|^2` for the given state `|ψ>` and the state `|φ(t)>` obtained by time evolution.

Parameters:

- **`state`** (`State`) –

  The state `|ψ>`. If its type is not the backend's state type, it is automatically converted when the config is given to the backend, provided it was created via `State.from_state_amplitudes()`.
- **`evaluation_times`** (`Sequence[float] | None`, default: `None` ) –

  The relative times at which to compute the fidelity. If left as `None`, uses the `default_evaluation_times` of the backend's `EmulationConfig`.
- **`tag_suffix`** (`str | None`, default: `None` ) –

  An optional suffix to append to the tag. Needed if multiple instances of the same observable are given to the same EmulationConfig.
- **`default_aggregation_method`** (`AggregationMethod`, default: `MEAN` ) –

  How to combine the values of this observable from multiple results.

Methods:

- **`__call__`** –

  Specifies a call to the observable at a specific time.
- **`apply`** –

  Calculates the observable to store in the Results.

Attributes:

- **`default_aggregation_method`** (`AggregationMethod`) –

  How the values from multiple results are combined.
- **`tag`** (`str`) –

  Label for the observable, used to index the Results object.
- **`uuid`** (`UUID`) –

  A universal unique identifier for this instance.

#### default\_aggregation\_method

```
default_aggregation_method: AggregationMethod
```

How the values from multiple results are combined.

#### tag

```
tag: str
```

Label for the observable, used to index the Results object.

Within a Results instance, all computed observables must have different tags.

Returns:

- `str` –

  The tag of the observable.

#### uuid

```
uuid: UUID
```

A universal unique identifier for this instance.

#### \_\_call\_\_

```
__call__(
    config: EmulationConfig,
    t: float,
    state: State,
    hamiltonian: Operator,
    result: Results,
) -> None
```

Specifies a call to the observable at a specific time.

This is called after each time step performed by the emulator. By default it calls `apply()` to compute a result and put it in Results if t in self.evaluation\_times. It can be overloaded to define general callbacks that don't put results in the Results object.

Parameters:

- **`config`** (`EmulationConfig`) –

  The config object passed to the backend.
- **`t`** (`float`) –

  The relative time as a float between 0 and 1.
- **`state`** (`State`) –

  The current state.
- **`hamiltonian`** (`Operator`) –

  The Hamiltonian at this time.
- **`result`** (`Results`) –

  The Results object to store the result in.

#### apply

```
apply(*, state: State, **kwargs: Any) -> Any
```

Calculates the observable to store in the Results.

### Job

Abstract representation of an asynchronous job or task.

A :class:`Job` tracks the lifecycle of a unit of work submitted for execution. It provides methods to inspect its state, wait for its result, and cancel it.

Lifecycle::

```
PENDING -> RUNNING -> DONE
                   -> ERROR
                   -> CANCELED
```

Concrete backend implementations (:class:`_LocalJob`, :class:`_RemoteJob`) must override all abstract methods. The leading underscore in their names indicates that they are internal to the library and must not be instantiated or referenced directly by library consumers. Instead, obtain a :class:`Job` from a backend submission function such as `backend.run(program)`.

> [!NOTE]
>
> A submitted job is not necessarily asynchronous. Whether execution is synchronous or asynchronous depends on the function that creates and returns the :class:`Job` instance (e.g. a local backend may execute synchronously and return an already-completed job, while a remote backend submits the work and returns a job that must be polled).

Methods:

- **`cancel`** –

  Request cancellation of the job.
- **`get_status`** –

  Return the current lifecycle state of the job.
- **`has_ended`** –

  Return whether the job has reached a terminal state.
- **`job_id`** –

  Return the unique identifier of the job.
- **`results`** –

  Return the results of the run.

#### cancel

```
cancel() -> None
```

Request cancellation of the job.

Has no effect if the job has already reached a terminal state. After a successful cancellation, :meth:`get_status` returns :attr:`~remote.JobStatus.CANCELED` and :meth:`has_ended` returns `True`.

> [!NOTE]
>
> Some implementations do not support cancellation. In that case this method is a no-op and the job status will never be :attr:`~remote.JobStatus.CANCELED`.

#### get\_status

```
get_status() -> JobStatus
```

Return the current lifecycle state of the job.

For remote jobs, each call queries the provider. To wait for a job to end, use :meth:`results` instead of calling this method in a loop.

Returns:

- **`JobStatus`** ( `JobStatus` ) –

  The current state of the job.

#### has\_ended

```
has_ended() -> bool
```

Return whether the job has reached a terminal state.

A job has ended when its status is one of :attr:`~remote.JobStatus.DONE`, :attr:`~remote.JobStatus.ERROR`, or :attr:`~remote.JobStatus.CANCELED`.

Like :meth:`get_status`, each call queries the provider for remote jobs, so use :meth:`results` to wait.

Returns:

- **`bool`** ( `bool` ) –

  `True` if the job is in a terminal state,
- `bool` –

  `False` otherwise.

#### job\_id

```
job_id() -> str
```

Return the unique identifier of the job.

For remote jobs this is the UUID used to track the job in the PASQAL Cloud Portal. For local jobs this is currently an empty string.

Returns:

- **`str`** ( `str` ) –

  A string uniquely identifying this job.

#### results

```
results(timeout: float = inf) -> ResultType
```

Return the results of the run.

Waits until the job reaches a terminal state, then returns the results.

> [!NOTE]
>
> Local runs are synchronous, so their results are returned immediately. For remote runs, the wait lasts as long as the job is queued and running on the provider. A `TimeoutError` doesn't cancel the job: call this method again to keep waiting.

Parameters:

- **`timeout`** (`float`, default: `inf` ) –

  Maximum seconds to wait for a remote run, ignored for local runs. Defaults to `math.inf` (wait indefinitely).

Returns:

- **`ResultType`** ( `ResultType` ) –

  The result produced by the job.

Raises:

- `TimeoutError` –

  If the job does not complete within *timeout* seconds.
- `JobFailedError` –

  If the job reached a failed or error state.
- `JobCancelledError` –

  If the job was cancelled.

### LocalEmulator

```
LocalEmulator(
    *,
    backend_type: type[EmulatorBackend] = QutipBackendV2,
    emulation_config: EmulationConfig | None = None,
    num_shots: int | None = None,
)
```

Run QoolQit `QuantumProgram`s on Pasqal local emulator backends.

Parameters:

- **`backend_type`** (`type[EmulatorBackend]`, default: `QutipBackendV2` ) –

  backend type. Must be a subtype of `pulser.backend.EmulatorBackend`.
- **`emulation_config`** (`EmulationConfig | None`, default: `None` ) –

  optional emulation config. If None, [`default_emulation_config`](<https://pasqal-io.github.io/qoolqit/main/reference/execution/index.md#qoolqit.execution.LocalEmulator.default_emulation_config> "<code class=\"doc-symbol doc-symbol-heading doc-symbol-method\"></code>            <span class=\"doc doc-object-name doc-function-name\">default_emulation_config</span>") is used.
- **`num_shots`** (`int | None`, default: `None` ) –

  number of bitstrings sampled from the final quantum state. If None, `default_num_shots` of the [`EmulationConfig`](<https://pasqal-io.github.io/qoolqit/main/reference/execution/index.md#qoolqit.execution.EmulationConfig> "<code class=\"doc-symbol doc-symbol-heading doc-symbol-class\"></code>            <span class=\"doc doc-object-name doc-class-name\">EmulationConfig</span>") is used.

Examples:

```
from qoolqit.execution import LocalEmulator, BackendType
backend = LocalEmulator(backend_type=BackendType.QutipBackendV2)
job = backend.run(program)
results = job.results()
```

Methods:

- **`default_emulation_config`** –

  Return the default emulation config, shared by all emulators.
- **`run`** –

  Run a compiled QuantumProgram and return a job handler.
- **`validate_emulation_config`** –

  Return a valid emulation config, ensuring bitstrings are sampled.

#### default\_emulation\_config

```
default_emulation_config() -> EmulationConfig
```

Return the default emulation config, shared by all emulators.

It only asks for the final bitstrings, sampled `num_shots` times.

#### run

```
run(program: QuantumProgram) -> Job[Results]
```

Run a compiled QuantumProgram and return a job handler.

Parameters:

- **`program`** (`QuantumProgram`) –

  the compiled quantum program to run.

Returns:

- `Job[Results]` –

  A `Job` handler, to retrieve the results with `job.results()`.

> [!NOTE]
>
> `LocalEmulator` runs synchronously: `run` waits for the job to be done before returning, so `job.results()` can be called directly, without checking the status. This may become asynchronous in a future version.

#### validate\_emulation\_config

```
validate_emulation_config(
    emulation_config: EmulationConfig | None,
) -> EmulationConfig
```

Return a valid emulation config, ensuring bitstrings are sampled.

Parameters:

- **`emulation_config`** (`EmulationConfig | None`) –

  optional emulation config. If None, `default_emulation_config` is used.

Returns:

- `EmulationConfig` –

  The default config if `emulation_config` is None. Otherwise `emulation_config`,
- `EmulationConfig` –

  with a `BitStrings` observable added if missing. In both cases, `default_num_shots`
- `EmulationConfig` –

  is set to `num_shots` when provided.

### Occupation

```
Occupation(
    *,
    evaluation_times: Sequence[float] | None = None,
    one_state: Eigenstate | None = None,
    tag_suffix: str | None = None,
    default_aggregation_method: AggregationMethod = MEAN,
)
```

Stores the occupation number of an eigenstate on each qudit.

For every qudit i, calculates `<φ(t)|n_i|φ(t)>`, where `n_i = |one_state><one_state|`.

Parameters:

- **`evaluation_times`** (`Sequence[float] | None`, default: `None` ) –

  The relative times at which to compute the occupation. If left as `None`, uses the `default_evaluation_times` of the backend's `EmulationConfig`.
- **`one_state`** (`Eigenstate | None`, default: `None` ) –

  The eigenstate to measure the population of. Can be left undefined if the state's eigenstates form a known eigenbasis with a defined "one state".
- **`tag_suffix`** (`str | None`, default: `None` ) –

  An optional suffix to append to the tag. Needed if multiple instances of the same observable are given to the same EmulationConfig.
- **`default_aggregation_method`** (`AggregationMethod`, default: `MEAN` ) –

  How to combine the values of this observable from multiple results.

Methods:

- **`__call__`** –

  Specifies a call to the observable at a specific time.
- **`apply`** –

  Calculates the observable to store in the Results.

Attributes:

- **`default_aggregation_method`** (`AggregationMethod`) –

  How the values from multiple results are combined.
- **`tag`** (`str`) –

  Label for the observable, used to index the Results object.
- **`uuid`** (`UUID`) –

  A universal unique identifier for this instance.

#### default\_aggregation\_method

```
default_aggregation_method: AggregationMethod
```

How the values from multiple results are combined.

#### tag

```
tag: str
```

Label for the observable, used to index the Results object.

Within a Results instance, all computed observables must have different tags.

Returns:

- `str` –

  The tag of the observable.

#### uuid

```
uuid: UUID
```

A universal unique identifier for this instance.

#### \_\_call\_\_

```
__call__(
    config: EmulationConfig,
    t: float,
    state: State,
    hamiltonian: Operator,
    result: Results,
) -> None
```

Specifies a call to the observable at a specific time.

This is called after each time step performed by the emulator. By default it calls `apply()` to compute a result and put it in Results if t in self.evaluation\_times. It can be overloaded to define general callbacks that don't put results in the Results object.

Parameters:

- **`config`** (`EmulationConfig`) –

  The config object passed to the backend.
- **`t`** (`float`) –

  The relative time as a float between 0 and 1.
- **`state`** (`State`) –

  The current state.
- **`hamiltonian`** (`Operator`) –

  The Hamiltonian at this time.
- **`result`** (`Results`) –

  The Results object to store the result in.

#### apply

```
apply(
    *, state: State, hamiltonian: Operator, **kwargs: Any
) -> list
```

Calculates the observable to store in the Results.

### QPU

```
QPU(
    *,
    connection: RemoteConnection,
    num_shots: int | None = None,
)
```

Execute QoolQit QuantumPrograms on Pasqal quantum processing units.

Runs on actual QPU hardware and requires an authenticated `connection`.

Parameters:

- **`connection`** (`RemoteConnection`) –

  Authenticated connection to the remote QPU backend.
- **`num_shots`** (`int | None`, default: `None` ) –

  Number of runs of the program on the QPU. Required.

Examples:

Using Pasqal Cloud:

```
from pasqal_cloud import PasqalCloudConnection
from qoolqit.execution import QPU
connection = PasqalCloudConnection(username=..., password=..., project_id=...)
backend = QPU(connection=connection, num_shots=100)
job = backend.run(program)
```

Using Atos MyQLM:

```
from pulser_myqlm import PulserQLMConnection
from qoolqit.execution import QPU
connection = PulserQLMConnection()
backend = QPU(connection=connection, num_shots=100)
job = backend.run(program)
```

See [`run`](<https://pasqal-io.github.io/qoolqit/main/reference/execution/index.md#qoolqit.execution.QPU.run> "<code class=\"doc-symbol doc-symbol-heading doc-symbol-method\"></code>            <span class=\"doc doc-object-name doc-function-name\">run</span>") to retrieve the results.

> [!NOTE]
>
> Contact your quantum computing provider for credentials and connection setup:
>
> - [Pasqal Cloud](<https://docs.pasqal.com/cloud/set-up/>)
> - [Third-party cloud providers](<https://docs.pasqal.com/third-party-cloud-providers/#create-a-connection>)
> - [Atos MyQLM Framework](<https://github.com/pasqal-io/Pulser-myQLM>)

Methods:

- **`run`** –

  Submit a compiled QuantumProgram and return a job handler.
- **`validate_connection`** –

  Validate the connection required by remote emulators and QPUs.

#### run

```
run(program: QuantumProgram) -> Job[Results]
```

Submit a compiled QuantumProgram and return a job handler.

`run` returns as soon as the job is submitted, the job runs remotely.

Parameters:

- **`program`** (`QuantumProgram`) –

  the compiled quantum program to run.

Returns:

- `Job[Results]` –

  A `Job` handler, to check the status and retrieve the results.

Examples:

Wait for the results, with a timeout. On timeout the job keeps running, and `job.results()` can be called again later:

```
job = backend.run(program)
try:
    results = job.results(timeout=600)
except TimeoutError:
    print(f"Job {job.job_id()} still running")
```

Check the status without blocking:

```
job = backend.run(program)
job.get_status()  # e.g. JobStatus.PENDING
job.has_ended()  # True once DONE, ERROR or CANCELED
results = job.results()  # blocks until the job has ended
```

Reconnect later, for long jobs (e.g. QPU queues), possibly from a new session:

```
from qoolqit.execution import get_batch_id, retrieve_remote_job
job = backend.run(program)
job_id, batch_id = job.job_id(), get_batch_id(job)  # store these
# later
job = retrieve_remote_job(connection, job_id, batch_id=batch_id)
results = job.results()
```

#### validate\_connection

```
validate_connection(
    connection: RemoteConnection,
) -> RemoteConnection
```

Validate the connection required by remote emulators and QPUs.

Remote emulators and QPUs require a `pulser.backend.remote.RemoteConnection`, or a subclass, to send jobs. Validation also happens inside the backend. Early validation just makes the error easier to understand.

Parameters:

- **`connection`** (`RemoteConnection`) –

  the connection to validate.

Returns:

- `RemoteConnection` –

  The same `connection`, if valid.

Raises:

- `TypeError` –

  if `connection` is not a `RemoteConnection`.

### RemoteEmulator

```
RemoteEmulator(
    *,
    backend_type: type[
        RemoteEmulatorBackend
    ] = RemoteEmuFreeBackend,
    connection: RemoteConnection,
    emulation_config: EmulationConfig | None = None,
    num_shots: int | None = None,
)
```

Run QoolQit `QuantumProgram`s on Pasqal remote emulator backends.

Works like [`LocalEmulator`](<https://pasqal-io.github.io/qoolqit/main/reference/execution/index.md#qoolqit.execution.LocalEmulator> "<code class=\"doc-symbol doc-symbol-heading doc-symbol-class\"></code>            <span class=\"doc doc-object-name doc-class-name\">LocalEmulator</span>"), but requires a `connection` to submit jobs, either through [Pasqal Cloud](<https://docs.pasqal.com/cloud/set-up/>) or through one of the [third-party cloud providers](<https://docs.pasqal.com/third-party-cloud-providers/#create-a-connection>).

Parameters:

- **`backend_type`** (`type[RemoteEmulatorBackend]`, default: `RemoteEmuFreeBackend` ) –

  backend type. Must be a subtype of `pasqal_cloud.backends.RemoteEmulatorBackend`.
- **`connection`** (`RemoteConnection`) –

  connection to execute the program on remote backends.
- **`emulation_config`** (`EmulationConfig | None`, default: `None` ) –

  optional emulation config. If None, [`default_emulation_config`](<https://pasqal-io.github.io/qoolqit/main/reference/execution/index.md#qoolqit.execution.RemoteEmulator.default_emulation_config> "<code class=\"doc-symbol doc-symbol-heading doc-symbol-method\"></code>            <span class=\"doc doc-object-name doc-function-name\">default_emulation_config</span>") is used.
- **`num_shots`** (`int | None`, default: `None` ) –

  number of bitstrings sampled from the final quantum state. If None, `default_num_shots` of the [`EmulationConfig`](<https://pasqal-io.github.io/qoolqit/main/reference/execution/index.md#qoolqit.execution.EmulationConfig> "<code class=\"doc-symbol doc-symbol-heading doc-symbol-class\"></code>            <span class=\"doc doc-object-name doc-class-name\">EmulationConfig</span>") is used.

Examples:

```
from pasqal_cloud import PasqalCloudConnection
from qoolqit.execution import RemoteEmulator, BackendType
connection = PasqalCloudConnection(username=..., password=..., project_id=...)
backend = RemoteEmulator(
    backend_type=BackendType.RemoteEmuFreeBackend, connection=connection
)
job = backend.run(program)
```

See [`run`](<https://pasqal-io.github.io/qoolqit/main/reference/execution/index.md#qoolqit.execution.RemoteEmulator.run> "<code class=\"doc-symbol doc-symbol-heading doc-symbol-method\"></code>            <span class=\"doc doc-object-name doc-function-name\">run</span>") to retrieve the results.

Methods:

- **`default_emulation_config`** –

  Return the default emulation config, shared by all emulators.
- **`run`** –

  Submit a compiled QuantumProgram and return a job handler.
- **`validate_connection`** –

  Validate the connection required by remote emulators and QPUs.
- **`validate_emulation_config`** –

  Return a valid emulation config, ensuring bitstrings are sampled.

#### default\_emulation\_config

```
default_emulation_config() -> EmulationConfig
```

Return the default emulation config, shared by all emulators.

It only asks for the final bitstrings, sampled `num_shots` times.

#### run

```
run(program: QuantumProgram) -> Job[Results]
```

Submit a compiled QuantumProgram and return a job handler.

`run` returns as soon as the job is submitted, the job runs remotely.

Parameters:

- **`program`** (`QuantumProgram`) –

  the compiled quantum program to run.

Returns:

- `Job[Results]` –

  A `Job` handler, to check the status and retrieve the results.

Examples:

Wait for the results, with a timeout. On timeout the job keeps running, and `job.results()` can be called again later:

```
job = backend.run(program)
try:
    results = job.results(timeout=600)
except TimeoutError:
    print(f"Job {job.job_id()} still running")
```

Check the status without blocking:

```
job = backend.run(program)
job.get_status()  # e.g. JobStatus.PENDING
job.has_ended()  # True once DONE, ERROR or CANCELED
results = job.results()  # blocks until the job has ended
```

Reconnect later, for long jobs (e.g. QPU queues), possibly from a new session:

```
from qoolqit.execution import get_batch_id, retrieve_remote_job
job = backend.run(program)
job_id, batch_id = job.job_id(), get_batch_id(job)  # store these
# later
job = retrieve_remote_job(connection, job_id, batch_id=batch_id)
results = job.results()
```

#### validate\_connection

```
validate_connection(
    connection: RemoteConnection,
) -> RemoteConnection
```

Validate the connection required by remote emulators and QPUs.

Remote emulators and QPUs require a `pulser.backend.remote.RemoteConnection`, or a subclass, to send jobs. Validation also happens inside the backend. Early validation just makes the error easier to understand.

Parameters:

- **`connection`** (`RemoteConnection`) –

  the connection to validate.

Returns:

- `RemoteConnection` –

  The same `connection`, if valid.

Raises:

- `TypeError` –

  if `connection` is not a `RemoteConnection`.

#### validate\_emulation\_config

```
validate_emulation_config(
    emulation_config: EmulationConfig | None,
) -> EmulationConfig
```

Return a valid emulation config, ensuring bitstrings are sampled.

Parameters:

- **`emulation_config`** (`EmulationConfig | None`) –

  optional emulation config. If None, `default_emulation_config` is used.

Returns:

- `EmulationConfig` –

  The default config if `emulation_config` is None. Otherwise `emulation_config`,
- `EmulationConfig` –

  with a `BitStrings` observable added if missing. In both cases, `default_num_shots`
- `EmulationConfig` –

  is set to `num_shots` when provided.

### Results

```
Results(atom_order: tuple[str, ...], total_duration: int)
```

A collection of results.

Parameters:

- **`atom_order`** (`tuple[str, ...]`) –

  The order of the atoms/qudits in the results.
- **`total_duration`** (`int`) –

  The total duration of the sequence, in ns.

Methods:

- **`aggregate`** –

  Aggregate a Sequence of Results objects into a single Results.
- **`from_abstract_repr`** –

  Deserializes a Results object from json.
- **`from_final_bitstrings`** –

  Creates a Results instance with bitstrings at evaluation time t=1.0.
- **`get_result`** –

  Get the a specific result at a given time.
- **`get_result_tags`** –

  Get a list of results tags present in this object.
- **`get_result_times`** –

  Get a list of times for which the given result has been stored.
- **`get_tagged_results`** –

  Gets the results for every tag.
- **`to_abstract_repr`** –

  Serializes this object into a json string.

Attributes:

- **`atom_order`** (`tuple[str, ...]`) –

  The order of the atoms/qudits in the results.
- **`final_bitstrings`** (`dict[str, int]`) –

  The bitstrings at the end of the sequence, if available.
- **`final_state`** (`State`) –

  The state at the end of the sequence, if available.
- **`total_duration`** (`int`) –

  The total duration of the sequence, in ns.

#### atom\_order

```
atom_order: tuple[str, ...]
```

The order of the atoms/qudits in the results.

#### final\_bitstrings

```
final_bitstrings: dict[str, int]
```

The bitstrings at the end of the sequence, if available.

#### final\_state

```
final_state: State
```

The state at the end of the sequence, if available.

#### total\_duration

```
total_duration: int
```

The total duration of the sequence, in ns.

#### aggregate

```
aggregate(
    results_to_aggregate: Sequence[Results],
    **aggregation_functions: Callable[[Any], Any]
    | AggregationMethod,
) -> Results
```

Aggregate a Sequence of Results objects into a single Results.

This is meant to accumulate the results of several runs with different noise trajectories into a single averaged Results. By default, results are averaged, with the exception of BitStrings, where the counters are joined. StateResult and EnergyVariance are not supported by default.

> [!WARNING]
>
> The ability to access a result from an observable instance (e.g. via Results.get\_result(obs)) is only preserved if all aggregated results originated from the same observable instance. When that is not the case, the aggregated result can still be accessed via the observable's tag.

Parameters:

- **`results_to_aggregate`** (`Sequence[Results]`) –

  The list of Results to aggregate

Other Parameters:

- **`aggregation_functions`** (`Callable[[Any], Any] | AggregationMethod`) –

  Overrides the default aggregator. The argument name should be the tag of the Observable. The value is a Callable taking a list of the type to aggregate, or an AggregationMethod enum. Note that this does not override the default aggregation behaviour of the aggregated results.

Returns:

- `Results` –

  The averaged Results object

#### from\_abstract\_repr

```
from_abstract_repr(repr: str) -> Results
```

Deserializes a Results object from json.

Returns:

- `Results` –

  The deserialized Results object.

#### from\_final\_bitstrings

```
from_final_bitstrings(
    atom_order: Sequence[str],
    total_duration: int,
    final_bitstrings: Mapping[str, int],
) -> ResultsType
```

Creates a Results instance with bitstrings at evaluation time t=1.0.

The bitstrings are stored under a fabricated BitStrings observable instance. Use `Results.final_bitstrings` or `Results.get_result("bitstrings", 1.0)` to retrieve them.

Parameters:

- **`atom_order`** (`Sequence[str]`) –

  The order of the atoms/qudits in the results.
- **`total_duration`** (`int`) –

  The total duration of the sequence, in ns.
- **`final_bitstrings`** (`Mapping[str, int]`) –

  The bitstring counter to store in the Results.

#### get\_result

```
get_result(
    observable: Observable | str, time: float
) -> Any
```

Get the a specific result at a given time.

Parameters:

- **`observable`** (`Observable | str`) –

  The observable instance used to calculate the result or its tag.
- **`time`** (`float`) –

  Relative time at which to get the result.

Returns:

- `Any` –

  The result.

#### get\_result\_tags

```
get_result_tags() -> list[str]
```

Get a list of results tags present in this object.

#### get\_result\_times

```
get_result_times(
    observable: Observable | str,
) -> list[float]
```

Get a list of times for which the given result has been stored.

Parameters:

- **`observable`** (`Observable | str`) –

  The observable instance used to calculate the result or its tag.

Returns:

- `list[float]` –

  List of relative times.

#### get\_tagged\_results

```
get_tagged_results() -> dict[str, list[Any]]
```

Gets the results for every tag.

Returns:

- `dict[str, list[Any]]` –

  A mapping between a tag and the results associated to it,
- `dict[str, list[Any]]` –

  at every evaluation time.

#### to\_abstract\_repr

```
to_abstract_repr(skip_validation: bool = False) -> str
```

Serializes this object into a json string.

Numpy arrays and torch Tensors are converted into lists, and their original class is lost forever.

Parameters:

- **`skip_validation`** (`bool`, default: `False` ) –

  Whether to skip validating the json against the schema used for deserialization.

Returns:

- `str` –

  The json string

### StateResult

```
StateResult(
    *,
    evaluation_times: Sequence[float] | None = None,
    tag_suffix: str | None = None,
    default_aggregation_method: AggregationMethod = SKIP_WARN,
)
```

Stores the quantum state at the evaluation times.

Parameters:

- **`evaluation_times`** (`Sequence[float] | None`, default: `None` ) –

  The relative times at which to store the state. If left as `None`, uses the `default_evaluation_times` of the backend's `EmulationConfig`.
- **`tag_suffix`** (`str | None`, default: `None` ) –

  An optional suffix to append to the tag. Needed if multiple instances of the same observable are given to the same EmulationConfig.
- **`default_aggregation_method`** (`AggregationMethod`, default: `SKIP_WARN` ) –

  How to combine the values of this observable from multiple results.

Methods:

- **`__call__`** –

  Specifies a call to the observable at a specific time.
- **`apply`** –

  Calculates the observable to store in the Results.

Attributes:

- **`default_aggregation_method`** (`AggregationMethod`) –

  How the values from multiple results are combined.
- **`tag`** (`str`) –

  Label for the observable, used to index the Results object.
- **`uuid`** (`UUID`) –

  A universal unique identifier for this instance.

#### default\_aggregation\_method

```
default_aggregation_method: AggregationMethod
```

How the values from multiple results are combined.

#### tag

```
tag: str
```

Label for the observable, used to index the Results object.

Within a Results instance, all computed observables must have different tags.

Returns:

- `str` –

  The tag of the observable.

#### uuid

```
uuid: UUID
```

A universal unique identifier for this instance.

#### \_\_call\_\_

```
__call__(
    config: EmulationConfig,
    t: float,
    state: State,
    hamiltonian: Operator,
    result: Results,
) -> None
```

Specifies a call to the observable at a specific time.

This is called after each time step performed by the emulator. By default it calls `apply()` to compute a result and put it in Results if t in self.evaluation\_times. It can be overloaded to define general callbacks that don't put results in the Results object.

Parameters:

- **`config`** (`EmulationConfig`) –

  The config object passed to the backend.
- **`t`** (`float`) –

  The relative time as a float between 0 and 1.
- **`state`** (`State`) –

  The current state.
- **`hamiltonian`** (`Operator`) –

  The Hamiltonian at this time.
- **`result`** (`Results`) –

  The Results object to store the result in.

#### apply

```
apply(*, state: StateType, **kwargs: Any) -> StateType
```

Calculates the observable to store in the Results.

### get\_batch\_id

```
get_batch_id(job: Job[Results]) -> str
```

Return the batch ID associated with a remote job.

Temporary utility for cases where *batch\_id* must be persisted and later passed to :func:`retrieve_remote_job`. Will be deprecated once `RemoteConnection` supports direct job lookup by job ID alone.

Parameters:

- **`job`** (`Job[Results]`) –

  Any :class:`Job` instance.

Returns:

- **`str`** ( `str` ) –

  The batch ID if *job* is a :class:`_RemoteJob`,
- `str` –

  otherwise an empty string.

### retrieve\_remote\_job

```
retrieve_remote_job(
    connection: RemoteConnection,
    job_id: str,
    *,
    batch_id: str = "",
) -> Job[Results]
```

Retrieve a previously submitted remote job by its identifiers.

Use this to reconnect to a job in a new session, or to monitor a job submitted outside the current context.

> [!NOTE]
>
> The *batch\_id* argument is required by some `RemoteConnection` implementations (e.g. `PasqalCloudConnection`) to query job progress. Use :func:`get_batch_id` to recover the batch ID from an existing :class:`Job` if needed.
>
> This dependency on *batch\_id* is temporary and will be removed once `RemoteConnection` supports direct lookup by job ID alone.

Parameters:

- **`connection`** (`RemoteConnection`) –

  The remote connection through which to query the job.
- **`job_id`** (`str`) –

  The UUID of the job to retrieve.
- **`batch_id`** (`str`, default: `''` ) –

  The batch identifier the job belongs to. Defaults to an empty string.

Returns:

- `Job[Results]` –

  Job\[Results\]: A :class:`_RemoteJob` connected to the
- `Job[Results]` –

  specified job.
