from __future__ import annotations

from qoolqit import __version__ as init_version


def test_qoolqit_version() -> None:
    try:
        import tomllib  # Python v3.11+

        with open("pyproject.toml", "rb") as file:
            pyproject_version = tomllib.load(file)["project"]["version"]

        assert init_version == pyproject_version
    except ModuleNotFoundError:
        pass
