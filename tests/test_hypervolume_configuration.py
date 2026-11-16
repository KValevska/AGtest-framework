from __future__ import annotations

import numpy as np
import pytest

from pymoo_gui.metrics import compute_metrics, get_hv_ref_point, resolve_hv_config


def test_known_front_freezes_normalized_hv_coordinate_system() -> None:
    front = np.array([[0.0, 4.0], [1.0, 1.0], [4.0, 0.0]])
    config = resolve_hv_config("Schaffer", 2, pareto_front=front)

    assert config is not None
    np.testing.assert_allclose(config.ideal, [0.0, 0.0])
    np.testing.assert_allclose(config.nadir, [4.0, 4.0])
    np.testing.assert_allclose(config.raw_reference_point, [4.4, 4.4])
    np.testing.assert_allclose(config.reference_point, [1.1, 1.1])
    np.testing.assert_allclose(config.transform(front), front / 4.0)
    assert config.normalized is True


def test_hv_uses_frozen_bounds_instead_of_generation_bounds() -> None:
    reference_front = np.array([[0.0, 4.0], [4.0, 0.0]])
    config = resolve_hv_config("example", 2, pareto_front=reference_front)
    generation = np.array([[0.0, 4.0], [4.0, 0.0]])

    first = compute_metrics(generation, reference_front, hv_config=config).hv
    second = compute_metrics(generation[[0]], reference_front, hv_config=config).hv

    assert first == pytest.approx(0.21)
    assert second == pytest.approx(0.11)
    np.testing.assert_allclose(config.ideal, [0.0, 0.0])
    np.testing.assert_allclose(config.nadir, [4.0, 4.0])


def test_hv_is_unavailable_when_reference_is_not_worse_than_every_point() -> None:
    reference_front = np.array([[0.0, 1.0], [1.0, 0.0]])
    config = resolve_hv_config("example", 2, pareto_front=reference_front)
    analyzed = np.array([[0.5, 1.2]])

    result = compute_metrics(analyzed, reference_front, hv_config=config)

    assert result.hv is None


def test_auto_hv_without_reliable_front_has_no_unsafe_fallback() -> None:
    assert resolve_hv_config("Integer Portfolio", 2, pareto_front=None) is None
    assert get_hv_ref_point("Integer Portfolio", 2, pareto_front=None) is None


def test_manual_hv_remains_available_without_normalization_bounds() -> None:
    config = resolve_hv_config(
        "Integer Portfolio",
        2,
        pareto_front=None,
        manual_ref_point=np.array([2.0, 3.0]),
    )

    assert config is not None
    assert config.normalized is False
    assert config.source == "manual_without_normalization"
    np.testing.assert_allclose(config.reference_point, [2.0, 3.0])


def test_manual_point_must_be_worse_than_known_front() -> None:
    front = np.array([[0.0, 4.0], [4.0, 0.0]])
    assert resolve_hv_config(
        "Schaffer", 2, pareto_front=front, manual_ref_point=np.array([3.0, 5.0])
    ) is None
