from __future__ import annotations

import warnings
from typing import Any, Generator

import pytest


@pytest.fixture(autouse=True)
def error_on_warnings() -> Generator[None, Any, None]:
    with warnings.catch_warnings():
        warnings.filterwarnings("error")
        yield
