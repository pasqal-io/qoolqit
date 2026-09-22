from __future__ import annotations

import math

import numpy as np
import pytest

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
        Drive()  # type: ignore [call-arg]

    with pytest.raises(TypeError, match="missing 1 required keyword-only argument: 'amplitude'"):
        Drive(detuning=ConstantWaveform(duration=10, value=1.0))  # type: ignore [call-arg]

    with pytest.raises(TypeError, match="'amplitude' and 'detuning' must be of type Waveform."):
        drive = Drive(amplitude=1.0, detuning=det_wf)  # type: ignore [arg-type]

    with pytest.raises(TypeError, match="'amplitude' and 'detuning' must be of type Waveform."):
        drive = Drive(amplitude=amp_wf, detuning=1.0)  # type: ignore [arg-type]

    with pytest.raises(ValueError, match="'amplitude' must be positive."):
        drive = Drive(amplitude=det_wf)

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
    phase_1 = math.pi / 2
    amp_2 = RampWaveform(5.0, 1.0, 0.0)
    det_2 = RampWaveform(5.0, 1.0, 0.0)
    phase_2 = 0.0

    drive_1 = Drive(amplitude=amp_1, detuning=det_1, phase=phase_1)
    drive_2 = Drive(amplitude=amp_2, detuning=det_2, phase=phase_2)

    composite_drive = drive_1 >> drive_2

    expected_duration = drive_1.duration + drive_2.duration
    np.testing.assert_allclose(composite_drive.duration, expected_duration)

    assert composite_drive._phase_groups == [
        (drive_1._amplitude, drive_1._detuning, phase_1),
        (drive_2._amplitude, drive_2._detuning, phase_2),
    ]


def test_drive_chained_phase_composition() -> None:
    amp_1 = RampWaveform(10.0, 0.0, 1.0)
    det_1 = RampWaveform(10.0, 0.0, 1.0)
    phase_1 = math.pi
    amp_2 = RampWaveform(5.0, 1.0, 0.0)
    det_2 = RampWaveform(5.0, 1.0, 0.0)
    phase_2 = 0.0
    amp_3 = RampWaveform(8.0, 0.0, 0.5)
    det_3 = RampWaveform(8.0, 0.0, 0.5)
    phase_3 = 0.343

    drive_1 = Drive(amplitude=amp_1, detuning=det_1, phase=phase_1)
    drive_2 = Drive(amplitude=amp_2, detuning=det_2, phase=phase_2)
    drive_3 = Drive(amplitude=amp_3, detuning=det_3, phase=phase_3)

    composite_drive = drive_1 >> drive_2 >> drive_3

    expected_duration = drive_1.duration + drive_2.duration + drive_3.duration
    np.testing.assert_allclose(composite_drive.duration, expected_duration)

    assert composite_drive._phase_groups == [
        (drive_1._amplitude, drive_1._detuning, phase_1),
        (drive_2._amplitude, drive_2._detuning, phase_2),
        (drive_3._amplitude, drive_3._detuning, phase_3),
    ]


def test_drive_phase_composition_with_padded_waveforms() -> None:
    # when amplitude and detuning have different durations, Drive pads the shorter one to
    # get equal duration. The phase groups must carry the padded waveforms.
    amp_1 = RampWaveform(10.0, 0.0, 1.0)
    det_1 = RampWaveform(5.0, 0.0, 1.0)
    amp_2 = RampWaveform(4.0, 1.0, 0.0)
    det_2 = RampWaveform(4.0, -1.0, 0.0)

    drive_1 = Drive(amplitude=amp_1, detuning=det_1, phase=math.pi / 2)
    drive_2 = Drive(amplitude=amp_2, detuning=det_2, phase=0.0)

    composite_drive = drive_1 >> drive_2

    group_1_amp, group_1_det, _ = composite_drive._phase_groups[0]
    group_2_amp, group_2_det, _ = composite_drive._phase_groups[1]

    # both waveforms of a group span the whole segment
    np.testing.assert_allclose(group_1_amp.duration, drive_1.duration)
    np.testing.assert_allclose(group_1_det.duration, drive_1.duration)
    np.testing.assert_allclose(group_2_amp.duration, drive_2.duration)
    np.testing.assert_allclose(group_2_det.duration, drive_2.duration)

    # the longer amplitude is carried over untouched
    times = np.linspace(0.0, drive_1.duration, 20)
    np.testing.assert_allclose(group_1_amp(times), drive_1.amplitude(times))

    # the shorter detuning keeps its own values, then the padding holds it at zero
    times_det = np.linspace(0.0, det_1.duration, 10, endpoint=False)
    np.testing.assert_allclose(group_1_det(times_det), drive_1.detuning(times_det))

    times_padding = np.linspace(det_1.duration, drive_1.duration, 10)
    np.testing.assert_allclose(group_1_det(times_padding), 0.0)

    # the second group needs no padding, so it holds the original waveforms
    times_2 = np.linspace(0.0, drive_2.duration, 20)
    np.testing.assert_allclose(group_2_amp(times_2), drive_2.amplitude(times_2))
    np.testing.assert_allclose(group_2_det(times_2), drive_2.detuning(times_2))


@pytest.mark.parametrize("phase", [math.pi, 0.0, np.pi / 2])
def test_drive_same_phase_composition(phase: float) -> None:
    amp = RampWaveform(10.0, 0.0, 1.0)
    det = RampWaveform(10.0, 0.0, 1.0)

    drive_1 = Drive(amplitude=amp, detuning=det, phase=phase)
    drive_2 = Drive(amplitude=amp, detuning=det, phase=phase)

    composite_drive = drive_1 >> drive_2

    np.testing.assert_allclose(composite_drive.duration, drive_1.duration + drive_2.duration)
    phases = [phase for _, _, phase in composite_drive._phase_groups]
    assert phases == [phase, phase]


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


def test_error_amplitude_negative() -> None:
    with pytest.raises(ValueError, match="'amplitude' must be positive."):
        neg_ramp = RampWaveform(10.0, -1.0, 2.0)
        Drive(amplitude=neg_ramp, detuning=neg_ramp)


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
        DetuningMapModulator(negative_wf, weights=invalid_weights)

    with pytest.raises(ValueError, match="`waveform` must be negative for all times."):
        DetuningMapModulator(positive_wf, weights=valid_weights)

    dmm = DetuningMapModulator(negative_wf, weights=valid_weights)
    assert isinstance(dmm.waveform, RampWaveform)
    assert dmm.weights == valid_weights
