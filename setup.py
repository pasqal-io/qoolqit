from setuptools import find_packages, setup

setup(
    name="qoolqit",
    version="0.3.4",
    install_requires=["pulser[torch]~=1.6.2", "networkx~=3.4"],
    packages=find_packages(),
)
