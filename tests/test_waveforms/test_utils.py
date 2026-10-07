from __future__ import annotations

import random

import pytest

from qoolqit.waveforms.utils import round_to_sum


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
