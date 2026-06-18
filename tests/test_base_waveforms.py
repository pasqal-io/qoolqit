from __future__ import annotations

import math
from unittest.mock import MagicMock

import numpy as np
import pytest
from pulser.waveforms import Waveform as PulserWaveform

from qoolqit.waveforms import CompositeWaveform, Waveform


class TestWaveform:
    """Test the base Waveform class."""

    class MockWaveform(Waveform):
        def function(self, t: float) -> float:
            return 2 * t

        def max(self) -> float:
            return 1.0

        def min(self) -> float:
            return 0.0

        def _to_pulser(self, duration: int) -> PulserWaveform:
            return MagicMock(spec=PulserWaveform)

    class SinWaveform(Waveform):
        amplitude: float

        def __init__(self, duration: float, amplitude: float) -> None:
            super().__init__(duration, amplitude=amplitude)

        def function(self, t: float) -> float:
            freq = np.pi / self.duration
            return self.amplitude * math.sin(freq * t)

        def max(self) -> float:
            return self.amplitude

        def min(self) -> float:
            return 0.0

        def _to_pulser(self, duration: int) -> PulserWaveform:
            return MagicMock(spec=PulserWaveform)

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
        assert wf(3.0) == wf.function(3.0)  # 2 * 3.0 = 6.0

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

        # t=5.0 is within wf1: local_t=5.0, function=2*5.0=10.0
        np.testing.assert_allclose(wf_composed(5.0), wf1.function(5.0))
        # t=11.1 is the start of wf2: local_t=0.0, function=0.5*sin(0)=0.0
        np.testing.assert_allclose(wf_composed(11.1), wf2.function(0.0))
        # t=21.1 is within wf2: local_t=10.0
        np.testing.assert_allclose(wf_composed(21.1), wf2.function(10.0))

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
