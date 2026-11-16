from __future__ import annotations

import numpy as np
import pytest

from pymoo_gui.metrics import (
    METRIC_LABELS,
    compute_mean_normalized_pairwise_separation,
    compute_spread,
)


def test_pairwise_separation_matches_documented_formula() -> None:
    front = np.array([[0.0, 10.0], [1.0, 20.0], [2.0, 30.0]])

    # Normalized points lie at (0, 0), (0.5, 0.5), and (1, 1).
    # Pairwise distances divided by sqrt(2) are 0.5, 1.0, and 0.5.
    expected = 2.0 / 3.0
    assert compute_mean_normalized_pairwise_separation(front) == pytest.approx(expected)
    assert compute_spread(front) == pytest.approx(expected)


def test_pairwise_separation_uses_current_set_min_max_normalization() -> None:
    front = np.array([[0.0, -4.0], [0.25, 2.0], [1.0, 8.0]])
    shifted_and_scaled = front * np.array([7.0, 0.5]) + np.array([100.0, -3.0])

    assert compute_mean_normalized_pairwise_separation(front) == pytest.approx(
        compute_mean_normalized_pairwise_separation(shifted_and_scaled)
    )


def test_pairwise_separation_handles_degenerate_and_invalid_sets() -> None:
    assert compute_mean_normalized_pairwise_separation(np.array([[1.0, 2.0]])) == 0.0
    assert compute_mean_normalized_pairwise_separation(np.ones((3, 2))) == 0.0
    assert compute_mean_normalized_pairwise_separation(np.empty((0, 2))) is None


def test_spread_key_has_unambiguous_visible_label() -> None:
    assert METRIC_LABELS["spread"] == "Pairwise objective-space spread"
