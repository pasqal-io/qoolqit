import tomllib
from qoolqit import __version__ as init_version


def test_qoolqit_version() -> None:
    """Check that the qoolqit version is the same for different ways to query it."""
    with open("pyproject.toml", "rb") as file:
        pyproject_version = tomllib.load(file)["project"]["version"]

    assert init_version == pyproject_version
