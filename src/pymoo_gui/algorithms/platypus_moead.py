"""Compatibility imports for the former, misleading module name.

Provenance: AGtest-framework compatibility shim; the implementation is the local
MOEA/D-IEpsilon adapted port in :mod:`pymoo_gui.algorithms.moead_iepsilon`, not
an optimizer imported from Platypus.
"""

from .moead_iepsilon import (
    MOEADIEpsilon,
    MOEAD_IEPSILON_DEFINITION,
    make_moead_iepsilon,
)

make_platypus_moead = make_moead_iepsilon
PLATYPUS_MOEAD_DEFINITION = MOEAD_IEPSILON_DEFINITION

__all__ = [
    "MOEADIEpsilon",
    "MOEAD_IEPSILON_DEFINITION",
    "PLATYPUS_MOEAD_DEFINITION",
    "make_moead_iepsilon",
    "make_platypus_moead",
]
