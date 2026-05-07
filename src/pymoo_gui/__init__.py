"""
EN:
Top-level package metadata for the `pymoo_gui` optimization framework.

PL:
Opisuje glowne czesci pakietu, z ktorych korzysta aplikacja graficzna do
uruchamiania i porownywania algorytmow optymalizacji.
"""

# ------------------------------------------------------------------------------------
# File: __init__.py
# Contents: package export metadata for the pymoo_gui namespace.
# What happens here: the public subpackages and modules of the GUI framework are declared.
# Role in the framework: exposes the package structure used by the doctoral-dissertation optimization framework.
# Author: mgr inż. Kristina Valevska
# ------------------------------------------------------------------------------------

__all__ = ["algoritms", "app", "metrics", "problems", "pymoo_registry", "runner", "viz"]
