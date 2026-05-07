"""
EN: Factory module for RVEA with GUI-specific termination handling.
"""

# ------------------------------------------------------------------------------------
# File: rvea.py
# Contents: RVEA factory, problem objective validation and reference-direction setup.
# What happens here: reference directions are generated from the selected problem and used to build pymoo RVEA.
# Role in the framework: provides a reference-vector-guided algorithm option for the dissertation GUI framework.
# Author: mgr inz. Kristina Valevska
# ------------------------------------------------------------------------------------

from __future__ import annotations

from typing import Any, Dict, Optional

from pymoo.core.termination import NoTermination
from pymoo.algorithms.moo.rvea import RVEA
from pymoo.optimize import minimize as _pymoo_minimize
from pymoo.termination.max_gen import MaximumGenerationTermination
from pymoo.util.ref_dirs import get_reference_directions

RVEA_RAN_VIRTUAL_N_GEN = 100


class _RveaRanTermination(MaximumGenerationTermination):
    """
    EN:
    Termination shim that keeps RVEA compatible with the GUI's unbounded RAN mode.

    PL:
    Pomocniczy warunek stopu, ktory pozwala RVEA dzialac do czasu klikniecia
    przycisku Stop w trybie bez limitu generacji.
    """

    def _update(self, algorithm: Any) -> float:
        """
        EN:
        Report no progress toward maximum-generation termination.

        PL:
        Informuje algorytm, ze limit generacji nie zostal jeszcze osiagniety.

        Args:
            algorithm (Any): EN: Running pymoo algorithm instance.
                             PL: Aktualnie dzialajacy algorytm.

        Returns:
            float: EN: Always `0.0` to prevent automatic termination.
                   PL: Zawsze `0.0`, aby algorytm sam nie zakonczyl pracy.
        """
        # RVEA requires MaximumGenerationTermination for n_max_gen, but GUI RAN
        # mode must keep running until the worker callback raises cancellation.
        return 0.0


def _parse_positive_int(value: Any, field_name: str) -> int:
    """
    EN:
    Parse a positive integer configuration value.

    PL:
    Sprawdza, czy ustawienie jest dodatnia liczba calkowita.
    """
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid {field_name}: {value!r}") from exc
    if parsed < 1:
        raise ValueError(f"{field_name} must be >= 1, got {parsed}")
    return parsed


def _parse_positive_float(value: Any, field_name: str) -> float:
    """
    EN:
    Parse a floating-point configuration value that must be greater than zero.

    PL:
    Sprawdza, czy ustawienie jest liczba wieksza od zera.

    Raises:
        ValueError: EN: If the value cannot be parsed or is not positive.
                    PL: Gdy wartosc nie jest poprawna liczba dodatnia.
    """
    try:
        parsed = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid {field_name}: {value!r}") from exc
    if parsed <= 0.0:
        raise ValueError(f"{field_name} must be > 0, got {parsed}")
    return parsed


def _parse_optional_positive_int(value: Any, field_name: str) -> Optional[int]:
    """
    EN:
    Parse an optional positive integer, preserving `None` for pymoo defaults.

    PL:
    Odczytuje dodatnia liczbe calkowita albo zostawia `None`, gdy algorytm ma
    uzyc ustawienia domyslnego.
    """
    if value is None:
        return None
    return _parse_positive_int(value, field_name)


def _problem_n_obj(problem: Any) -> int:
    """
    EN:
    Validate objective dimensionality required to generate RVEA reference vectors.

    PL:
    Sprawdza liczbe funkcji celu potrzebna do przygotowania wektorow odniesienia.

    Raises:
        ValueError: EN: If the problem has no valid objective count.
                    PL: Gdy problem nie podaje poprawnej liczby celow.
    """
    try:
        n_obj = int(getattr(problem, "n_obj", None))
    except (TypeError, ValueError) as exc:
        raise ValueError("Selected problem does not expose a valid n_obj") from exc
    if n_obj < 2:
        raise ValueError(f"RVEA requires at least 2 objectives, got {n_obj}")
    return n_obj


def _is_no_termination(termination: Any) -> bool:
    """
    EN:
    Detect pymoo `NoTermination` objects across compatible API versions.

    PL:
    Rozpoznaje tryb bez limitu generacji, nawet jesli pochodzi z innej wersji pymoo.
    """
    return isinstance(termination, NoTermination) or termination.__class__.__name__ == "NoTermination"


def _rvea_gui_termination(termination: Any) -> Any:
    """
    EN:
    Replace unbounded GUI termination with the RVEA-compatible shim when needed.

    PL:
    Zamienia tryb bez limitu na wersje, ktora RVEA potrafi obsluzyc.
    """
    if _is_no_termination(termination):
        return _RveaRanTermination(n_max_gen=RVEA_RAN_VIRTUAL_N_GEN)
    return termination


def make_rvea(
    problem: Any,
    pop_size: Optional[int] = 100,
    n_partitions: int = 99,
    alpha: float = 2.0,
    adapt_freq: float = 0.1,
) -> RVEA:
    """
    EN:
    Create an RVEA algorithm and attach a GUI-aware `gui_minimize` runner.

    PL:
    Tworzy algorytm RVEA i dodaje sposob uruchamiania zgodny z aplikacja.

    Args:
        problem (Any): EN: Problem used to infer objective count.
                       PL: Problem, z ktorego pobierana jest liczba celow.
        pop_size (Optional[int]): EN: Population size or `None` for pymoo default behavior.
                                  PL: Rozmiar populacji albo `None`, aby uzyc domyslnych ustawien.
        n_partitions (int): EN: Partition count for reference directions.
                            PL: Liczba podzialow przy tworzeniu kierunkow odniesienia.
        alpha (float): EN: APD penalty parameter.
                       PL: Parametr kary uzywany przez RVEA.
        adapt_freq (float): EN: Reference-vector adaptation frequency.
                            PL: Czestotliwosc dopasowywania wektorow odniesienia.

    Returns:
        RVEA: EN: Configured RVEA instance with GUI minimize support.
              PL: Gotowy algorytm RVEA do uruchomienia w GUI.

    Raises:
        ValueError: EN: If problem metadata or numeric parameters are invalid.
                    PL: Gdy dane problemu albo parametry sa niepoprawne.
    """
    n_obj = _problem_n_obj(problem)
    ref_dirs = get_reference_directions(
        "das-dennis",
        n_obj,
        n_partitions=_parse_positive_int(n_partitions, "n_partitions"),
    )
    algorithm = RVEA(
        ref_dirs=ref_dirs,
        pop_size=_parse_optional_positive_int(pop_size, "pop_size"),
        alpha=_parse_positive_float(alpha, "alpha"),
        adapt_freq=_parse_positive_float(adapt_freq, "adapt_freq"),
    )

    def gui_minimize(*, problem: Any, termination: Any, **kwargs: Any) -> Any:
        """
        EN:
        Run pymoo minimize with termination adapted for RVEA's internal requirements.

        PL:
        Uruchamia RVEA tak, aby tryb bez limitu generacji dzialal poprawnie w GUI.
        """
        return _pymoo_minimize(problem, algorithm, _rvea_gui_termination(termination), **kwargs)

    algorithm.gui_minimize = gui_minimize
    return algorithm


RVEA_DEFINITION: Dict[str, Any] = {
    "label": "RVEA",
    "factory": make_rvea,
    "form_fields": {
        "pop_size": {
            "default": 100,
            "kind": "int",
            "minimum": 1,
            "tooltip": "Rozmiar populacji.",
        },
        "n_partitions": {
            "default": 99,
            "kind": "int",
            "minimum": 1,
            "tooltip": "Liczba partycji dla ref_dirs.",
        },
        "alpha": {
            "default": 2.0,
            "kind": "float",
            "minimum": 0.0000000001,
            "tooltip": "Parametr alpha dla kary APD.",
        },
        "adapt_freq": {
            "default": 0.1,
            "kind": "float",
            "minimum": 0.0000000001,
            "tooltip": "Czestotliwosc adaptacji reference vectors wzgledem liczby generacji.",
        },
    },
    "form_note": "RVEA generuje reference directions z liczby celow wybranego problemu.",
}
