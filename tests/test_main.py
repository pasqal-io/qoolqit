from __future__ import annotations

import pytest

from qoolqit import hello


@pytest.mark.parametrize("name", ["Jane", "John"])
def test_hello(name: str) -> None:
    assert hello(name) == "Hello" + name
