from __future__ import annotations

import numpy as np


def round_to_sum(values: list[float]) -> list[int]:
    """Round a list of numbers such that their sum is the rounded sum.

    Σᵢround(aᵢ) = round(Σᵢaᵢ)

    Example:
        ```python
        >>> round_to_sum([100.3, 100.3, 100.4])
        >>> [100, 100, 101]
        ```
    """
    rounded_values = [round(el) for el in values]
    reminders = [el - rel for rel, el in zip(rounded_values, values)]
    sum_reminders = round(sum(reminders))
    p = np.argsort(reminders)

    for i in range(abs(sum_reminders)):
        if sum_reminders < 0:
            rounded_values[p[i]] -= 1
        if sum_reminders > 0:
            rounded_values[p[-1 - i]] += 1

    return rounded_values
