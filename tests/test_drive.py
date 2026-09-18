from __future__ import annotations

import math

import matplotlib.pyplot as plt
import numpy as np
import pytest
from matplotlib.figure import Figure

from qoolqit.drive import DetuningMapModulator, Drive
from qoolqit.waveforms import ConstantWaveform, DelayWaveform, PiecewiseLinearWaveform, RampWaveform
from qoolqit.waveforms.base_waveforms import Waveform


@pytest.mark.parametrize(
    "amp_wf, det_wf",
    [
        (RampWaveform(10.0, 1.0, 0.0), RampWaveform(12.1, -2.1, 2.1)),
        (
            ConstantWaveform(10.0, math.pi),
            PiecewiseLinearWaveform(
                [4.60132814, 4.18237748, 5.21984795, 3.5963718],
                [0.1443786, -0.2027756, 0.46146151, 0.07375925, 0.52915184],
            ),
        ),
    ],
)
def test_drive_init_and_composition(amp_wf: Waveform, det_wf: Waveform) -> None:

    with pytest.raises(TypeError, match="missing 1 required keyword-only argument: 'amplitude'"):
        _ = Drive()  # type: ignore [call-arg]

    with pytest.raises(TypeError, match="missing 1 required keyword-only argument: 'amplitude'"):
        _ = Drive(detuning=ConstantWaveform(duration=10, value=1.0))  # type: ignore [call-arg]

    with pytest.raises(TypeError, match="'amplitude' and 'detuning' must be of type Waveform."):
        _ = Drive(amplitude=1.0, detuning=det_wf)  # type: ignore [arg-type]

    with pytest.raises(TypeError, match="'amplitude' and 'detuning' must be of type Waveform."):
        _ = Drive(amplitude=amp_wf, detuning=1.0)  # type: ignore [arg-type]

    with pytest.raises(ValueError, match="'amplitude' must be positive."):
        _ = Drive(amplitude=det_wf)

    drive = Drive(amplitude=amp_wf, detuning=det_wf)

    with pytest.raises(
        NotImplementedError, match="Composing with object of type <class 'float'> not supported."
    ):
        drive >> 1.0  # type: ignore [operator]

    duration_amp = amp_wf.duration
    duration_det = det_wf.duration

    assert math.isclose(drive.duration, max([duration_amp, duration_det]))

    drive = drive >> drive
    assert math.isclose(drive.duration, 2.0 * max([duration_amp, duration_det]))

    drive = drive >> drive
    assert math.isclose(drive.duration, 4.0 * max([duration_amp, duration_det]))

    drive = Drive(amplitude=amp_wf)
    assert isinstance(drive.detuning, DelayWaveform)
    assert math.isclose(drive.duration, duration_amp)


def test_drive_different_phase_composition() -> None:
    amp_1 = RampWaveform(10.0, 0.0, 1.0)
    det_1 = RampWaveform(10.0, 0.0, 1.0)
    amp_2 = RampWaveform(5.0, 1.0, 0.0)
    det_2 = RampWaveform(5.0, 1.0, 0.0)

    drive_1 = Drive(amplitude=amp_1, detuning=det_1, phase=math.pi)
    drive_2 = Drive(amplitude=amp_2, detuning=det_2, phase=0.0)

    composite = drive_1 >> drive_2

    assert math.isclose(composite.duration, drive_1.duration + drive_2.duration)

    assert len(composite._phase_groups) == 2
    group_1_amp, group_1_det, group_1_phase = composite._phase_groups[0]
    group_2_amp, group_2_det, group_2_phase = composite._phase_groups[1]

    assert math.isclose(group_1_phase, math.pi)
    assert math.isclose(group_2_phase, 0.0)

    assert math.isclose(group_1_amp.duration, drive_1.duration)
    assert math.isclose(group_2_amp.duration, drive_2.duration)

    t_1 = np.linspace(0.0, drive_1.duration, 20)
    assert np.allclose(group_1_amp(t_1), drive_1.amplitude(t_1))
    assert np.allclose(group_1_det(t_1), drive_1.detuning(t_1))

    t_2 = np.linspace(0.0, drive_2.duration, 20)
    assert np.allclose(group_2_amp(t_2), drive_2.amplitude(t_2))
    assert np.allclose(group_2_det(t_2), drive_2.detuning(t_2))


def test_drive_chained_phase_composition() -> None:
    amp_1 = RampWaveform(10.0, 0.0, 1.0)
    det_1 = RampWaveform(10.0, 0.0, 1.0)
    amp_2 = RampWaveform(5.0, 1.0, 0.0)
    det_2 = RampWaveform(5.0, 1.0, 0.0)
    amp_3 = RampWaveform(8.0, 0.0, 0.5)
    det_3 = RampWaveform(8.0, 0.0, 0.5)

    drive_1 = Drive(amplitude=amp_1, detuning=det_1, phase=math.pi)
    drive_2 = Drive(amplitude=amp_2, detuning=det_2, phase=0.0)
    drive_3 = Drive(amplitude=amp_3, detuning=det_3, phase=math.pi / 2)

    composite = drive_1 >> drive_2 >> drive_3

    assert math.isclose(composite.duration, drive_1.duration + drive_2.duration + drive_3.duration)

    assert len(composite._phase_groups) == 3
    phases = [phase for _, _, phase in composite._phase_groups]
    assert phases == [math.pi, 0.0, math.pi / 2]

    durations = [amp.duration for amp, _, _ in composite._phase_groups]
    assert durations == [drive_1.duration, drive_2.duration, drive_3.duration]


def test_drive_same_phase_composition() -> None:
    amp = RampWaveform(10.0, 0.0, 1.0)
    det = RampWaveform(10.0, 0.0, 1.0)

    drive_1 = Drive(amplitude=amp, detuning=det, phase=math.pi)
    drive_2 = Drive(amplitude=amp, detuning=det, phase=math.pi)

    composite = drive_1 >> drive_2

    assert math.isclose(composite.duration, drive_1.duration + drive_2.duration)
    phases = [phase for _, _, phase in composite._phase_groups]
    assert phases == [math.pi, math.pi]


def test_drive_composition_with_dmm_not_supported() -> None:
    amp = RampWaveform(10.0, 0.0, 1.0)
    det = RampWaveform(10.0, 0.0, 1.0)
    dmm = DetuningMapModulator(RampWaveform(10.0, -1.0, -2.0), weights={0: 1.0})

    drive = Drive(amplitude=amp, detuning=det)
    drive_with_dmm = Drive(amplitude=amp, detuning=det, dmm=dmm)

    with pytest.raises(NotImplementedError, match="Composing drives with a dmm is not supported."):
        drive >> drive_with_dmm

    with pytest.raises(NotImplementedError, match="Composing drives with a dmm is not supported."):
        drive_with_dmm >> drive

    with pytest.raises(NotImplementedError, match="Composing drives with a dmm is not supported."):
        drive_with_dmm >> drive_with_dmm


def test_drive_draw_plain_drive() -> None:
    amp = RampWaveform(10.0, 0.0, 1.0)
    det = RampWaveform(10.0, 0.0, 1.0)
    drive = Drive(amplitude=amp, detuning=det)

    plt.close("all")
    drive.draw()
    plt.close("all")


def test_drive_draw_adds_phase_row_for_nonzero_phase() -> None:
    amp = RampWaveform(10.0, 0.0, 1.0)
    det = RampWaveform(10.0, 0.0, 1.0)

    zero_phase = Drive(amplitude=amp, detuning=det, phase=0.0) >> Drive(
        amplitude=amp, detuning=det, phase=0.0
    )
    nonzero_phase = Drive(amplitude=amp, detuning=det, phase=math.pi) >> Drive(
        amplitude=amp, detuning=det, phase=0.0
    )

    plt.close("all")
    zero_phase.draw()
    n_axes_zero_phase = len(plt.gcf().axes)
    plt.close("all")

    nonzero_phase.draw()
    n_axes_nonzero_phase = len(plt.gcf().axes)
    plt.close("all")

    assert n_axes_nonzero_phase == n_axes_zero_phase + 1


def test_drive_draw_uses_pyplot_figure_by_default() -> None:
    amp = RampWaveform(10.0, 0.0, 1.0)
    det = RampWaveform(10.0, 0.0, 1.0)
    drive = Drive(amplitude=amp, detuning=det)

    plt.close("all")
    assert plt.get_fignums() == []
    drive.draw()
    assert plt.get_fignums() != []
    plt.close("all")

    # an explicit figure can still be provided and is drawn on directly.
    fig = Figure()
    drive.draw(fig=fig)
    assert len(fig.axes) > 0


def test_error_amplitude_negative() -> None:
    with pytest.raises(ValueError, match="'amplitude' must be positive."):
        neg_ramp = RampWaveform(10.0, -1.0, 2.0)
        _ = Drive(amplitude=neg_ramp, detuning=neg_ramp)


@pytest.mark.parametrize("amp_duration, det_duration", [(1.0, 1.005), (20.0, 10.0)])
def test_drive_duration_with_delays(amp_duration: float, det_duration: float) -> None:
    amp_wf = RampWaveform(amp_duration, 1.0, 0.0)
    det_wf = RampWaveform(det_duration, -1.0, 0.0)
    drive = Drive(amplitude=amp_wf, detuning=det_wf)
    assert drive.duration == max(amp_duration, det_duration)


def test_dmm_init() -> None:
    positive_wf = RampWaveform(10.0, -10.0, 1.0)
    negative_wf = RampWaveform(10.0, -1.0, -2.0)

    valid_weights = {0: 0.1, 1: 0.2, 2: 0.3}
    invalid_weights = {0: 1.1, 1: 0.3}

    with pytest.raises(ValueError, match="`weights` must be a dictionary of values in \\[0, 1\\]."):
        _ = DetuningMapModulator(negative_wf, weights=invalid_weights)

    with pytest.raises(ValueError, match="`waveform` must be negative for all times."):
        _ = DetuningMapModulator(positive_wf, weights=valid_weights)

    dmm = DetuningMapModulator(negative_wf, weights=valid_weights)
    assert isinstance(dmm.waveform, RampWaveform)
    assert dmm.weights == valid_weights
