# Standalone MOEA/D-RNN implementation.
# Provenance: AGtest-framework standalone implementation; not imported from pymoo or Platypus.
# ------------------------------------------------------------------------------------
# Article: Y. Hu, J. Ou, P. N. Suganthan, W. Pedrycz, R. Wang, J. Zheng,
#          J. Zou, and Y. Song, "Dynamic Multiobjective Optimization Algorithm
#          Guided by Recurrent Neural Network," IEEE TEVC, 2025.
# DOI: 10.1109/TEVC.2024.3419892
# Implementation: own Python/NumPy implementation of online RNN learning, random
#                 change detection, adaptive auxiliary response and MOEA/D-DE search.
# Author: Kristina Valevska, MSc Eng.
# ------------------------------------------------------------------------------------

from __future__ import annotations

from typing import Any, Dict

import numpy as np

from .article_algorithms_common import MOEADAlgorithm
from .research_common import (
    FEASIBILITY_TOL,
    PopulationState,
    polynomial_mutation,
    project_to_bounds,
    select_survivors_nsga2,
    parse_positive_float,
    parse_positive_int,
    parse_probability,
)


class RNNGuidedDMO(MOEADAlgorithm):
    """MOEA/D-RNN with an online-trained recurrent predictor."""

    def __init__(
        self,
        *,
        hidden_size: int = 16,
        prediction_fraction: float = 0.2,
        detector_fraction: float = 0.1,
        learning_rate: float = 0.01,
        training_epochs: int = 20,
        change_tolerance: float = 1e-10,
        mutation_scale: float = 0.1,
        utest_threshold: float = 0.5,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.hidden_size = parse_positive_int(hidden_size, "hidden_size")
        self.prediction_fraction = parse_probability(prediction_fraction, "prediction_fraction")
        self.detector_fraction = parse_probability(detector_fraction, "detector_fraction")
        self.learning_rate = parse_positive_float(learning_rate, "learning_rate")
        self.training_epochs = parse_positive_int(training_epochs, "training_epochs")
        self.change_tolerance = parse_positive_float(change_tolerance, "change_tolerance")
        self.mutation_scale = parse_positive_float(mutation_scale, "mutation_scale")
        self.utest_threshold = parse_probability(utest_threshold, "utest_threshold")
        self.Wxh = np.empty((0, 0))
        self.Whh = np.empty((0, 0))
        self.Whq = np.empty((0, 0))
        self.bh = np.empty(0)
        self.bq = np.empty(0)
        self.hidden = np.empty((0, 0))
        self.previous_samples: np.ndarray | None = None
        self.previous_prediction: np.ndarray | None = None
        self.previous_center: np.ndarray | None = None
        self.loss_history: list[float] = []
        self.online_updates = 0
        self.detected_changes = 0

    @property
    def sample_size(self) -> int:
        return max(1, int(round(self.population_size * self.prediction_fraction)))

    def after_initialize(self) -> None:
        # Initialize trainable RNN parameters and the MOEA/D neighborhoods.
        super().after_initialize()
        # MOEA/D-RNN uses polynomial mutation with probability 1 / n.
        self.mutation_rate = 1.0 / max(1, self.n_var)
        scale_x = np.sqrt(2.0 / max(1, self.n_var + self.hidden_size))
        scale_h = np.sqrt(2.0 / max(1, 2 * self.hidden_size))
        self.Wxh = self.random_state.normal(0.0, scale_x, size=(self.n_var, self.hidden_size))
        self.Whh = self.random_state.normal(0.0, scale_h, size=(self.hidden_size, self.hidden_size))
        self.Whq = self.random_state.normal(0.0, scale_h, size=(self.hidden_size, self.n_var))
        self.bh = np.zeros(self.hidden_size)
        self.bq = np.zeros(self.n_var)
        self.hidden = np.zeros((self.sample_size, self.hidden_size))
        self.previous_samples = None
        self.previous_prediction = None
        self.previous_center = None
        self.loss_history = []
        self.online_updates = 0
        self.detected_changes = 0

    def _best_samples(self, state: PopulationState) -> np.ndarray:
        # Use fast nondominated rank and crowding to build the fixed-size RNN input set.
        selected = select_survivors_nsga2(
            state.X, state.F, state.CV, min(self.sample_size, state.X.shape[0])
        ).X
        if selected.shape[0] < self.sample_size:
            ids = self.random_state.integers(0, selected.shape[0], size=self.sample_size - selected.shape[0])
            selected = np.vstack((selected, selected[ids]))
        return selected

    def _forward(
        self,
        inputs: np.ndarray,
        hidden_previous: np.ndarray,
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        # Evaluate Equations 3-4 with the article's ReLU hidden activation.
        preactivation = inputs @ self.Wxh + hidden_previous @ self.Whh + self.bh
        hidden = np.maximum(preactivation, 0.0)
        output = hidden @ self.Whq + self.bq
        return output, hidden, preactivation

    def _online_train(self, inputs: np.ndarray, targets: np.ndarray) -> float:
        # Update all RNN weights by online gradient descent on Equation 6.
        hidden_previous = self.hidden.copy()
        loss = 0.0
        for _ in range(self.training_epochs):
            output, hidden, preactivation = self._forward(inputs, hidden_previous)
            error = output - targets
            # Equation 6 averages the half squared Euclidean norm over samples,
            # not over both samples and decision variables.
            loss = float(0.5 * np.sum(error**2) / max(1, error.shape[0]))
            grad_output = error / max(1, error.shape[0])
            grad_Whq = hidden.T @ grad_output
            grad_bq = np.sum(grad_output, axis=0)
            grad_hidden = grad_output @ self.Whq.T
            grad_pre = grad_hidden * (preactivation > 0.0)
            grad_Wxh = inputs.T @ grad_pre
            grad_Whh = hidden_previous.T @ grad_pre
            grad_bh = np.sum(grad_pre, axis=0)
            clip = 5.0
            for gradient in (grad_Wxh, grad_Whh, grad_Whq, grad_bh, grad_bq):
                np.clip(gradient, -clip, clip, out=gradient)
            self.Wxh -= self.learning_rate * grad_Wxh
            self.Whh -= self.learning_rate * grad_Whh
            self.Whq -= self.learning_rate * grad_Whq
            self.bh -= self.learning_rate * grad_bh
            self.bq -= self.learning_rate * grad_bq
        self.online_updates += 1
        return loss

    def _change_detected(self) -> bool:
        # Reevaluate random detectors and compare their objective values.
        assert self.state is not None
        count = max(1, int(round(self.population_size * self.detector_fraction)))
        ids = self.random_state.choice(self.population_size, size=min(count, self.population_size), replace=False)
        old_F = self.state.F[ids].copy()
        new_F, new_CV = self.evaluate(self.state.X[ids])
        scale = np.maximum(np.abs(old_F), 1.0)
        changed = bool(np.any(np.abs(new_F - old_F) > self.change_tolerance * scale))
        if changed:
            self.state.F[ids] = new_F
            self.state.CV[ids] = new_CV
        return changed

    def _auxiliary_response(
        self,
        candidates: np.ndarray,
        current_samples: np.ndarray,
        prediction: np.ndarray,
        loss: float,
    ) -> np.ndarray:
        # Implement the loss-ranked random/mutated response and Equation 9 update.
        if self.loss_history:
            alpha = float(np.mean(loss <= np.asarray(self.loss_history)))
        else:
            alpha = 1.0
        auxiliary_count = max(1, int(round(0.2 * self.population_size)))
        additions: list[np.ndarray] = []
        if alpha > 0.5:
            random_count = int(round(auxiliary_count * alpha))
            mutation_count = auxiliary_count - random_count
            if random_count:
                additions.append(
                    self.random_state.uniform(self.xl, self.xu, size=(random_count, self.n_var))
                )
            if mutation_count:
                base = current_samples[
                    self.random_state.integers(0, current_samples.shape[0], size=mutation_count)
                ]
                noise = self.random_state.normal(size=base.shape) * (self.xu - self.xl) * self.mutation_scale
                additions.append(project_to_bounds(base + noise, self.xl, self.xu))

        center = np.mean(current_samples, axis=0)
        if self.previous_center is not None:
            shift = center - self.previous_center
            severity = np.abs(shift) / np.maximum(self.xu - self.xl, 1e-15)
            base = current_samples[
                self.random_state.integers(0, current_samples.shape[0], size=auxiliary_count)
            ].copy()
            update = severity > self.utest_threshold
            base[:, update] += shift[update]
            additions.append(project_to_bounds(base, self.xl, self.xu))
        self.previous_center = center
        self.loss_history.append(float(loss))
        return np.vstack([candidates, *additions]) if additions else candidates

    def _respond_to_change(self) -> None:
        # Run PSRNN and the adaptive auxiliary strategy after a detected change.
        assert self.state is not None
        current_samples = self._best_samples(self.state)
        if self.previous_samples is None:
            # Algorithm 2, t == 0: the first prediction set is random because
            # no historical transition exists from which to train the RNN.
            output = self.random_state.uniform(
                self.xl, self.xu, size=(self.sample_size, self.n_var)
            )
            hidden = self.hidden.copy()
            error = output - current_samples
            loss = float(0.5 * np.sum(error**2) / max(1, error.shape[0]))
        else:
            loss = self._online_train(self.previous_samples, current_samples)
            output, hidden, _ = self._forward(current_samples, self.hidden)
        prediction = project_to_bounds(output, self.xl, self.xu)
        self.hidden = hidden
        candidates = np.vstack((self.state.X, prediction))
        candidates = self._auxiliary_response(candidates, current_samples, prediction, loss)
        F, CV = self.evaluate(candidates)
        self.state = select_survivors_nsga2(candidates, F, CV, self.population_size)
        self.archive = self.build_archive(self.state)
        self.previous_samples = current_samples.copy()
        self.previous_prediction = prediction.copy()
        self.detected_changes += 1

    def generate_child(self, subproblem: int, pool: np.ndarray) -> np.ndarray:
        # Generate one MOEA/D-DE child before polynomial mutation.
        assert self.state is not None
        source = pool if pool.size >= 3 else np.arange(self.population_size)
        replace = source.size < 3
        r1, r2, r3 = self.random_state.choice(source, size=3, replace=replace)
        mutant = self.state.X[r1] + 0.5 * (self.state.X[r2] - self.state.X[r3])
        target = self.state.X[subproblem]
        trial = target.copy()
        forced = int(self.random_state.integers(0, self.n_var))
        mask = self.random_state.random(self.n_var) <= 1.0
        mask[forced] = True
        trial[mask] = mutant[mask]
        child = project_to_bounds(trial[None, :], self.xl, self.xu)
        return polynomial_mutation(
            child, self.xl, self.xu, self.mutation_eta,
            self.mutation_rate, self.random_state,
        )

    def step(self) -> None:
        # Detect and respond to a new environment before static MOEA/D-DE evolution.
        advance_time = getattr(self.problem, "advance_time", None)
        if callable(advance_time):
            advance_time(self.n_gen + 1)
        if self._change_detected():
            self._respond_to_change()
        super().step()


def make_rnn_guided_dmo(
    population_size: int = 100,
    neighborhood_size: int = 20,
    hidden_size: int = 16,
    prediction_fraction: float = 0.2,
    detector_fraction: float = 0.1,
    learning_rate: float = 0.01,
    training_epochs: int = 20,
    change_tolerance: float = 1e-10,
    mutation_scale: float = 0.1,
    utest_threshold: float = 0.5,
    seed: int = 1,
) -> RNNGuidedDMO:
    # Create the MOEA/D-RNN defined by Hu et al.
    size = parse_positive_int(population_size, "population_size")
    return RNNGuidedDMO(
        population_size=size,
        archive_size=size,
        n_neighbors=min(parse_positive_int(neighborhood_size, "neighborhood_size"), size),
        # The shared direction builder augments a modest lattice with deterministic
        # Dirichlet directions, avoiding a combinatorial lattice explosion for MaOPs.
        n_partitions=12,
        prob_neighbor_mating=0.9,
        max_replacements=2,
        mutation_rate=0.1,
        hidden_size=hidden_size,
        prediction_fraction=prediction_fraction,
        detector_fraction=detector_fraction,
        learning_rate=learning_rate,
        training_epochs=training_epochs,
        change_tolerance=change_tolerance,
        mutation_scale=mutation_scale,
        utest_threshold=utest_threshold,
        seed=seed,
    )


RNN_GUIDED_DMO_DEFINITION: Dict[str, Any] = {
    "label": "MOEA/D-RNN (adapted port)",
    "factory": make_rnn_guided_dmo,
    "implementation_type": "adapted_port",
    "source_commit": None,
    "reference": "Y. Hu et al., IEEE Transactions on Evolutionary Computation 29(5), 1820-1833 (2025), DOI 10.1109/TEVC.2024.3419892",
    "verified_against": "online-gradient, change-detection, auxiliary-response and MOEA/D-DE mechanism tests; no claim of statistical equivalence",
    "form_fields": {
        "population_size": {"default": 100, "kind": "int", "minimum": 4},
        "neighborhood_size": {"default": 20, "kind": "int", "minimum": 2},
        "hidden_size": {"default": 16, "kind": "int", "minimum": 1},
        "prediction_fraction": {"default": 0.2, "kind": "float", "minimum": 0.01, "maximum": 1.0},
        "detector_fraction": {"default": 0.1, "kind": "float", "minimum": 0.01, "maximum": 1.0},
        "learning_rate": {"default": 0.01, "kind": "float", "minimum": 1e-9},
        "training_epochs": {"default": 20, "kind": "int", "minimum": 1},
        "change_tolerance": {"default": 1e-10, "kind": "float", "minimum": 1e-15},
        "mutation_scale": {"default": 0.1, "kind": "float", "minimum": 1e-9},
        "utest_threshold": {"default": 0.5, "kind": "float", "minimum": 0.0, "maximum": 1.0},
        "seed": {"default": 1, "kind": "int", "minimum": 0},
    },
    "form_note": "Adapted MOEA/D-RNN port with online gradient training; mechanism-tested, without a claim of statistical equivalence to the article experiments.",
}
