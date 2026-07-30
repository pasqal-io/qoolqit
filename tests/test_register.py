from __future__ import annotations

import importlib
import random
from unittest import mock

import matplotlib.pyplot as plt
import numpy as np
import pytest
import torch

from qoolqit.graphs import DataGraph
from qoolqit.register import Register


def test_register_without_torch() -> None:
    import qoolqit.register as register_module

    # Remove torch from sys.modules and block the import
    with mock.patch.dict("sys.modules", {"torch": None}):
        # Reload register so the try/except runs again
        importlib.reload(register_module)
        assert register_module._has_torch is False

    # Reload the module to its original state
    importlib.reload(register_module)
    assert register_module._has_torch is True


@pytest.mark.parametrize(
    "qubits",
    [
        {"a": (0, 0), "b": (1, 0), "c": [0, 1]},
        {1: [0, 0], 2: [1, 0]},
        {0: np.array([0.1, 1.2]), 1: np.array([-0.7, -0.4]), 2: np.array([5.0, 0.0])},
        {
            "q0": torch.tensor([0.0, 0.0], dtype=torch.float64),
            "q1": torch.tensor([1.2, 0.0], dtype=torch.float64),
            "q2": torch.tensor([0.6, 1.04], dtype=torch.float64),
        },
        {"q0": [torch.tensor(0.0), torch.tensor(1.0)]},
    ],
)
def test_init(qubits: dict) -> None:
    reg = Register(qubits)

    assert reg.n_qubits == len(qubits)
    assert reg.qubits_ids == tuple(qubits.keys())

    for k, v in reg.qubits.items():
        assert k in qubits
        if isinstance(v, torch.Tensor):
            assert torch.allclose(v, qubits[k])
        else:
            assert isinstance(v, np.ndarray)
            np.testing.assert_allclose(v, qubits[k])


def test_empty_register() -> None:
    with pytest.raises(ValueError, match=r"Register cannot be empty\."):
        Register({})  # type: ignore [call-arg]


def test_init_wrong_qubits_type() -> None:
    with pytest.raises(
        TypeError,
        match=r"`qubits` must be a Mapping of qubit ids to coordinates",
    ):
        Register("I'm not a dict")  # type: ignore [arg-type]


@pytest.mark.parametrize(
    "qubits",
    [
        {0: (1, 2, 3)},
        {"q0": np.array([1.0, -2.0]), "q1": np.array([[-1.0, -1.0], [-1.0, -1.0]])},
        {7: 32},
        {"q_inf": np.array([np.inf, 0.1]), "q_nan": np.array([[0.1, np.nan]])},
    ],
)
def test_init_invalid_coordinate_shape(qubits: dict) -> None:
    with pytest.raises(ValueError, match="must be a 2D point, got"):
        Register(qubits)


@pytest.mark.parametrize(
    "qubits",
    [
        {"3": np.array(["a", "b"])},
    ],
)
def test_init_invalid_coordinate_type(qubits: dict) -> None:
    with pytest.raises(
        ValueError,
        match=r"Coordinate for qubit '3' must be castable to an array of floats, got",
    ):
        Register(qubits)


@pytest.mark.parametrize(
    "qubits",
    [
        {"q0": [0.0, 3.0], "q1": [1.0, 0.0]},
        {"q0": (np.pi, np.pi)},
        {"q0": np.array([1.0, 0.0])},
        {1: torch.tensor([0.0, 3.0]), 2: torch.tensor([1.0, 3.0], requires_grad=True)},
    ],
)
def test_qubits_dict_copy(qubits: dict) -> None:
    register = Register(qubits)
    qubits1 = register.qubits
    qubits2 = register.qubits

    for key in qubits:
        # Check that the qubits are not the same object (to verify that they are distinct copies)
        assert qubits1[key] is not qubits2[key]

        qubits1[key][0] = 0.01
        assert qubits1[key][0] != qubits2[key][0]


def test_from_coordinates_wrong_type() -> None:
    with pytest.raises(TypeError, match="from_coordinates"):
        Register.from_coordinates({"a": (0.0, 0.0)})  # type: ignore [arg-type]


@pytest.mark.parametrize("n_qubits", [3, 4, 10])
def test_register_from_coordinates(n_qubits: int) -> None:
    random.seed(0)  # Ensure reproducibility
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


def test_draw() -> None:
    # Just check that no exception is raised
    reg = Register({"a": (0.0, 0.0), "b": (1.0, 0.0)})
    reg.draw()

    # to ax
    fig, ax = plt.subplots()
    reg.draw(ax=ax, marker_size=50)
    plt.close(fig)


def test_rectangular() -> None:
    spacing = 0.5
    register = Register.rectangular(3, 3, spacing=spacing)
    expected = [
        (-spacing, -spacing),
        (-spacing, 0.0),
        (-spacing, spacing),
        (0.0, -spacing),
        (0.0, 0.0),
        (0.0, spacing),
        (spacing, -spacing),
        (spacing, 0.0),
        (spacing, spacing),
    ]

    assert register.n_qubits == 9
    np.testing.assert_allclose(register._coords, expected, atol=1e-8)


@pytest.mark.parametrize("rows, cols", [(0, 2), (2, 0), (0, 0), (-1, 2)])
def test_invalid_rows_cols(rows: int, cols: int) -> None:
    with pytest.raises(ValueError, match="Number of rows and columns must be at least 1."):
        Register.rectangular(rows, cols, spacing=1.0)


@pytest.mark.parametrize("rows, cols, spacing", [(2, 3, 1.0), (3, 3, 0.75), (1, 5, 1.28)])
def test_rectangular_min_distance(rows: int, cols: int, spacing: float) -> None:
    register = Register.rectangular(rows, cols, spacing=spacing)


def test_circle() -> None:
    spacing = 0.5
    n_qubits = 4
    register = Register.circle(n_qubits, spacing=spacing)

    radius = spacing / (2 * np.sin(np.pi / n_qubits))
    expected = [
        (radius, 0.0),
        (0.0, radius),
        (-radius, 0.0),
        (0.0, -radius),
    ]

    assert register.n_qubits == n_qubits
    np.testing.assert_allclose(register._coords, expected, atol=1e-8)


def test_invalid_spacing() -> None:
    with pytest.raises(ValueError, match="Spacing must be positive."):
        Register.circle(2, spacing=-1)


def test_invalid_n_qubits() -> None:
    with pytest.raises(ValueError, match="Number of qubits must be at least 1."):
        Register.circle(0, spacing=1.0)


@pytest.mark.parametrize("n, spacing", [(2, 1.0), (5, 1.28)])
def test_circle_min_distance(n: int, spacing: float) -> None:
    register = Register.circle(n, spacing=spacing)
    np.testing.assert_allclose(register.min_distance(), spacing, atol=1e-8)
