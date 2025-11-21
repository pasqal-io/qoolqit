from __future__ import annotations

import sys

from qoolqit import __version__ as init_version


def test_qoolqit_version() -> None:
    """Check that the qoolqit version is the same for different ways to query it."""
    if sys.version_info >= (3, 11):
        import tomllib

        with open("pyproject.toml", "rb") as file:
            pyproject_version = tomllib.load(file)["project"]["version"]

        assert init_version == pyproject_version
