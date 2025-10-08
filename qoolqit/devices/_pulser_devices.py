from __future__ import annotations

import numpy as np
from pulser.channels import Rydberg
from pulser.channels.eom import RydbergBeam, RydbergEOM
from pulser.devices import AnalogDevice, DigitalAnalogDevice, MockDevice
from pulser.devices._device_datacls import Device
from pulser.register.special_layouts import TriangularLatticeLayout

"""The Pulser ideal device."""
_MockDevice = MockDevice

"""The Pulser analog device."""
_AnalogDevice = AnalogDevice

"""The Pulser digital-analog device."""
_DigitalAnalogDevice = DigitalAnalogDevice

"""Replicates the AnalogDevice but changes many parameters for testing."""
_TestAnalogDevice = Device(
    name="TestAnalogDevice",
    dimensions=2,
    rydberg_level=61,
    max_atom_num=80,
    max_radial_distance=38,
    min_atom_distance=4.5,
    max_sequence_duration=7500,
    max_runs=2000,
    requires_layout=True,
    accepts_new_layouts=True,
    optimal_layout_filling=0.45,
    channel_objects=(
        Rydberg.Global(
            max_abs_detuning=2 * np.pi * 15,
            max_amp=4 * np.pi * 2,
            clock_period=5,
            min_duration=16,
            mod_bandwidth=8,
            eom_config=RydbergEOM(
                limiting_beam=RydbergBeam.RED,
                max_limiting_amp=25 * 2 * np.pi,
                intermediate_detuning=470 * 2 * np.pi,
                mod_bandwidth=40,
                controlled_beams=(RydbergBeam.BLUE,),
                custom_buffer_time=240,
            ),
        ),
    ),
    pre_calibrated_layouts=(TriangularLatticeLayout(61, 5),),
    short_description="A realistic device for analog sequence execution.",
)
