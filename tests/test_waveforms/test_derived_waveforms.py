from __future__ import annotations

import random

import numpy as np
import pulser
import pytest
from numpy.typing import ArrayLike
from scipy.integrate import quad

from qoolqit.waveforms import (
    BlackmanWaveform,
    CompositeWaveform,
    ConstantWaveform,
    DelayWaveform,
    InterpolatedWaveform,
    PiecewiseLinearWaveform,
    RampWaveform,
    Waveform,
)
from qoolqit.waveforms.utils import round_to_sum


def test_delay_init() -> None:
    with pytest.raises(ValueError):
        DelayWaveform(duration=0.0)

    with pytest.raises(ValueError):
        DelayWaveform(duration=-1.0)

    duration = 2.1
    wf = DelayWaveform(duration)

    assert wf.duration == duration

    t_val = [0.0, 0.1, 0.2, 1.3, 2.0, 2.1]
    np.testing.assert_array_equal(wf(t_val), 0.0)


def test_delay_min_max() -> None:
    wf = DelayWaveform(duration=1.0)
    assert wf.min() == 0.0
    assert wf.max() == 0.0


def test_delay_mul() -> None:
    wf = DelayWaveform(duration=1.0)
    scaled = wf * 2.0
    assert scaled is wf


def test_delay_to_pulser() -> None:
    wf = DelayWaveform(duration=1.0)
    pulser_duration = 100
    pulser_wf = wf._to_pulser(duration=pulser_duration)
    assert isinstance(pulser_wf, pulser.ConstantWaveform)
    assert pulser_wf.duration == pulser_duration
    assert np.all(pulser_wf.samples == 0.0)


def test_constant_init() -> None:
    wf = ConstantWaveform(10.0, value=2.7)
    assert wf.duration == 10.0
    assert wf.value == 2.7


@pytest.mark.parametrize(
    "duration, times",
    [
        (1.57843, np.random.uniform(0.0, 1.57843, size=10)),
        (11.7, [11.7 * random.random() for _ in range(11)]),
    ],
)
def test_constant_samples(duration: float, times: list[float] | np.ndarray) -> None:
    value = 2.3
    wf = ConstantWaveform(duration, value=value)

    wf_samples = wf(times)
    assert isinstance(wf_samples, type(times))
    assert len(wf_samples) == len(times)

    np.testing.assert_allclose(wf_samples, value)
    assert all(val <= wf.max() for val in wf_samples)
    assert all(val >= wf.min() for val in wf_samples)


def test_constant_min_max() -> None:
    wf = ConstantWaveform(duration=1.0, value=np.pi)
    assert wf.min() == np.pi
    assert wf.max() == np.pi


def test_constant_mul() -> None:
    wf = ConstantWaveform(duration=1.0, value=np.pi)
    scaled = wf * 2.0
    assert scaled is not wf
    assert isinstance(scaled, ConstantWaveform)
    assert scaled.duration == wf.duration
    assert scaled.value == wf.value * 2.0


def test_ramp_init() -> None:
    wf = RampWaveform(duration=5.0, initial_value=-1.3, final_value=1.0)
    assert wf.duration == 5.0
    assert wf.initial_value == -1.3
    assert wf.final_value == 1.0


def test_ramp_samples() -> None:
    wf = RampWaveform(duration=5.0, initial_value=-1.3, final_value=1.0)
    times = np.linspace(0.0, 5.0, 100)
    samples = wf(times)
    assert isinstance(samples, np.ndarray)
    assert len(samples) == len(times)
    assert np.all(samples >= wf.min())
    assert np.all(samples <= wf.max())


def test_ramp_min_max() -> None:
    wf = RampWaveform(duration=5.0, initial_value=-1.3, final_value=1.0)
    assert wf.min() == -1.3
    assert wf.max() == 1.0


def test_ramp_mul() -> None:
    wf = RampWaveform(duration=5.0, initial_value=-1.3, final_value=1.0)
    scaled = wf * 2.0
    assert scaled is not wf
    assert isinstance(scaled, RampWaveform)
    assert scaled.duration == wf.duration
    assert scaled.initial_value == wf.initial_value * 2.0
    assert scaled.final_value == wf.final_value * 2.0


def test_blackman_init() -> None:
    area = 1.5 * np.pi
    wf = BlackmanWaveform(duration=11.0, area=area)
    assert wf.duration == 11.0
    assert wf.area == area
    assert wf.params == {"area": area}

    # test area as integral
    res, _ = quad(wf, 0.0, wf.duration)
    assert np.isclose(res, area)


def test_blackman_samples() -> None:
    wf = BlackmanWaveform(duration=1.0, area=np.pi)
    times = np.linspace(0.0, wf.duration, 25)
    samples = wf(times)
    assert isinstance(samples, np.ndarray)
    assert np.all(samples >= wf.min())
    assert np.all(samples <= wf.max())


def test_blackman_min_max() -> None:
    wf = BlackmanWaveform(duration=5.0, area=np.pi)
    assert wf.min() == 0.0
    expected_max = wf.area / (0.42 * wf.duration)
    np.testing.assert_allclose(wf.max(), expected_max)


def test_blackman_mul() -> None:
    wf = BlackmanWaveform(duration=5.0, area=np.pi)
    scaled = wf * 3.0
    assert scaled is not wf
    assert isinstance(scaled, BlackmanWaveform)
    assert scaled.duration == wf.duration
    assert scaled.area == wf.area * 3.0


def test_blackman_to_pulser() -> None:
    duration = 11.0
    area = 1.5 * np.pi
    blackman = BlackmanWaveform(duration, area=area)
    pulser_blackman = blackman._to_pulser(duration=200)
    assert isinstance(pulser_blackman, pulser.BlackmanWaveform)
    assert pulser_blackman.duration == 200
    assert pulser_blackman._area == area


@pytest.mark.parametrize("n_pieces", [3, 4, 5])
def test_piecewise_init(n_pieces: int) -> None:

    durations = [1.0 for _ in range(n_pieces)]
    values = np.random.rand(n_pieces + 1).tolist()

    with pytest.raises(ValueError):
        wf = PiecewiseLinearWaveform([1.0], values)

    with pytest.raises(TypeError):
        wf = PiecewiseLinearWaveform(1.0, values)  # type: ignore [arg-type]

    with pytest.raises(ValueError):
        durations[0] = 0.0
        wf = PiecewiseLinearWaveform(durations, values)

    durations[0] = 1.0
    wf = PiecewiseLinearWaveform(durations, values)

    assert wf.n_waveforms == n_pieces


def test_piecewise_samples() -> None:
    durations = np.array([1.0, 2.0, 3.0])
    values = np.array([-2.1, 5.3, 3.12, 1.04])
    wf = PiecewiseLinearWaveform(durations, values=values)
    times = np.linspace(0.0, wf.duration, 100)
    samples = wf(times)
    assert isinstance(samples, np.ndarray)
    assert len(samples) == len(times)
    assert np.all(samples >= wf.min())
    assert np.all(samples <= wf.max())


def test_piecewise_mul() -> None:
    wf = PiecewiseLinearWaveform([1.0, 2.0, 3.0], values=[-1.3, 1.0, 2.0, 3.0])
    scaled = wf * 2.0
    assert scaled is not wf
    assert isinstance(scaled, PiecewiseLinearWaveform)
    assert scaled.duration == wf.duration
    expected_values = np.array([-1.3, 1.0, 2.0, 3.0]) * 2.0
    np.testing.assert_allclose(scaled.values, expected_values)
    assert scaled.times == wf.times


def test_interpolated_samples() -> None:
    values = [-2.1, 5.3, 3.12, 1.04]
    duration = 100
    interpolated = InterpolatedWaveform(duration, values=values)

    expected_fractional_times = np.linspace(0, 1, len(values))
    np.testing.assert_allclose(interpolated._times, expected_fractional_times)

    waveform_times = duration * expected_fractional_times
    interpolated_values = interpolated(waveform_times)
    np.testing.assert_allclose(interpolated_values, values)
    assert all(val <= interpolated.max() for val in interpolated_values)
    assert all(val >= interpolated.min() for val in interpolated_values)


def test_interpolated_samples_with_times() -> None:
    values = [0.1, 0.3, -0.5, 1.0]
    times = [0.0, 0.2, 0.8, 1.0]
    duration = 100
    interpolated = InterpolatedWaveform(duration, values=values, times=times)

    waveform_times = duration * np.array(times, dtype=float)
    interpolated_values = interpolated(waveform_times)
    np.testing.assert_allclose(interpolated_values, values)
    assert all(val <= interpolated.max() for val in interpolated_values)
    assert all(val >= interpolated.min() for val in interpolated_values)


def test_interpolated_fractional_times() -> None:
    with pytest.raises(ValueError, match=r"must be in \[0,1\]."):
        InterpolatedWaveform(10, values=[0, 1], times=[0, 10])


def test_interpolated_wrong_times_len() -> None:
    with pytest.raises(ValueError, match="must be arrays of the same length."):
        InterpolatedWaveform(10, values=[0, 1], times=[0, 0.5, 0.8])


def test_interpolated_mul() -> None:
    values = np.array([3.15826815, 4.50277306, 3.38569084, 4.82395945, 1.41445813])
    scaling = 3.4

    wf = InterpolatedWaveform(3.45, values=values)
    scaled = wf * scaling
    assert scaled is not wf
    assert isinstance(scaled, InterpolatedWaveform)
    assert scaled.duration == wf.duration
    expected_values = values * scaling
    np.testing.assert_allclose(scaled._values, expected_values)


def test_interpolated_to_pulser() -> None:
    values = [0.1, 0.3, -0.5, 1.0, 5.7]
    interpolated = InterpolatedWaveform(20.46, values=values)

    pulser_interpolated = interpolated._to_pulser(duration=222)
    assert isinstance(pulser_interpolated, pulser.InterpolatedWaveform)
    assert pulser_interpolated.duration == 222


@pytest.mark.parametrize(
    "values", [[0.1, 0.3, -0.5, 1.0, 5.7], np.sin(np.linspace(0, 2 * np.pi, 10))]
)
@pytest.mark.parametrize("energy_factor", [0.5, 1.0, np.pi])
def test_interpolated_to_pulser_energy_factor(values: ArrayLike, energy_factor: float) -> None:
    interpolated = InterpolatedWaveform(20.46, values=values)

    pulser_interpolated = interpolated._to_pulser(duration=20, energy_factor=energy_factor)
    assert isinstance(pulser_interpolated, pulser.InterpolatedWaveform)

    # check that pulser values are scaled correctly, within the expected tolerance
    expected_pulser_values = np.array(values) * energy_factor
    np.testing.assert_allclose(pulser_interpolated._values, expected_pulser_values, atol=1e-8)

    # check that pulser samples are within the expected range
    min_value, max_value = expected_pulser_values.min(), expected_pulser_values.max()
    pulser_interpolated_samples = pulser_interpolated.samples
    assert np.all(pulser_interpolated_samples >= min_value)
    assert np.all(pulser_interpolated_samples <= max_value)


@pytest.mark.parametrize("n_waveforms", [3, 4, 5])
def test_waveform_composition(n_waveforms: int) -> None:

    duration = 1.0

    wf: Waveform = RampWaveform(1.0, random.random(), random.random())

    for _ in range(n_waveforms - 1):
        wf = wf >> RampWaveform(1.0, random.random(), random.random())

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

    with pytest.raises(TypeError, match="All arguments must be instances of Waveform."):
        CompositeWaveform(wf, 1.0)  # type: ignore [arg-type]
    with pytest.raises(
        NotImplementedError, match="Composing with object of type <class 'float'> not supported."
    ):
        wf >> 1.0  # type: ignore [operator]
    with pytest.raises(ValueError, match="At least one Waveform must be provided."):
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
        ConstantWaveform(-10.0, value=2.0)


def test_to_pulser_sub_ns_delay_single_wf() -> None:
    """
    Add a delay to a Waveform and test conversion to Pulser.

    Check that, when translated, the delay is ignored if lasts less than 1 ns.
    """
    qoolqit_duration = 2.83
    qoolqit_delay_duration = 0.004
    pulser_duration = 100

    # check that the added delay will be translated into a < 1 ns pulser delay
    pulser_delay_duration = (qoolqit_delay_duration / qoolqit_duration) * pulser_duration
    assert pulser_delay_duration < 1

    composite_waveform = CompositeWaveform(
        ConstantWaveform(2.83, 0.5), DelayWaveform(qoolqit_delay_duration)
    )
    pulser_waveform = composite_waveform._to_pulser(duration=pulser_duration)

    # assert that it is ignored when compiled to a pulser.Waveform without the delay
    assert isinstance(pulser_waveform, pulser.ConstantWaveform)
    assert pulser_waveform.duration == 100


def test_to_pulser_sub_ns_delay_composite_wf() -> None:
    """
    Add a delay to a CompositeWaveform and test conversion to Pulser.

    Check that, when translated, the delay is ignored if lasts less than 1 ns.
    """
    qoolqit_duration = 10.0
    qoolqit_delay_duration = 3.0e-4
    pulser_duration = 1223

    # check that the added delay will be translated into a < 1 ns pulser delay
    pulser_delay_duration = (qoolqit_delay_duration / qoolqit_duration) * pulser_duration
    assert pulser_delay_duration < 1

    composite_waveform = CompositeWaveform(
        ConstantWaveform(qoolqit_duration / 5, 0.5),
        RampWaveform(4 * qoolqit_duration / 5, -1.0, 1.3),
        DelayWaveform(qoolqit_delay_duration),
    )
    pulser_waveform = composite_waveform._to_pulser(duration=pulser_duration)

    # assert that it is ignored when compiled to a pulser.CompositeWaveform without the delay
    assert isinstance(pulser_waveform, pulser.CompositeWaveform)
    assert len(pulser_waveform.waveforms) == 2
    assert pulser_waveform.duration == 1223
