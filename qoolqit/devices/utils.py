from __future__ import annotations

from qoolqit.utils import StrEnum


class AvailableDevices(StrEnum):

    MOCK = "MockDevice"
    ANALOG = "AnalogDevice"
    DigitalAnalogDevice = "DigitalAnalogDevice"
    TEST_ANALOG = "TestAnalogDevice"
