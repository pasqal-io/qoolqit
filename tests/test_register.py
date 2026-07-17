from __future__ import annotations

import random

import numpy as np
import pytest

from qoolqit.graphs import DataGraph
from qoolqit.register import Register


@pytest.mark.parametrize(
    "qubits",
    [
        {"a": (0, 0), "b": (1, 0), "c": (0, 1)},
        {1: [0, 0], 2: [1, 0]},
        {0: np.array([0.1, 1.2]), 1: np.array([-0.7, -0.4]), 2: np.array([5.0, 0.0])},
    ],
)
def test_register_init(qubits: dict) -> None:
    reg = Register(qubits)

    assert reg.n_qubits == len(qubits)

    for k, v in reg.qubits.items():
        assert k in qubits
        np.testing.assert_allclose(v, qubits[k])
    assert reg.qubits_ids == list(qubits.keys())


def test_empty_register() -> None:
    with pytest.raises(ValueError, match="empty"):
        Register({})  # type: ignore [call-arg]


def test_wrong_qubits_type() -> None:
    with pytest.raises(
        TypeError,
        match="Register must be initialized with a dictionary of ",
    ):
        Register("I'm not a dict")  # type: ignore [arg-type]


@pytest.mark.parametrize(
    "qubits",
    [
        {0: (1, 2, 3)},
        {"q0": np.array([1.0, -2.0]), "q1": np.array([[-1.0, -1.0], [-1.0, -1.0]])},
        {7: 32},
    ],
)
def test_invalid_coordinates(qubits: dict) -> None:
    with pytest.raises(ValueError, match="must be a tuple, list, or array of length 2, got"):
        Register(qubits)


def test_wrong_from_coordinates_type() -> None:
    with pytest.raises(TypeError, match="from_coordinates"):
        Register.from_coordinates({"a": (0.0, 0.0)})  # type: ignore [arg-type]


@pytest.mark.parametrize("n_qubits", [3, 4, 10])
def test_register_from_coordinates(n_qubits: int) -> None:

    coords = [(random.random(), random.random()) for _ in range(n_qubits)]
    qubits = {i: coords[i] for i in range(n_qubits)}

    r1 = Register(qubits)
    r2 = Register.from_coordinates(coords)

    assert r1.n_qubits == n_qubits
    assert r2.n_qubits == n_qubits

    for (q1, pos1), (q2, pos2) in zip(r1.qubits.items(), r2.qubits.items()):
        assert q1 == q2
        assert tuple(pos1) == tuple(pos2)

    assert r1.min_distance() == r2.min_distance()
    assert np.allclose(list(r1.interactions().values()), list(r2.interactions().values()))
    assert np.allclose(list(r1.distances().values()), list(r2.distances().values()))


@pytest.mark.parametrize("n_nodes", [3, 4, 10])
def test_register_from_graph(n_nodes: int) -> None:

    coords = [(random.random(), random.random()) for _ in range(n_nodes)]

    graph = DataGraph.from_coordinates(coords)

    register = Register.from_graph(graph)

    for (q, pos1), (v, pos2) in zip(register.qubits.items(), graph.coords.items()):
        assert q == v
        assert tuple(pos1) == tuple(pos2)

    with pytest.raises(ValueError):
        graph = DataGraph.random_er(n_nodes, 0.5)
        register = Register.from_graph(graph)

    with pytest.raises(ValueError):
        graph = DataGraph()
        register = Register.from_graph(graph)


def test_radial_distances() -> None:
    coords = [(-0.3, -0.3), (-0.3, 0.3), (0.3, 0.3)]
    register = Register.from_coordinates(coords)
    radial_dists = register.radial_distances()
    expected_radial_distances = {i: 0.3 * np.sqrt(2) for i in range(3)}
    assert radial_dists == expected_radial_distances
