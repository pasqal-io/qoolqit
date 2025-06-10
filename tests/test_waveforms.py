from __future__ import annotations

import random

import numpy as np
import pytest

from qoolqit.utils import EQUAL
from qoolqit.waveforms import (
    CompositeWaveform,
    Constant,
    Delay,
    PiecewiseLinear,
    Ramp,
    Sin,
    Waveform,
)


def test_delay() -> None:
    with pytest.raises(ValueError):
        wf = Delay(duration=0.0)

    with pytest.raises(ValueError):
        wf = Delay(duration=-1.0)

    duration = 1.0
    wf = Delay(duration)

    t_val = random.random()

    assert wf.duration == duration
    assert wf(t_val) == 0.0
    assert wf.max() == 0.0
    assert wf.min() == 0.0


def test_constant() -> None:
    duration = 1.0
    value = random.random()

    wf = Constant(duration, value)

    assert wf.value == value

    t_val = random.random()

    assert wf(0.0 - t_val) == 0.0
    assert wf(t_val) == value
    assert wf(duration + t_val) == 0.0
    assert wf.max() == value
    assert wf.min() == value

    n_points = 10
    t_array = np.random.rand(n_points)
    assert isinstance(wf(t_array), np.ndarray)
    assert len(wf(t_array)) == n_points

    t_list = [random.random() for i in range(n_points)]
    assert isinstance(wf(t_list), list)
    assert len(wf(t_list)) == n_points


def test_ramp() -> None:
    duration = 1.0
    initial_value = random.random()
    final_value = random.random()
    wf = Ramp(duration, initial_value, final_value)

    t_val = random.random()

    assert wf.initial_value == initial_value
    assert wf.final_value == final_value
    min_val, max_val = min([initial_value, final_value]), max([initial_value, final_value])
    value: float = wf(t_val)
    assert min_val <= value <= max_val
    assert wf.max() == max_val
    assert wf.min() == min_val


def test_sin() -> None:
    duration = 1.0
    amplitude = random.random()
    omega = random.random()
    phi = random.random()
    shift = random.random()

    wf = Sin(duration, amplitude, omega, phi, shift)

    assert wf.amplitude == amplitude
    assert wf.omega == omega
    assert wf.phi == phi
    assert wf.shift == shift

    n_points = 100
    t_array = t_array = np.random.uniform(low=-1.0, high=2.0, size=(n_points,))
    approx_max = wf.max()
    approx_min = wf.min()
    random_samples_max = np.max(wf(t_array))
    random_samples_min = np.min(wf(t_array))
    assert (approx_max > random_samples_max) or EQUAL(approx_max, random_samples_max, atol=1e-05)
    assert (approx_min > random_samples_min) or EQUAL(approx_min, random_samples_min, atol=1e-05)


@pytest.mark.parametrize("n_pieces", [3, 4, 5])
def test_piecewise(n_pieces: int) -> None:

    durations = [1.0 for _ in range(n_pieces)]
    values = np.random.rand(n_pieces + 1)

    with pytest.raises(ValueError):
        wf = PiecewiseLinear([1.0], values)

    with pytest.raises(TypeError):
        wf = PiecewiseLinear(1.0, values)  # type: ignore [arg-type]

    with pytest.raises(ValueError):
        durations[0] = 0.0
        wf = PiecewiseLinear(durations, values)

    durations[0] = 1.0
    wf = PiecewiseLinear(durations, values)

    assert wf.n_waveforms == n_pieces


@pytest.mark.parametrize("n_waveforms", [3, 4, 5])
def test_waveform_composition(n_waveforms: int) -> None:

    duration = 1.0

    wf: Waveform = Ramp(1.0, random.random(), random.random())

    for _ in range(n_waveforms - 1):
        wf = wf >> Ramp(1.0, random.random(), random.random())

    wf = wf >> wf

    with pytest.raises(NotImplementedError):
        wf >> 1.0  # type: ignore [operator]

    assert isinstance(wf, CompositeWaveform)
    assert wf.n_waveforms == 2 * n_waveforms
    assert EQUAL(wf.duration, 2 * n_waveforms * duration)
    assert len(wf.durations) == 2 * n_waveforms
    assert len(wf.times) == 2 * n_waveforms + 1

    n_points = 100
    t_array = np.random.uniform(low=-1.0, high=2.0 * duration * n_waveforms + 1.0, size=(n_points,))
    approx_max = wf.max()
    approx_min = wf.min()
    random_samples_max = np.max(wf(t_array))
    random_samples_min = np.min(wf(t_array))
    assert (approx_max > random_samples_max) or EQUAL(approx_max, random_samples_max, atol=1e-05)
    assert (approx_min > random_samples_min) or EQUAL(approx_min, random_samples_min, atol=1e-05)

    with pytest.raises(TypeError):
        CompositeWaveform(wf, 1.0)  # type: ignore [arg-type]
    with pytest.raises(ValueError):
        CompositeWaveform()
