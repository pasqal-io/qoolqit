from __future__ import annotations

import random

import numpy as np
import pytest

from qoolqit.waveforms import (
    CompositeWaveform,
    Constant,
    Delay,
    Interpolated,
    PiecewiseLinear,
    Ramp,
    Sin,
    Waveform,
)
from qoolqit.waveforms.utils import round_to_sum


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
    assert (approx_max > random_samples_max) or np.isclose(
        approx_max, random_samples_max, atol=1e-05
    )
    assert (approx_min > random_samples_min) or np.isclose(
        approx_min, random_samples_min, atol=1e-05
    )


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


@pytest.mark.parametrize("interpolator", ["PchipInterpolator", "interp1d"])
def test_interpolated(interpolator: str) -> None:
    values = [-2.1, 5.3, 3.12, 1.04]
    duration = 100
    interpolated = Interpolated(duration, values=values, interpolator=interpolator)

    expected_fractional_times = np.linspace(0, 1, len(values))
    assert np.allclose(interpolated._times, expected_fractional_times)

    waveform_times = duration * expected_fractional_times
    interpolated_values = interpolated(waveform_times)
    assert np.allclose(interpolated_values, values)


@pytest.mark.parametrize("interpolator", ["PchipInterpolator", "interp1d"])
def test_interpolated_with_times(interpolator: str) -> None:
    values = [0.1, 0.3, -0.5, 1.0]
    times = [0.0, 0.2, 0.8, 1.0]
    duration = 100
    interpolated = Interpolated(duration, values=values, times=times, interpolator=interpolator)

    waveform_times = duration * np.array(times, dtype=float)
    interpolated_values = interpolated(waveform_times)
    assert np.allclose(interpolated_values, values)


def test_interpolated_fractional_times() -> None:
    with pytest.raises(ValueError, match=r"must be in \[0,1\]."):
        Interpolated(10, values=[0, 1], times=[0, 10])


def test_interpolated_wrong_times_len() -> None:
    with pytest.raises(ValueError, match="must be arrays of the same length."):
        Interpolated(10, values=[0, 1], times=[0, 0.5, 0.8])


def test_interpolated_to_pulser() -> None:
    values = [0.1, 0.3, -0.5, 1.0, 5.7]
    interpolated = Interpolated(20.46, values=values)

    pulser_interpolated = interpolated._to_pulser(duration=222)
    assert pulser_interpolated.duration == 222


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
    assert np.isclose(wf.duration, 2 * n_waveforms * duration)
    assert len(wf.durations) == 2 * n_waveforms
    assert len(wf.times) == 2 * n_waveforms + 1

    # Testing composing directly with the class
    wf2 = CompositeWaveform(wf, wf)
    assert wf2.n_waveforms == 2 * wf.n_waveforms
    assert np.isclose(wf2.duration, 2 * wf.duration)
    assert len(wf2.durations) == 2 * len(wf.durations)
    assert len(wf2.times) == 2 * len(wf.times) - 1

    n_points = 100
    t_array = np.random.uniform(low=-1.0, high=2.0 * duration * n_waveforms + 1.0, size=(n_points,))
    approx_max = wf.max()
    approx_min = wf.min()
    random_samples_max = np.max(wf(t_array))
    random_samples_min = np.min(wf(t_array))
    assert (approx_max > random_samples_max) or np.isclose(
        approx_max, random_samples_max, atol=1e-05
    )
    assert (approx_min > random_samples_min) or np.isclose(
        approx_min, random_samples_min, atol=1e-05
    )

    with pytest.raises(TypeError):
        CompositeWaveform(wf, 1.0)  # type: ignore [arg-type]
    with pytest.raises(ValueError):
        CompositeWaveform()


@pytest.mark.parametrize(
    "values, expected",
    [
        ([10.3, 10.3, 10.4], [10, 10, 11]),
        ([1.5, 1.5, 1.5], [1, 1, 2]),
        ([20.7, 20.8, 20.9], [20, 21, 21]),
    ],
)
def test_round_to_sum(values: list[float], expected: list[int]) -> None:
    rounded_values = round_to_sum(values)
    assert sum(rounded_values) == round(sum(values))
    assert rounded_values == expected


def test_round_to_sum_random() -> None:
    values = [100 * random.random() for _ in range(20)]
    rounded_values = round_to_sum(values)
    assert sum(rounded_values) == round(sum(values))


def test_negative_duration() -> None:
    with pytest.raises(ValueError, match="Duration needs to be a positive non-zero value."):
        Constant(-10.0, value=2.0)


def test_waveform_only_kwarg() -> None:
    # mock waveform class
    class MockWaveform(Waveform):
        def function(self, t: float) -> float:
            return t

    wf = MockWaveform(200.0, p1=2.0, p2=3.1)
    assert wf.params == {"p1": 2.0, "p2": 3.1}

    with pytest.raises(
        ValueError,
        match="Extra arguments in MockWaveform need to be passed as keyword arguments",
    ):
        MockWaveform(200.0, 2.0, 3.1)
