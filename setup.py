from setuptools import find_packages, setup

setup(
    name="qoolqit",
    version="0.3.3",
    install_requires=["pulser~=1.6.3", "torch~=2.9", "networkx~=3.4"],
    packages=find_packages(),
)
