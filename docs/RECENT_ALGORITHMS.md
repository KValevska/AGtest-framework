# Recent algorithm catalogue and verification scope

This document records the recent surrogate-assisted methods added in response
to the request for broader coverage of developments from the last five years.
They are standalone Python implementations based on the cited articles. The
document does not claim exact numerical or statistical reproduction.

## Provenance policy

Every recent registry entry contains:

- `implementation_type`: identifies a standalone Python implementation;
- `reference`: publication or source description;
- `verified_against`: the verification performed and its explicit limits.

A `standalone_python_implementation` implements the article mechanisms directly
in the project and does not call an external algorithm package. It may use a
different numerical library, optimizer, random stream, or GUI termination
contract and must not be described as numerically identical to the article experiments.

## Catalogue

| GUI label | Year | Type | Main mechanisms | Intended problem class |
| --- | ---: | --- | --- | --- |
| PIEA | 2024 | standalone Python | SDE/I-epsilon+/Minkowski adaptation, RBF-SVR, DE infill | expensive continuous MOO |
| TEA | 2024 | standalone Python | two phases, Gaussian-process models, P-PD | expensive continuous constrained MOO |
| SSDE | 2024 | standalone Python | self-organizing map surrogate, DE, rank/crowding infill | expensive continuous MOO |
| DISK | 2025 | standalone Python | decision distribution, Kriging, DIPD, angular infill | expensive unconstrained many-objective optimization |
| DISK+ | 2025 | standalone Python | objective/constraint Kriging, CDIPD, uncertainty search | expensive constrained MOO |
| PEAplus | 2025 | standalone Python | CPPD and shifted objective/violation distance | expensive constrained MOO |
| TSPP | 2026 | standalone Python | three probabilistic-penalty phases and Kriging | expensive constrained MOO |
| MaO-TSP+ | 2026 | standalone Python | two-stage probabilistic penalty with angular survival and infill diversity | expensive constrained many-objective optimization |
| DSSEA | 2025 | standalone Python | ALDVA decision-variable ranking, dynamic subspaces, pbest/GA alternation, epsilon-SPEA2 | large-scale constrained MOO |
| PIMD | 2024 | standalone Python | Kriging, probability improvement, PF-shape mapping, NSGA-III infill search | expensive unconstrained MOO |
| CMOEA-CD | 2025 | standalone Python | constraint-Pareto dominance, FA/DA/FEA archives, GA/DE alternation | constrained MOO |
| CMOBR | 2024 | standalone Python | decomposition push/pull transition, dual populations, epsilon/objective relaxation, SPEA2 archive | constrained MOO |
| DVCEA | 2025 | standalone Python | FEA/INFEA decision-variable classification, pbest DE, diversity DE, epsilon-SPEA2 | constrained MOO |
| muMaOEA | 2024 | standalone Python | merge controller, nominal convergence, adaptive PBI, fuzzy two-stage archive | micro many-objective optimization |

## Rewritten article algorithms

| GUI label | Article DOI | Directly implemented mechanisms |
| --- | --- | --- |
| ε-NSGA-II | `10.1016/j.advwatres.2005.07.010` | epsilon archive, connected runs, archive injection, adaptive population size |
| DISK+ | `10.1109/TEVC.2024.3519185` | objective/constraint Kriging, CDIPD, distribution learning, angular and local infill |
| Learning-across-problems EDMO | `10.1109/TEVC.2025.3596468` | dynamic features, task labels, centralized classifier, cross-problem transfer |
| MaO-TSP+ | `10.1109/TEVC.2026.3703985` | PoB/PoF penalties, three phases, distribution phase, angular infill |
| MOEA/D-RNN | `10.1109/TEVC.2024.3419892` | change detection, online-trained RNN, adaptive response, MOEA/D-DE |
| TS-NSGA-II | `10.1109/TSMC.2022.3143657` | SPD, LPD, article stage switch, restricted mating, two environmental selections |

## Default GUI settings

The GUI generation limit counts **outer surrogate/infill iterations** after the
initial Latin-hypercube design. It is not the same as the number of exact
function evaluations.

| Algorithm | Initial population | Surrogate search | Exact infill per GUI generation | Other defaults |
| --- | ---: | ---: | ---: | --- |
| PIEA | 40 | 20 iterations | 1 | eta=5, adaptation window=20 |
| TEA | 40 | 20 iterations | up to 5 | two-phase constraint handling |
| SSDE | 40 | SOM training=50 epochs | selected DE candidates | 40 SOM nodes, learning rate=0.2 |
| DISK | 40 | 10 iterations | up to 5 plus optional local trial | unconstrained only |
| DISK+ | 40 | 10 iterations | up to 5 plus optional local trial | constraint models enabled |
| PEAplus | 40 | 10 iterations | up to 5 | CPPD selection |
| TSPP | 40 | 10 iterations | up to 5 | Euclidean diversity |
| MaO-TSP+ | 40 | 10 iterations | up to 5 | angular diversity |
| DSSEA | 100 | ALDVA before generation 1 | population size | n_sel=2, n_per=4 |
| PIMD | 20 | 15 model generations | up to 5 | probability and mapped-distance infill |
| muMaOEA | 30 plus archive 30 | not surrogate-assisted | block-dependent | block=5, reference pool=5000 |

DISK, DISK+, PEA+, TSPP and MaO-TSP+ require an even population size.
The implementations currently support bounded real-valued decision variables.

## Verification performed

Automated tests cover:

- deterministic probability limits and feasible-first dominance;
- distribution-density ordering used by DISK;
- CPPD feasibility ordering used by PEAplus;
- TSPP phase-two feasibility priority;
- Kriging interpolation of a known linear trend and non-negative MSE;
- finite two-generation GUI runs with generation callbacks;
- constrained execution on Tanaka;
- deterministic replay for PIEA, TEA and SSDE;
- ALDVA evaluation accounting and epsilon-feasibility ordering for DSSEA;
- PF-shape estimation, exact infill budgets and constraint compatibility for PIMD;
- merge ordering, reference-vector construction and deterministic short runs for muMaOEA;
- full registry, Main/Multi callback, XLSX export and packaging smoke paths.

## Verification not claimed

The repository does **not yet claim**:

- bitwise identity with another implementation;
- statistical equivalence of HV or IGD distributions from the papers;
- reproduction of every experimental table in the cited publications;
- support for integer, permutation, label, or mixed-variable encodings in these ports.

A publication claiming reproduced algorithm performance should additionally run
the same benchmark definitions, budgets, parameter settings and independent
seeds in both implementations, then report paired distributions and statistical
comparisons.
