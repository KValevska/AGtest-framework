"""Capability metadata shared by benchmark and algorithm registries.

Provenance: AGtest-framework infrastructure; no benchmark equations are defined here.
"""

from __future__ import annotations

from typing import Any, Iterable


VARIABLE_TYPES = frozenset({"real", "binary", "integer", "mixed"})


def problem_capabilities(
    *,
    variable_type: str = "real",
    family: str = "classical",
    constrained: bool = False,
    dynamic: bool = False,
    multimodal: bool = False,
    large_scale: bool = False,
    reference_front: str = "unavailable",
    metrics: Iterable[str] = ("hv",),
) -> dict[str, Any]:
    """Return a validated, JSON-friendly benchmark capability description."""
    variable_type = str(variable_type).lower()
    if variable_type not in VARIABLE_TYPES:
        raise ValueError(f"Unknown variable type: {variable_type}")
    reference_front = str(reference_front).lower()
    if reference_front not in {"analytical", "file", "sampled", "library", "unavailable"}:
        raise ValueError(f"Unknown reference-front source: {reference_front}")
    return {
        "variable_type": variable_type,
        "family": str(family),
        "constrained": bool(constrained),
        "dynamic": bool(dynamic),
        "multimodal": bool(multimodal),
        "large_scale": bool(large_scale),
        "reference_front": reference_front,
        "recommended_metrics": tuple(dict.fromkeys(str(item).lower() for item in metrics)),
    }


def algorithm_capabilities(
    *,
    variable_types: Iterable[str] = ("real",),
    constraints: bool = True,
    dynamic: bool = False,
) -> dict[str, Any]:
    """Return normalized algorithm capabilities used by compatibility checks."""
    encodings = frozenset(str(item).lower() for item in variable_types)
    unknown = encodings - VARIABLE_TYPES
    if unknown:
        raise ValueError(f"Unknown algorithm variable types: {sorted(unknown)}")
    return {
        "variable_types": encodings,
        "constraints": bool(constraints),
        "dynamic": bool(dynamic),
    }


def infer_problem_variable_type(problem: Any) -> str:
    """Read the explicit encoding marker, falling back conservatively to real."""
    value = str(getattr(problem, "variable_type", "real")).lower()
    return value if value in VARIABLE_TYPES else "real"

