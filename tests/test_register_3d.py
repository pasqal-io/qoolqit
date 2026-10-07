"""Tests of the 3D registers: construction, geometry, graphs, compilation and emulation."""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pytest
import torch
from pulser.backend import Occupation
from pulser.register.register import Register as PulserRegister
from pulser.register.register3d import Register3D as PulserRegister3D
from scipy.spatial.distance import pdist, squareform

from qoolqit import (
    AnalogDevice,
    AnalogDevice3DWithDMM,
    AnalogDeviceWithDMM,
    Drive,
    MockDevice,
    QuantumProgram,
    Register,
)
from qoolqit.drive import DetuningMapModulator
from qoolqit.exceptions import CompilationError
from qoolqit.execution import BackendType, EmulationConfig, LocalEmulator
from qoolqit.execution.compilation_functions import CompilerProfile
from qoolqit.graphs import DataGraph
from qoolqit.graphs.utils import scale_coords
from qoolqit.register import SUPPORTED_DIMENSIONS
from qoolqit.waveforms import ConstantWaveform, PiecewiseLinearWaveform, RampWaveform

TETRAHEDRON = [
    (0.0, 0.0, 0.0),
    (1.0, 0.0, 0.0),
    (0.5, np.sqrt(3.0) / 2.0, 0.0),
    (0.5, np.sqrt(3.0) / 6.0, np.sqrt(2.0 / 3.0)),
]


def _rotation(axis: np.ndarray, angle: float) -> np.ndarray:
    """The rotation matrix of `angle` about `axis` (Rodrigues' formula)."""
    k = np.asarray(axis, dtype=float) / np.linalg.norm(axis)
    kx = np.array([[0.0, -k[2], k[1]], [k[2], 0.0, -k[0]], [-k[1], k[0], 0.0]])
    return np.eye(3) + np.sin(angle) * kx + (1.0 - np.cos(angle)) * kx @ kx


# --------------------------------------------------------------------------- #
#  Register                                                                   #
# --------------------------------------------------------------------------- #


def test_supported_dimensions() -> None:
    assert SUPPORTED_DIMENSIONS == (2, 3)


def test_register_3d_construction_and_geometry() -> None:
    reg = Register.from_coordinates(TETRAHEDRON)
    assert reg.dimension == 3 and reg.is_3d and reg.n_qubits == 4
    assert repr(reg) == "Register(n_qubits = 4, dimension = 3)"
    # A regular tetrahedron of unit edge: all six distances are 1.
    np.testing.assert_allclose(list(reg.distances().values()), 1.0)
    assert reg.min_distance() == pytest.approx(1.0)
    np.testing.assert_allclose(reg.radial_distances()[3], 1.0)
    # The interaction matrix is C6 / r^6 with C6 = 1, zero on the diagonal.
    expected = squareform(pdist(np.array(TETRAHEDRON)) ** -6.0)
    np.testing.assert_allclose(reg.interaction_matrix(), expected)


def test_register_2d_is_unchanged() -> None:
    reg = Register({"a": (0.0, 0.0), "b": (1.0, 0.0)})
    assert reg.dimension == 2 and not reg.is_3d
    assert repr(reg) == "Register(n_qubits = 2)"


def test_register_mixed_dimensions_raise() -> None:
    with pytest.raises(ValueError, match="same dimension"):
        Register({0: (0.0, 0.0), 1: (0.0, 0.0, 1.0)})


@pytest.mark.parametrize("coord", [(1.0,), (1.0, 2.0, 3.0, 4.0), [[0.0, 0.0, 0.0]]])
def test_register_invalid_dimension_raises(coord: tuple) -> None:
    with pytest.raises(ValueError, match="must be a 2D or 3D point"):
        Register({0: coord})


def test_register_3d_torch() -> None:
    q = torch.tensor(TETRAHEDRON, dtype=torch.float64, requires_grad=True)
    reg = Register({i: q[i] for i in range(4)})
    assert reg.dimension == 3
    energy = reg.interaction_matrix().sum()
    energy.backward()
    assert q.grad is not None and q.grad.shape == (4, 3)


@pytest.mark.parametrize("n,spacing", [(1, 1.0), (2, 1.5), (3, 2.0)])
def test_cubic(n: int, spacing: float) -> None:
    reg = Register.cubic(n, spacing=spacing)
    assert reg.n_qubits == n**3 and reg.dimension == 3
    coords = np.array(list(reg.qubits.values()))
    np.testing.assert_allclose(coords.mean(axis=0), 0.0, atol=1e-12)
    if n > 1:
        assert reg.min_distance() == pytest.approx(spacing)


def test_cuboid_validation() -> None:
    reg = Register.cuboid(2, 3, 4, row_spacing=1.0, col_spacing=2.0, layer_spacing=3.0)
    coords = np.array(list(reg.qubits.values()))
    np.testing.assert_allclose(np.ptp(coords, axis=0), [1.0, 4.0, 9.0])
    with pytest.raises(ValueError):
        Register.cuboid(0, 1, 1)
    with pytest.raises(ValueError):
        Register.cuboid(1, 1, 1, layer_spacing=0.0)


def test_draw_3d() -> None:
    reg = Register.cubic(2)
    reg.draw()
    ax = plt.figure().add_subplot(projection="3d")
    reg.draw(ax=ax)
    with pytest.raises(ValueError, match="3D axes"):
        reg.draw(ax=plt.figure().add_subplot())
    plt.close("all")


# --------------------------------------------------------------------------- #
#  Graphs                                                                     #
# --------------------------------------------------------------------------- #


def test_graph_3d_coords_and_register_from_graph() -> None:
    graph = DataGraph.from_coordinates(TETRAHEDRON)
    graph.set_ud_edges(radius=1.0)
    assert graph.dimension == 3 and graph.number_of_edges() == 6
    reg = Register.from_graph(graph)
    assert reg.dimension == 3
    graph.rescale_coords(scaling=2.0)
    assert graph.min_distance() == pytest.approx(2.0)
    graph.draw()
    plt.close("all")


def test_scale_coords_3d() -> None:
    assert scale_coords({0: (1.0, 2.0, 3.0)}, 2.0) == {0: (2.0, 4.0, 6.0)}
    assert scale_coords({0: (1.0, 2.0)}, 2.0) == {0: (2.0, 4.0)}


def test_from_nx_3d_and_mixed() -> None:
    g = nx.Graph()
    g.add_node(0, pos=(0.0, 0.0, 0.0))
    g.add_node(1, pos=(1.0, 0.0, 0.0))
    g.add_edge(0, 1)
    assert DataGraph.from_nx(g).dimension == 3
    g.add_node(2, pos=(0.0, 1.0))
    with pytest.raises(ValueError, match="same dimension"):
        DataGraph.from_nx(g)


# --------------------------------------------------------------------------- #
#  Devices and compilation                                                    #
# --------------------------------------------------------------------------- #


def test_device_dimensions() -> None:
    assert AnalogDevice().dimensions == 2 and not AnalogDeviceWithDMM().supports_3d
    assert MockDevice().dimensions == 3
    dev = AnalogDevice3DWithDMM()
    assert dev.supports_3d and dev._device.dmm_channels and not dev._requires_layout
    # Same limits as the 2D analog device with DMM.
    assert dev.specs == AnalogDeviceWithDMM().specs
    longer = AnalogDevice3DWithDMM(max_sequence_duration=20000)
    assert longer.specs["max_duration"] > dev.specs["max_duration"]
    with pytest.raises(ValueError, match="dimensions = 3"):
        AnalogDevice3DWithDMM(dimensions=2)


def _program(register: Register, weights: dict | None = None) -> QuantumProgram:
    """An adiabatic-like program on `register`, with an optional DMM."""
    duration = 20.0
    amp = PiecewiseLinearWaveform([5.0, 10.0, 5.0], [0.0, 0.2, 0.2, 0.0])
    det = RampWaveform(duration, -0.5, 0.5)
    dmm = None
    if weights is not None:
        dmm = DetuningMapModulator(waveform=ConstantWaveform(duration, -0.5), weights=weights)
    return QuantumProgram(register=register, drive=Drive(amplitude=amp, detuning=det, dmm=dmm))


@pytest.mark.parametrize("profile", [CompilerProfile.DEFAULT, CompilerProfile.MAX_ENERGY])
@pytest.mark.parametrize("device", [AnalogDevice3DWithDMM(), MockDevice()])
def test_compile_3d(profile: CompilerProfile, device: object) -> None:
    reg = Register({f"q{i}": 1.2 * np.array(c) for i, c in enumerate(TETRAHEDRON)})
    program = _program(reg, weights={"q0": 0.0, "q1": 0.3, "q2": 0.6, "q3": 1.0})
    program.compile_to(device=device, profile=profile)
    seq = program.compiled_sequence
    assert isinstance(seq.register, PulserRegister3D)
    assert set(seq.declared_channels) == {"rydberg", "dmm_0"}
    # The compiled register is the register scaled by one positive factor.
    q = np.array([seq.register.qubits[f"q{i}"] for i in range(4)])
    d = pdist(q)
    np.testing.assert_allclose(d / d[0], 1.0)


def test_compile_2d_still_uses_planar_register() -> None:
    program = _program(Register.from_coordinates([(0.0, 0.0), (1.2, 0.0)]))
    program.compile_to(device=AnalogDevice3DWithDMM())
    assert isinstance(program.compiled_sequence.register, PulserRegister)


@pytest.mark.parametrize("device", [AnalogDevice(), AnalogDeviceWithDMM()])
def test_compile_3d_to_planar_device_raises(device: object) -> None:
    program = _program(Register.from_coordinates(TETRAHEDRON))
    with pytest.raises(CompilationError, match="accepts only 2D registers"):
        program.compile_to(device=device)


# --------------------------------------------------------------------------- #
#  Emulation                                                                  #
# --------------------------------------------------------------------------- #


def test_rotated_planar_register_emulates_like_2d() -> None:
    """A planar register rotated into 3D has the same dynamics: H depends on distances only.

    With the same drive and DMM, the final Rydberg occupations of the 2D register
    and of its rigid rotation into 3D coincide.
    """
    planar = {"a": (0.0, 0.0), "b": (1.1, 0.0), "c": (0.4, 1.0), "d": (1.6, 1.2)}
    rot = _rotation(np.array([1.0, 2.0, 0.5]), 0.9)
    lifted = {k: tuple(rot @ np.array([x, y, 0.0])) for k, (x, y) in planar.items()}
    weights = {"a": 0.0, "b": 0.5, "c": 0.25, "d": 1.0}
    occupations = []
    for coords in (planar, lifted):
        program = _program(Register(coords), weights=weights)
        program.compile_to(device=MockDevice())
        config = EmulationConfig(observables=(Occupation(),))
        job = LocalEmulator(backend_type=BackendType.QutipBackendV2, emulation_config=config)
        occupations.append(np.asarray(job.run(program).results().occupation, dtype=float))
    np.testing.assert_allclose(occupations[0], occupations[1], atol=1e-6)


def test_tetrahedron_is_fully_blockaded() -> None:
    """Four mutually blockaded atoms in 3D (a regular tetrahedron, not realizable in 2D).

    Four equidistant atoms exist only in 3D. With the final detuning below the
    interaction, the ground state of the final Hamiltonian has one excitation, and
    a ramp of duration 20 reaches states with two or more excitations with
    probability of a few percent at most (non-adiabatic leakage).
    """
    reg = Register.from_coordinates(TETRAHEDRON)
    program = _program(reg)
    program.compile_to(device=AnalogDevice3DWithDMM())
    job = LocalEmulator(backend_type=BackendType.QutipBackendV2, num_shots=500)
    counts = job.run(program).results().final_bitstrings
    multiple = sum(c for s, c in counts.items() if s.count("1") >= 2)
    assert multiple / sum(counts.values()) < 0.05


def test_long_sequence_with_dmm_on_3d_device() -> None:
    """A longer maximal duration also lengthens the DMM channel (long adiabatic ramps)."""
    device = AnalogDevice3DWithDMM(max_sequence_duration=20000)
    duration = 0.9 * device.specs["max_duration"]
    reg = Register.from_coordinates(TETRAHEDRON)
    drive = Drive(
        amplitude=ConstantWaveform(duration, 0.1),
        detuning=RampWaveform(duration, -0.3, 0.3),
        dmm=DetuningMapModulator(
            waveform=ConstantWaveform(duration, -0.2), weights={0: 0.0, 1: 0.5, 2: 1.0, 3: 0.2}
        ),
    )
    program = QuantumProgram(register=reg, drive=drive)
    program.compile_to(device=device)
    assert program.compiled_sequence.get_duration() > 6000
    with pytest.raises(CompilationError):
        program.compile_to(device=AnalogDevice3DWithDMM())
