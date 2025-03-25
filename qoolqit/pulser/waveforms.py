from __future__ import annotations

from pulser.waveforms import BlackmanWaveform as _BlackmanWaveform
from pulser.waveforms import CompositeWaveform as _CompositeWaveform
from pulser.waveforms import ConstantWaveform as _ConstantWaveform
from pulser.waveforms import CustomWaveform as _CustomWaveform
from pulser.waveforms import InterpolatedWaveform as _InterpolatedWaveform
from pulser.waveforms import KaiserWaveform as _KaiserWaveform
from pulser.waveforms import RampWaveform as _RampWaveform
from pulser.waveforms import Waveform


class WaveformMixin(Waveform):
    def __mul__(self, other: Waveform) -> Waveform:
        if isinstance(other, Waveform):
            return CompositeWaveform(self, other)
        else:
            raise NotImplementedError


class CompositeWaveform(_CompositeWaveform):
    def __mul__(self, other: Waveform) -> Waveform:
        if isinstance(other, _CompositeWaveform):
            return CompositeWaveform(*self.waveforms, *other.waveforms)
        elif isinstance(other, Waveform):
            return CompositeWaveform(*self.waveforms, other)
        else:
            raise NotImplementedError

    def __rmul__(self, other: Waveform) -> Waveform:
        return self.__mul__(other)


class RampWaveform(WaveformMixin, _RampWaveform):
    pass


class CustomWaveform(WaveformMixin, _CustomWaveform):
    pass


class ConstantWaveform(WaveformMixin, _ConstantWaveform):
    pass


class BlackmanWaveform(WaveformMixin, _BlackmanWaveform):
    pass


class InterpolatedWaveform(WaveformMixin, _InterpolatedWaveform):
    pass


class KaiserWaveform(WaveformMixin, _KaiserWaveform):
    pass


class PWLWaveform(CompositeWaveform):
    """
    A piecewise linear waveform.

    Arguments:
        durations: List or tuple of N duration values.
        values: List or tuple of N+1 waveform values.
    """

    def __init__(
        self,
        durations: list | tuple,
        values: list | tuple,
    ):
        if not (isinstance(durations, (list, tuple)) or isinstance(values, (list, tuple))):
            raise TypeError("A PWLWaveform requires a list or tuple of durations and values.")

        if len(durations) + 1 != len(values) or len(durations) == 1:
            raise ValueError("A PWLWaveform requires N durations and N + 1 values, for N >= 2.")

        self.durations = durations
        self.values = values

        wfs = [RampWaveform(dur, values[i], values[i + 1]) for i, dur in enumerate(self.durations)]

        super().__init__(*wfs)

    @property
    def n_pieces(self) -> int:
        return len(self.durations)

    def __repr__(self) -> str:
        intervals = [
            f"{wf._duration}: {float(wf._start):.3g}->{float(wf._stop):.3g}"
            for wf in self.waveforms
        ]
        string = ""
        for i, interval in enumerate(intervals):
            string += interval
            if i != len(intervals) - 1:
                string += ", "
        return self.__class__.__name__ + "(" + string + ")"
