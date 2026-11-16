# Adapted MOEA/D-IEpsilon implementation.
# Provenance: AGtest-framework adapted article port; not imported from Platypus or pymoo.
# ------------------------------------------------------------------------------------
# Article: Z. Fan et al., "An Improved Epsilon Constraint-Handling Method in
#          MOEA/D for CMOPs with Large Infeasible Regions", Soft Computing, 2019.
# DOI: 10.1007/s00500-019-03794-x
# Implementation: own Python/NumPy implementation based on the article.
# Author: Kristina Valevska, MSc Eng.
# ------------------------------------------------------------------------------------
from typing import Any, Dict
import numpy as np
from .article_algorithms_common import MOEADAlgorithm
from .research_common import (
    FEASIBILITY_TOL, das_dennis_reference_directions, parse_positive_int,
    parse_probability, polynomial_mutation, problem_n_obj, project_to_bounds,
    termination_generations,
)

class MOEADIEpsilon(MOEADAlgorithm):
    """MOEA/D with a feasible-ratio-driven improved epsilon constraint level."""
    def after_initialize(self) -> None:
        super().after_initialize()
        assert self.state is not None
        # Equation (8): x^theta is selected after descending CV sorting.
        ordered = np.sort(self.state.CV)[::-1]
        theta = min(ordered.size - 1, max(0, int(np.ceil(0.05 * ordered.size)) - 1))
        self.initial_epsilon = float(ordered[theta])
        self.phi_max = float(np.max(self.state.CV))
        self.constraint_epsilon = self.initial_epsilon
        self.tau = 0.1
        self.alpha = 0.95
        self.control_generation = max(1, int(0.8 * getattr(self, "maximum_generations", 100)))

    def gui_minimize(self, *, problem, termination, **kwargs):
        self.maximum_generations = termination_generations(termination) or 100
        return super().gui_minimize(problem=problem, termination=termination, **kwargs)

    def step(self) -> None:
        assert self.state is not None
        self.phi_max = max(self.phi_max, float(np.max(self.state.CV)))
        feasible_ratio = float(np.mean(self.state.CV <= FEASIBILITY_TOL))
        if self.n_gen >= self.control_generation:
            self.constraint_epsilon = 0.0
        elif feasible_ratio < self.alpha:
            self.constraint_epsilon = (1.0 - self.tau) * self.constraint_epsilon
        else:
            self.constraint_epsilon = (1.0 + self.tau) * self.phi_max
        super().step()

    def generate_child(self, subproblem: int, pool: np.ndarray) -> np.ndarray:
        # MOEA/D-IEpsilon uses DE/rand/1/bin followed by polynomial mutation.
        source = pool if pool.size >= 3 else np.arange(self.population_size)
        r1, r2, r3 = self.random_state.choice(source, size=3, replace=source.size < 3)
        mutant = self.state.X[r1] + 0.5 * (self.state.X[r2] - self.state.X[r3])
        trial = self.state.X[subproblem].copy()
        forced = int(self.random_state.integers(0, self.n_var))
        mask = self.random_state.random(self.n_var) <= 1.0
        mask[forced] = True
        trial[mask] = mutant[mask]
        child = project_to_bounds(trial[None, :], self.xl, self.xu)
        return polynomial_mutation(
            child, self.xl, self.xu, self.mutation_eta,
            self.mutation_rate, self.random_state,
        )

    def replacement_allowed(self, child_f, child_cv, target_f, target_cv, weights) -> bool:
        eps = self.constraint_epsilon
        child_ok, target_ok = child_cv <= eps, target_cv <= eps
        if child_ok and not target_ok:
            return True
        if target_ok and not child_ok:
            return False
        if not child_ok and not target_ok:
            if abs(child_cv - target_cv) <= FEASIBILITY_TOL:
                return self._scalar(child_f[None, :], weights[None, :])[0] <= self._scalar(target_f[None, :], weights[None, :])[0]
            return child_cv < target_cv
        return self._scalar(child_f[None, :], weights[None, :])[0] <= self._scalar(target_f[None, :], weights[None, :])[0]

def make_moead_iepsilon(problem: Any, population_size: int = 100, neighborhood_size: int = 10,
                        delta: float = 0.9, eta: int = 2) -> MOEADIEpsilon:
    n_obj = problem_n_obj(problem)
    requested = parse_positive_int(population_size, "population_size")
    partitions = 1
    while len(das_dennis_reference_directions(n_obj, partitions)) < requested:
        partitions += 1
    size = len(das_dennis_reference_directions(n_obj, partitions))
    return MOEADIEpsilon(population_size=size, archive_size=size, n_partitions=partitions,
                         n_neighbors=min(parse_positive_int(neighborhood_size, "neighborhood_size"), size),
                         prob_neighbor_mating=parse_probability(delta, "delta"),
                         max_replacements=parse_positive_int(eta, "eta"),
                         mutation_rate=1.0 / max(1, int(problem.n_var)))

MOEAD_IEPSILON_DEFINITION: Dict[str, Any] = {
    "label": "MOEA/D-IEpsilon (adapted port)", "factory": make_moead_iepsilon,
    "implementation_type": "adapted_port",
    "reference": "Z. Fan et al., Soft Computing 23, 12491-12510 (2019), DOI 10.1007/s00500-019-03794-x",
    "source_commit": None,
    "verified_against": "Equations 6 and 8 and Algorithms 1-3; mechanism and runtime tests; no claim of statistical equivalence",
    "form_fields": {
        "population_size": {"default": 100, "kind": "int", "minimum": 1, "tooltip": "Requested minimum population size."},
        "neighborhood_size": {"default": 10, "kind": "int", "minimum": 1, "tooltip": "Neighborhood size."},
        "delta": {"default": 0.9, "kind": "float", "minimum": 0.0, "maximum": 1.0, "tooltip": "Neighborhood mating probability."},
        "eta": {"default": 2, "kind": "int", "minimum": 1, "tooltip": "Maximum replacements per child."},
    },
    "form_note": "Adapted Python port of MOEA/D-IEpsilon; not a Platypus algorithm and not claimed statistically equivalent to the reference experiments.",
}

