import numpy as np


def roundsum(a: list[float]) -> list[int]:
    a_round = [round(el) for el in a]
    reminders = [el - rel for rel, el in zip(a_round, a)]
    p = np.argsort(reminders)

    sum_reminders = round(sum(reminders))
    for i in range(abs(sum_reminders)):
        if sum_reminders < 0:
            a_round[p[i]] -= 1
        if sum_reminders > 0:
            a_round[p[-1 - i]] += 1

    assert round(sum(a)) == sum(a_round)
    return a_round
