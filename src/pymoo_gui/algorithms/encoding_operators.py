"""Variation operators selected from the decision-variable encoding.

Provenance: AGtest-framework implementation of standard uniform crossover,
bit-flip mutation and integer/mixed repair operators; not imported from pymoo.
"""

from __future__ import annotations

import numpy as np


def binary_sample(size: tuple[int, int], rng: np.random.Generator) -> np.ndarray:
    return rng.integers(0, 2, size=size, dtype=np.int8)


def binary_crossover(
    population: np.ndarray,
    parent_pairs: np.ndarray,
    probability: float,
    rng: np.random.Generator,
) -> np.ndarray:
    """Uniform crossover; each child receives every bit independently."""
    X = np.asarray(population, dtype=bool)
    children = np.empty((len(parent_pairs), X.shape[1]), dtype=np.int8)
    for row, (a, b) in enumerate(parent_pairs):
        if rng.random() <= probability:
            mask = rng.random(X.shape[1]) < 0.5
            children[row] = np.where(mask, X[int(a)], X[int(b)])
        else:
            children[row] = X[int(a)]
    return children


def bitflip_mutation(X: np.ndarray, probability: float, rng: np.random.Generator) -> np.ndarray:
    Y = np.asarray(X, dtype=bool).copy()
    Y ^= rng.random(Y.shape) < float(probability)
    return Y.astype(np.int8)


def integer_sample(
    lower: np.ndarray,
    upper: np.ndarray,
    count: int,
    rng: np.random.Generator,
) -> np.ndarray:
    lo = np.ceil(lower).astype(int)
    hi = np.floor(upper).astype(int)
    return np.column_stack([rng.integers(a, b + 1, size=count) for a, b in zip(lo, hi)])


def integer_repair(X: np.ndarray, lower: np.ndarray, upper: np.ndarray) -> np.ndarray:
    return np.rint(np.clip(np.asarray(X, dtype=float), lower, upper)).astype(int)


def mixed_repair(X: np.ndarray, problem: object) -> np.ndarray:
    repair = getattr(problem, "repair", None)
    if not callable(repair):
        raise ValueError("A mixed-variable problem must provide repair(X).")
    return np.asarray(repair(X))

