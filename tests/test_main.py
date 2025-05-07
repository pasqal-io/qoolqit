from __future__ import annotations

import pytest


@pytest.mark.parametrize("name", ["Jane", "John"])
def test_smth(name: str) -> None:
    assert 1 == 1
