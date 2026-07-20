"""Test the Waveform base class."""

from __future__ import annotations

import math

import numpy as np
import pytest
from pulser.waveforms import Waveform as PulserWaveform

from qoolqit.waveforms import CompositeWaveform, Waveform


class TestWaveform:
    """Test the base Waveform class.

    Methods `max`, `min`, `_to_pulser` are tested in the subclasses concrete implementation.

    Attributes:
        MockWaveform: A mock waveform for testing.
        SinWaveform: A sine waveform for testing.
    """

    class MockWaveform(Waveform):
        def function(self, t: float) -> float:
            return 2 * t + 1.0

        def max(self) -> float:
            raise NotImplementedError

        def min(self) -> float:
            raise NotImplementedError

        def __mul__(self, other: float) -> Waveform:
            raise NotImplementedError

        def _to_pulser(self, duration: int) -> PulserWaveform:
            raise NotImplementedError

    class SinWaveform(Waveform):
        amplitude: float

        def __init__(self, duration: float, amplitude: float) -> None:
            super().__init__(duration, amplitude=amplitude)

        def function(self, t: float) -> float:
            freq = np.pi / self.duration
            return self.amplitude * math.sin(freq * t)

        def max(self) -> float:
            raise NotImplementedError

        def min(self) -> float:
            raise NotImplementedError

        def __mul__(self, other: float) -> Waveform:
            raise NotImplementedError

        def _to_pulser(self, duration: int) -> PulserWaveform:
            raise NotImplementedError

    def test_waveform_init_stores_params(self) -> None:
        wf = self.MockWaveform(200.0, p1=2.0, p2=3.1)

        assert wf.duration == 200.0
        assert wf.params == {"p1": 2.0, "p2": 3.1}

    def test_waveform_init_rejects_positional_args(self) -> None:
        with pytest.raises(
            ValueError,
            match="Extra arguments in MockWaveform need to be passed as keyword arguments",
        ):
            self.MockWaveform(200.0, 2.0, 3.1)

    def test_positive_duration(self) -> None:
        with pytest.raises(ValueError, match="Duration needs to be a positive non-zero value."):
            self.MockWaveform(0.0)
        with pytest.raises(ValueError, match="Duration needs to be a positive non-zero value."):
            self.MockWaveform(-10.0)

    def test_call_outside_duration(self) -> None:
        wf = self.MockWaveform(1.0)

        # test boundaries
        assert wf(0.0) == wf.function(0.0)
        assert wf(1.0) == wf.function(1.0)

        # test out of bounds
        assert wf(-1.0) == 0.0
        assert wf(1.1) == 0.0

    def test_call(self) -> None:
        wf = self.MockWaveform(10.0)

        # scalar call
        assert wf(3.0) == wf.function(3.0)  # 2 * 3.0 + 1.0 = 7.0

        # list call returns a list with element-wise values
        result_list = wf([1.0, 2.0, 3.0])
        assert isinstance(result_list, list)
        assert result_list == [wf.function(t) for t in [1.0, 2.0, 3.0]]

        # ndarray call returns an ndarray with element-wise values
        t_array = np.array([1.0, 2.0, 3.0])
        result_array = wf(t_array)
        assert isinstance(result_array, np.ndarray)
        np.testing.assert_array_equal(result_array, np.array([wf.function(t) for t in t_array]))

    def test_composition(self) -> None:
        wf1 = self.MockWaveform(11.1)
        wf2 = self.SinWaveform(20.1, amplitude=0.5)

        wf_composed = wf1 >> wf2
        assert isinstance(wf_composed, CompositeWaveform)
        np.testing.assert_allclose(wf_composed.duration, 31.2, rtol=1e-9)

        wf_composer_waveforms = wf_composed.waveforms
        assert len(wf_composer_waveforms) == 2
        assert isinstance(wf_composer_waveforms[0], self.MockWaveform)
        assert isinstance(wf_composer_waveforms[1], self.SinWaveform)

    def test_composition_evaluates_correctly(self) -> None:
        wf1 = self.MockWaveform(11.1)
        wf2 = self.SinWaveform(20.1, amplitude=0.5)

        wf_composed = wf1 >> wf2

        # test out of bounds cases, expecting 0.0
        # t=-1.0 is before the left boundary: returns 0.0
        np.testing.assert_allclose(wf_composed(-1.0), 0.0)
        # t=40.2 is is beyond the right boundary: returns 0.0
        np.testing.assert_allclose(wf_composed(40.2), 0.0)

        # test within bounds cases
        # t=0.0 is the left boundary of wf1 (inclusive): local_t=0.0, function=2*0.0+1.0=1.0
        np.testing.assert_allclose(wf_composed(0.0), wf1.function(0.0))
        # t=5.0 is within wf1: local_t=5.0, function=2*5.0+1.0=11.0
        np.testing.assert_allclose(wf_composed(5.0), wf1.function(5.0))
        # t=11.1 is the start of wf2: local_t=0.0, function=0.5*sin(0)=0.0
        np.testing.assert_allclose(wf_composed(11.1), wf2.function(0.0))
        # t=21.1 is within wf2: local_t=10.0
        np.testing.assert_allclose(wf_composed(21.1), wf2.function(10.0))
        # t=31.2 is the right boundary of wf2 (inclusive): local_t=20.1
        np.testing.assert_allclose(wf_composed(31.2), wf2.function(20.1))

    def test_composition_order(self) -> None:
        wf1 = self.MockWaveform(11.1)
        wf2 = self.SinWaveform(20.1, amplitude=0.5)

        # order matters: wf2 >> wf1 is different from wf1 >> wf2
        wf_forward = wf1 >> wf2
        wf_reversed = wf2 >> wf1

        assert isinstance(wf_forward.waveforms[0], self.MockWaveform)
        assert isinstance(wf_reversed.waveforms[0], self.SinWaveform)
        np.testing.assert_allclose(wf_forward.duration, wf_reversed.duration, rtol=1e-9)

    def test_composition_flattens(self) -> None:
        wf1 = self.MockWaveform(5.0)
        wf2 = self.MockWaveform(10.0)
        wf3 = self.SinWaveform(15.0, amplitude=0.5)

        # chained composition should flatten into a single CompositeWaveform
        wf_composed = wf1 >> wf2 >> wf3
        assert isinstance(wf_composed, CompositeWaveform)
        assert len(wf_composed.waveforms) == 3
        np.testing.assert_allclose(wf_composed.duration, 30.0, rtol=1e-9)
