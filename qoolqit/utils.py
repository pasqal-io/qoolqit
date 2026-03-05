from __future__ import annotations

import math

ATOL_32 = 1e-07
ATOL_64 = 1e-14


def EQUAL(a: float, b: float, rtol: float = 0.0, atol: float = ATOL_32) -> bool:
    return math.isclose(a, b, rel_tol=rtol, abs_tol=atol)
