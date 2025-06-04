from __future__ import annotations

import random

import pytest

from qoolqit.graphs import DataGraph
from qoolqit.register import Register


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
