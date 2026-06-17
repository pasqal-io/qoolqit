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

    def test_subclass_missing_abstract_methods(self) -> None:
        class MockWaveformMissingMethods(Waveform):
            def function(self, t: float) -> float:
                return t

        with pytest.raises(
            Exception,
            match=(
                "Can't instantiate abstract class MockWaveformMissingMethods "
                "without an implementation for abstract methods '_to_pulser', 'max', 'min'"
            ),
        ):
            MockWaveformMissingMethods(10.0)  # type: ignore

    def test_waveform_init(self) -> None:
        wf = self.MockWaveform(200.0, p1=2.0, p2=3.1)

        assert wf.params == {"p1": 2.0, "p2": 3.1}
        assert wf.duration == 200.0

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
        assert wf(-1.0) == 0.0
        assert wf(1.0) == wf.function(1.0)
        assert wf(1.1) == 0.0

    def test_call(self) -> None:
        pass

    def test_composition(self) -> None:
        wf1 = self.MockWaveform(11.1)
        wf2 = self.SinWaveform(20.1, amplitude=0.5)

        wf_composed = wf1 >> wf2
        assert isinstance(wf_composed, CompositeWaveform)
        np.testing.assert_allclose(wf_composed.duration, 31.2)

        wf_composer_waveforms = wf_composed.waveforms
        assert len(wf_composer_waveforms) == 2
        assert isinstance(wf_composer_waveforms[0], self.MockWaveform)
        assert isinstance(wf_composer_waveforms[1], self.SinWaveform)
