from __future__ import annotations

import numpy as np

RELATIVE_TOLERANCE = 1e-7
"""Tolerance of `nearly_equal`, relative to the largest off-diagonal term."""


def nearly_equal(matrix: np.ndarray, other: np.ndarray) -> bool:
    """Whether two matrices are equal up to a tolerance relative to `matrix`.

    The tolerance is `RELATIVE_TOLERANCE` times the largest absolute off-diagonal term
    of `matrix`, so that the result does not depend on the scale of the matrix nor on
    its diagonal. Matrices of different shapes are not equal.
    """
    if matrix.shape != other.shape:
        return False
    off_diagonal = np.eye(*matrix.shape) == 0
    scale = np.max(np.abs(matrix[off_diagonal]), initial=0.0)
    return bool(np.allclose(matrix, other, rtol=0.0, atol=RELATIVE_TOLERANCE * scale))
