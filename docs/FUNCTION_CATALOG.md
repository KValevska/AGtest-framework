# Katalog funkcji AGtest-framework v0.1

Dokument jest generowany z aktualnych drzew składniowych AST poleceniem
`python scripts/generate_function_catalog.py`. Obejmuje kod aplikacji, testy, metody,
funkcje zagnieżdżone i wyrażenia `lambda`; nie obejmuje symboli importowanych.

## Wynik analizy

- Przeanalizowano **101** plików Python.
- Kod uruchomieniowy zawiera **891** deklaracji funkcji i metod.
- Testy zawierają **119** deklaracji funkcji i metod.
- Łącznie znaleziono **1010** deklaracji, **139** klas i **62** wyrażeń `lambda`.

## Aktualny przepływ sterowania

1. `run_gui.py` uruchamia aplikację lub samodzielny test pakietu EXE.
2. `MainWindow` buduje trzy zakładki z rejestrów `PROBLEMS` i `ALGORITHMS`.
3. `OptimizationWorker` prowadzi obliczenia poza wątkiem GUI, również w trybie `RAN step`.
4. Callback generacyjny oblicza metryki i przekazuje migawki populacji do historii epok.
5. Widoki Pareto i trajektorii prezentują dane, a warstwa eksportu zapisuje PNG i XLSX.
6. `MultiExperimentWorker` wykonuje wybrane kombinacje problem–algorytm bez renderowania wykresów.

## Zestawienie modułów

| Plik | Deklaracje | Klasy | Lambda |
|---|---:|---:|---:|
| `run_gui.py` | 2 | 0 | 0 |
| `scripts/check_built_exe.py` | 1 | 0 | 0 |
| `scripts/generate_function_catalog.py` | 9 | 2 | 0 |
| `src/pymoo_gui/__init__.py` | 0 | 0 | 0 |
| `src/pymoo_gui/algorithms/__init__.py` | 3 | 1 | 0 |
| `src/pymoo_gui/algorithms/age.py` | 15 | 2 | 0 |
| `src/pymoo_gui/algorithms/article_algorithms_common.py` | 20 | 4 | 2 |
| `src/pymoo_gui/algorithms/cmobr.py` | 11 | 1 | 0 |
| `src/pymoo_gui/algorithms/cmoea_cd.py` | 12 | 1 | 1 |
| `src/pymoo_gui/algorithms/common.py` | 14 | 2 | 0 |
| `src/pymoo_gui/algorithms/disk.py` | 6 | 1 | 0 |
| `src/pymoo_gui/algorithms/diskplus.py` | 7 | 1 | 0 |
| `src/pymoo_gui/algorithms/dssea.py` | 11 | 1 | 2 |
| `src/pymoo_gui/algorithms/dvcea.py` | 10 | 1 | 0 |
| `src/pymoo_gui/algorithms/empty_algorithm_template.py` | 7 | 1 | 0 |
| `src/pymoo_gui/algorithms/encoding_operators.py` | 6 | 0 | 0 |
| `src/pymoo_gui/algorithms/eps_moea.py` | 2 | 1 | 0 |
| `src/pymoo_gui/algorithms/eps_nsga2.py` | 6 | 1 | 0 |
| `src/pymoo_gui/algorithms/gde3.py` | 9 | 1 | 0 |
| `src/pymoo_gui/algorithms/hype.py` | 28 | 2 | 0 |
| `src/pymoo_gui/algorithms/ibea.py` | 10 | 1 | 0 |
| `src/pymoo_gui/algorithms/learning_edmo.py` | 15 | 3 | 0 |
| `src/pymoo_gui/algorithms/lmoea_ds.py` | 18 | 1 | 0 |
| `src/pymoo_gui/algorithms/maotspp.py` | 7 | 1 | 0 |
| `src/pymoo_gui/algorithms/moead.py` | 1 | 1 | 0 |
| `src/pymoo_gui/algorithms/nsga2.py` | 1 | 1 | 0 |
| `src/pymoo_gui/algorithms/nsga3.py` | 1 | 1 | 0 |
| `src/pymoo_gui/algorithms/peaplus.py` | 5 | 1 | 0 |
| `src/pymoo_gui/algorithms/piea.py` | 19 | 2 | 0 |
| `src/pymoo_gui/algorithms/pimd.py` | 8 | 1 | 1 |
| `src/pymoo_gui/algorithms/platypus_common.py` | 15 | 3 | 0 |
| `src/pymoo_gui/algorithms/moead_iepsilon.py` | 6 | 1 | 0 |
| `src/pymoo_gui/algorithms/platypus_moead.py` | 0 | 0 | 0 |
| `src/pymoo_gui/algorithms/research_common.py` | 58 | 3 | 0 |
| `src/pymoo_gui/algorithms/rnn_guided_dmo.py` | 12 | 1 | 0 |
| `src/pymoo_gui/algorithms/rnsga3.py` | 7 | 1 | 0 |
| `src/pymoo_gui/algorithms/rvea.py` | 6 | 1 | 0 |
| `src/pymoo_gui/algorithms/spea2.py` | 1 | 1 | 0 |
| `src/pymoo_gui/algorithms/ssde.py` | 9 | 1 | 0 |
| `src/pymoo_gui/algorithms/surrogate_common.py` | 31 | 5 | 1 |
| `src/pymoo_gui/algorithms/tea.py` | 12 | 1 | 0 |
| `src/pymoo_gui/algorithms/ts_nsga.py` | 13 | 1 | 3 |
| `src/pymoo_gui/algorithms/tspp.py` | 5 | 1 | 0 |
| `src/pymoo_gui/algorithms/umaoea.py` | 13 | 1 | 2 |
| `src/pymoo_gui/algoritms/__init__.py` | 0 | 0 | 0 |
| `src/pymoo_gui/app.py` | 145 | 7 | 4 |
| `src/pymoo_gui/metrics/__init__.py` | 0 | 0 | 0 |
| `src/pymoo_gui/metrics/export.py` | 13 | 0 | 0 |
| `src/pymoo_gui/metrics/quality.py` | 25 | 1 | 0 |
| `src/pymoo_gui/multi.py` | 13 | 3 | 0 |
| `src/pymoo_gui/packaging_smoke.py` | 2 | 0 | 0 |
| `src/pymoo_gui/parallel.py` | 12 | 1 | 0 |
| `src/pymoo_gui/problems/__init__.py` | 0 | 0 | 0 |
| `src/pymoo_gui/problems/binh2.py` | 2 | 1 | 0 |
| `src/pymoo_gui/problems/capabilities.py` | 3 | 0 | 0 |
| `src/pymoo_gui/problems/constrex.py` | 2 | 1 | 0 |
| `src/pymoo_gui/problems/discrete.py` | 8 | 3 | 0 |
| `src/pymoo_gui/problems/dynamic.py` | 4 | 1 | 0 |
| `src/pymoo_gui/problems/empty_benchmark_template.py` | 4 | 1 | 0 |
| `src/pymoo_gui/problems/extended_continuous.py` | 19 | 4 | 0 |
| `src/pymoo_gui/problems/fonseca.py` | 2 | 1 | 0 |
| `src/pymoo_gui/problems/golinski.py` | 2 | 1 | 0 |
| `src/pymoo_gui/problems/kursawe.py` | 2 | 1 | 0 |
| `src/pymoo_gui/problems/lz09.py` | 16 | 10 | 0 |
| `src/pymoo_gui/problems/mw.py` | 50 | 15 | 0 |
| `src/pymoo_gui/problems/osyczka2.py` | 2 | 1 | 0 |
| `src/pymoo_gui/problems/registry.py` | 21 | 0 | 30 |
| `src/pymoo_gui/problems/schaffer.py` | 2 | 1 | 0 |
| `src/pymoo_gui/problems/srinivas.py` | 2 | 1 | 0 |
| `src/pymoo_gui/problems/tanaka.py` | 2 | 1 | 0 |
| `src/pymoo_gui/problems/uf.py` | 15 | 11 | 0 |
| `src/pymoo_gui/problems/viennet2.py` | 2 | 1 | 0 |
| `src/pymoo_gui/problems/viennet3.py` | 2 | 1 | 0 |
| `src/pymoo_gui/problems/water.py` | 2 | 1 | 0 |
| `src/pymoo_gui/problems/wfg.py` | 2 | 0 | 0 |
| `src/pymoo_gui/runtime.py` | 1 | 0 | 0 |
| `src/pymoo_gui/viz/__init__.py` | 0 | 0 | 0 |
| `src/pymoo_gui/viz/metric_trajectories.py` | 6 | 2 | 0 |
| `src/pymoo_gui/viz/pareto_dialogs.py` | 56 | 10 | 0 |
| `tests/conftest.py` | 0 | 0 | 0 |
| `tests/test_article_alignment_corrections.py` | 9 | 0 | 0 |
| `tests/test_cmoea_cd_cmobr.py` | 7 | 0 | 1 |
| `tests/test_custom_algorithm_runtime.py` | 6 | 0 | 0 |
| `tests/test_delta.py` | 5 | 0 | 0 |
| `tests/test_dssea_pimd_umaoea.py` | 8 | 0 | 2 |
| `tests/test_dtlz_pareto_fronts.py` | 4 | 0 | 0 |
| `tests/test_dvcea_dssea_import.py` | 7 | 0 | 1 |
| `tests/test_empty_benchmark_template.py` | 3 | 0 | 0 |
| `tests/test_expanded_benchmark_capabilities.py` | 10 | 0 | 0 |
| `tests/test_kktpm.py` | 4 | 0 | 0 |
| `tests/test_lmoea_ds_runtime.py` | 1 | 0 | 0 |
| `tests/test_metric_trajectories.py` | 5 | 0 | 0 |
| `tests/test_multi.py` | 10 | 0 | 0 |
| `tests/test_package_exports.py` | 2 | 0 | 0 |
| `tests/test_pareto_labels.py` | 1 | 0 | 0 |
| `tests/test_plot_controls.py` | 10 | 0 | 12 |
| `tests/test_recent_algorithms.py` | 9 | 0 | 0 |
| `tests/test_registry_integrity.py` | 4 | 0 | 0 |
| `tests/test_rewritten_article_algorithms.py` | 9 | 1 | 0 |
| `tests/test_runtime_paths.py` | 2 | 0 | 0 |
| `tests/test_standalone_classic_algorithms.py` | 2 | 0 | 0 |
| `tests/test_version.py` | 1 | 0 | 0 |

## Pełny indeks deklaracji

### `run_gui.py`

- `_ensure_src_on_path() -> None` — funkcja modułowa; [wiersz 18](../run_gui.py#L18).
- `main() -> None` — funkcja modułowa; [wiersz 28](../run_gui.py#L28).

### `scripts/check_built_exe.py`

- `main() -> None` — funkcja modułowa; [wiersz 11](../scripts/check_built_exe.py#L11).

### `scripts/generate_function_catalog.py`

- `CatalogVisitor.__init__(self) -> None` — metoda; [wiersz 24](../scripts/generate_function_catalog.py#L24).
- `CatalogVisitor.visit_ClassDef(self, node: ast.ClassDef) -> None` — metoda; [wiersz 30](../scripts/generate_function_catalog.py#L30).
- `CatalogVisitor.visit_FunctionDef(self, node: ast.FunctionDef) -> None` — metoda; [wiersz 36](../scripts/generate_function_catalog.py#L36).
- `CatalogVisitor.visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None` — metoda; [wiersz 39](../scripts/generate_function_catalog.py#L39).
- `CatalogVisitor._record_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef, *, async_function: bool) -> None` — metoda; [wiersz 42](../scripts/generate_function_catalog.py#L42).
- `CatalogVisitor.visit_Lambda(self, node: ast.Lambda) -> None` — metoda; [wiersz 58](../scripts/generate_function_catalog.py#L58).
- `python_files() -> list[Path]` — funkcja modułowa; [wiersz 63](../scripts/generate_function_catalog.py#L63).
- `analyze(path: Path) -> CatalogVisitor` — funkcja modułowa; [wiersz 70](../scripts/generate_function_catalog.py#L70).
- `main() -> None` — funkcja modułowa; [wiersz 76](../scripts/generate_function_catalog.py#L76).

### `src/pymoo_gui/__init__.py`

Brak deklaracji funkcji i wyrażeń `lambda`.

### `src/pymoo_gui/algorithms/__init__.py`

- `minimize(problem: Any, algorithm: Any, termination: Any, **kwargs: Any) -> Any` — funkcja modułowa; [wiersz 110](../src/pymoo_gui/algorithms/__init__.py#L110).
- `validate_algorithm_problem(algorithm_entry: Dict[str, Any], problem: Any) -> None` — funkcja modułowa; [wiersz 126](../src/pymoo_gui/algorithms/__init__.py#L126).
- `compatibility_matrix(problems: Dict[str, Dict[str, Any]]) -> list[Dict[str, str]]` — funkcja modułowa; [wiersz 165](../src/pymoo_gui/algorithms/__init__.py#L165).

### `src/pymoo_gui/algorithms/age.py`

- `_parse_positive_int(value: Any, field_name: str) -> int` — funkcja modułowa; [wiersz 28](../src/pymoo_gui/algorithms/age.py#L28).
- `_parse_optional_positive_int(value: Any, field_name: str) -> Optional[int]` — funkcja modułowa; [wiersz 39](../src/pymoo_gui/algorithms/age.py#L39).
- `point_2_line_distance(points: np.ndarray, start: np.ndarray, end: np.ndarray) -> np.ndarray` — funkcja modułowa; [wiersz 46](../src/pymoo_gui/algorithms/age.py#L46).
- `find_corner_solutions(front: np.ndarray) -> np.ndarray` — funkcja modułowa; [wiersz 59](../src/pymoo_gui/algorithms/age.py#L59).
- `normalize(front: np.ndarray, extreme: np.ndarray) -> tuple[np.ndarray, np.ndarray]` — funkcja modułowa; [wiersz 78](../src/pymoo_gui/algorithms/age.py#L78).
- `AGEMOEASurvival.__init__(self) -> None` — metoda; [wiersz 106](../src/pymoo_gui/algorithms/age.py#L106).
- `AGEMOEASurvival._do(self, problem, pop, *args, n_survive=None, **kwargs)` — metoda; [wiersz 110](../src/pymoo_gui/algorithms/age.py#L110).
- `AGEMOEASurvival.survival_score(self, front: np.ndarray, ideal_point: np.ndarray) -> tuple[np.ndarray, float, np.ndarray]` — metoda; [wiersz 143](../src/pymoo_gui/algorithms/age.py#L143).
- `AGEMOEASurvival.compute_geometry(front: np.ndarray, extreme: np.ndarray, n_obj: int) -> float` — metoda; [wiersz 191](../src/pymoo_gui/algorithms/age.py#L191).
- `AGEMOEASurvival.pairwise_distances(front: np.ndarray, p: float) -> np.ndarray` — metoda; [wiersz 208](../src/pymoo_gui/algorithms/age.py#L208).
- `AGEMOEASurvival.minkowski_distances(A: np.ndarray, B: np.ndarray, p: float) -> np.ndarray` — metoda; [wiersz 217](../src/pymoo_gui/algorithms/age.py#L217).
- `AGE.__init__(self, pop_size: int=100, n_offsprings: Optional[int]=None, **kwargs)` — metoda; [wiersz 231](../src/pymoo_gui/algorithms/age.py#L231).
- `AGE.create_offspring(self) -> np.ndarray` — metoda; [wiersz 242](../src/pymoo_gui/algorithms/age.py#L242).
- `AGE.environmental_selection(self, X, F, CV, n_survive)` — metoda; [wiersz 246](../src/pymoo_gui/algorithms/age.py#L246).
- `make_age(pop_size: int=100, n_offsprings: Optional[int]=None) -> AGE` — funkcja modułowa; [wiersz 276](../src/pymoo_gui/algorithms/age.py#L276).

### `src/pymoo_gui/algorithms/article_algorithms_common.py`

- `_state(X: np.ndarray, F: np.ndarray, CV: np.ndarray) -> PopulationState` — funkcja modułowa; [wiersz 32](../src/pymoo_gui/algorithms/article_algorithms_common.py#L32).
- `nsga3_normalize(F: np.ndarray) -> np.ndarray` — funkcja modułowa; [wiersz 37](../src/pymoo_gui/algorithms/article_algorithms_common.py#L37).
- `associate(F: np.ndarray, ref_dirs: np.ndarray) -> tuple[np.ndarray, np.ndarray]` — funkcja modułowa; [wiersz 59](../src/pymoo_gui/algorithms/article_algorithms_common.py#L59).
- `nsga3_survival(X: np.ndarray, F: np.ndarray, CV: np.ndarray, n_survive: int, ref_dirs: np.ndarray, rng: np.random.Generator) -> PopulationState` — funkcja modułowa; [wiersz 70](../src/pymoo_gui/algorithms/article_algorithms_common.py#L70).
- `NSGA3Algorithm.environmental_selection(self, X, F, CV, n_survive)` — metoda; [wiersz 125](../src/pymoo_gui/algorithms/article_algorithms_common.py#L125).
- `MOEADAlgorithm.__init__(self, prob_neighbor_mating: float=0.7, max_replacements: int=2, **kwargs)` — metoda; [wiersz 133](../src/pymoo_gui/algorithms/article_algorithms_common.py#L133).
- `MOEADAlgorithm.after_initialize(self) -> None` — metoda; [wiersz 140](../src/pymoo_gui/algorithms/article_algorithms_common.py#L140).
- `MOEADAlgorithm._scalar(self, F: np.ndarray, weights: np.ndarray) -> np.ndarray` — metoda; [wiersz 148](../src/pymoo_gui/algorithms/article_algorithms_common.py#L148).
- `MOEADAlgorithm.build_archive(self, state: PopulationState) -> PopulationState` — metoda; [wiersz 151](../src/pymoo_gui/algorithms/article_algorithms_common.py#L151).
- `MOEADAlgorithm.replacement_allowed(self, child_f, child_cv, target_f, target_cv, weights) -> bool` — metoda; [wiersz 173](../src/pymoo_gui/algorithms/article_algorithms_common.py#L173).
- `MOEADAlgorithm.generate_child(self, subproblem: int, pool: np.ndarray) -> np.ndarray` — metoda; [wiersz 183](../src/pymoo_gui/algorithms/article_algorithms_common.py#L183).
- `MOEADAlgorithm.step(self) -> None` — metoda; [wiersz 196](../src/pymoo_gui/algorithms/article_algorithms_common.py#L196).
- `epsilon_box(F: np.ndarray, epsilons: np.ndarray) -> np.ndarray` — funkcja modułowa; [wiersz 229](../src/pymoo_gui/algorithms/article_algorithms_common.py#L229).
- `epsilon_archive_indices(F: np.ndarray, CV: np.ndarray, epsilons: np.ndarray) -> np.ndarray` — funkcja modułowa; [wiersz 233](../src/pymoo_gui/algorithms/article_algorithms_common.py#L233).
- `EpsilonArchiveAlgorithm.__init__(self, epsilons: np.ndarray, steady_state: bool=False, **kwargs)` — metoda; [wiersz 262](../src/pymoo_gui/algorithms/article_algorithms_common.py#L262).
- `EpsilonArchiveAlgorithm.build_archive(self, state: PopulationState) -> PopulationState` — metoda; [wiersz 267](../src/pymoo_gui/algorithms/article_algorithms_common.py#L267).
- `EpsilonArchiveAlgorithm.step(self) -> None` — metoda; [wiersz 280](../src/pymoo_gui/algorithms/article_algorithms_common.py#L280).
- `spea2_fitness(F: np.ndarray, CV: np.ndarray) -> np.ndarray` — funkcja modułowa; [wiersz 300](../src/pymoo_gui/algorithms/article_algorithms_common.py#L300).
- `spea2_survival(X, F, CV, n_survive) -> PopulationState` — funkcja modułowa; [wiersz 317](../src/pymoo_gui/algorithms/article_algorithms_common.py#L317).
- `SPEA2Algorithm.environmental_selection(self, X, F, CV, n_survive)` — metoda; [wiersz 338](../src/pymoo_gui/algorithms/article_algorithms_common.py#L338).
- `lambda` — wyrażenie anonimowe; [wiersz 112](../src/pymoo_gui/algorithms/article_algorithms_common.py#L112).
- `lambda` — wyrażenie anonimowe; [wiersz 329](../src/pymoo_gui/algorithms/article_algorithms_common.py#L329).

### `src/pymoo_gui/algorithms/cmobr.py`

- `relative_front_change(history: list[np.ndarray], window: int) -> float` — funkcja modułowa; [wiersz 38](../src/pymoo_gui/algorithms/cmobr.py#L38).
- `epsilon_relaxation(current: float, initial: float, feasible_ratio: float, progress: float) -> float` — funkcja modułowa; [wiersz 46](../src/pymoo_gui/algorithms/cmobr.py#L46).
- `CMOBR.__init__(self, population_size: int=40, delta: float=0.9, nr: int=2, stagnation_window: int=20, change_threshold: float=0.1, seed: int=1) -> None` — metoda; [wiersz 55](../src/pymoo_gui/algorithms/cmobr.py#L55).
- `CMOBR.gui_minimize(self, *, problem: Any, termination: Any, **kwargs: Any)` — metoda; [wiersz 83](../src/pymoo_gui/algorithms/cmobr.py#L83).
- `CMOBR.after_initialize(self) -> None` — metoda; [wiersz 87](../src/pymoo_gui/algorithms/cmobr.py#L87).
- `CMOBR._trial_matrix(self, state: PopulationState) -> tuple[np.ndarray, list[np.ndarray]]` — metoda; [wiersz 99](../src/pymoo_gui/algorithms/cmobr.py#L99).
- `CMOBR._tchebycheff(F: np.ndarray, ideal: np.ndarray, weights: np.ndarray) -> np.ndarray` — metoda; [wiersz 115](../src/pymoo_gui/algorithms/cmobr.py#L115).
- `CMOBR._replace(self, state: PopulationState, child_X: np.ndarray, child_F: np.ndarray, child_CV: float, pool: np.ndarray, ideal: np.ndarray, epsilon: float | None, eta: float | None=None) -> None` — metoda; [wiersz 118](../src/pymoo_gui/algorithms/cmobr.py#L118).
- `CMOBR._evolve(self, state: PopulationState, ideal: np.ndarray, epsilon: float | None, eta: float | None=None) -> np.ndarray` — metoda; [wiersz 139](../src/pymoo_gui/algorithms/cmobr.py#L139).
- `CMOBR.step(self) -> None` — metoda; [wiersz 148](../src/pymoo_gui/algorithms/cmobr.py#L148).
- `make_cmobr(pop_size: int=40, delta: float=0.9, nr: int=2, stagnation_window: int=20, change_threshold: float=0.1, seed: int=1) -> CMOBR` — funkcja modułowa; [wiersz 181](../src/pymoo_gui/algorithms/cmobr.py#L181).

### `src/pymoo_gui/algorithms/cmoea_cd.py`

- `_state(X: np.ndarray, F: np.ndarray, CV: np.ndarray) -> PopulationState` — funkcja modułowa; [wiersz 38](../src/pymoo_gui/algorithms/cmoea_cd.py#L38).
- `constraint_pareto_mask(F: np.ndarray, CV: np.ndarray, constrained: bool) -> np.ndarray` — funkcja modułowa; [wiersz 43](../src/pymoo_gui/algorithms/cmoea_cd.py#L43).
- `_truncate_distance(F: np.ndarray, count: int) -> np.ndarray` — funkcja modułowa; [wiersz 59](../src/pymoo_gui/algorithms/cmoea_cd.py#L59).
- `_mode_indices(F: np.ndarray, count: int, mode: int, refs: np.ndarray) -> np.ndarray` — funkcja modułowa; [wiersz 71](../src/pymoo_gui/algorithms/cmoea_cd.py#L71).
- `CMOEACD.__init__(self, population_size: int=90, e1: int=1, e2: int=1, seed: int=1)` — metoda; [wiersz 89](../src/pymoo_gui/algorithms/cmoea_cd.py#L89).
- `CMOEACD.after_initialize(self) -> None` — metoda; [wiersz 100](../src/pymoo_gui/algorithms/cmoea_cd.py#L100).
- `CMOEACD._merged(self, old: PopulationState | None, new: PopulationState) -> tuple[np.ndarray, np.ndarray, np.ndarray]` — metoda; [wiersz 107](../src/pymoo_gui/algorithms/cmoea_cd.py#L107).
- `CMOEACD._update_archive(self, old: PopulationState | None, new: PopulationState, count: int, mode: int, constrained: bool) -> PopulationState` — metoda; [wiersz 112](../src/pymoo_gui/algorithms/cmoea_cd.py#L112).
- `CMOEACD._update_da(self, old: PopulationState | None, new: PopulationState, count: int) -> PopulationState` — metoda; [wiersz 119](../src/pymoo_gui/algorithms/cmoea_cd.py#L119).
- `CMOEACD._children(self) -> np.ndarray` — metoda; [wiersz 136](../src/pymoo_gui/algorithms/cmoea_cd.py#L136).
- `CMOEACD.step(self) -> None` — metoda; [wiersz 155](../src/pymoo_gui/algorithms/cmoea_cd.py#L155).
- `make_cmoea_cd(pop_size: int=90, e1: int=1, e2: int=1, seed: int=1) -> CMOEACD` — funkcja modułowa; [wiersz 169](../src/pymoo_gui/algorithms/cmoea_cd.py#L169).
- `lambda` — wyrażenie anonimowe; [wiersz 67](../src/pymoo_gui/algorithms/cmoea_cd.py#L67).

### `src/pymoo_gui/algorithms/common.py`

- `_safe_int(value: Optional[object]) -> Optional[int]` — funkcja modułowa; [wiersz 51](../src/pymoo_gui/algorithms/common.py#L51).
- `_report_issue(messages: Optional[list[str]], message: str) -> None` — funkcja modułowa; [wiersz 61](../src/pymoo_gui/algorithms/common.py#L61).
- `_record_diagnostic(messages: Optional[list[str]], context: str, exc: BaseException) -> None` — funkcja modułowa; [wiersz 69](../src/pymoo_gui/algorithms/common.py#L69).
- `_pareto_front_call_kwargs(pf_fn: Any) -> Dict[str, Any]` — funkcja modułowa; [wiersz 74](../src/pymoo_gui/algorithms/common.py#L74).
- `_default_ref_dirs(pf_fn: Any) -> np.ndarray` — funkcja modułowa; [wiersz 86](../src/pymoo_gui/algorithms/common.py#L86).
- `_as_objective_matrix(values: Optional[np.ndarray]) -> Optional[np.ndarray]` — funkcja modułowa; [wiersz 98](../src/pymoo_gui/algorithms/common.py#L98).
- `known_pareto_front(problem: Any, diagnostics: Optional[list[str]]=None) -> Optional[np.ndarray]` — funkcja modułowa; [wiersz 114](../src/pymoo_gui/algorithms/common.py#L114).
- `_feasibility_mask_from_cv(cv: Optional[np.ndarray]) -> Optional[np.ndarray]` — funkcja modułowa; [wiersz 153](../src/pymoo_gui/algorithms/common.py#L153).
- `_unique_rows(values: Optional[np.ndarray]) -> Optional[np.ndarray]` — funkcja modułowa; [wiersz 168](../src/pymoo_gui/algorithms/common.py#L168).
- `_feasible_nondominated_front(F: Optional[np.ndarray], CV: Optional[np.ndarray]=None, diagnostics: Optional[list[str]]=None) -> tuple[Optional[np.ndarray], Optional[int]]` — funkcja modułowa; [wiersz 180](../src/pymoo_gui/algorithms/common.py#L180).
- `_feasible_nondominated_front_with_indices(F: Optional[np.ndarray], CV: Optional[np.ndarray]=None, diagnostics: Optional[list[str]]=None) -> tuple[Optional[np.ndarray], Optional[np.ndarray], Optional[int]]` — funkcja modułowa; [wiersz 190](../src/pymoo_gui/algorithms/common.py#L190).
- `_population_values(algorithm: Any) -> tuple[Optional[np.ndarray], Optional[np.ndarray], Optional[np.ndarray]]` — funkcja modułowa; [wiersz 256](../src/pymoo_gui/algorithms/common.py#L256).
- `make_generation_callback(on_generation: Callable[[GenerationPayload], None], problem: Any=None, hv_ref_point: Optional[list[float]]=None, known_pf: Optional[np.ndarray]=None, algorithm_key: Optional[str]=None) -> Callback` — funkcja modułowa; [wiersz 267](../src/pymoo_gui/algorithms/common.py#L267).
- `make_generation_callback._GenCallback.notify(self, algorithm)` — metoda; [wiersz 297](../src/pymoo_gui/algorithms/common.py#L297).

### `src/pymoo_gui/algorithms/disk.py`

- `distribution_weights(decisions: np.ndarray, mean: np.ndarray, covariance: np.ndarray) -> np.ndarray` — funkcja modułowa; [wiersz 41](../src/pymoo_gui/algorithms/disk.py#L41).
- `_reference(objectives: np.ndarray, constraints: np.ndarray, count: int) -> np.ndarray` — funkcja modułowa; [wiersz 54](../src/pymoo_gui/algorithms/disk.py#L54).
- `run_disk(function: Callable[[np.ndarray], Any], lower: np.ndarray, upper: np.ndarray, population_size: int, maximum_generations: Optional[int], surrogate_generations: int, infill_batch_size: int, seed: int, constrained: bool, generation_hook: Callable[[SurrogateProblem], None]) -> SurrogateResult` — funkcja modułowa; [wiersz 66](../src/pymoo_gui/algorithms/disk.py#L66).
- `DISK.__init__(self, population_size: int=40, surrogate_generations: int=10, infill_batch_size: int=5, seed: int=1) -> None` — metoda; [wiersz 245](../src/pymoo_gui/algorithms/disk.py#L245).
- `DISK._run_surrogate(self, function, lower, upper, maximum_generations, seed, generation_hook)` — metoda; [wiersz 262](../src/pymoo_gui/algorithms/disk.py#L262).
- `make_disk(population_size: int=40, surrogate_generations: int=10, infill_batch_size: int=5, seed: int=1) -> DISK` — funkcja modułowa; [wiersz 278](../src/pymoo_gui/algorithms/disk.py#L278).

### `src/pymoo_gui/algorithms/diskplus.py`

- `decision_distribution(decisions: np.ndarray, center: np.ndarray, covariance: np.ndarray) -> np.ndarray` — funkcja modułowa; [wiersz 38](../src/pymoo_gui/algorithms/diskplus.py#L38).
- `cdipd_sort(decisions: np.ndarray, objectives: np.ndarray, objective_variance: np.ndarray, constraints: np.ndarray, center: np.ndarray, covariance: np.ndarray) -> np.ndarray` — funkcja modułowa; [wiersz 52](../src/pymoo_gui/algorithms/diskplus.py#L52).
- `_reference_mask(objectives: np.ndarray, constraints: np.ndarray, count: int) -> np.ndarray` — funkcja modułowa; [wiersz 70](../src/pymoo_gui/algorithms/diskplus.py#L70).
- `run_diskplus(function: Callable[[np.ndarray], Any], lower: np.ndarray, upper: np.ndarray, population_size: int, maximum_generations: Optional[int], surrogate_generations: int, infill_batch_size: int, seed: int, generation_hook: Callable[[SurrogateProblem], None]) -> SurrogateResult` — funkcja modułowa; [wiersz 80](../src/pymoo_gui/algorithms/diskplus.py#L80).
- `DISKplus.__init__(self, population_size: int=40, surrogate_generations: int=60, infill_batch_size: int=5, seed: int=1) -> None` — metoda; [wiersz 203](../src/pymoo_gui/algorithms/diskplus.py#L203).
- `DISKplus._run_surrogate(self, function, lower, upper, maximum_generations, seed, generation_hook)` — metoda; [wiersz 216](../src/pymoo_gui/algorithms/diskplus.py#L216).
- `make_diskplus(population_size: int=40, surrogate_generations: int=60, infill_batch_size: int=5, seed: int=1) -> DISKplus` — funkcja modułowa; [wiersz 230](../src/pymoo_gui/algorithms/diskplus.py#L230).

### `src/pymoo_gui/algorithms/dssea.py`

- `epsilon_spea2_fitness(F: np.ndarray, CV: np.ndarray, epsilon: float) -> np.ndarray` — funkcja modułowa; [wiersz 35](../src/pymoo_gui/algorithms/dssea.py#L35).
- `epsilon_spea2_survival(X: np.ndarray, F: np.ndarray, CV: np.ndarray, count: int, epsilon: float) -> tuple[PopulationState, np.ndarray]` — funkcja modułowa; [wiersz 60](../src/pymoo_gui/algorithms/dssea.py#L60).
- `DSSEA.__init__(self, population_size: int=100, n_sel: int=2, n_per: int=4, seed: int=1) -> None` — metoda; [wiersz 91](../src/pymoo_gui/algorithms/dssea.py#L91).
- `DSSEA._aldva(self) -> np.ndarray` — metoda; [wiersz 113](../src/pymoo_gui/algorithms/dssea.py#L113).
- `DSSEA.after_initialize(self) -> None` — metoda; [wiersz 156](../src/pymoo_gui/algorithms/dssea.py#L156).
- `DSSEA._active_variables(self) -> np.ndarray` — metoda; [wiersz 164](../src/pymoo_gui/algorithms/dssea.py#L164).
- `DSSEA._pbest_offspring(self, active: np.ndarray) -> np.ndarray` — metoda; [wiersz 176](../src/pymoo_gui/algorithms/dssea.py#L176).
- `DSSEA._ga_offspring(self, active: np.ndarray) -> np.ndarray` — metoda; [wiersz 208](../src/pymoo_gui/algorithms/dssea.py#L208).
- `DSSEA.step(self) -> None` — metoda; [wiersz 231](../src/pymoo_gui/algorithms/dssea.py#L231).
- `DSSEA.gui_minimize(self, *, problem: Any, termination: Any, **kwargs: Any)` — metoda; [wiersz 257](../src/pymoo_gui/algorithms/dssea.py#L257).
- `make_dssea(population_size: int=100, n_sel: int=2, n_per: int=4, seed: int=1) -> DSSEA` — funkcja modułowa; [wiersz 263](../src/pymoo_gui/algorithms/dssea.py#L263).
- `lambda` — wyrażenie anonimowe; [wiersz 80](../src/pymoo_gui/algorithms/dssea.py#L80).
- `lambda` — wyrażenie anonimowe; [wiersz 82](../src/pymoo_gui/algorithms/dssea.py#L82).

### `src/pymoo_gui/algorithms/dvcea.py`

- `kmeans_centroids(X: np.ndarray, count: int, rng: np.random.Generator, iterations: int=35) -> np.ndarray` — funkcja modułowa; [wiersz 36](../src/pymoo_gui/algorithms/dvcea.py#L36).
- `improved_epsilon_survival(X: np.ndarray, F: np.ndarray, CV: np.ndarray, count: int, epsilon: float) -> tuple[PopulationState, np.ndarray]` — funkcja modułowa; [wiersz 54](../src/pymoo_gui/algorithms/dvcea.py#L54).
- `DVCEA.__init__(self, population_size: int=40, classification_threshold: float=1e-05, seed: int=1)` — metoda; [wiersz 87](../src/pymoo_gui/algorithms/dvcea.py#L87).
- `DVCEA.gui_minimize(self, *, problem: Any, termination: Any, **kwargs: Any)` — metoda; [wiersz 99](../src/pymoo_gui/algorithms/dvcea.py#L99).
- `DVCEA.after_initialize(self) -> None` — metoda; [wiersz 104](../src/pymoo_gui/algorithms/dvcea.py#L104).
- `DVCEA._pbest_children(self) -> np.ndarray` — metoda; [wiersz 123](../src/pymoo_gui/algorithms/dvcea.py#L123).
- `DVCEA._diversity_children(self) -> np.ndarray` — metoda; [wiersz 142](../src/pymoo_gui/algorithms/dvcea.py#L142).
- `DVCEA._select_with(self, children: np.ndarray) -> None` — metoda; [wiersz 162](../src/pymoo_gui/algorithms/dvcea.py#L162).
- `DVCEA.step(self) -> None` — metoda; [wiersz 168](../src/pymoo_gui/algorithms/dvcea.py#L168).
- `make_dvcea(pop_size: int=40, classification_threshold: float=1e-05, seed: int=1) -> DVCEA` — funkcja modułowa; [wiersz 180](../src/pymoo_gui/algorithms/dvcea.py#L180).

### `src/pymoo_gui/algorithms/empty_algorithm_template.py`

- `EmptyAlgorithmTemplate.__init__(self, population_size: int=100, archive_size: int=100, crossover_rate: float=0.9, mutation_rate: float=0.1, template_bias: float=0.5, seed: int=1) -> None` — metoda; [wiersz 26](../src/pymoo_gui/algorithms/empty_algorithm_template.py#L26).
- `EmptyAlgorithmTemplate.after_initialize(self) -> None` — metoda; [wiersz 52](../src/pymoo_gui/algorithms/empty_algorithm_template.py#L52).
- `EmptyAlgorithmTemplate.guided_candidates(self) -> np.ndarray` — metoda; [wiersz 57](../src/pymoo_gui/algorithms/empty_algorithm_template.py#L57).
- `EmptyAlgorithmTemplate.create_offspring(self) -> np.ndarray` — metoda; [wiersz 64](../src/pymoo_gui/algorithms/empty_algorithm_template.py#L64).
- `EmptyAlgorithmTemplate.environmental_selection(self, X: np.ndarray, F: np.ndarray, CV: np.ndarray, n_survive: int) -> PopulationState` — metoda; [wiersz 76](../src/pymoo_gui/algorithms/empty_algorithm_template.py#L76).
- `EmptyAlgorithmTemplate.after_generation(self, previous: PopulationState, current: PopulationState) -> None` — metoda; [wiersz 96](../src/pymoo_gui/algorithms/empty_algorithm_template.py#L96).
- `make_empty_algorithm_template(population_size: int=100, archive_size: int=100, crossover_rate: float=0.9, mutation_rate: float=0.1, template_bias: float=0.5, seed: int=1) -> EmptyAlgorithmTemplate` — funkcja modułowa; [wiersz 106](../src/pymoo_gui/algorithms/empty_algorithm_template.py#L106).

### `src/pymoo_gui/algorithms/encoding_operators.py`

- `binary_sample(size: tuple[int, int], rng: np.random.Generator) -> np.ndarray` — funkcja modułowa; [wiersz 8](../src/pymoo_gui/algorithms/encoding_operators.py#L8).
- `binary_crossover(population: np.ndarray, parent_pairs: np.ndarray, probability: float, rng: np.random.Generator) -> np.ndarray` — funkcja modułowa; [wiersz 12](../src/pymoo_gui/algorithms/encoding_operators.py#L12).
- `bitflip_mutation(X: np.ndarray, probability: float, rng: np.random.Generator) -> np.ndarray` — funkcja modułowa; [wiersz 30](../src/pymoo_gui/algorithms/encoding_operators.py#L30).
- `integer_sample(lower: np.ndarray, upper: np.ndarray, count: int, rng: np.random.Generator) -> np.ndarray` — funkcja modułowa; [wiersz 36](../src/pymoo_gui/algorithms/encoding_operators.py#L36).
- `integer_repair(X: np.ndarray, lower: np.ndarray, upper: np.ndarray) -> np.ndarray` — funkcja modułowa; [wiersz 47](../src/pymoo_gui/algorithms/encoding_operators.py#L47).
- `mixed_repair(X: np.ndarray, problem: object) -> np.ndarray` — funkcja modułowa; [wiersz 51](../src/pymoo_gui/algorithms/encoding_operators.py#L51).

### `src/pymoo_gui/algorithms/eps_moea.py`

- `EpsMOEA.create_offspring(self) -> np.ndarray` — metoda; [wiersz 22](../src/pymoo_gui/algorithms/eps_moea.py#L22).
- `make_eps_moea(problem: Any, population_size: int=100, epsilons: Any=0.01) -> EpsMOEA` — funkcja modułowa; [wiersz 40](../src/pymoo_gui/algorithms/eps_moea.py#L40).

### `src/pymoo_gui/algorithms/eps_nsga2.py`

- `_state(X: np.ndarray, F: np.ndarray, CV: np.ndarray) -> PopulationState` — funkcja modułowa; [wiersz 30](../src/pymoo_gui/algorithms/eps_nsga2.py#L30).
- `EpsNSGAII.__init__(self, *, injection_rate: float=0.25, window_size: int=20, improvement_threshold: float=0.1, minimum_population_size: int=10, maximum_population_size: int=10000, **kwargs: Any) -> None` — metoda; [wiersz 39](../src/pymoo_gui/algorithms/eps_nsga2.py#L39).
- `EpsNSGAII.after_initialize(self) -> None` — metoda; [wiersz 68](../src/pymoo_gui/algorithms/eps_nsga2.py#L68).
- `EpsNSGAII._connected_run_restart(self) -> None` — metoda; [wiersz 73](../src/pymoo_gui/algorithms/eps_nsga2.py#L73).
- `EpsNSGAII.after_generation(self, previous: PopulationState, current: PopulationState) -> None` — metoda; [wiersz 91](../src/pymoo_gui/algorithms/eps_nsga2.py#L91).
- `make_eps_nsga2(problem: Any, population_size: int=10, epsilons: Any=0.01, injection_rate: float=0.25, window_size: int=20, improvement_threshold: float=0.1, minimum_population_size: int=10, maximum_population_size: int=10000) -> EpsNSGAII` — funkcja modułowa; [wiersz 103](../src/pymoo_gui/algorithms/eps_nsga2.py#L103).

### `src/pymoo_gui/algorithms/gde3.py`

- `_dominates(lhs: np.ndarray, rhs: np.ndarray) -> bool` — funkcja modułowa; [wiersz 33](../src/pymoo_gui/algorithms/gde3.py#L33).
- `_weakly_constraint_dominates(lhs_f: np.ndarray, lhs_cv: float, rhs_f: np.ndarray, rhs_cv: float) -> bool` — funkcja modułowa; [wiersz 38](../src/pymoo_gui/algorithms/gde3.py#L38).
- `_parse_de_weight(value: Any, field_name: str) -> float` — funkcja modułowa; [wiersz 51](../src/pymoo_gui/algorithms/gde3.py#L51).
- `GDE3.__init__(self, pop_size: int=100, f_weight: float=0.5, crossover_rate: float=0.3, seed: int=1) -> None` — metoda; [wiersz 62](../src/pymoo_gui/algorithms/gde3.py#L62).
- `GDE3._trial_population(self) -> np.ndarray` — metoda; [wiersz 78](../src/pymoo_gui/algorithms/gde3.py#L78).
- `GDE3._pruning_crowding(self, F: np.ndarray, n_survive: int) -> np.ndarray` — metoda; [wiersz 98](../src/pymoo_gui/algorithms/gde3.py#L98).
- `GDE3._reduce_population(self, X: np.ndarray, F: np.ndarray, CV: np.ndarray, n_survive: int) -> PopulationState` — metoda; [wiersz 113](../src/pymoo_gui/algorithms/gde3.py#L113).
- `GDE3.step(self) -> None` — metoda; [wiersz 149](../src/pymoo_gui/algorithms/gde3.py#L149).
- `make_gde3(pop_size: int=100, f_weight: float=0.5, crossover_rate: float=0.3, seed: int=1) -> GDE3` — funkcja modułowa; [wiersz 205](../src/pymoo_gui/algorithms/gde3.py#L205).

### `src/pymoo_gui/algorithms/hype.py`

- `_parse_positive_int(value: Any, field_name: str) -> int` — funkcja modułowa; [wiersz 25](../src/pymoo_gui/algorithms/hype.py#L25).
- `_rng_int(rng: Optional[np.random.Generator], high: int, size: Optional[int | tuple[int, ...]]=None)` — funkcja modułowa; [wiersz 38](../src/pymoo_gui/algorithms/hype.py#L38).
- `_rng_random(rng: Optional[np.random.Generator]) -> float` — funkcja modułowa; [wiersz 47](../src/pymoo_gui/algorithms/hype.py#L47).
- `_clean_reference(value: Any) -> Any` — funkcja modułowa; [wiersz 54](../src/pymoo_gui/algorithms/hype.py#L54).
- `_auto_reference_point(problem: Any, n_obj: int) -> np.ndarray` — funkcja modułowa; [wiersz 71](../src/pymoo_gui/algorithms/hype.py#L71).
- `_reference_values(n_obj: int, problem: Any=None, reference_point: Any=None, reference_set: Any=None) -> np.ndarray` — funkcja modułowa; [wiersz 87](../src/pymoo_gui/algorithms/hype.py#L87).
- `prepare_reference_set(n_obj: int, reference_point: Sequence[float] | None=None, reference_set: Sequence[Sequence[float]] | None=None) -> np.ndarray` — funkcja modułowa; [wiersz 106](../src/pymoo_gui/algorithms/hype.py#L106).
- `fast_non_dominated_sort(objectives: np.ndarray) -> List[List[int]]` — funkcja modułowa; [wiersz 129](../src/pymoo_gui/algorithms/hype.py#L129).
- `_alpha(n: int, k: int, i: int) -> float` — funkcja modułowa; [wiersz 151](../src/pymoo_gui/algorithms/hype.py#L151).
- `_axis_edges(F: np.ndarray, R: np.ndarray) -> list[np.ndarray]` — funkcja modułowa; [wiersz 161](../src/pymoo_gui/algorithms/hype.py#L161).
- `exact_hype_fitness(objectives: np.ndarray, reference_set: np.ndarray, k: int) -> np.ndarray` — funkcja modułowa; [wiersz 172](../src/pymoo_gui/algorithms/hype.py#L172).
- `estimated_hype_fitness(objectives: np.ndarray, reference_set: np.ndarray, k: int, n_samples: int, rng: Optional[np.random.Generator]=None) -> np.ndarray` — funkcja modułowa; [wiersz 207](../src/pymoo_gui/algorithms/hype.py#L207).
- `hype_fitness(objectives: np.ndarray, reference_set: np.ndarray, k: int, n_samples: int, rng: Optional[np.random.Generator]=None) -> np.ndarray` — funkcja modułowa; [wiersz 250](../src/pymoo_gui/algorithms/hype.py#L250).
- `mating_selection(population: np.ndarray, n_obj: int, reference_set: np.ndarray, n_offspring: int, n_samples: int, rng: Optional[np.random.Generator]=None) -> np.ndarray` — funkcja modułowa; [wiersz 263](../src/pymoo_gui/algorithms/hype.py#L263).
- `_eval_objectives(x: np.ndarray, functions: Sequence[ObjectiveFn]) -> np.ndarray` — funkcja modułowa; [wiersz 288](../src/pymoo_gui/algorithms/hype.py#L288).
- `_new_population(size: int, min_values: np.ndarray, max_values: np.ndarray, functions: Sequence[ObjectiveFn], rng: np.random.Generator) -> np.ndarray` — funkcja modułowa; [wiersz 293](../src/pymoo_gui/algorithms/hype.py#L293).
- `crossover(parents: np.ndarray, min_values: Sequence[float], max_values: Sequence[float], functions: Sequence[ObjectiveFn], size: int, mu: float=20.0, rng: Optional[np.random.Generator]=None) -> np.ndarray` — funkcja modułowa; [wiersz 306](../src/pymoo_gui/algorithms/hype.py#L306).
- `mutation(offspring: np.ndarray, min_values: Sequence[float], max_values: Sequence[float], functions: Sequence[ObjectiveFn], mutation_rate: float=0.1, eta: float=20.0, rng: Optional[np.random.Generator]=None) -> np.ndarray` — funkcja modułowa; [wiersz 358](../src/pymoo_gui/algorithms/hype.py#L358).
- `environmental_selection(population: np.ndarray, population_size: int, n_obj: int, reference_set: np.ndarray, n_samples: int, rng: Optional[np.random.Generator]=None) -> np.ndarray` — funkcja modułowa; [wiersz 399](../src/pymoo_gui/algorithms/hype.py#L399).
- `hype_tournament(pop, P, random_state=None, **kwargs)` — funkcja modułowa; [wiersz 432](../src/pymoo_gui/algorithms/hype.py#L432).
- `HypESurvival.__init__(self, reference_point: Any='auto', reference_set: Any=None, n_samples: int=1000)` — metoda; [wiersz 464](../src/pymoo_gui/algorithms/hype.py#L464).
- `HypESurvival._do(self, problem, pop, *args, n_survive=None, **kwargs)` — metoda; [wiersz 470](../src/pymoo_gui/algorithms/hype.py#L470).
- `HypE.__init__(self, pop_size: int=40, reference_point: Any='auto', reference_set: Any=None, n_samples: int=1000, **kwargs)` — metoda; [wiersz 503](../src/pymoo_gui/algorithms/hype.py#L503).
- `HypE.reference_values(self, n_obj: int) -> np.ndarray` — metoda; [wiersz 518](../src/pymoo_gui/algorithms/hype.py#L518).
- `HypE.select(self) -> np.ndarray` — metoda; [wiersz 522](../src/pymoo_gui/algorithms/hype.py#L522).
- `HypE.environmental_selection(self, X, F, CV, n_survive)` — metoda; [wiersz 535](../src/pymoo_gui/algorithms/hype.py#L535).
- `hype(min_values: Sequence[float], max_values: Sequence[float], functions: Sequence[ObjectiveFn], population_size: int=100, generations: int=50, reference_point: Sequence[float] | None=None, reference_set: Sequence[Sequence[float]] | None=None, n_samples: int=1000, mutation_rate: float=0.1, mu: float=20.0, eta: float=20.0, rng: Optional[np.random.Generator]=None) -> np.ndarray` — funkcja modułowa; [wiersz 555](../src/pymoo_gui/algorithms/hype.py#L555).
- `make_hype(problem: Any=None, pop_size: int=40, reference_point: Any='auto', reference_set: Any=None, n_samples: int=1000) -> HypE` — funkcja modułowa; [wiersz 594](../src/pymoo_gui/algorithms/hype.py#L594).

### `src/pymoo_gui/algorithms/ibea.py`

- `_normalize_objectives(F: np.ndarray) -> np.ndarray` — funkcja modułowa; [wiersz 29](../src/pymoo_gui/algorithms/ibea.py#L29).
- `_epsilon_plus_indicator(F: np.ndarray) -> np.ndarray` — funkcja modułowa; [wiersz 40](../src/pymoo_gui/algorithms/ibea.py#L40).
- `_indicator_scale(indicator: np.ndarray) -> float` — funkcja modułowa; [wiersz 45](../src/pymoo_gui/algorithms/ibea.py#L45).
- `_fitness_from_indicator(indicator: np.ndarray, kappa: float, scale: float) -> np.ndarray` — funkcja modułowa; [wiersz 54](../src/pymoo_gui/algorithms/ibea.py#L54).
- `IBEA.__init__(self, pop_size: int=100, kappa: float=0.05, crossover_rate: float=1.0, mutation_rate: float=0.01, crossover_eta: float=20.0, mutation_eta: float=20.0, seed: int=1) -> None` — metoda; [wiersz 67](../src/pymoo_gui/algorithms/ibea.py#L67).
- `IBEA._fitness_for_population(self, F: np.ndarray) -> np.ndarray` — metoda; [wiersz 89](../src/pymoo_gui/algorithms/ibea.py#L89).
- `IBEA._select_feasible_by_ibea(self, F: np.ndarray, n_survive: int) -> tuple[np.ndarray, np.ndarray]` — metoda; [wiersz 96](../src/pymoo_gui/algorithms/ibea.py#L96).
- `IBEA.select(self) -> np.ndarray` — metoda; [wiersz 124](../src/pymoo_gui/algorithms/ibea.py#L124).
- `IBEA.environmental_selection(self, X: np.ndarray, F: np.ndarray, CV: np.ndarray, n_survive: int) -> PopulationState` — metoda; [wiersz 158](../src/pymoo_gui/algorithms/ibea.py#L158).
- `make_ibea(pop_size: int=100, kappa: float=0.05, crossover_rate: float=1.0, mutation_rate: float=0.01, crossover_eta: float=20.0, mutation_eta: float=20.0, seed: int=1) -> IBEA` — funkcja modułowa; [wiersz 203](../src/pymoo_gui/algorithms/ibea.py#L203).

### `src/pymoo_gui/algorithms/learning_edmo.py`

- `CentralizedClassifier.__init__(self, feature_count: int=10) -> None` — metoda; [wiersz 41](../src/pymoo_gui/algorithms/learning_edmo.py#L41).
- `CentralizedClassifier.predict(self, features: np.ndarray) -> np.ndarray` — metoda; [wiersz 46](../src/pymoo_gui/algorithms/learning_edmo.py#L46).
- `CentralizedClassifier.fit(self, features: np.ndarray, labels: np.ndarray, rate: float, epochs: int) -> None` — metoda; [wiersz 50](../src/pymoo_gui/algorithms/learning_edmo.py#L50).
- `LearningAcrossProblemsEDMO.__init__(self, *, transfer_fraction: float=0.2, candidate_multiplier: int=5, learning_rate: float=0.05, learning_epochs: int=20, knowledge_size: int=32, **kwargs: Any) -> None` — metoda; [wiersz 69](../src/pymoo_gui/algorithms/learning_edmo.py#L69).
- `LearningAcrossProblemsEDMO._normalized(self, X: np.ndarray) -> np.ndarray` — metoda; [wiersz 89](../src/pymoo_gui/algorithms/learning_edmo.py#L89).
- `LearningAcrossProblemsEDMO._resample_profile(profile: np.ndarray, dimension: int) -> np.ndarray` — metoda; [wiersz 93](../src/pymoo_gui/algorithms/learning_edmo.py#L93).
- `LearningAcrossProblemsEDMO._dynamic_features(self, state: PopulationState) -> np.ndarray` — metoda; [wiersz 102](../src/pymoo_gui/algorithms/learning_edmo.py#L102).
- `LearningAcrossProblemsEDMO._solution_features(self, X: np.ndarray, task_features: np.ndarray) -> np.ndarray` — metoda; [wiersz 119](../src/pymoo_gui/algorithms/learning_edmo.py#L119).
- `LearningAcrossProblemsEDMO._knowledge_candidates(self, count: int) -> np.ndarray` — metoda; [wiersz 139](../src/pymoo_gui/algorithms/learning_edmo.py#L139).
- `LearningAcrossProblemsEDMO.warm_start_candidates(self) -> np.ndarray | None` — metoda; [wiersz 157](../src/pymoo_gui/algorithms/learning_edmo.py#L157).
- `LearningAcrossProblemsEDMO.guided_candidates(self) -> np.ndarray` — metoda; [wiersz 172](../src/pymoo_gui/algorithms/learning_edmo.py#L172).
- `LearningAcrossProblemsEDMO.after_initialize(self) -> None` — metoda; [wiersz 192](../src/pymoo_gui/algorithms/learning_edmo.py#L192).
- `LearningAcrossProblemsEDMO._learn_from_state(self, state: PopulationState) -> None` — metoda; [wiersz 198](../src/pymoo_gui/algorithms/learning_edmo.py#L198).
- `LearningAcrossProblemsEDMO.after_generation(self, previous: PopulationState, current: PopulationState) -> None` — metoda; [wiersz 213](../src/pymoo_gui/algorithms/learning_edmo.py#L213).
- `make_learning_edmo(population_size: int=100, archive_size: int=100, crossover_rate: float=0.9, mutation_rate: float=0.1, transfer_fraction: float=0.2, candidate_multiplier: int=5, learning_rate: float=0.05, learning_epochs: int=20, knowledge_size: int=32, seed: int=1) -> LearningAcrossProblemsEDMO` — funkcja modułowa; [wiersz 231](../src/pymoo_gui/algorithms/learning_edmo.py#L231).

### `src/pymoo_gui/algorithms/lmoea_ds.py`

- `_simple_kmeans(points: np.ndarray, n_clusters: int, rng: np.random.Generator, n_iter: int=20) -> np.ndarray` — funkcja modułowa; [wiersz 36](../src/pymoo_gui/algorithms/lmoea_ds.py#L36).
- `_boundary_reference_vectors(ref_dirs: np.ndarray, n_obj: int) -> np.ndarray` — funkcja modułowa; [wiersz 60](../src/pymoo_gui/algorithms/lmoea_ds.py#L60).
- `_unique_rows(arr: np.ndarray) -> np.ndarray` — funkcja modułowa; [wiersz 76](../src/pymoo_gui/algorithms/lmoea_ds.py#L76).
- `_normalize_rows(arr: np.ndarray) -> np.ndarray` — funkcja modułowa; [wiersz 85](../src/pymoo_gui/algorithms/lmoea_ds.py#L85).
- `_pairwise_sbx(parents_a: np.ndarray, parents_b: np.ndarray, xl: np.ndarray, xu: np.ndarray, eta: float, prob: float, rng: np.random.Generator) -> np.ndarray` — funkcja modułowa; [wiersz 92](../src/pymoo_gui/algorithms/lmoea_ds.py#L92).
- `LMOEADS.__init__(self, population_size: int=153, archive_size: int=153, crossover_rate: float=0.9, mutation_rate: float=0.0, crossover_eta: float=20.0, mutation_eta: float=20.0, guiding_vector_count: int=12, samples_per_direction: int=30, selection_threshold_ratio: float=2.0 / 3.0, seed: int=1) -> None` — metoda; [wiersz 111](../src/pymoo_gui/algorithms/lmoea_ds.py#L111).
- `LMOEADS.after_initialize(self) -> None` — metoda; [wiersz 138](../src/pymoo_gui/algorithms/lmoea_ds.py#L138).
- `LMOEADS._effective_mutation_rate(self) -> float` — metoda; [wiersz 142](../src/pymoo_gui/algorithms/lmoea_ds.py#L142).
- `LMOEADS.mutation(self, offspring: np.ndarray) -> np.ndarray` — metoda; [wiersz 148](../src/pymoo_gui/algorithms/lmoea_ds.py#L148).
- `LMOEADS._build_guiding_reference_directions(self) -> np.ndarray` — metoda; [wiersz 161](../src/pymoo_gui/algorithms/lmoea_ds.py#L161).
- `LMOEADS._guided_assignment_objectives(self) -> tuple[np.ndarray, np.ndarray, np.ndarray]` — metoda; [wiersz 197](../src/pymoo_gui/algorithms/lmoea_ds.py#L197).
- `LMOEADS._identify_search_seeds(self) -> np.ndarray` — metoda; [wiersz 204](../src/pymoo_gui/algorithms/lmoea_ds.py#L204).
- `LMOEADS._sample_guiding_solutions(self) -> tuple[np.ndarray, np.ndarray, np.ndarray]` — metoda; [wiersz 242](../src/pymoo_gui/algorithms/lmoea_ds.py#L242).
- `LMOEADS._first_reproduction(self, guiding: np.ndarray) -> np.ndarray` — metoda; [wiersz 281](../src/pymoo_gui/algorithms/lmoea_ds.py#L281).
- `LMOEADS._performance_measure(self, F: np.ndarray, ref_dirs: np.ndarray) -> tuple[np.ndarray, np.ndarray]` — metoda; [wiersz 298](../src/pymoo_gui/algorithms/lmoea_ds.py#L298).
- `LMOEADS.environmental_selection(self, X: np.ndarray, F: np.ndarray, CV: np.ndarray, n_survive: int) -> PopulationState` — metoda; [wiersz 310](../src/pymoo_gui/algorithms/lmoea_ds.py#L310).
- `LMOEADS.step(self) -> None` — metoda; [wiersz 375](../src/pymoo_gui/algorithms/lmoea_ds.py#L375).
- `make_lmoea_ds(problem: Any=None, population_size: int=153, archive_size: int=153, crossover_rate: float=0.9, mutation_rate: float=0.0, crossover_eta: float=20.0, mutation_eta: float=20.0, guiding_vector_count: Optional[int]=None, samples_per_direction: int=30, selection_threshold_ratio: float=2.0 / 3.0, seed: int=1) -> LMOEADS` — funkcja modułowa; [wiersz 412](../src/pymoo_gui/algorithms/lmoea_ds.py#L412).

### `src/pymoo_gui/algorithms/maotspp.py`

- `_distribution_density(decisions: np.ndarray, center: np.ndarray, covariance: np.ndarray) -> np.ndarray` — funkcja modułowa; [wiersz 36](../src/pymoo_gui/algorithms/maotspp.py#L36).
- `tsp_penalty_sort(decisions: np.ndarray, objectives: np.ndarray, objective_variance: np.ndarray, constraints: np.ndarray, constraint_variance: np.ndarray, phase: int, center: np.ndarray | None=None, covariance: np.ndarray | None=None) -> np.ndarray` — funkcja modułowa; [wiersz 50](../src/pymoo_gui/algorithms/maotspp.py#L50).
- `_reference_set(problem: SurrogateProblem, population_size: int) -> np.ndarray` — funkcja modułowa; [wiersz 99](../src/pymoo_gui/algorithms/maotspp.py#L99).
- `run_maotspp(function: Callable[[np.ndarray], Any], lower: np.ndarray, upper: np.ndarray, population_size: int, maximum_generations: Optional[int], surrogate_generations: int, infill_batch_size: int, seed: int, generation_hook: Callable[[SurrogateProblem], None]) -> SurrogateResult` — funkcja modułowa; [wiersz 109](../src/pymoo_gui/algorithms/maotspp.py#L109).
- `MaOTSPP.__init__(self, population_size: int=40, surrogate_generations: int=20, infill_batch_size: int=5, seed: int=1) -> None` — metoda; [wiersz 238](../src/pymoo_gui/algorithms/maotspp.py#L238).
- `MaOTSPP._run_surrogate(self, function, lower, upper, maximum_generations, seed, generation_hook)` — metoda; [wiersz 251](../src/pymoo_gui/algorithms/maotspp.py#L251).
- `make_maotspp(population_size: int=40, surrogate_generations: int=20, infill_batch_size: int=5, seed: int=1) -> MaOTSPP` — funkcja modułowa; [wiersz 265](../src/pymoo_gui/algorithms/maotspp.py#L265).

### `src/pymoo_gui/algorithms/moead.py`

- `make_moead(problem: Any, n_partitions: int=12, n_neighbors: int=15, prob_neighbor_mating: float=0.7) -> MOEAD` — funkcja modułowa; [wiersz 16](../src/pymoo_gui/algorithms/moead.py#L16).

### `src/pymoo_gui/algorithms/nsga2.py`

- `make_nsga2(pop_size: int=100) -> NSGA2` — funkcja modułowa; [wiersz 15](../src/pymoo_gui/algorithms/nsga2.py#L15).

### `src/pymoo_gui/algorithms/nsga3.py`

- `make_nsga3(problem: Any, pop_size: int=100, n_partitions: int=12) -> NSGA3` — funkcja modułowa; [wiersz 17](../src/pymoo_gui/algorithms/nsga3.py#L17).

### `src/pymoo_gui/algorithms/peaplus.py`

- `cppd(objectives: np.ndarray, variance: np.ndarray, constraints: np.ndarray, constraint_variance: np.ndarray) -> np.ndarray` — funkcja modułowa; [wiersz 40](../src/pymoo_gui/algorithms/peaplus.py#L40).
- `run_peaplus(function: Callable[[np.ndarray], Any], lower: np.ndarray, upper: np.ndarray, population_size: int, maximum_generations: Optional[int], surrogate_generations: int, infill_batch_size: int, seed: int, generation_hook: Callable[[SurrogateProblem], None]) -> SurrogateResult` — funkcja modułowa; [wiersz 52](../src/pymoo_gui/algorithms/peaplus.py#L52).
- `PEAplus.__init__(self, population_size: int=40, surrogate_generations: int=10, infill_batch_size: int=5, seed: int=1) -> None` — metoda; [wiersz 186](../src/pymoo_gui/algorithms/peaplus.py#L186).
- `PEAplus._run_surrogate(self, function, lower, upper, maximum_generations, seed, generation_hook)` — metoda; [wiersz 203](../src/pymoo_gui/algorithms/peaplus.py#L203).
- `make_peaplus(population_size: int=40, surrogate_generations: int=10, infill_batch_size: int=5, seed: int=1) -> PEAplus` — funkcja modułowa; [wiersz 218](../src/pymoo_gui/algorithms/peaplus.py#L218).

### `src/pymoo_gui/algorithms/piea.py`

- `_safe_normalize(values: np.ndarray) -> np.ndarray` — funkcja modułowa; [wiersz 40](../src/pymoo_gui/algorithms/piea.py#L40).
- `nondominated_sort(objectives: np.ndarray) -> np.ndarray` — funkcja modułowa; [wiersz 48](../src/pymoo_gui/algorithms/piea.py#L48).
- `_sdr_sort(objectives: np.ndarray) -> np.ndarray` — funkcja modułowa; [wiersz 69](../src/pymoo_gui/algorithms/piea.py#L69).
- `_estimate_shape(objectives: np.ndarray) -> float` — funkcja modułowa; [wiersz 103](../src/pymoo_gui/algorithms/piea.py#L103).
- `_fitness_sde(objectives: np.ndarray, shape: float) -> np.ndarray` — funkcja modułowa; [wiersz 123](../src/pymoo_gui/algorithms/piea.py#L123).
- `_fitness_epsilon(objectives: np.ndarray, kappa: float=0.05) -> np.ndarray` — funkcja modułowa; [wiersz 149](../src/pymoo_gui/algorithms/piea.py#L149).
- `_fitness_minkowski(objectives: np.ndarray, shape: float) -> np.ndarray` — funkcja modułowa; [wiersz 157](../src/pymoo_gui/algorithms/piea.py#L157).
- `_tournament(fitness: np.ndarray, count: int, rng: np.random.Generator) -> np.ndarray` — funkcja modułowa; [wiersz 168](../src/pymoo_gui/algorithms/piea.py#L168).
- `operator_de(parent: np.ndarray, donor_a: np.ndarray, donor_b: np.ndarray, lower: np.ndarray, upper: np.ndarray, rng: np.random.Generator, crossover_rate: float=1.0, differential_weight: float=0.5, mutation_probability: float=1.0, mutation_eta: float=20.0) -> np.ndarray` — funkcja modułowa; [wiersz 174](../src/pymoo_gui/algorithms/piea.py#L174).
- `SurrogateArchiveAlgorithm.__init__(self, population_size: int, seed: int) -> None` — metoda; [wiersz 224](../src/pymoo_gui/algorithms/piea.py#L224).
- `SurrogateArchiveAlgorithm._evaluate(self, decisions: np.ndarray) -> tuple[np.ndarray, np.ndarray]` — metoda; [wiersz 243](../src/pymoo_gui/algorithms/piea.py#L243).
- `SurrogateArchiveAlgorithm._refresh_population(self) -> None` — metoda; [wiersz 249](../src/pymoo_gui/algorithms/piea.py#L249).
- `SurrogateArchiveAlgorithm.initialize(self, problem: Any) -> None` — metoda; [wiersz 260](../src/pymoo_gui/algorithms/piea.py#L260).
- `SurrogateArchiveAlgorithm.finalize_result(self) -> Result` — metoda; [wiersz 272](../src/pymoo_gui/algorithms/piea.py#L272).
- `SurrogateArchiveAlgorithm.gui_minimize(self, *, problem: Any, termination: Any, seed: Optional[int]=None, callback: Any=None, **kwargs: Any) -> Result` — metoda; [wiersz 282](../src/pymoo_gui/algorithms/piea.py#L282).
- `PIEA.__init__(self, population_size: int=40, eta: int=5, surrogate_generations: int=20, adaptation_window: int=20, seed: int=1) -> None` — metoda; [wiersz 316](../src/pymoo_gui/algorithms/piea.py#L316).
- `PIEA.initialize(self, problem: Any) -> None` — metoda; [wiersz 337](../src/pymoo_gui/algorithms/piea.py#L337).
- `PIEA.step(self) -> None` — metoda; [wiersz 344](../src/pymoo_gui/algorithms/piea.py#L344).
- `make_piea(population_size: int=40, eta: int=5, surrogate_generations: int=20, adaptation_window: int=20, seed: int=1) -> PIEA` — funkcja modułowa; [wiersz 413](../src/pymoo_gui/algorithms/piea.py#L413).

### `src/pymoo_gui/algorithms/pimd.py`

- `estimate_pf_shape(objectives: np.ndarray) -> float` — funkcja modułowa; [wiersz 22](../src/pymoo_gui/algorithms/pimd.py#L22).
- `_mapped(values: np.ndarray, power: float) -> np.ndarray` — funkcja modułowa; [wiersz 42](../src/pymoo_gui/algorithms/pimd.py#L42).
- `_normalize_pair(left: np.ndarray, right: np.ndarray) -> tuple[np.ndarray, np.ndarray]` — funkcja modułowa; [wiersz 48](../src/pymoo_gui/algorithms/pimd.py#L48).
- `_nsga3_indices(objectives: np.ndarray, count: int, directions: np.ndarray, rng: np.random.Generator, ideal: Optional[np.ndarray]=None) -> np.ndarray` — funkcja modułowa; [wiersz 55](../src/pymoo_gui/algorithms/pimd.py#L55).
- `run_pimd(function, lower: np.ndarray, upper: np.ndarray, population_size: int, maximum_generations: Optional[int], wmax: int, eta: int, seed: int, generation_hook) -> SurrogateResult` — funkcja modułowa; [wiersz 121](../src/pymoo_gui/algorithms/pimd.py#L121).
- `PIMD.__init__(self, population_size: int=20, wmax: int=15, eta: int=5, seed: int=1) -> None` — metoda; [wiersz 228](../src/pymoo_gui/algorithms/pimd.py#L228).
- `PIMD._run_surrogate(self, function, lower, upper, maximum_generations, seed, generation_hook)` — metoda; [wiersz 239](../src/pymoo_gui/algorithms/pimd.py#L239).
- `make_pimd(population_size: int=20, wmax: int=15, eta: int=5, seed: int=1) -> PIMD` — funkcja modułowa; [wiersz 253](../src/pymoo_gui/algorithms/pimd.py#L253).
- `lambda` — wyrażenie anonimowe; [wiersz 111](../src/pymoo_gui/algorithms/pimd.py#L111).

### `src/pymoo_gui/algorithms/platypus_common.py`

- `_platypus_imports() -> tuple[Any, Any, Any]` — funkcja modułowa; [wiersz 23](../src/pymoo_gui/algorithms/platypus_common.py#L23).
- `parse_positive_int(value: Any, field_name: str) -> int` — funkcja modułowa; [wiersz 37](../src/pymoo_gui/algorithms/platypus_common.py#L37).
- `parse_positive_float(value: Any, field_name: str) -> float` — funkcja modułowa; [wiersz 55](../src/pymoo_gui/algorithms/platypus_common.py#L55).
- `parse_probability(value: Any, field_name: str) -> float` — funkcja modułowa; [wiersz 66](../src/pymoo_gui/algorithms/platypus_common.py#L66).
- `problem_n_obj(problem: Any, algorithm_name: str) -> int` — funkcja modułowa; [wiersz 79](../src/pymoo_gui/algorithms/platypus_common.py#L79).
- `parse_epsilons(value: Any, n_obj: int, field_name: str='epsilons') -> list[float]` — funkcja modułowa; [wiersz 97](../src/pymoo_gui/algorithms/platypus_common.py#L97).
- `PlatypusProblemAdapter.__init__(self, pymoo_problem: Any)` — metoda; [wiersz 134](../src/pymoo_gui/algorithms/platypus_common.py#L134).
- `PlatypusProblemAdapter._evaluate(self, variables: Iterable[Any]) -> Any` — metoda; [wiersz 169](../src/pymoo_gui/algorithms/platypus_common.py#L169).
- `PlatypusPopulationView.__init__(self, solutions: Iterable[Any])` — metoda; [wiersz 200](../src/pymoo_gui/algorithms/platypus_common.py#L200).
- `PlatypusPopulationView.get(self, name: str) -> Optional[np.ndarray]` — metoda; [wiersz 204](../src/pymoo_gui/algorithms/platypus_common.py#L204).
- `PlatypusAlgorithmAdapter.__init__(self, pymoo_problem: Any, algorithm_factory: Callable[[Any], Any])` — metoda; [wiersz 226](../src/pymoo_gui/algorithms/platypus_common.py#L226).
- `PlatypusAlgorithmAdapter._sync_state(self) -> None` — metoda; [wiersz 238](../src/pymoo_gui/algorithms/platypus_common.py#L238).
- `PlatypusAlgorithmAdapter._should_stop(self, termination: Any, max_generations: Optional[int]) -> bool` — metoda; [wiersz 244](../src/pymoo_gui/algorithms/platypus_common.py#L244).
- `PlatypusAlgorithmAdapter.gui_minimize(self, *, problem: Any, termination: Any, seed: Optional[int]=None, callback: Any=None, **kwargs: Any) -> Result` — metoda; [wiersz 250](../src/pymoo_gui/algorithms/platypus_common.py#L250).
- `termination_generations(termination: Any) -> Optional[int]` — funkcja modułowa; [wiersz 281](../src/pymoo_gui/algorithms/platypus_common.py#L281).

### `src/pymoo_gui/algorithms/moead_iepsilon.py`

- `MOEADIEpsilon.after_initialize(self) -> None` — metoda; [wiersz 19](../src/pymoo_gui/algorithms/moead_iepsilon.py#L19).
- `MOEADIEpsilon.gui_minimize(self, *, problem, termination, **kwargs)` — metoda; [wiersz 32](../src/pymoo_gui/algorithms/moead_iepsilon.py#L32).
- `MOEADIEpsilon.step(self) -> None` — metoda; [wiersz 36](../src/pymoo_gui/algorithms/moead_iepsilon.py#L36).
- `MOEADIEpsilon.generate_child(self, subproblem: int, pool: np.ndarray) -> np.ndarray` — metoda; [wiersz 48](../src/pymoo_gui/algorithms/moead_iepsilon.py#L48).
- `MOEADIEpsilon.replacement_allowed(self, child_f, child_cv, target_f, target_cv, weights) -> bool` — metoda; [wiersz 64](../src/pymoo_gui/algorithms/moead_iepsilon.py#L64).
- `make_moead_iepsilon(problem: Any, population_size: int=100, neighborhood_size: int=10, delta: float=0.9, eta: int=2) -> MOEADIEpsilon` — funkcja modułowa; [wiersz 79](../src/pymoo_gui/algorithms/moead_iepsilon.py#L79).

### `src/pymoo_gui/algorithms/platypus_moead.py`

Moduł zgodności ze starą nazwą; nie zawiera implementacji algorytmu Platypus.

### `src/pymoo_gui/algorithms/research_common.py`

- `non_dominated_fronts(F: np.ndarray) -> list[np.ndarray]` — funkcja modułowa; [wiersz 35](../src/pymoo_gui/algorithms/research_common.py#L35).
- `das_dennis_reference_directions(n_obj: int, n_partitions: int) -> np.ndarray` — funkcja modułowa; [wiersz 57](../src/pymoo_gui/algorithms/research_common.py#L57).
- `das_dennis_reference_directions.enumerate_compositions(prefix: list[int], remaining: int, dimensions: int) -> None` — funkcja zagnieżdżona; [wiersz 63](../src/pymoo_gui/algorithms/research_common.py#L63).
- `parse_positive_int(value: Any, field_name: str) -> int` — funkcja modułowa; [wiersz 74](../src/pymoo_gui/algorithms/research_common.py#L74).
- `parse_optional_positive_int(value: Any, field_name: str) -> Optional[int]` — funkcja modułowa; [wiersz 85](../src/pymoo_gui/algorithms/research_common.py#L85).
- `parse_positive_float(value: Any, field_name: str) -> float` — funkcja modułowa; [wiersz 92](../src/pymoo_gui/algorithms/research_common.py#L92).
- `parse_probability(value: Any, field_name: str) -> float` — funkcja modułowa; [wiersz 103](../src/pymoo_gui/algorithms/research_common.py#L103).
- `parse_epsilons(value: Any, n_obj: int, field_name: str='epsilons') -> list[float]` — funkcja modułowa; [wiersz 114](../src/pymoo_gui/algorithms/research_common.py#L114).
- `termination_generations(termination: Any) -> Optional[int]` — funkcja modułowa; [wiersz 133](../src/pymoo_gui/algorithms/research_common.py#L133).
- `parse_reference_directions(value: Any, n_obj: int) -> Optional[np.ndarray]` — funkcja modułowa; [wiersz 145](../src/pymoo_gui/algorithms/research_common.py#L145).
- `problem_bounds(problem: Any) -> tuple[np.ndarray, np.ndarray, int]` — funkcja modułowa; [wiersz 159](../src/pymoo_gui/algorithms/research_common.py#L159).
- `problem_n_obj(problem: Any) -> int` — funkcja modułowa; [wiersz 175](../src/pymoo_gui/algorithms/research_common.py#L175).
- `project_to_bounds(X: np.ndarray, xl: np.ndarray, xu: np.ndarray) -> np.ndarray` — funkcja modułowa; [wiersz 180](../src/pymoo_gui/algorithms/research_common.py#L180).
- `evaluate_problem(problem: Any, X: np.ndarray) -> tuple[np.ndarray, np.ndarray]` — funkcja modułowa; [wiersz 185](../src/pymoo_gui/algorithms/research_common.py#L185).
- `feasible_mask(cv: np.ndarray) -> np.ndarray` — funkcja modułowa; [wiersz 215](../src/pymoo_gui/algorithms/research_common.py#L215).
- `crowding_distance(F: np.ndarray) -> np.ndarray` — funkcja modułowa; [wiersz 220](../src/pymoo_gui/algorithms/research_common.py#L220).
- `assign_rank_and_crowding(F: np.ndarray, CV: np.ndarray) -> tuple[np.ndarray, np.ndarray]` — funkcja modułowa; [wiersz 241](../src/pymoo_gui/algorithms/research_common.py#L241).
- `stable_survivor_order(rank: np.ndarray, crowding: np.ndarray, cv: np.ndarray) -> np.ndarray` — funkcja modułowa; [wiersz 271](../src/pymoo_gui/algorithms/research_common.py#L271).
- `select_survivors_nsga2(X: np.ndarray, F: np.ndarray, CV: np.ndarray, n_survive: int) -> 'PopulationState'` — funkcja modułowa; [wiersz 279](../src/pymoo_gui/algorithms/research_common.py#L279).
- `tournament_indices(rank: np.ndarray, crowding: np.ndarray, cv: np.ndarray, n_parents: int, rng: np.random.Generator) -> np.ndarray` — funkcja modułowa; [wiersz 292](../src/pymoo_gui/algorithms/research_common.py#L292).
- `sbx_crossover(X: np.ndarray, parent_pairs: np.ndarray, xl: np.ndarray, xu: np.ndarray, eta: float, prob: float, rng: np.random.Generator) -> np.ndarray` — funkcja modułowa; [wiersz 331](../src/pymoo_gui/algorithms/research_common.py#L331).
- `polynomial_mutation(X: np.ndarray, xl: np.ndarray, xu: np.ndarray, eta: float, prob: float, rng: np.random.Generator, strength: float=1.0) -> np.ndarray` — funkcja modułowa; [wiersz 383](../src/pymoo_gui/algorithms/research_common.py#L383).
- `gaussian_mutation(X: np.ndarray, xl: np.ndarray, xu: np.ndarray, prob: float, sigma: float, rng: np.random.Generator) -> np.ndarray` — funkcja modułowa; [wiersz 424](../src/pymoo_gui/algorithms/research_common.py#L424).
- `de_crossover(X: np.ndarray, xl: np.ndarray, xu: np.ndarray, F_weight: np.ndarray, CR: np.ndarray, rng: np.random.Generator) -> np.ndarray` — funkcja modułowa; [wiersz 442](../src/pymoo_gui/algorithms/research_common.py#L442).
- `sample_reference_directions(n_obj: int, population_size: int, n_partitions: int, rng: np.random.Generator, reference_directions: Optional[np.ndarray]=None) -> np.ndarray` — funkcja modułowa; [wiersz 469](../src/pymoo_gui/algorithms/research_common.py#L469).
- `normalized_objectives(F: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]` — funkcja modułowa; [wiersz 492](../src/pymoo_gui/algorithms/research_common.py#L492).
- `associate_to_reference_directions(F: np.ndarray, ref_dirs: np.ndarray) -> tuple[np.ndarray, np.ndarray]` — funkcja modułowa; [wiersz 501](../src/pymoo_gui/algorithms/research_common.py#L501).
- `tchebycheff_scores(F: np.ndarray, ref_dirs: np.ndarray) -> np.ndarray` — funkcja modułowa; [wiersz 517](../src/pymoo_gui/algorithms/research_common.py#L517).
- `shifted_density(F: np.ndarray) -> np.ndarray` — funkcja modułowa; [wiersz 526](../src/pymoo_gui/algorithms/research_common.py#L526).
- `PopulationState.feasible(self) -> np.ndarray` — metoda; [wiersz 552](../src/pymoo_gui/algorithms/research_common.py#L552).
- `ArrayPopulationView.__init__(self, state: Optional[PopulationState])` — metoda; [wiersz 561](../src/pymoo_gui/algorithms/research_common.py#L561).
- `ArrayPopulationView.get(self, name: str) -> Optional[np.ndarray]` — metoda; [wiersz 565](../src/pymoo_gui/algorithms/research_common.py#L565).
- `ResearchMOOAlgorithm.__init__(self, population_size: int=100, archive_size: int=100, crossover_rate: float=0.9, mutation_rate: float=0.1, crossover_eta: float=15.0, mutation_eta: float=20.0, epsilon: float=0.05, n_neighbors: int=15, n_partitions: int=12, reference_directions: Any=None, seed: int=1) -> None` — metoda; [wiersz 584](../src/pymoo_gui/algorithms/research_common.py#L584).
- `ResearchMOOAlgorithm.setup_rng(self, seed: Optional[int]) -> None` — metoda; [wiersz 626](../src/pymoo_gui/algorithms/research_common.py#L626).
- `ResearchMOOAlgorithm.initialize(self, problem: Any) -> None` — metoda; [wiersz 633](../src/pymoo_gui/algorithms/research_common.py#L633).
- `ResearchMOOAlgorithm.after_initialize(self) -> None` — metoda; [wiersz 662](../src/pymoo_gui/algorithms/research_common.py#L662).
- `ResearchMOOAlgorithm.sample_initial_population(self) -> np.ndarray` — metoda; [wiersz 666](../src/pymoo_gui/algorithms/research_common.py#L666).
- `ResearchMOOAlgorithm.warm_start_candidates(self) -> Optional[np.ndarray]` — metoda; [wiersz 677](../src/pymoo_gui/algorithms/research_common.py#L677).
- `ResearchMOOAlgorithm.evaluate(self, X: np.ndarray) -> tuple[np.ndarray, np.ndarray]` — metoda; [wiersz 681](../src/pymoo_gui/algorithms/research_common.py#L681).
- `ResearchMOOAlgorithm.select(self) -> np.ndarray` — metoda; [wiersz 694](../src/pymoo_gui/algorithms/research_common.py#L694).
- `ResearchMOOAlgorithm.crossover(self, parent_pairs: np.ndarray) -> np.ndarray` — metoda; [wiersz 705](../src/pymoo_gui/algorithms/research_common.py#L705).
- `ResearchMOOAlgorithm.mutation(self, offspring: np.ndarray) -> np.ndarray` — metoda; [wiersz 722](../src/pymoo_gui/algorithms/research_common.py#L722).
- `ResearchMOOAlgorithm.guided_candidates(self) -> np.ndarray` — metoda; [wiersz 746](../src/pymoo_gui/algorithms/research_common.py#L746).
- `ResearchMOOAlgorithm.create_offspring(self) -> np.ndarray` — metoda; [wiersz 750](../src/pymoo_gui/algorithms/research_common.py#L750).
- `ResearchMOOAlgorithm.environmental_selection(self, X: np.ndarray, F: np.ndarray, CV: np.ndarray, n_survive: int) -> PopulationState` — metoda; [wiersz 755](../src/pymoo_gui/algorithms/research_common.py#L755).
- `ResearchMOOAlgorithm.build_archive(self, state: PopulationState) -> PopulationState` — metoda; [wiersz 765](../src/pymoo_gui/algorithms/research_common.py#L765).
- `ResearchMOOAlgorithm.archive_elites(self, count: int) -> np.ndarray` — metoda; [wiersz 777](../src/pymoo_gui/algorithms/research_common.py#L777).
- `ResearchMOOAlgorithm.state_centroid(self, state: Optional[PopulationState]=None, elite_fraction: float=0.25) -> np.ndarray` — metoda; [wiersz 784](../src/pymoo_gui/algorithms/research_common.py#L784).
- `ResearchMOOAlgorithm.state_spread(self, state: Optional[PopulationState]=None, elite_fraction: float=0.25) -> np.ndarray` — metoda; [wiersz 792](../src/pymoo_gui/algorithms/research_common.py#L792).
- `ResearchMOOAlgorithm.diversity_score(self, state: Optional[PopulationState]=None) -> float` — metoda; [wiersz 802](../src/pymoo_gui/algorithms/research_common.py#L802).
- `ResearchMOOAlgorithm.progress_score(self, previous: PopulationState, current: PopulationState) -> float` — metoda; [wiersz 812](../src/pymoo_gui/algorithms/research_common.py#L812).
- `ResearchMOOAlgorithm.after_generation(self, previous: PopulationState, current: PopulationState) -> None` — metoda; [wiersz 822](../src/pymoo_gui/algorithms/research_common.py#L822).
- `ResearchMOOAlgorithm._remember_state(self) -> None` — metoda; [wiersz 826](../src/pymoo_gui/algorithms/research_common.py#L826).
- `ResearchMOOAlgorithm._update_population_view(self) -> None` — metoda; [wiersz 843](../src/pymoo_gui/algorithms/research_common.py#L843).
- `ResearchMOOAlgorithm.step(self) -> None` — metoda; [wiersz 847](../src/pymoo_gui/algorithms/research_common.py#L847).
- `ResearchMOOAlgorithm.run(self, n_generations: int, callback: Any=None) -> None` — metoda; [wiersz 878](../src/pymoo_gui/algorithms/research_common.py#L878).
- `ResearchMOOAlgorithm.finalize_result(self) -> SimpleNamespace` — metoda; [wiersz 885](../src/pymoo_gui/algorithms/research_common.py#L885).
- `ResearchMOOAlgorithm.gui_minimize(self, *, problem: Any, termination: Any, seed: Optional[int]=None, callback: Any=None, **kwargs: Any) -> SimpleNamespace` — metoda; [wiersz 895](../src/pymoo_gui/algorithms/research_common.py#L895).

### `src/pymoo_gui/algorithms/rnn_guided_dmo.py`

- `RNNGuidedDMO.__init__(self, *, hidden_size: int=16, prediction_fraction: float=0.2, detector_fraction: float=0.1, learning_rate: float=0.01, training_epochs: int=20, change_tolerance: float=1e-10, mutation_scale: float=0.1, utest_threshold: float=0.5, **kwargs: Any) -> None` — metoda; [wiersz 34](../src/pymoo_gui/algorithms/rnn_guided_dmo.py#L34).
- `RNNGuidedDMO.sample_size(self) -> int` — metoda; [wiersz 70](../src/pymoo_gui/algorithms/rnn_guided_dmo.py#L70).
- `RNNGuidedDMO.after_initialize(self) -> None` — metoda; [wiersz 73](../src/pymoo_gui/algorithms/rnn_guided_dmo.py#L73).
- `RNNGuidedDMO._best_samples(self, state: PopulationState) -> np.ndarray` — metoda; [wiersz 93](../src/pymoo_gui/algorithms/rnn_guided_dmo.py#L93).
- `RNNGuidedDMO._forward(self, inputs: np.ndarray, hidden_previous: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]` — metoda; [wiersz 103](../src/pymoo_gui/algorithms/rnn_guided_dmo.py#L103).
- `RNNGuidedDMO._online_train(self, inputs: np.ndarray, targets: np.ndarray) -> float` — metoda; [wiersz 114](../src/pymoo_gui/algorithms/rnn_guided_dmo.py#L114).
- `RNNGuidedDMO._change_detected(self) -> bool` — metoda; [wiersz 141](../src/pymoo_gui/algorithms/rnn_guided_dmo.py#L141).
- `RNNGuidedDMO._auxiliary_response(self, candidates: np.ndarray, current_samples: np.ndarray, prediction: np.ndarray, loss: float) -> np.ndarray` — metoda; [wiersz 155](../src/pymoo_gui/algorithms/rnn_guided_dmo.py#L155).
- `RNNGuidedDMO._respond_to_change(self) -> None` — metoda; [wiersz 197](../src/pymoo_gui/algorithms/rnn_guided_dmo.py#L197).
- `RNNGuidedDMO.generate_child(self, subproblem: int, pool: np.ndarray) -> np.ndarray` — metoda; [wiersz 218](../src/pymoo_gui/algorithms/rnn_guided_dmo.py#L218).
- `RNNGuidedDMO.step(self) -> None` — metoda; [wiersz 237](../src/pymoo_gui/algorithms/rnn_guided_dmo.py#L237).
- `make_rnn_guided_dmo(population_size: int=100, neighborhood_size: int=20, hidden_size: int=16, prediction_fraction: float=0.2, detector_fraction: float=0.1, learning_rate: float=0.01, training_epochs: int=20, change_tolerance: float=1e-10, mutation_scale: float=0.1, utest_threshold: float=0.5, seed: int=1) -> RNNGuidedDMO` — funkcja modułowa; [wiersz 244](../src/pymoo_gui/algorithms/rnn_guided_dmo.py#L244).

### `src/pymoo_gui/algorithms/rnsga3.py`

- `_points(value: Any, n_obj: int) -> np.ndarray` — funkcja modułowa; [wiersz 20](../src/pymoo_gui/algorithms/rnsga3.py#L20).
- `_uniform_directions(n_obj: int, count: int) -> np.ndarray` — funkcja modułowa; [wiersz 31](../src/pymoo_gui/algorithms/rnsga3.py#L31).
- `_line_plane_intersection(point: np.ndarray) -> np.ndarray` — funkcja modułowa; [wiersz 44](../src/pymoo_gui/algorithms/rnsga3.py#L44).
- `reference_directions_from_points(unit_points: np.ndarray, aspiration_directions: np.ndarray, mu: float) -> np.ndarray` — funkcja modułowa; [wiersz 52](../src/pymoo_gui/algorithms/rnsga3.py#L52).
- `RNSGA3.__init__(self, ref_points: np.ndarray, aspiration_directions: np.ndarray, mu: float, **kwargs)` — metoda; [wiersz 75](../src/pymoo_gui/algorithms/rnsga3.py#L75).
- `RNSGA3.environmental_selection(self, X, F, CV, n_survive)` — metoda; [wiersz 81](../src/pymoo_gui/algorithms/rnsga3.py#L81).
- `make_rnsga3(problem: Any, ref_points: Any=None, pop_per_ref_point: int=50, mu: float=0.1) -> RNSGA3` — funkcja modułowa; [wiersz 94](../src/pymoo_gui/algorithms/rnsga3.py#L94).

### `src/pymoo_gui/algorithms/rvea.py`

- `RVEA.__init__(self, alpha: float=2.0, adapt_freq: float=0.1, **kwargs)` — metoda; [wiersz 18](../src/pymoo_gui/algorithms/rvea.py#L18).
- `RVEA.gui_minimize(self, *, problem, termination, **kwargs)` — metoda; [wiersz 25](../src/pymoo_gui/algorithms/rvea.py#L25).
- `RVEA.after_initialize(self) -> None` — metoda; [wiersz 30](../src/pymoo_gui/algorithms/rvea.py#L30).
- `RVEA.environmental_selection(self, X, F, CV, n_survive)` — metoda; [wiersz 37](../src/pymoo_gui/algorithms/rvea.py#L37).
- `RVEA.after_generation(self, previous, current) -> None` — metoda; [wiersz 67](../src/pymoo_gui/algorithms/rvea.py#L67).
- `make_rvea(problem: Any, pop_size: Optional[int]=100, n_partitions: int=99, alpha: float=2.0, adapt_freq: float=0.1) -> RVEA` — funkcja modułowa; [wiersz 74](../src/pymoo_gui/algorithms/rvea.py#L74).

### `src/pymoo_gui/algorithms/spea2.py`

- `make_spea2(pop_size: int=100) -> SPEA2` — funkcja modułowa; [wiersz 16](../src/pymoo_gui/algorithms/spea2.py#L16).

### `src/pymoo_gui/algorithms/ssde.py`

- `_crowding(objectives: np.ndarray, fronts: np.ndarray) -> np.ndarray` — funkcja modułowa; [wiersz 33](../src/pymoo_gui/algorithms/ssde.py#L33).
- `_select(objectives: np.ndarray, count: int) -> np.ndarray` — funkcja modułowa; [wiersz 53](../src/pymoo_gui/algorithms/ssde.py#L53).
- `_train_som(weights: np.ndarray, sample_X: np.ndarray, sample_F: np.ndarray, lower: np.ndarray, upper: np.ndarray, learning_rate: float, neighborhood_radius: float, training_epochs: int, rng: np.random.Generator) -> np.ndarray` — funkcja modułowa; [wiersz 67](../src/pymoo_gui/algorithms/ssde.py#L67).
- `SSDE.__init__(self, population_size: int=40, num_nodes: int=40, learning_rate: float=0.2, neighborhood_radius: float=40.0, training_epochs: int=50, seed: int=1) -> None` — metoda; [wiersz 116](../src/pymoo_gui/algorithms/ssde.py#L116).
- `SSDE.initialize(self, problem: Any) -> None` — metoda; [wiersz 140](../src/pymoo_gui/algorithms/ssde.py#L140).
- `SSDE._refresh_current_population(self) -> None` — metoda; [wiersz 152](../src/pymoo_gui/algorithms/ssde.py#L152).
- `SSDE.step(self) -> None` — metoda; [wiersz 165](../src/pymoo_gui/algorithms/ssde.py#L165).
- `SSDE.finalize_result(self) -> Any` — metoda; [wiersz 246](../src/pymoo_gui/algorithms/ssde.py#L246).
- `make_ssde(population_size: int=40, num_nodes: int=40, learning_rate: float=0.2, neighborhood_radius: float=40.0, training_epochs: int=50, seed: int=1) -> SSDE` — funkcja modułowa; [wiersz 252](../src/pymoo_gui/algorithms/ssde.py#L252).

### `src/pymoo_gui/algorithms/surrogate_common.py`

- `SurrogateProblem.__init__(self, function: Callable[[np.ndarray], Any], lower: np.ndarray, upper: np.ndarray, budget: int) -> None` — metoda; [wiersz 48](../src/pymoo_gui/algorithms/surrogate_common.py#L48).
- `SurrogateProblem.evaluate(self, decisions: np.ndarray) -> None` — metoda; [wiersz 71](../src/pymoo_gui/algorithms/surrogate_common.py#L71).
- `SurrogateProblem.initial(self, count: int, rng: np.random.Generator) -> None` — metoda; [wiersz 103](../src/pymoo_gui/algorithms/surrogate_common.py#L103).
- `SurrogateProblem.result(self, reason: str='generations') -> SurrogateResult` — metoda; [wiersz 110](../src/pymoo_gui/algorithms/surrogate_common.py#L110).
- `graph_sort(dominates: np.ndarray) -> np.ndarray` — funkcja modułowa; [wiersz 115](../src/pymoo_gui/algorithms/surrogate_common.py#L115).
- `dominance(objectives: np.ndarray, constraints: Optional[np.ndarray]=None) -> np.ndarray` — funkcja modułowa; [wiersz 129](../src/pymoo_gui/algorithms/surrogate_common.py#L129).
- `normalize(values: np.ndarray) -> np.ndarray` — funkcja modułowa; [wiersz 145](../src/pymoo_gui/algorithms/surrogate_common.py#L145).
- `angles(left: np.ndarray, right: np.ndarray) -> np.ndarray` — funkcja modułowa; [wiersz 152](../src/pymoo_gui/algorithms/surrogate_common.py#L152).
- `distances(left: np.ndarray, right: np.ndarray, metric: str) -> np.ndarray` — funkcja modułowa; [wiersz 167](../src/pymoo_gui/algorithms/surrogate_common.py#L167).
- `survival(front: np.ndarray, values: np.ndarray, count: int, metric: str='angle') -> np.ndarray` — funkcja modułowa; [wiersz 179](../src/pymoo_gui/algorithms/surrogate_common.py#L179).
- `constraint_coordinate(objectives: np.ndarray, constraints: np.ndarray) -> np.ndarray` — funkcja modułowa; [wiersz 198](../src/pymoo_gui/algorithms/surrogate_common.py#L198).
- `probability_leq(mean_difference: np.ndarray, variance: np.ndarray) -> np.ndarray` — funkcja modułowa; [wiersz 208](../src/pymoo_gui/algorithms/surrogate_common.py#L208).
- `weighted_probability_sort(objectives: np.ndarray, variance: np.ndarray, weight: np.ndarray, constraints: Optional[np.ndarray]=None) -> np.ndarray` — funkcja modułowa; [wiersz 225](../src/pymoo_gui/algorithms/surrogate_common.py#L225).
- `mutate(decisions: np.ndarray, lower: np.ndarray, upper: np.ndarray, rng: np.random.Generator) -> np.ndarray` — funkcja modułowa; [wiersz 250](../src/pymoo_gui/algorithms/surrogate_common.py#L250).
- `ga(decisions: np.ndarray, lower: np.ndarray, upper: np.ndarray, rng: np.random.Generator) -> np.ndarray` — funkcja modułowa; [wiersz 281](../src/pymoo_gui/algorithms/surrogate_common.py#L281).
- `differential_evolution(decisions: np.ndarray, lower: np.ndarray, upper: np.ndarray, rng: np.random.Generator, current: bool=False) -> np.ndarray` — funkcja modułowa; [wiersz 307](../src/pymoo_gui/algorithms/surrogate_common.py#L307).
- `simplex(count: int, objectives: int) -> np.ndarray` — funkcja modułowa; [wiersz 328](../src/pymoo_gui/algorithms/surrogate_common.py#L328).
- `Kriging.__init__(self, linear: bool=True, theta: Optional[np.ndarray]=None) -> None` — metoda; [wiersz 348](../src/pymoo_gui/algorithms/surrogate_common.py#L348).
- `Kriging.basis(self, values: np.ndarray) -> np.ndarray` — metoda; [wiersz 352](../src/pymoo_gui/algorithms/surrogate_common.py#L352).
- `Kriging.fit(self, decisions: np.ndarray, targets: np.ndarray) -> 'Kriging'` — metoda; [wiersz 356](../src/pymoo_gui/algorithms/surrogate_common.py#L356).
- `Kriging.likelihood(self, logtheta: np.ndarray, save: bool=False) -> float` — metoda; [wiersz 381](../src/pymoo_gui/algorithms/surrogate_common.py#L381).
- `Kriging.predict(self, decisions: np.ndarray) -> tuple[np.ndarray, np.ndarray]` — metoda; [wiersz 405](../src/pymoo_gui/algorithms/surrogate_common.py#L405).
- `Models.fit(self, decisions: np.ndarray, objectives: np.ndarray, constraints: np.ndarray, constant_constraints: bool=False) -> 'Models'` — metoda; [wiersz 423](../src/pymoo_gui/algorithms/surrogate_common.py#L423).
- `Models.predict(self, decisions: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]` — metoda; [wiersz 447](../src/pymoo_gui/algorithms/surrogate_common.py#L447).
- `SurrogateAlgorithm.__init__(self, population_size: int, seed: int=1) -> None` — metoda; [wiersz 464](../src/pymoo_gui/algorithms/surrogate_common.py#L464).
- `SurrogateAlgorithm._objective(self, decisions: np.ndarray) -> tuple[np.ndarray, np.ndarray]` — metoda; [wiersz 475](../src/pymoo_gui/algorithms/surrogate_common.py#L475).
- `SurrogateAlgorithm._sync(self, surrogate_problem: SurrogateProblem) -> None` — metoda; [wiersz 498](../src/pymoo_gui/algorithms/surrogate_common.py#L498).
- `SurrogateAlgorithm._run_surrogate(self, function: Callable[[np.ndarray], Any], lower: np.ndarray, upper: np.ndarray, maximum_generations: Optional[int], seed: int, generation_hook: Callable[[SurrogateProblem], None]) -> SurrogateResult` — metoda; [wiersz 516](../src/pymoo_gui/algorithms/surrogate_common.py#L516).
- `SurrogateAlgorithm.gui_minimize(self, *, problem: Any, termination: Any, seed: Optional[int]=None, callback: Any=None, **kwargs: Any) -> Result` — metoda; [wiersz 528](../src/pymoo_gui/algorithms/surrogate_common.py#L528).
- `SurrogateAlgorithm.gui_minimize.generation_hook(surrogate_problem: SurrogateProblem) -> None` — funkcja zagnieżdżona; [wiersz 545](../src/pymoo_gui/algorithms/surrogate_common.py#L545).
- `evaluation_budget(population_size: int, maximum_generations: Optional[int], batch: int) -> int` — funkcja modułowa; [wiersz 569](../src/pymoo_gui/algorithms/surrogate_common.py#L569).
- `lambda` — wyrażenie anonimowe; [wiersz 189](../src/pymoo_gui/algorithms/surrogate_common.py#L189).

### `src/pymoo_gui/algorithms/tea.py`

- `_normalize(objectives: np.ndarray) -> tuple[np.ndarray, np.ndarray]` — funkcja modułowa; [wiersz 29](../src/pymoo_gui/algorithms/tea.py#L29).
- `_standard_sort(objectives: np.ndarray, constraints: Optional[np.ndarray]=None) -> np.ndarray` — funkcja modułowa; [wiersz 37](../src/pymoo_gui/algorithms/tea.py#L37).
- `ppd_sort(objectives: np.ndarray, mse: np.ndarray, n_sort: int, constraints: Optional[np.ndarray]=None, constraint_mse: Optional[np.ndarray]=None) -> np.ndarray` — funkcja modułowa; [wiersz 63](../src/pymoo_gui/algorithms/tea.py#L63).
- `_truncate(objectives: np.ndarray, keep: int) -> np.ndarray` — funkcja modułowa; [wiersz 123](../src/pymoo_gui/algorithms/tea.py#L123).
- `_environmental_selection(objectives: np.ndarray, mse: np.ndarray, constraints: np.ndarray, constraint_mse: np.ndarray, size: int, phase: int) -> np.ndarray` — funkcja modułowa; [wiersz 136](../src/pymoo_gui/algorithms/tea.py#L136).
- `_fit_models(decisions: np.ndarray, values: np.ndarray, seed: Optional[int]) -> list[Kriging]` — funkcja modułowa; [wiersz 171](../src/pymoo_gui/algorithms/tea.py#L171).
- `_predict(models: list[Kriging], decisions: np.ndarray) -> tuple[np.ndarray, np.ndarray]` — funkcja modułowa; [wiersz 184](../src/pymoo_gui/algorithms/tea.py#L184).
- `TEA.__init__(self, population_size: int=40, surrogate_generations: int=20, infill_batch_size: int=5, seed: int=1) -> None` — metoda; [wiersz 200](../src/pymoo_gui/algorithms/tea.py#L200).
- `TEA._evaluate_exact(self, decisions: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]` — metoda; [wiersz 220](../src/pymoo_gui/algorithms/tea.py#L220).
- `TEA.initialize(self, problem: Any) -> None` — metoda; [wiersz 258](../src/pymoo_gui/algorithms/tea.py#L258).
- `TEA.step(self) -> None` — metoda; [wiersz 275](../src/pymoo_gui/algorithms/tea.py#L275).
- `make_tea(population_size: int=40, surrogate_generations: int=20, infill_batch_size: int=5, seed: int=1) -> TEA` — funkcja modułowa; [wiersz 385](../src/pymoo_gui/algorithms/tea.py#L385).

### `src/pymoo_gui/algorithms/ts_nsga.py`

- `_rank_relation(relation: np.ndarray) -> np.ndarray` — funkcja modułowa; [wiersz 29](../src/pymoo_gui/algorithms/ts_nsga.py#L29).
- `_objective_geometry(objectives: np.ndarray, reference_vectors: np.ndarray, theta: float) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]` — funkcja modułowa; [wiersz 49](../src/pymoo_gui/algorithms/ts_nsga.py#L49).
- `spd_ranks(objectives: np.ndarray, constraints: np.ndarray, reference_vectors: np.ndarray, theta: float=5.0) -> tuple[np.ndarray, np.ndarray, np.ndarray]` — funkcja modułowa; [wiersz 68](../src/pymoo_gui/algorithms/ts_nsga.py#L68).
- `lpd_ranks(objectives: np.ndarray, constraints: np.ndarray, division_level: int) -> np.ndarray` — funkcja modułowa; [wiersz 84](../src/pymoo_gui/algorithms/ts_nsga.py#L84).
- `_snapshot(X: np.ndarray, F: np.ndarray, CV: np.ndarray, ranks: np.ndarray) -> PopulationState` — funkcja modułowa; [wiersz 106](../src/pymoo_gui/algorithms/ts_nsga.py#L106).
- `TSNSGA.__init__(self, *, theta: float=5.0, stage_parameter: float=5.0, division_level: Optional[int]=None, automatic_mutation_rate: bool=False, **kwargs: Any) -> None` — metoda; [wiersz 115](../src/pymoo_gui/algorithms/ts_nsga.py#L115).
- `TSNSGA.gui_minimize(self, *, problem, termination, **kwargs)` — metoda; [wiersz 133](../src/pymoo_gui/algorithms/ts_nsga.py#L133).
- `TSNSGA.after_initialize(self) -> None` — metoda; [wiersz 138](../src/pymoo_gui/algorithms/ts_nsga.py#L138).
- `TSNSGA._current_stage(self) -> int` — metoda; [wiersz 148](../src/pymoo_gui/algorithms/ts_nsga.py#L148).
- `TSNSGA._measures(self, F: np.ndarray, CV: np.ndarray) -> tuple[np.ndarray, np.ndarray]` — metoda; [wiersz 152](../src/pymoo_gui/algorithms/ts_nsga.py#L152).
- `TSNSGA.select(self) -> np.ndarray` — metoda; [wiersz 164](../src/pymoo_gui/algorithms/ts_nsga.py#L164).
- `TSNSGA.environmental_selection(self, X, F, CV, n_survive)` — metoda; [wiersz 185](../src/pymoo_gui/algorithms/ts_nsga.py#L185).
- `make_ts_nsga(population_size: int=100, crossover_rate: float=1.0, mutation_rate: Optional[float]=None, theta: float=5.0, stage_parameter: float=5.0, division_level: Optional[int]=None, n_partitions: int=12, seed: int=1) -> TSNSGA` — funkcja modułowa; [wiersz 234](../src/pymoo_gui/algorithms/ts_nsga.py#L234).
- `lambda` — wyrażenie anonimowe; [wiersz 209](../src/pymoo_gui/algorithms/ts_nsga.py#L209).
- `lambda` — wyrażenie anonimowe; [wiersz 222](../src/pymoo_gui/algorithms/ts_nsga.py#L222).
- `lambda` — wyrażenie anonimowe; [wiersz 226](../src/pymoo_gui/algorithms/ts_nsga.py#L226).

### `src/pymoo_gui/algorithms/tspp.py`

- `tspp_sort(decisions: np.ndarray, objectives: np.ndarray, variance: np.ndarray, constraints: np.ndarray, constraint_variance: np.ndarray, phase: int, center: Optional[np.ndarray]=None, covariance: Optional[np.ndarray]=None) -> np.ndarray` — funkcja modułowa; [wiersz 40](../src/pymoo_gui/algorithms/tspp.py#L40).
- `run_tspp(function: Callable[[np.ndarray], Any], lower: np.ndarray, upper: np.ndarray, population_size: int, maximum_generations: Optional[int], surrogate_generations: int, infill_batch_size: int, seed: int, many_objective: bool, generation_hook: Callable[[SurrogateProblem], None]) -> SurrogateResult` — funkcja modułowa; [wiersz 79](../src/pymoo_gui/algorithms/tspp.py#L79).
- `TSPP.__init__(self, population_size: int=40, surrogate_generations: int=10, infill_batch_size: int=5, seed: int=1) -> None` — metoda; [wiersz 231](../src/pymoo_gui/algorithms/tspp.py#L231).
- `TSPP._run_surrogate(self, function, lower, upper, maximum_generations, seed, generation_hook)` — metoda; [wiersz 248](../src/pymoo_gui/algorithms/tspp.py#L248).
- `make_tspp(population_size: int=40, surrogate_generations: int=10, infill_batch_size: int=5, seed: int=1) -> TSPP` — funkcja modułowa; [wiersz 264](../src/pymoo_gui/algorithms/tspp.py#L264).

### `src/pymoo_gui/algorithms/umaoea.py`

- `reference_weights(count: int, objectives: int, rng: np.random.Generator, pool_size: int=5000) -> np.ndarray` — funkcja modułowa; [wiersz 25](../src/pymoo_gui/algorithms/umaoea.py#L25).
- `merge_sequence(count: int, block: int) -> np.ndarray` — funkcja modułowa; [wiersz 45](../src/pymoo_gui/algorithms/umaoea.py#L45).
- `merge_sequence.recurse(left: int, right: int) -> None` — funkcja zagnieżdżona; [wiersz 53](../src/pymoo_gui/algorithms/umaoea.py#L53).
- `sde_truncation(F: np.ndarray, count: int) -> np.ndarray` — funkcja modułowa; [wiersz 69](../src/pymoo_gui/algorithms/umaoea.py#L69).
- `MuMaOEA.__init__(self, population_size: int=30, block: int=5, reference_pool: int=5000, seed: int=1) -> None` — metoda; [wiersz 86](../src/pymoo_gui/algorithms/umaoea.py#L86).
- `MuMaOEA.after_initialize(self) -> None` — metoda; [wiersz 104](../src/pymoo_gui/algorithms/umaoea.py#L104).
- `MuMaOEA._update_neighborhood(self) -> None` — metoda; [wiersz 119](../src/pymoo_gui/algorithms/umaoea.py#L119).
- `MuMaOEA._nominal_convergence(self, parent_ids: np.ndarray) -> tuple[np.ndarray, np.ndarray, float]` — metoda; [wiersz 123](../src/pymoo_gui/algorithms/umaoea.py#L123).
- `MuMaOEA._pbi(F: np.ndarray, weight: np.ndarray, theta: float, ideal: np.ndarray) -> float` — metoda; [wiersz 143](../src/pymoo_gui/algorithms/umaoea.py#L143).
- `MuMaOEA._controller_archive(self, active_block: np.ndarray) -> None` — metoda; [wiersz 150](../src/pymoo_gui/algorithms/umaoea.py#L150).
- `MuMaOEA.step(self) -> None` — metoda; [wiersz 187](../src/pymoo_gui/algorithms/umaoea.py#L187).
- `MuMaOEA.gui_minimize(self, *, problem: Any, termination: Any, **kwargs: Any)` — metoda; [wiersz 243](../src/pymoo_gui/algorithms/umaoea.py#L243).
- `make_umaoea(population_size: int=30, block: int=5, reference_pool: int=5000, seed: int=1) -> MuMaOEA` — funkcja modułowa; [wiersz 249](../src/pymoo_gui/algorithms/umaoea.py#L249).
- `lambda` — wyrażenie anonimowe; [wiersz 39](../src/pymoo_gui/algorithms/umaoea.py#L39).
- `lambda` — wyrażenie anonimowe; [wiersz 78](../src/pymoo_gui/algorithms/umaoea.py#L78).

### `src/pymoo_gui/algoritms/__init__.py`

Brak deklaracji funkcji i wyrażeń `lambda`.

### `src/pymoo_gui/app.py`

- `NoTermination.__init__(self)` — metoda; [wiersz 66](../src/pymoo_gui/app.py#L66).
- `NoTermination.update(self, algorithm)` — metoda; [wiersz 71](../src/pymoo_gui/app.py#L71).
- `NoTermination.has_terminated(self)` — metoda; [wiersz 76](../src/pymoo_gui/app.py#L76).
- `NoTermination.do_continue(self)` — metoda; [wiersz 80](../src/pymoo_gui/app.py#L80).
- `translate_ui_text(text: Any) -> str` — funkcja modułowa; [wiersz 271](../src/pymoo_gui/app.py#L271).
- `pl_param_label(name: str) -> str` — funkcja modułowa; [wiersz 329](../src/pymoo_gui/app.py#L329).
- `callable_signature(obj: Any) -> inspect.Signature` — funkcja modułowa; [wiersz 334](../src/pymoo_gui/app.py#L334).
- `filter_callable_kwargs(fn: Any, params: Mapping[str, Any]) -> Dict[str, Any]` — funkcja modułowa; [wiersz 339](../src/pymoo_gui/app.py#L339).
- `_literal_or_str(value: str) -> Any` — funkcja modułowa; [wiersz 351](../src/pymoo_gui/app.py#L351).
- `should_save_nondominated_solutions_for_epoch(epoch: Any, mode: str, step: int=1, *, is_final: bool=False) -> bool` — funkcja modułowa; [wiersz 362](../src/pymoo_gui/app.py#L362).
- `_specs(raw_specs: Optional[Any]) -> list[FieldSpec]` — funkcja modułowa; [wiersz 408](../src/pymoo_gui/app.py#L408).
- `ParamForm.__init__(self, title: str, parent=None)` — metoda; [wiersz 444](../src/pymoo_gui/app.py#L444).
- `ParamForm.clear(self) -> None` — metoda; [wiersz 453](../src/pymoo_gui/app.py#L453).
- `ParamForm.binding(self, name: str) -> Optional[WidgetBinding]` — metoda; [wiersz 459](../src/pymoo_gui/app.py#L459).
- `ParamForm.bindings(self) -> Sequence[WidgetBinding]` — metoda; [wiersz 463](../src/pymoo_gui/app.py#L463).
- `ParamForm.build_for_callable(self, fn: Any, extra_fields: Optional[Any]=None) -> None` — metoda; [wiersz 467](../src/pymoo_gui/app.py#L467).
- `ParamForm.build_for_signature(self, sig: inspect.Signature, extra_fields: Optional[Any]=None) -> None` — metoda; [wiersz 471](../src/pymoo_gui/app.py#L471).
- `ParamForm.build_from_specs(self, raw_specs: Optional[Any]) -> None` — metoda; [wiersz 486](../src/pymoo_gui/app.py#L486).
- `ParamForm._kind(self, annotation: Any, default: Any) -> str` — metoda; [wiersz 492](../src/pymoo_gui/app.py#L492).
- `ParamForm._bounds(self, spec: FieldSpec) -> Tuple[float, float]` — metoda; [wiersz 504](../src/pymoo_gui/app.py#L504).
- `ParamForm._apply_read_only(self, widget: Any, spec: FieldSpec) -> None` — metoda; [wiersz 523](../src/pymoo_gui/app.py#L523).
- `ParamForm._add_field(self, spec: FieldSpec) -> None` — metoda; [wiersz 536](../src/pymoo_gui/app.py#L536).
- `ParamForm.values(self) -> Dict[str, Any]` — metoda; [wiersz 578](../src/pymoo_gui/app.py#L578).
- `OptimizationWorker.__init__(self, problem_key: str, alg_key: str, problem_params: Mapping[str, Any], algorithm_params: Mapping[str, Any], n_gen: Optional[int], seed: int, verbose: bool, hv_ref_point: Optional[list[float]], parallel_eval: bool=False, parallel_workers: int=1, parallel_backend: str='process', parent=None, step_mode: bool=False)` — metoda; [wiersz 612](../src/pymoo_gui/app.py#L612).
- `OptimizationWorker.request_cancel(self) -> None` — metoda; [wiersz 647](../src/pymoo_gui/app.py#L647).
- `OptimizationWorker.request_next_epoch(self) -> bool` — metoda; [wiersz 654](../src/pymoo_gui/app.py#L654).
- `OptimizationWorker._cancel_pending(self) -> bool` — metoda; [wiersz 663](../src/pymoo_gui/app.py#L663).
- `OptimizationWorker._emit_generation(self, payload: dict) -> None` — metoda; [wiersz 667](../src/pymoo_gui/app.py#L667).
- `OptimizationWorker.run(self) -> None` — metoda; [wiersz 683](../src/pymoo_gui/app.py#L683).
- `MainWindow.__init__(self)` — metoda; [wiersz 736](../src/pymoo_gui/app.py#L736).
- `MainWindow._apply_default_window_geometry(self) -> None` — metoda; [wiersz 774](../src/pymoo_gui/app.py#L774).
- `MainWindow.showEvent(self, event) -> None` — metoda; [wiersz 782](../src/pymoo_gui/app.py#L782).
- `MainWindow._make_window_square(self) -> None` — metoda; [wiersz 789](../src/pymoo_gui/app.py#L789).
- `MainWindow._build_ui(self) -> None` — metoda; [wiersz 794](../src/pymoo_gui/app.py#L794).
- `MainWindow._build_checkable_registry_list(self, registry: Mapping[str, Dict[str, Any]]) -> QListWidget` — metoda; [wiersz 825](../src/pymoo_gui/app.py#L825).
- `MainWindow._build_multi_selection_group(self, title: str, widget: QListWidget) -> QGroupBox` — metoda; [wiersz 837](../src/pymoo_gui/app.py#L837).
- `MainWindow._build_multi_panel(self) -> QWidget` — metoda; [wiersz 852](../src/pymoo_gui/app.py#L852).
- `MainWindow._apply_english_ui_texts(self) -> None` — metoda; [wiersz 937](../src/pymoo_gui/app.py#L937).
- `MainWindow._build_controls_panel(self) -> QWidget` — metoda; [wiersz 957](../src/pymoo_gui/app.py#L957).
- `MainWindow._build_results_panel(self) -> QWidget` — metoda; [wiersz 969](../src/pymoo_gui/app.py#L969).
- `MainWindow._build_problem_controls(self) -> None` — metoda; [wiersz 1032](../src/pymoo_gui/app.py#L1032).
- `MainWindow._build_hv_controls(self) -> None` — metoda; [wiersz 1051](../src/pymoo_gui/app.py#L1051).
- `MainWindow._build_run_controls(self) -> None` — metoda; [wiersz 1070](../src/pymoo_gui/app.py#L1070).
- `MainWindow._build_console(self) -> None` — metoda; [wiersz 1119](../src/pymoo_gui/app.py#L1119).
- `MainWindow._connect_signals(self) -> None` — metoda; [wiersz 1129](../src/pymoo_gui/app.py#L1129).
- `MainWindow._configure_placeholders(self) -> None` — metoda; [wiersz 1168](../src/pymoo_gui/app.py#L1168).
- `MainWindow._set_all_multi_items(self, widget: QListWidget, checked: bool) -> None` — metoda; [wiersz 1184](../src/pymoo_gui/app.py#L1184).
- `MainWindow._checked_multi_keys(self, widget: QListWidget) -> list[str]` — metoda; [wiersz 1197](../src/pymoo_gui/app.py#L1197).
- `MainWindow._update_multi_selection_state(self, *_args: Any) -> None` — metoda; [wiersz 1208](../src/pymoo_gui/app.py#L1208).
- `MainWindow._set_multi_running_state(self, running: bool) -> None` — metoda; [wiersz 1221](../src/pymoo_gui/app.py#L1221).
- `MainWindow._multi_row_key(self, payload: Mapping[str, Any]) -> tuple[str, str]` — metoda; [wiersz 1237](../src/pymoo_gui/app.py#L1237).
- `MainWindow._set_multi_table_value(self, row: int, column: int, value: Any) -> None` — metoda; [wiersz 1241](../src/pymoo_gui/app.py#L1241).
- `MainWindow._on_multi_run_started(self, payload: Mapping[str, Any]) -> None` — metoda; [wiersz 1248](../src/pymoo_gui/app.py#L1248).
- `MainWindow._on_multi_run_progress(self, payload: Mapping[str, Any]) -> None` — metoda; [wiersz 1272](../src/pymoo_gui/app.py#L1272).
- `MainWindow._on_multi_run_finished(self, payload: Mapping[str, Any]) -> None` — metoda; [wiersz 1291](../src/pymoo_gui/app.py#L1291).
- `MainWindow.start_multi_experiment(self) -> None` — metoda; [wiersz 1317](../src/pymoo_gui/app.py#L1317).
- `MainWindow.stop_multi_experiment(self) -> None` — metoda; [wiersz 1368](../src/pymoo_gui/app.py#L1368).
- `MainWindow._finish_multi_experiment(self, status: str, results: Sequence[Mapping[str, Any]]) -> None` — metoda; [wiersz 1378](../src/pymoo_gui/app.py#L1378).
- `MainWindow._on_multi_experiment_done(self, results: Sequence[Mapping[str, Any]]) -> None` — metoda; [wiersz 1394](../src/pymoo_gui/app.py#L1394).
- `MainWindow._on_multi_experiment_cancelled(self, results: Sequence[Mapping[str, Any]]) -> None` — metoda; [wiersz 1398](../src/pymoo_gui/app.py#L1398).
- `MainWindow._on_multi_experiment_failed(self, error: str) -> None` — metoda; [wiersz 1402](../src/pymoo_gui/app.py#L1402).
- `MainWindow._entry(self, combo: QComboBox, registry: Mapping[str, Dict[str, Any]]) -> Dict[str, Any]` — metoda; [wiersz 1410](../src/pymoo_gui/app.py#L1410).
- `MainWindow._known_pf_for_problem(self, entry: Mapping[str, Any], problem: Any) -> Optional[np.ndarray]` — metoda; [wiersz 1415](../src/pymoo_gui/app.py#L1415).
- `MainWindow._instantiate_selected_problem(self, params: Optional[Mapping[str, Any]]=None) -> Tuple[Optional[Any], Optional[str]]` — metoda; [wiersz 1436](../src/pymoo_gui/app.py#L1436).
- `MainWindow._connect_problem_form_signals(self) -> None` — metoda; [wiersz 1451](../src/pymoo_gui/app.py#L1451).
- `MainWindow._ensure_plot_widget(self) -> UnifiedParetoWidget` — metoda; [wiersz 1464](../src/pymoo_gui/app.py#L1464).
- `MainWindow._reset_plot_axes(self) -> None` — metoda; [wiersz 1489](../src/pymoo_gui/app.py#L1489).
- `MainWindow._set_plot_message(self, text: str) -> None` — metoda; [wiersz 1494](../src/pymoo_gui/app.py#L1494).
- `MainWindow._reset_plot_run_data(self) -> None` — metoda; [wiersz 1502](../src/pymoo_gui/app.py#L1502).
- `MainWindow._update_epoch_controls(self) -> None` — metoda; [wiersz 1510](../src/pymoo_gui/app.py#L1510).
- `MainWindow._remember_epoch(self, payload: Mapping[str, Any]) -> None` — metoda; [wiersz 1523](../src/pymoo_gui/app.py#L1523).
- `MainWindow._show_epoch(self, epoch: int) -> None` — metoda; [wiersz 1535](../src/pymoo_gui/app.py#L1535).
- `MainWindow._move_epoch(self, direction: int) -> None` — metoda; [wiersz 1544](../src/pymoo_gui/app.py#L1544).
- `MainWindow._show_latest_epoch(self) -> None` — metoda; [wiersz 1550](../src/pymoo_gui/app.py#L1550).
- `MainWindow._apply_grid_options(self, *_args: Any) -> None` — metoda; [wiersz 1554](../src/pymoo_gui/app.py#L1554).
- `MainWindow._export_window_screenshot(self) -> None` — metoda; [wiersz 1559](../src/pymoo_gui/app.py#L1559).
- `MainWindow._export_plot_png(self) -> None` — metoda; [wiersz 1575](../src/pymoo_gui/app.py#L1575).
- `MainWindow._run_next_epoch(self) -> None` — metoda; [wiersz 1591](../src/pymoo_gui/app.py#L1591).
- `MainWindow._reset_run_result_state(self) -> None` — metoda; [wiersz 1600](../src/pymoo_gui/app.py#L1600).
- `MainWindow._update_run_form_state(self) -> None` — metoda; [wiersz 1606](../src/pymoo_gui/app.py#L1606).
- `MainWindow._current_nd_save_mode(self) -> str` — metoda; [wiersz 1630](../src/pymoo_gui/app.py#L1630).
- `MainWindow._update_nd_save_controls_state(self) -> None` — metoda; [wiersz 1635](../src/pymoo_gui/app.py#L1635).
- `MainWindow._collect_nd_save_args(self) -> Tuple[Optional[dict], Optional[str]]` — metoda; [wiersz 1639](../src/pymoo_gui/app.py#L1639).
- `MainWindow._set_run_state(self, status_text: str, running: bool) -> None` — metoda; [wiersz 1649](../src/pymoo_gui/app.py#L1649).
- `MainWindow._apply_generation_payload(self, payload: Mapping[str, Any]) -> None` — metoda; [wiersz 1665](../src/pymoo_gui/app.py#L1665).
- `MainWindow._apply_problem_preview_state(self, problem: Any) -> None` — metoda; [wiersz 1674](../src/pymoo_gui/app.py#L1674).
- `MainWindow._refresh_problem_plot(self) -> None` — metoda; [wiersz 1684](../src/pymoo_gui/app.py#L1684).
- `MainWindow._render_plot(self) -> None` — metoda; [wiersz 1698](../src/pymoo_gui/app.py#L1698).
- `MainWindow._rebuild_problem_form(self) -> None` — metoda; [wiersz 1715](../src/pymoo_gui/app.py#L1715).
- `MainWindow._rebuild_alg_form(self) -> None` — metoda; [wiersz 1726](../src/pymoo_gui/app.py#L1726).
- `MainWindow._connect_problem_param_signals(self) -> None` — metoda; [wiersz 1732](../src/pymoo_gui/app.py#L1732).
- `MainWindow._on_n_obj_changed(self, _value: int) -> None` — metoda; [wiersz 1749](../src/pymoo_gui/app.py#L1749).
- `MainWindow._on_problem_form_changed(self, *_args: Any) -> None` — metoda; [wiersz 1754](../src/pymoo_gui/app.py#L1754).
- `MainWindow._on_show_population_toggled(self, checked: bool) -> None` — metoda; [wiersz 1758](../src/pymoo_gui/app.py#L1758).
- `MainWindow._on_hide_pareto_front_toggled(self, checked: bool) -> None` — metoda; [wiersz 1763](../src/pymoo_gui/app.py#L1763).
- `MainWindow._on_auto_scale_toggled(self, checked: bool) -> None` — metoda; [wiersz 1770](../src/pymoo_gui/app.py#L1770).
- `MainWindow._on_nd_save_mode_changed(self, _index: int) -> None` — metoda; [wiersz 1779](../src/pymoo_gui/app.py#L1779).
- `MainWindow._on_ran_toggled(self, checked: bool) -> None` — metoda; [wiersz 1783](../src/pymoo_gui/app.py#L1783).
- `MainWindow._on_parallel_eval_toggled(self, checked: bool) -> None` — metoda; [wiersz 1788](../src/pymoo_gui/app.py#L1788).
- `MainWindow._toggle_console_dock(self) -> None` — metoda; [wiersz 1793](../src/pymoo_gui/app.py#L1793).
- `MainWindow._on_console_visibility_changed(self, visible: bool) -> None` — metoda; [wiersz 1797](../src/pymoo_gui/app.py#L1797).
- `MainWindow._log(self, msg: str) -> None` — metoda; [wiersz 1801](../src/pymoo_gui/app.py#L1801).
- `MainWindow._warn(self, title: str, message: str, log_message: Optional[str]=None) -> None` — metoda; [wiersz 1807](../src/pymoo_gui/app.py#L1807).
- `MainWindow._current_n_obj(self) -> int` — metoda; [wiersz 1813](../src/pymoo_gui/app.py#L1813).
- `MainWindow._parse_float_token(self, token: str) -> Optional[float]` — metoda; [wiersz 1826](../src/pymoo_gui/app.py#L1826).
- `MainWindow._parse_ref_point_text(self, text: str) -> Tuple[Optional[list[float]], Optional[str]]` — metoda; [wiersz 1844](../src/pymoo_gui/app.py#L1844).
- `MainWindow._auto_hv_ref_point(self) -> list[float]` — metoda; [wiersz 1865](../src/pymoo_gui/app.py#L1865).
- `MainWindow._hv_ref_point_state(self) -> Tuple[bool, Optional[list[float]], str, Optional[str]]` — metoda; [wiersz 1872](../src/pymoo_gui/app.py#L1872).
- `MainWindow._validate_hv_manual_ref_point(self) -> bool` — metoda; [wiersz 1887](../src/pymoo_gui/app.py#L1887).
- `MainWindow._update_hv_ref_point_label(self) -> None` — metoda; [wiersz 1898](../src/pymoo_gui/app.py#L1898).
- `MainWindow._on_hv_mode_changed(self, _checked: bool) -> None` — metoda; [wiersz 1908](../src/pymoo_gui/app.py#L1908).
- `MainWindow._on_hv_manual_changed(self, _text: str) -> None` — metoda; [wiersz 1917](../src/pymoo_gui/app.py#L1917).
- `MainWindow._on_live_updates_toggled(self, checked: bool) -> None` — metoda; [wiersz 1922](../src/pymoo_gui/app.py#L1922).
- `MainWindow._update_run_button_state(self) -> None` — metoda; [wiersz 1927](../src/pymoo_gui/app.py#L1927).
- `MainWindow._update_plot_status(self, payload: Optional[dict]=None, message: Optional[str]=None) -> None` — metoda; [wiersz 1937](../src/pymoo_gui/app.py#L1937).
- `MainWindow._fmt_int(self, value: Optional[int]) -> str` — metoda; [wiersz 1953](../src/pymoo_gui/app.py#L1953).
- `MainWindow._fmt_metric(self, value: Optional[float]) -> str` — metoda; [wiersz 1960](../src/pymoo_gui/app.py#L1960).
- `MainWindow._update_metrics_label(self, payload: Optional[dict]) -> None` — metoda; [wiersz 1967](../src/pymoo_gui/app.py#L1967).
- `MainWindow._metrics_label_text(self, payload: Mapping[str, Any]) -> str` — metoda; [wiersz 1971](../src/pymoo_gui/app.py#L1971).
- `MainWindow._clear_table(self) -> None` — metoda; [wiersz 1977](../src/pymoo_gui/app.py#L1977).
- `MainWindow._should_scroll_table(self) -> bool` — metoda; [wiersz 1982](../src/pymoo_gui/app.py#L1982).
- `MainWindow._append_generation_row(self, payload: dict) -> None` — metoda; [wiersz 1987](../src/pymoo_gui/app.py#L1987).
- `MainWindow._append_last_payload_once(self, payload: Mapping[str, Any]) -> None` — metoda; [wiersz 2010](../src/pymoo_gui/app.py#L2010).
- `MainWindow._metrics_table_data(self) -> Tuple[list[str], list[list[str]]]` — metoda; [wiersz 2018](../src/pymoo_gui/app.py#L2018).
- `MainWindow._export_metrics_table(self) -> None` — metoda; [wiersz 2034](../src/pymoo_gui/app.py#L2034).
- `MainWindow._xlsx_value(self, value: Any) -> object` — metoda; [wiersz 2053](../src/pymoo_gui/app.py#L2053).
- `MainWindow._solution_table_data(self, payload: Mapping[str, Any]) -> Tuple[list[str], list[list[object]]]` — metoda; [wiersz 2065](../src/pymoo_gui/app.py#L2065).
- `MainWindow._export_solution_table(self, payload: Mapping[str, Any]) -> None` — metoda; [wiersz 2106](../src/pymoo_gui/app.py#L2106).
- `MainWindow._export_nondominated_solutions_for_epoch(self, payload: Mapping[str, Any]) -> None` — metoda; [wiersz 2135](../src/pymoo_gui/app.py#L2135).
- `MainWindow._export_nondominated_solutions_for_final_epoch(self, payload: Mapping[str, Any]) -> None` — metoda; [wiersz 2155](../src/pymoo_gui/app.py#L2155).
- `MainWindow._validated_int(self, value: Any, label: str, minimum: int) -> Tuple[Optional[int], Optional[str]]` — metoda; [wiersz 2180](../src/pymoo_gui/app.py#L2180).
- `MainWindow._collect_run_args(self) -> Tuple[Optional[dict], Optional[str]]` — metoda; [wiersz 2192](../src/pymoo_gui/app.py#L2192).
- `MainWindow._collect_algorithm_args(self) -> Tuple[Optional[dict], Optional[str]]` — metoda; [wiersz 2220](../src/pymoo_gui/app.py#L2220).
- `MainWindow._collect_problem_args(self) -> Tuple[dict, Optional[str]]` — metoda; [wiersz 2230](../src/pymoo_gui/app.py#L2230).
- `MainWindow._prepare_run_visuals(self) -> None` — metoda; [wiersz 2234](../src/pymoo_gui/app.py#L2234).
- `MainWindow._finish_run(self, status_text: str, last_payload: Optional[dict]) -> None` — metoda; [wiersz 2248](../src/pymoo_gui/app.py#L2248).
- `MainWindow._on_generation(self, payload: dict) -> None` — metoda; [wiersz 2267](../src/pymoo_gui/app.py#L2267).
- `MainWindow.start_run(self, _checked: bool=False, *, step_mode: bool=False) -> None` — metoda; [wiersz 2290](../src/pymoo_gui/app.py#L2290).
- `MainWindow.stop_run(self) -> None` — metoda; [wiersz 2405](../src/pymoo_gui/app.py#L2405).
- `MainWindow._on_run_done(self, last_payload: dict) -> None` — metoda; [wiersz 2416](../src/pymoo_gui/app.py#L2416).
- `MainWindow._on_run_cancelled(self, last_payload: dict) -> None` — metoda; [wiersz 2420](../src/pymoo_gui/app.py#L2420).
- `MainWindow._on_run_failed(self, err: str) -> None` — metoda; [wiersz 2425](../src/pymoo_gui/app.py#L2425).
- `MainWindow._clear_console_and_visuals(self) -> None` — metoda; [wiersz 2434](../src/pymoo_gui/app.py#L2434).
- `MainWindow.closeEvent(self, event) -> None` — metoda; [wiersz 2447](../src/pymoo_gui/app.py#L2447).
- `main() -> None` — funkcja modułowa; [wiersz 2461](../src/pymoo_gui/app.py#L2461).
- `lambda` — wyrażenie anonimowe; [wiersz 845](../src/pymoo_gui/app.py#L845).
- `lambda` — wyrażenie anonimowe; [wiersz 846](../src/pymoo_gui/app.py#L846).
- `lambda` — wyrażenie anonimowe; [wiersz 1143](../src/pymoo_gui/app.py#L1143).
- `lambda` — wyrażenie anonimowe; [wiersz 1144](../src/pymoo_gui/app.py#L1144).

### `src/pymoo_gui/metrics/__init__.py`

Brak deklaracji funkcji i wyrażeń `lambda`.

### `src/pymoo_gui/metrics/export.py`

- `safe_filename_part(value: object, fallback: str) -> str` — funkcja modułowa; [wiersz 33](../src/pymoo_gui/metrics/export.py#L33).
- `timestamp_for_filename(now: datetime | None=None) -> str` — funkcja modułowa; [wiersz 49](../src/pymoo_gui/metrics/export.py#L49).
- `date_for_filename(now: datetime | None=None) -> str` — funkcja modułowa; [wiersz 60](../src/pymoo_gui/metrics/export.py#L60).
- `metrics_export_path(project_root: Path, algorithm_name: object, problem_name: object, now: datetime | None=None) -> Path` — funkcja modułowa; [wiersz 71](../src/pymoo_gui/metrics/export.py#L71).
- `solutions_export_path(project_root: Path, algorithm_name: object, problem_name: object, now: datetime | None=None) -> Path` — funkcja modułowa; [wiersz 93](../src/pymoo_gui/metrics/export.py#L93).
- `next_available_export_path(path: Path) -> Path` — funkcja modułowa; [wiersz 115](../src/pymoo_gui/metrics/export.py#L115).
- `_safe_sheet_name(value: object) -> str` — funkcja modułowa; [wiersz 137](../src/pymoo_gui/metrics/export.py#L137).
- `_column_name(index: int) -> str` — funkcja modułowa; [wiersz 150](../src/pymoo_gui/metrics/export.py#L150).
- `_cell_xml(row_idx: int, col_idx: int, value: object) -> str` — funkcja modułowa; [wiersz 166](../src/pymoo_gui/metrics/export.py#L166).
- `_worksheet_xml(headers: Sequence[str], rows: Sequence[Sequence[object]]) -> str` — funkcja modułowa; [wiersz 189](../src/pymoo_gui/metrics/export.py#L189).
- `_deduplicate_sheet_names(names: Sequence[object]) -> list[str]` — funkcja modułowa; [wiersz 220](../src/pymoo_gui/metrics/export.py#L220).
- `write_xlsx_workbook(path: Path, sheets: Sequence[tuple[object, Sequence[str], Sequence[Sequence[object]]]]) -> Path` — funkcja modułowa; [wiersz 244](../src/pymoo_gui/metrics/export.py#L244).
- `write_xlsx_table(path: Path, headers: Sequence[str], rows: Sequence[Sequence[object]], sheet_name: object='Metrics') -> Path` — funkcja modułowa; [wiersz 323](../src/pymoo_gui/metrics/export.py#L323).

### `src/pymoo_gui/metrics/quality.py`

- `is_delta_supported(algorithm_key: Optional[str], n_obj: Optional[int]=None) -> bool` — funkcja modułowa; [wiersz 35](../src/pymoo_gui/metrics/quality.py#L35).
- `compute_igdx(X: np.ndarray, reference_set: np.ndarray) -> Optional[float]` — funkcja modułowa; [wiersz 62](../src/pymoo_gui/metrics/quality.py#L62).
- `compute_psp(X: np.ndarray, reference_set: np.ndarray) -> Optional[float]` — funkcja modułowa; [wiersz 75](../src/pymoo_gui/metrics/quality.py#L75).
- `compute_dynamic_average(values: list[Optional[float]]) -> Optional[float]` — funkcja modułowa; [wiersz 89](../src/pymoo_gui/metrics/quality.py#L89).
- `_safe_float(x) -> Optional[float]` — funkcja modułowa; [wiersz 96](../src/pymoo_gui/metrics/quality.py#L96).
- `_as_2d(arr: Optional[np.ndarray], n_obj: Optional[int]=None) -> Optional[np.ndarray]` — funkcja modułowa; [wiersz 104](../src/pymoo_gui/metrics/quality.py#L104).
- `_as_decision_matrix(values: Optional[np.ndarray], n_var: Optional[int]=None) -> Optional[np.ndarray]` — funkcja modułowa; [wiersz 123](../src/pymoo_gui/metrics/quality.py#L123).
- `_finite_rows(arr: np.ndarray) -> np.ndarray` — funkcja modułowa; [wiersz 140](../src/pymoo_gui/metrics/quality.py#L140).
- `_safe_solve(A: np.ndarray, b: np.ndarray) -> Optional[np.ndarray]` — funkcja modułowa; [wiersz 146](../src/pymoo_gui/metrics/quality.py#L146).
- `_problem_n_ieq_constr(problem: Any) -> int` — funkcja modułowa; [wiersz 157](../src/pymoo_gui/metrics/quality.py#L157).
- `_problem_bounds(problem: Any, n_var: int) -> tuple[np.ndarray, np.ndarray]` — funkcja modułowa; [wiersz 169](../src/pymoo_gui/metrics/quality.py#L169).
- `_problem_bounds._bound(name: str, fill: float) -> np.ndarray` — funkcja zagnieżdżona; [wiersz 171](../src/pymoo_gui/metrics/quality.py#L171).
- `_evaluate_fg(problem: Any, X: np.ndarray) -> Optional[tuple[np.ndarray, np.ndarray]]` — funkcja modułowa; [wiersz 190](../src/pymoo_gui/metrics/quality.py#L190).
- `_valid_derivative(values: Any, expected_shape: tuple[int, int, int]) -> Optional[np.ndarray]` — funkcja modułowa; [wiersz 214](../src/pymoo_gui/metrics/quality.py#L214).
- `_finite_difference_derivatives(problem: Any, X: np.ndarray, F: np.ndarray, G: np.ndarray, eps: float=FINITE_DIFF_EPS) -> tuple[Optional[np.ndarray], Optional[np.ndarray]]` — funkcja modułowa; [wiersz 225](../src/pymoo_gui/metrics/quality.py#L225).
- `_evaluate_kktpm_inputs(X: np.ndarray, problem: Any, finite_diff_eps: float=FINITE_DIFF_EPS) -> Optional[tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]]` — funkcja modułowa; [wiersz 287](../src/pymoo_gui/metrics/quality.py#L287).
- `_append_bound_constraints(problem: Any, X: np.ndarray, G: np.ndarray, dG: np.ndarray) -> tuple[np.ndarray, np.ndarray]` — funkcja modułowa; [wiersz 325](../src/pymoo_gui/metrics/quality.py#L325).
- `_calc_cv(G: np.ndarray) -> np.ndarray` — funkcja modułowa; [wiersz 368](../src/pymoo_gui/metrics/quality.py#L368).
- `compute_spread(F: np.ndarray) -> Optional[float]` — funkcja modułowa; [wiersz 375](../src/pymoo_gui/metrics/quality.py#L375).
- `compute_delta(F: np.ndarray, pareto_front: np.ndarray) -> Optional[float]` — funkcja modułowa; [wiersz 405](../src/pymoo_gui/metrics/quality.py#L405).
- `compute_kktpm(X: np.ndarray, problem: Any, ideal: Optional[np.ndarray]=None, utopian_eps: float=0.0001, rho: float=0.001, finite_diff_eps: float=FINITE_DIFF_EPS) -> Optional[np.ndarray]` — funkcja modułowa; [wiersz 451](../src/pymoo_gui/metrics/quality.py#L451).
- `_feasibility_mask_from_cv(cv: Optional[np.ndarray]) -> Optional[np.ndarray]` — funkcja modułowa; [wiersz 568](../src/pymoo_gui/metrics/quality.py#L568).
- `compute_metrics(F: np.ndarray, pareto_front: Optional[np.ndarray], cv: Optional[np.ndarray]=None, ref_point: Optional[np.ndarray]=None, n_obj: Optional[int]=None, X: Optional[np.ndarray]=None, problem: Any=None, kktpm_ideal: Optional[np.ndarray]=None, delta_supported: bool=True) -> MetricResult` — funkcja modułowa; [wiersz 583](../src/pymoo_gui/metrics/quality.py#L583).
- `get_hv_ref_point(problem_name: Optional[str], n_obj: Optional[int], pareto_front: Optional[np.ndarray]=None) -> Optional[np.ndarray]` — funkcja modułowa; [wiersz 715](../src/pymoo_gui/metrics/quality.py#L715).
- `fixed_ref_point_for_problem(problem_name: Optional[str], n_obj: Optional[int]) -> Optional[np.ndarray]` — funkcja modułowa; [wiersz 745](../src/pymoo_gui/metrics/quality.py#L745).

### `src/pymoo_gui/multi.py`

- `default_entry_params(entry: Mapping[str, Any]) -> dict[str, Any]` — funkcja modułowa; [wiersz 51](../src/pymoo_gui/multi.py#L51).
- `filter_callable_kwargs(fn: Any, params: Mapping[str, Any]) -> dict[str, Any]` — funkcja modułowa; [wiersz 65](../src/pymoo_gui/multi.py#L65).
- `build_multi_run_specs(problem_keys: Sequence[str], algorithm_keys: Sequence[str]) -> list[MultiRunSpec]` — funkcja modułowa; [wiersz 77](../src/pymoo_gui/multi.py#L77).
- `metrics_table_data(history: Sequence[Mapping[str, Any]]) -> tuple[list[str], list[list[object]]]` — funkcja modułowa; [wiersz 102](../src/pymoo_gui/multi.py#L102).
- `_xlsx_value(value: Any) -> object` — funkcja modułowa; [wiersz 117](../src/pymoo_gui/multi.py#L117).
- `solution_table_data(payload: Mapping[str, Any], n_obj: int) -> tuple[list[str], list[list[object]]]` — funkcja modułowa; [wiersz 130](../src/pymoo_gui/multi.py#L130).
- `MultiExperimentWorker.__init__(self, specs: Sequence[MultiRunSpec], n_gen: int, seed: int, project_root: Path, parent=None) -> None` — metoda; [wiersz 188](../src/pymoo_gui/multi.py#L188).
- `MultiExperimentWorker.request_cancel(self) -> None` — metoda; [wiersz 207](../src/pymoo_gui/multi.py#L207).
- `MultiExperimentWorker._cancel_pending(self) -> bool` — metoda; [wiersz 212](../src/pymoo_gui/multi.py#L212).
- `MultiExperimentWorker._write_result_files(self, spec: MultiRunSpec, history: Sequence[Mapping[str, Any]], last_payload: Mapping[str, Any], n_obj: int) -> tuple[Optional[Path], Optional[Path], list[str]]` — metoda; [wiersz 216](../src/pymoo_gui/multi.py#L216).
- `MultiExperimentWorker._execute_spec(self, spec: MultiRunSpec, index: int, total: int) -> dict[str, Any]` — metoda; [wiersz 245](../src/pymoo_gui/multi.py#L245).
- `MultiExperimentWorker._execute_spec.on_generation(payload: Mapping[str, Any]) -> None` — funkcja zagnieżdżona; [wiersz 284](../src/pymoo_gui/multi.py#L284).
- `MultiExperimentWorker.run(self) -> None` — metoda; [wiersz 376](../src/pymoo_gui/multi.py#L376).

### `src/pymoo_gui/packaging_smoke.py`

- `_offline_socket(*args, **kwargs)` — funkcja modułowa; [wiersz 11](../src/pymoo_gui/packaging_smoke.py#L11).
- `main(args: list[str]) -> int` — funkcja modułowa; [wiersz 15](../src/pymoo_gui/packaging_smoke.py#L15).

### `src/pymoo_gui/parallel.py`

- `_init_process_problem(problem: Any) -> None` — funkcja modułowa; [wiersz 23](../src/pymoo_gui/parallel.py#L23).
- `_row_output(value: Any) -> np.ndarray` — funkcja modułowa; [wiersz 29](../src/pymoo_gui/parallel.py#L29).
- `_evaluate_problem_row(problem: Any, x: Any, return_values_of: Sequence[str]) -> dict[str, np.ndarray]` — funkcja modułowa; [wiersz 37](../src/pymoo_gui/parallel.py#L37).
- `_evaluate_thread_row(args: tuple[Any, Any, Sequence[str]]) -> dict[str, np.ndarray]` — funkcja modułowa; [wiersz 48](../src/pymoo_gui/parallel.py#L48).
- `_evaluate_process_row(args: tuple[Any, Sequence[str]]) -> dict[str, np.ndarray]` — funkcja modułowa; [wiersz 55](../src/pymoo_gui/parallel.py#L55).
- `ParallelProblem.__init__(self, problem: Any, workers: int, backend: str='process')` — metoda; [wiersz 68](../src/pymoo_gui/parallel.py#L68).
- `ParallelProblem._make_pool(self) -> Any` — metoda; [wiersz 96](../src/pymoo_gui/parallel.py#L96).
- `ParallelProblem.__getattr__(self, name: str) -> Any` — metoda; [wiersz 107](../src/pymoo_gui/parallel.py#L107).
- `ParallelProblem._map_rows(self, X: np.ndarray, return_values_of: Sequence[str]) -> Iterable[dict[str, np.ndarray]]` — metoda; [wiersz 111](../src/pymoo_gui/parallel.py#L111).
- `ParallelProblem._evaluate(self, X: np.ndarray, out: dict[str, Any], *args: Any, **kwargs: Any) -> None` — metoda; [wiersz 119](../src/pymoo_gui/parallel.py#L119).
- `ParallelProblem.close(self) -> None` — metoda; [wiersz 133](../src/pymoo_gui/parallel.py#L133).
- `make_parallel_problem(problem: Any, workers: int, backend: str='process') -> ParallelProblem` — funkcja modułowa; [wiersz 150](../src/pymoo_gui/parallel.py#L150).

### `src/pymoo_gui/problems/__init__.py`

Brak deklaracji funkcji i wyrażeń `lambda`.

### `src/pymoo_gui/problems/binh2.py`

- `Binh2Problem.__init__(self)` — metoda; [wiersz 21](../src/pymoo_gui/problems/binh2.py#L21).
- `Binh2Problem._evaluate(self, X, out, *args, **kwargs)` — metoda; [wiersz 30](../src/pymoo_gui/problems/binh2.py#L30).

### `src/pymoo_gui/problems/capabilities.py`

- `problem_capabilities(*, variable_type: str='real', family: str='classical', constrained: bool=False, dynamic: bool=False, multimodal: bool=False, large_scale: bool=False, reference_front: str='unavailable', metrics: Iterable[str]=('hv',)) -> dict[str, Any]` — funkcja modułowa; [wiersz 11](../src/pymoo_gui/problems/capabilities.py#L11).
- `algorithm_capabilities(*, variable_types: Iterable[str]=('real',), constraints: bool=True, dynamic: bool=False) -> dict[str, Any]` — funkcja modułowa; [wiersz 41](../src/pymoo_gui/problems/capabilities.py#L41).
- `infer_problem_variable_type(problem: Any) -> str` — funkcja modułowa; [wiersz 59](../src/pymoo_gui/problems/capabilities.py#L59).

### `src/pymoo_gui/problems/constrex.py`

- `ConstrExProblem.__init__(self)` — metoda; [wiersz 22](../src/pymoo_gui/problems/constrex.py#L22).
- `ConstrExProblem._evaluate(self, X, out, *args, **kwargs)` — metoda; [wiersz 31](../src/pymoo_gui/problems/constrex.py#L31).

### `src/pymoo_gui/problems/discrete.py`

- `ZDT5Problem.__init__(self, blocks: int=11, block_size: int=5, normalize: bool=True)` — metoda; [wiersz 14](../src/pymoo_gui/problems/discrete.py#L14).
- `ZDT5Problem._evaluate(self, X, out, *args, **kwargs)` — metoda; [wiersz 28](../src/pymoo_gui/problems/discrete.py#L28).
- `ZDT5Problem._calc_pareto_front(self, n_pareto_points: int=31)` — metoda; [wiersz 42](../src/pymoo_gui/problems/discrete.py#L42).
- `IntegerPortfolioProblem.__init__(self, n_var: int=8, upper: int=10, budget: int=30)` — metoda; [wiersz 57](../src/pymoo_gui/problems/discrete.py#L57).
- `IntegerPortfolioProblem._evaluate(self, X, out, *args, **kwargs)` — metoda; [wiersz 61](../src/pymoo_gui/problems/discrete.py#L61).
- `MixedDesignProblem.__init__(self)` — metoda; [wiersz 75](../src/pymoo_gui/problems/discrete.py#L75).
- `MixedDesignProblem.repair(self, X: np.ndarray) -> np.ndarray` — metoda; [wiersz 78](../src/pymoo_gui/problems/discrete.py#L78).
- `MixedDesignProblem._evaluate(self, X, out, *args, **kwargs)` — metoda; [wiersz 84](../src/pymoo_gui/problems/discrete.py#L84).

### `src/pymoo_gui/problems/dynamic.py`

- `DynamicDFProblem.__init__(self, variant: int, n_var: int=10, change_period: int=20, severity: int=10)` — metoda; [wiersz 15](../src/pymoo_gui/problems/dynamic.py#L15).
- `DynamicDFProblem.advance_time(self, generation: int) -> bool` — metoda; [wiersz 34](../src/pymoo_gui/problems/dynamic.py#L34).
- `DynamicDFProblem._evaluate(self, X, out, *args, **kwargs)` — metoda; [wiersz 40](../src/pymoo_gui/problems/dynamic.py#L40).
- `DynamicDFProblem._calc_pareto_front(self, n_pareto_points: int=200)` — metoda; [wiersz 90](../src/pymoo_gui/problems/dynamic.py#L90).

### `src/pymoo_gui/problems/empty_benchmark_template.py`

- `EmptyBenchmarkTemplate.__init__(self, n_var: int=10, n_obj: int=2, lower_bound: float=-1.0, upper_bound: float=1.0) -> None` — metoda; [wiersz 26](../src/pymoo_gui/problems/empty_benchmark_template.py#L26).
- `EmptyBenchmarkTemplate._evaluate(self, X, out, *args, **kwargs) -> None` — metoda; [wiersz 61](../src/pymoo_gui/problems/empty_benchmark_template.py#L61).
- `empty_benchmark_known_pf(problem: EmptyBenchmarkTemplate, n_points: int=200) -> Optional[np.ndarray]` — funkcja modułowa; [wiersz 89](../src/pymoo_gui/problems/empty_benchmark_template.py#L89).
- `make_empty_benchmark_template(n_var: int=10, n_obj: int=2, lower_bound: float=-1.0, upper_bound: float=1.0) -> EmptyBenchmarkTemplate` — funkcja modułowa; [wiersz 104](../src/pymoo_gui/problems/empty_benchmark_template.py#L104).

### `src/pymoo_gui/problems/extended_continuous.py`

- `simplex_lattice(n_obj: int, partitions: int=40) -> np.ndarray` — funkcja modułowa; [wiersz 10](../src/pymoo_gui/problems/extended_continuous.py#L10).
- `simplex_lattice.visit(prefix: list[int], left: int, dims: int) -> None` — funkcja zagnieżdżona; [wiersz 12](../src/pymoo_gui/problems/extended_continuous.py#L12).
- `LocalDTLZProblem.__init__(self, variant: int, n_var: int=12, n_obj: int=3, alpha: float=100.0)` — metoda; [wiersz 27](../src/pymoo_gui/problems/extended_continuous.py#L27).
- `LocalDTLZProblem.distance(self, X: np.ndarray) -> np.ndarray` — metoda; [wiersz 36](../src/pymoo_gui/problems/extended_continuous.py#L36).
- `LocalDTLZProblem._evaluate(self, X, out, *args, **kwargs)` — metoda; [wiersz 42](../src/pymoo_gui/problems/extended_continuous.py#L42).
- `LocalDTLZProblem._calc_pareto_front(self, partitions: int=40)` — metoda; [wiersz 57](../src/pymoo_gui/problems/extended_continuous.py#L57).
- `ConstrainedDTLZProblem.__init__(self, kind: str, base: int, n_var: int=12, n_obj: int=3)` — metoda; [wiersz 67](../src/pymoo_gui/problems/extended_continuous.py#L67).
- `ConstrainedDTLZProblem._evaluate(self, X, out, *args, **kwargs)` — metoda; [wiersz 76](../src/pymoo_gui/problems/extended_continuous.py#L76).
- `ConstrainedDTLZProblem._calc_pareto_front(self, n_points: int=12000)` — metoda; [wiersz 108](../src/pymoo_gui/problems/extended_continuous.py#L108).
- `DASCMOPProblem.__init__(self, variant: int, difficulty: int=1)` — metoda; [wiersz 131](../src/pymoo_gui/problems/extended_continuous.py#L131).
- `DASCMOPProblem._distance(self, X)` — metoda; [wiersz 138](../src/pymoo_gui/problems/extended_continuous.py#L138).
- `DASCMOPProblem._constraints2(self, X, F, g)` — metoda; [wiersz 147](../src/pymoo_gui/problems/extended_continuous.py#L147).
- `DASCMOPProblem._constraints3(self, X, F, g)` — metoda; [wiersz 156](../src/pymoo_gui/problems/extended_continuous.py#L156).
- `DASCMOPProblem._evaluate(self, X, out, *args, **kwargs)` — metoda; [wiersz 165](../src/pymoo_gui/problems/extended_continuous.py#L165).
- `DASCMOPProblem._calc_pareto_front(self, n_points: int=4000)` — metoda; [wiersz 178](../src/pymoo_gui/problems/extended_continuous.py#L178).
- `MMF1Problem.__init__(self)` — metoda; [wiersz 197](../src/pymoo_gui/problems/extended_continuous.py#L197).
- `MMF1Problem._evaluate(self, X, out, *args, **kwargs)` — metoda; [wiersz 200](../src/pymoo_gui/problems/extended_continuous.py#L200).
- `MMF1Problem._calc_pareto_front(self, n_pareto_points: int=500)` — metoda; [wiersz 204](../src/pymoo_gui/problems/extended_continuous.py#L204).
- `MMF1Problem.pareto_set(self, n_points: int=500)` — metoda; [wiersz 207](../src/pymoo_gui/problems/extended_continuous.py#L207).

### `src/pymoo_gui/problems/fonseca.py`

- `FonsecaProblem.__init__(self, n_var: int=3)` — metoda; [wiersz 24](../src/pymoo_gui/problems/fonseca.py#L24).
- `FonsecaProblem._evaluate(self, X, out, *args, **kwargs)` — metoda; [wiersz 35](../src/pymoo_gui/problems/fonseca.py#L35).

### `src/pymoo_gui/problems/golinski.py`

- `GolinskiProblem.__init__(self)` — metoda; [wiersz 22](../src/pymoo_gui/problems/golinski.py#L22).
- `GolinskiProblem._evaluate(self, X, out, *args, **kwargs)` — metoda; [wiersz 31](../src/pymoo_gui/problems/golinski.py#L31).

### `src/pymoo_gui/problems/kursawe.py`

- `KursaweProblem.__init__(self, n_var: int=3)` — metoda; [wiersz 20](../src/pymoo_gui/problems/kursawe.py#L20).
- `KursaweProblem._evaluate(self, X, out, *args, **kwargs)` — metoda; [wiersz 30](../src/pymoo_gui/problems/kursawe.py#L30).

### `src/pymoo_gui/problems/lz09.py`

- `LZ09Problem.__init__(self, n_var: int, n_obj: int, ptype: int, dtype: int, ltype: int)` — metoda; [wiersz 23](../src/pymoo_gui/problems/lz09.py#L23).
- `LZ09Problem._ps_func2(self, x: float, t1: float, dim: int, curve_type: int, css: int) -> float` — metoda; [wiersz 35](../src/pymoo_gui/problems/lz09.py#L35).
- `LZ09Problem._ps_func3(self, x: float, t1: float, t2: float, dim: int, curve_type: int) -> float` — metoda; [wiersz 82](../src/pymoo_gui/problems/lz09.py#L82).
- `LZ09Problem._alpha_func(self, values: list[float], dim: int, pf_type: int) -> list[float]` — metoda; [wiersz 95](../src/pymoo_gui/problems/lz09.py#L95).
- `LZ09Problem._beta_func(self, values: list[float], distance_type: int) -> float` — metoda; [wiersz 129](../src/pymoo_gui/problems/lz09.py#L129).
- `LZ09Problem.objective(self, values: list[float]) -> list[float]` — metoda; [wiersz 154](../src/pymoo_gui/problems/lz09.py#L154).
- `LZ09Problem._evaluate(self, X, out, *args, **kwargs)` — metoda; [wiersz 209](../src/pymoo_gui/problems/lz09.py#L209).
- `LZ09F1Problem.__init__(self, n_var: int=10)` — metoda; [wiersz 214](../src/pymoo_gui/problems/lz09.py#L214).
- `LZ09F2Problem.__init__(self, n_var: int=30)` — metoda; [wiersz 219](../src/pymoo_gui/problems/lz09.py#L219).
- `LZ09F3Problem.__init__(self, n_var: int=30)` — metoda; [wiersz 224](../src/pymoo_gui/problems/lz09.py#L224).
- `LZ09F4Problem.__init__(self, n_var: int=30)` — metoda; [wiersz 229](../src/pymoo_gui/problems/lz09.py#L229).
- `LZ09F5Problem.__init__(self, n_var: int=30)` — metoda; [wiersz 234](../src/pymoo_gui/problems/lz09.py#L234).
- `LZ09F6Problem.__init__(self, n_var: int=10)` — metoda; [wiersz 239](../src/pymoo_gui/problems/lz09.py#L239).
- `LZ09F7Problem.__init__(self, n_var: int=10)` — metoda; [wiersz 244](../src/pymoo_gui/problems/lz09.py#L244).
- `LZ09F8Problem.__init__(self, n_var: int=10)` — metoda; [wiersz 249](../src/pymoo_gui/problems/lz09.py#L249).
- `LZ09F9Problem.__init__(self, n_var: int=30)` — metoda; [wiersz 254](../src/pymoo_gui/problems/lz09.py#L254).

### `src/pymoo_gui/problems/mw.py`

- `get_ref_dirs(n_obj: int) -> np.ndarray` — funkcja modułowa; [wiersz 13](../src/pymoo_gui/problems/mw.py#L13).
- `MW.__init__(self, n_var: int, n_obj: int, n_ieq_constr: int, **kwargs) -> None` — metoda; [wiersz 20](../src/pymoo_gui/problems/mw.py#L20).
- `MW.LA1(A: float, B: float, C: float, D: float, theta: np.ndarray) -> np.ndarray` — metoda; [wiersz 30](../src/pymoo_gui/problems/mw.py#L30).
- `MW.LA2(A: float, B: float, C: float, D: float, theta: np.ndarray) -> np.ndarray` — metoda; [wiersz 34](../src/pymoo_gui/problems/mw.py#L34).
- `MW.LA3(A: float, B: float, C: float, D: float, theta: np.ndarray) -> np.ndarray` — metoda; [wiersz 38](../src/pymoo_gui/problems/mw.py#L38).
- `MW.g1(self, X: np.ndarray) -> np.ndarray` — metoda; [wiersz 41](../src/pymoo_gui/problems/mw.py#L41).
- `MW.g2(self, X: np.ndarray) -> np.ndarray` — metoda; [wiersz 52](../src/pymoo_gui/problems/mw.py#L52).
- `MW.g3(self, X: np.ndarray) -> np.ndarray` — metoda; [wiersz 64](../src/pymoo_gui/problems/mw.py#L64).
- `MW1.__init__(self, n_var: int=15, **kwargs) -> None` — metoda; [wiersz 76](../src/pymoo_gui/problems/mw.py#L76).
- `MW1._evaluate(self, X: np.ndarray, out: dict, *args, **kwargs) -> None` — metoda; [wiersz 79](../src/pymoo_gui/problems/mw.py#L79).
- `MW1._calc_pareto_front(self, ref_dirs: np.ndarray | None=None) -> np.ndarray` — metoda; [wiersz 93](../src/pymoo_gui/problems/mw.py#L93).
- `MW2.__init__(self, n_var: int=15, **kwargs) -> None` — metoda; [wiersz 107](../src/pymoo_gui/problems/mw.py#L107).
- `MW2._evaluate(self, X: np.ndarray, out: dict, *args, **kwargs) -> None` — metoda; [wiersz 110](../src/pymoo_gui/problems/mw.py#L110).
- `MW2._calc_pareto_front(self, ref_dirs: np.ndarray | None=None) -> np.ndarray` — metoda; [wiersz 124](../src/pymoo_gui/problems/mw.py#L124).
- `MW3.__init__(self, n_var: int=15, **kwargs) -> None` — metoda; [wiersz 135](../src/pymoo_gui/problems/mw.py#L135).
- `MW3._evaluate(self, X: np.ndarray, out: dict, *args, **kwargs) -> None` — metoda; [wiersz 138](../src/pymoo_gui/problems/mw.py#L138).
- `MW3._calc_pareto_front(self, ref_dirs: np.ndarray | None=None) -> np.ndarray` — metoda; [wiersz 158](../src/pymoo_gui/problems/mw.py#L158).
- `MW4.__init__(self, n_var: int | None=None, n_obj: int=3, **kwargs) -> None` — metoda; [wiersz 183](../src/pymoo_gui/problems/mw.py#L183).
- `MW4._evaluate(self, X: np.ndarray, out: dict, *args, **kwargs) -> None` — metoda; [wiersz 188](../src/pymoo_gui/problems/mw.py#L188).
- `MW4._calc_pareto_front(self, ref_dirs: np.ndarray | None=None) -> np.ndarray` — metoda; [wiersz 202](../src/pymoo_gui/problems/mw.py#L202).
- `MW5.__init__(self, n_var: int=15, **kwargs) -> None` — metoda; [wiersz 212](../src/pymoo_gui/problems/mw.py#L212).
- `MW5._evaluate(self, X: np.ndarray, out: dict, *args, **kwargs) -> None` — metoda; [wiersz 215](../src/pymoo_gui/problems/mw.py#L215).
- `MW5._calc_pareto_front(self, **kwargs) -> np.ndarray` — metoda; [wiersz 230](../src/pymoo_gui/problems/mw.py#L230).
- `MW6.__init__(self, n_var: int=15, **kwargs) -> None` — metoda; [wiersz 235](../src/pymoo_gui/problems/mw.py#L235).
- `MW6._evaluate(self, X: np.ndarray, out: dict, *args, **kwargs) -> None` — metoda; [wiersz 238](../src/pymoo_gui/problems/mw.py#L238).
- `MW6._calc_pareto_front(self, ref_dirs: np.ndarray | None=None) -> np.ndarray` — metoda; [wiersz 254](../src/pymoo_gui/problems/mw.py#L254).
- `MW7.__init__(self, n_var: int=15, **kwargs) -> None` — metoda; [wiersz 272](../src/pymoo_gui/problems/mw.py#L272).
- `MW7._evaluate(self, X: np.ndarray, out: dict, *args, **kwargs) -> None` — metoda; [wiersz 275](../src/pymoo_gui/problems/mw.py#L275).
- `MW7._calc_pareto_front(self, **kwargs) -> np.ndarray` — metoda; [wiersz 292](../src/pymoo_gui/problems/mw.py#L292).
- `MW8.__init__(self, n_var: int | None=None, n_obj: int=3, **kwargs) -> None` — metoda; [wiersz 297](../src/pymoo_gui/problems/mw.py#L297).
- `MW8._evaluate(self, X: np.ndarray, out: dict, *args, **kwargs) -> None` — metoda; [wiersz 302](../src/pymoo_gui/problems/mw.py#L302).
- `MW8._calc_pareto_front(self, ref_dirs: np.ndarray | None=None) -> np.ndarray` — metoda; [wiersz 320](../src/pymoo_gui/problems/mw.py#L320).
- `MW9.__init__(self, n_var: int=15, **kwargs) -> None` — metoda; [wiersz 333](../src/pymoo_gui/problems/mw.py#L333).
- `MW9._evaluate(self, X: np.ndarray, out: dict, *args, **kwargs) -> None` — metoda; [wiersz 336](../src/pymoo_gui/problems/mw.py#L336).
- `MW9._calc_pareto_front(self, **kwargs) -> np.ndarray` — metoda; [wiersz 349](../src/pymoo_gui/problems/mw.py#L349).
- `MW10.__init__(self, n_var: int=15, **kwargs) -> None` — metoda; [wiersz 354](../src/pymoo_gui/problems/mw.py#L354).
- `MW10._evaluate(self, X: np.ndarray, out: dict, *args, **kwargs) -> None` — metoda; [wiersz 357](../src/pymoo_gui/problems/mw.py#L357).
- `MW10._calc_pareto_front(self, **kwargs) -> np.ndarray` — metoda; [wiersz 368](../src/pymoo_gui/problems/mw.py#L368).
- `MW11.__init__(self, n_var: int=15, **kwargs) -> None` — metoda; [wiersz 373](../src/pymoo_gui/problems/mw.py#L373).
- `MW11._evaluate(self, X: np.ndarray, out: dict, *args, **kwargs) -> None` — metoda; [wiersz 376](../src/pymoo_gui/problems/mw.py#L376).
- `MW11._calc_pareto_front(self, **kwargs) -> np.ndarray` — metoda; [wiersz 388](../src/pymoo_gui/problems/mw.py#L388).
- `MW12.__init__(self, n_var: int=15, **kwargs) -> None` — metoda; [wiersz 393](../src/pymoo_gui/problems/mw.py#L393).
- `MW12._evaluate(self, X: np.ndarray, out: dict, *args, **kwargs) -> None` — metoda; [wiersz 396](../src/pymoo_gui/problems/mw.py#L396).
- `MW12._calc_pareto_front(self, ref_dirs: np.ndarray | None=None) -> np.ndarray` — metoda; [wiersz 412](../src/pymoo_gui/problems/mw.py#L412).
- `MW13.__init__(self, n_var: int=15, **kwargs) -> None` — metoda; [wiersz 448](../src/pymoo_gui/problems/mw.py#L448).
- `MW13._evaluate(self, X: np.ndarray, out: dict, *args, **kwargs) -> None` — metoda; [wiersz 451](../src/pymoo_gui/problems/mw.py#L451).
- `MW13._calc_pareto_front(self, **kwargs) -> np.ndarray` — metoda; [wiersz 467](../src/pymoo_gui/problems/mw.py#L467).
- `MW14.__init__(self, n_var: int | None=None, n_obj: int=3, **kwargs) -> None` — metoda; [wiersz 472](../src/pymoo_gui/problems/mw.py#L472).
- `MW14._evaluate(self, X: np.ndarray, out: dict, *args, **kwargs) -> None` — metoda; [wiersz 477](../src/pymoo_gui/problems/mw.py#L477).
- `MW14._calc_pareto_front(self, **kwargs) -> np.ndarray` — metoda; [wiersz 490](../src/pymoo_gui/problems/mw.py#L490).

### `src/pymoo_gui/problems/osyczka2.py`

- `Osyczka2Problem.__init__(self)` — metoda; [wiersz 22](../src/pymoo_gui/problems/osyczka2.py#L22).
- `Osyczka2Problem._evaluate(self, X, out, *args, **kwargs)` — metoda; [wiersz 31](../src/pymoo_gui/problems/osyczka2.py#L31).

### `src/pymoo_gui/problems/registry.py`

- `_problem_entry(label: str, factory: Any, form_fields: Dict[str, Dict[str, Any]], form_note: str, known_pf_factory: Any=None, capabilities: Dict[str, Any] | None=None) -> Dict[str, Any]` — funkcja modułowa; [wiersz 72](../src/pymoo_gui/problems/registry.py#L72).
- `_normalize_pf(values: Any, expected_n_obj: int | None=None) -> np.ndarray | None` — funkcja modułowa; [wiersz 94](../src/pymoo_gui/problems/registry.py#L94).
- `_load_pf_file(filename: str, expected_n_obj: int | None=None) -> np.ndarray | None` — funkcja modułowa; [wiersz 120](../src/pymoo_gui/problems/registry.py#L120).
- `_pf_file_loader(filename: str, expected_n_obj: int)` — funkcja modułowa; [wiersz 132](../src/pymoo_gui/problems/registry.py#L132).
- `_zdt_known_pf(problem: Any) -> np.ndarray | None` — funkcja modułowa; [wiersz 137](../src/pymoo_gui/problems/registry.py#L137).
- `_dtlz_reference_directions(n_obj: int, target_points: int) -> np.ndarray` — funkcja modułowa; [wiersz 149](../src/pymoo_gui/problems/registry.py#L149).
- `_dtlz_degenerate_known_pf(n_obj: int, n_points: int=1000) -> np.ndarray` — funkcja modułowa; [wiersz 158](../src/pymoo_gui/problems/registry.py#L158).
- `_dtlz7_known_pf(n_obj: int, target_points: int=2000) -> np.ndarray` — funkcja modułowa; [wiersz 177](../src/pymoo_gui/problems/registry.py#L177).
- `_dtlz_known_pf(problem: Any, target_points: int=2000) -> np.ndarray | None` — funkcja modułowa; [wiersz 197](../src/pymoo_gui/problems/registry.py#L197).
- `_readonly_n_obj_field(label: str, n_obj: int) -> Dict[str, Any]` — funkcja modułowa; [wiersz 220](../src/pymoo_gui/problems/registry.py#L220).
- `_n_var_field(label: str, default: int, minimum: int=1) -> Dict[str, Any]` — funkcja modułowa; [wiersz 229](../src/pymoo_gui/problems/registry.py#L229).
- `_zdt_entry(name: str, default_n_var: int) -> Dict[str, Any]` — funkcja modułowa; [wiersz 238](../src/pymoo_gui/problems/registry.py#L238).
- `_dtlz_entry(name: str, default_n_var: int, default_n_obj: int=3) -> Dict[str, Any]` — funkcja modułowa; [wiersz 253](../src/pymoo_gui/problems/registry.py#L253).
- `_local_entry(key_label: str, factory: Any, n_obj: int, pf_filename: str, n_var_default: int | None=None, n_var_minimum: int=1, form_note: str | None=None) -> Dict[str, Any]` — funkcja modułowa; [wiersz 277](../src/pymoo_gui/problems/registry.py#L277).
- `_wfg_entry(problem_name: str, n_obj: int) -> Dict[str, Any]` — funkcja modułowa; [wiersz 301](../src/pymoo_gui/problems/registry.py#L301).
- `_wfg_known_pf(problem: Any, filename: str, n_obj: int) -> np.ndarray | None` — funkcja modułowa; [wiersz 330](../src/pymoo_gui/problems/registry.py#L330).
- `make_kursawe(n_var: int=3) -> KursaweProblem` — funkcja modułowa; [wiersz 344](../src/pymoo_gui/problems/registry.py#L344).
- `make_schaffer() -> SchafferProblem` — funkcja modułowa; [wiersz 348](../src/pymoo_gui/problems/registry.py#L348).
- `make_zdt5()` — funkcja modułowa; [wiersz 352](../src/pymoo_gui/problems/registry.py#L352).
- `_analytical_pf(problem: Any) -> np.ndarray | None` — funkcja modułowa; [wiersz 506](../src/pymoo_gui/problems/registry.py#L506).
- `_mw_factory(n_var=15, n_obj=default_n_obj, problem_cls=cls)` — funkcja modułowa; [wiersz 619](../src/pymoo_gui/problems/registry.py#L619).
- `lambda` — wyrażenie anonimowe; [wiersz 134](../src/pymoo_gui/problems/registry.py#L134).
- `lambda` — wyrażenie anonimowe; [wiersz 243](../src/pymoo_gui/problems/registry.py#L243).
- `lambda` — wyrażenie anonimowe; [wiersz 258](../src/pymoo_gui/problems/registry.py#L258).
- `lambda` — wyrażenie anonimowe; [wiersz 307](../src/pymoo_gui/problems/registry.py#L307).
- `lambda` — wyrażenie anonimowe; [wiersz 322](../src/pymoo_gui/problems/registry.py#L322).
- `lambda` — wyrażenie anonimowe; [wiersz 376](../src/pymoo_gui/problems/registry.py#L376).
- `lambda` — wyrażenie anonimowe; [wiersz 398](../src/pymoo_gui/problems/registry.py#L398).
- `lambda` — wyrażenie anonimowe; [wiersz 414](../src/pymoo_gui/problems/registry.py#L414).
- `lambda` — wyrażenie anonimowe; [wiersz 421](../src/pymoo_gui/problems/registry.py#L421).
- `lambda` — wyrażenie anonimowe; [wiersz 428](../src/pymoo_gui/problems/registry.py#L428).
- `lambda` — wyrażenie anonimowe; [wiersz 435](../src/pymoo_gui/problems/registry.py#L435).
- `lambda` — wyrażenie anonimowe; [wiersz 442](../src/pymoo_gui/problems/registry.py#L442).
- `lambda` — wyrażenie anonimowe; [wiersz 449](../src/pymoo_gui/problems/registry.py#L449).
- `lambda` — wyrażenie anonimowe; [wiersz 456](../src/pymoo_gui/problems/registry.py#L456).
- `lambda` — wyrażenie anonimowe; [wiersz 463](../src/pymoo_gui/problems/registry.py#L463).
- `lambda` — wyrażenie anonimowe; [wiersz 470](../src/pymoo_gui/problems/registry.py#L470).
- `lambda` — wyrażenie anonimowe; [wiersz 475](../src/pymoo_gui/problems/registry.py#L475).
- `lambda` — wyrażenie anonimowe; [wiersz 476](../src/pymoo_gui/problems/registry.py#L476).
- `lambda` — wyrażenie anonimowe; [wiersz 477](../src/pymoo_gui/problems/registry.py#L477).
- `lambda` — wyrażenie anonimowe; [wiersz 478](../src/pymoo_gui/problems/registry.py#L478).
- `lambda` — wyrażenie anonimowe; [wiersz 479](../src/pymoo_gui/problems/registry.py#L479).
- `lambda` — wyrażenie anonimowe; [wiersz 480](../src/pymoo_gui/problems/registry.py#L480).
- `lambda` — wyrażenie anonimowe; [wiersz 481](../src/pymoo_gui/problems/registry.py#L481).
- `lambda` — wyrażenie anonimowe; [wiersz 482](../src/pymoo_gui/problems/registry.py#L482).
- `lambda` — wyrażenie anonimowe; [wiersz 483](../src/pymoo_gui/problems/registry.py#L483).
- `lambda` — wyrażenie anonimowe; [wiersz 484](../src/pymoo_gui/problems/registry.py#L484).
- `lambda` — wyrażenie anonimowe; [wiersz 518](../src/pymoo_gui/problems/registry.py#L518).
- `lambda` — wyrażenie anonimowe; [wiersz 543](../src/pymoo_gui/problems/registry.py#L543).
- `lambda` — wyrażenie anonimowe; [wiersz 559](../src/pymoo_gui/problems/registry.py#L559).
- `lambda` — wyrażenie anonimowe; [wiersz 585](../src/pymoo_gui/problems/registry.py#L585).

### `src/pymoo_gui/problems/schaffer.py`

- `SchafferProblem.__init__(self)` — metoda; [wiersz 20](../src/pymoo_gui/problems/schaffer.py#L20).
- `SchafferProblem._evaluate(self, X, out, *args, **kwargs)` — metoda; [wiersz 30](../src/pymoo_gui/problems/schaffer.py#L30).

### `src/pymoo_gui/problems/srinivas.py`

- `SrinivasProblem.__init__(self)` — metoda; [wiersz 22](../src/pymoo_gui/problems/srinivas.py#L22).
- `SrinivasProblem._evaluate(self, X, out, *args, **kwargs)` — metoda; [wiersz 31](../src/pymoo_gui/problems/srinivas.py#L31).

### `src/pymoo_gui/problems/tanaka.py`

- `TanakaProblem.__init__(self)` — metoda; [wiersz 22](../src/pymoo_gui/problems/tanaka.py#L22).
- `TanakaProblem._evaluate(self, X, out, *args, **kwargs)` — metoda; [wiersz 31](../src/pymoo_gui/problems/tanaka.py#L31).

### `src/pymoo_gui/problems/uf.py`

- `_platypus_solution_class() -> Any` — funkcja modułowa; [wiersz 21](../src/pymoo_gui/problems/uf.py#L21).
- `_platypus_uf_class(name: str) -> Type[Any]` — funkcja modułowa; [wiersz 29](../src/pymoo_gui/problems/uf.py#L29).
- `PlatypusUFProblem.__init__(self, uf_name: str, n_var: int=30)` — metoda; [wiersz 51](../src/pymoo_gui/problems/uf.py#L51).
- `PlatypusUFProblem._evaluate_one(self, values: np.ndarray) -> tuple[list[float], list[float]]` — metoda; [wiersz 71](../src/pymoo_gui/problems/uf.py#L71).
- `PlatypusUFProblem._evaluate(self, X, out, *args, **kwargs)` — metoda; [wiersz 79](../src/pymoo_gui/problems/uf.py#L79).
- `UF1Problem.__init__(self, n_var: int=30)` — metoda; [wiersz 95](../src/pymoo_gui/problems/uf.py#L95).
- `UF2Problem.__init__(self, n_var: int=30)` — metoda; [wiersz 100](../src/pymoo_gui/problems/uf.py#L100).
- `UF3Problem.__init__(self, n_var: int=30)` — metoda; [wiersz 105](../src/pymoo_gui/problems/uf.py#L105).
- `UF4Problem.__init__(self, n_var: int=30)` — metoda; [wiersz 110](../src/pymoo_gui/problems/uf.py#L110).
- `UF5Problem.__init__(self, n_var: int=30)` — metoda; [wiersz 115](../src/pymoo_gui/problems/uf.py#L115).
- `UF6Problem.__init__(self, n_var: int=30)` — metoda; [wiersz 120](../src/pymoo_gui/problems/uf.py#L120).
- `UF7Problem.__init__(self, n_var: int=30)` — metoda; [wiersz 125](../src/pymoo_gui/problems/uf.py#L125).
- `UF8Problem.__init__(self, n_var: int=30)` — metoda; [wiersz 130](../src/pymoo_gui/problems/uf.py#L130).
- `UF9Problem.__init__(self, n_var: int=30)` — metoda; [wiersz 135](../src/pymoo_gui/problems/uf.py#L135).
- `UF10Problem.__init__(self, n_var: int=30)` — metoda; [wiersz 140](../src/pymoo_gui/problems/uf.py#L140).

### `src/pymoo_gui/problems/viennet2.py`

- `Viennet2Problem.__init__(self)` — metoda; [wiersz 22](../src/pymoo_gui/problems/viennet2.py#L22).
- `Viennet2Problem._evaluate(self, X, out, *args, **kwargs)` — metoda; [wiersz 31](../src/pymoo_gui/problems/viennet2.py#L31).

### `src/pymoo_gui/problems/viennet3.py`

- `Viennet3Problem.__init__(self)` — metoda; [wiersz 21](../src/pymoo_gui/problems/viennet3.py#L21).
- `Viennet3Problem._evaluate(self, X, out, *args, **kwargs)` — metoda; [wiersz 30](../src/pymoo_gui/problems/viennet3.py#L30).

### `src/pymoo_gui/problems/water.py`

- `WaterProblem.__init__(self)` — metoda; [wiersz 21](../src/pymoo_gui/problems/water.py#L21).
- `WaterProblem._evaluate(self, X, out, *args, **kwargs)` — metoda; [wiersz 30](../src/pymoo_gui/problems/water.py#L30).

### `src/pymoo_gui/problems/wfg.py`

- `default_wfg_n_var(n_obj: int) -> int` — funkcja modułowa; [wiersz 17](../src/pymoo_gui/problems/wfg.py#L17).
- `make_wfg_problem(problem_name: str, n_obj: int, n_var: int | None=None)` — funkcja modułowa; [wiersz 23](../src/pymoo_gui/problems/wfg.py#L23).

### `src/pymoo_gui/runtime.py`

- `results_root() -> Path` — funkcja modułowa; [wiersz 7](../src/pymoo_gui/runtime.py#L7).

### `src/pymoo_gui/viz/__init__.py`

Brak deklaracji funkcji i wyrażeń `lambda`.

### `src/pymoo_gui/viz/metric_trajectories.py`

- `PlainDecimalAxisItem.tickStrings(self, values, scale, spacing)` — metoda; [wiersz 18](../src/pymoo_gui/viz/metric_trajectories.py#L18).
- `MetricTrajectoriesWidget.__init__(self, parent=None) -> None` — metoda; [wiersz 46](../src/pymoo_gui/viz/metric_trajectories.py#L46).
- `MetricTrajectoriesWidget.reset(self, algorithm_name: Optional[str]=None, problem_name: Optional[str]=None) -> None` — metoda; [wiersz 114](../src/pymoo_gui/viz/metric_trajectories.py#L114).
- `MetricTrajectoriesWidget.is_metric_visible(self, metric_key: str) -> bool` — metoda; [wiersz 136](../src/pymoo_gui/viz/metric_trajectories.py#L136).
- `MetricTrajectoriesWidget.append_payload(self, payload: Mapping[str, Any]) -> None` — metoda; [wiersz 140](../src/pymoo_gui/viz/metric_trajectories.py#L140).
- `MetricTrajectoriesWidget.history(self) -> dict[str, list[tuple[int, float]]]` — metoda; [wiersz 168](../src/pymoo_gui/viz/metric_trajectories.py#L168).

### `src/pymoo_gui/viz/pareto_dialogs.py`

- `_compute_stable_limits(ref_arr: Optional[np.ndarray], front_arr: Optional[np.ndarray], pop_arr: Optional[np.ndarray]) -> Optional[Tuple[np.ndarray, np.ndarray]]` — funkcja modułowa; [wiersz 30](../src/pymoo_gui/viz/pareto_dialogs.py#L30).
- `_UniformLegendSample.paint(self, painter, *args)` — metoda; [wiersz 68](../src/pymoo_gui/viz/pareto_dialogs.py#L68).
- `PyQtGraphParetoDialog.__init__(self, ideal_front: np.ndarray, parent=None, axis_labels: Optional[Sequence[str]]=None, title: Optional[str]=None, point_label: str='Population', front_label: str='Nondominated solutions', ref_label: str='Reference PF')` — metoda; [wiersz 80](../src/pymoo_gui/viz/pareto_dialogs.py#L80).
- `PyQtGraphParetoDialog._set_plot_title(self, title: str) -> None` — metoda; [wiersz 170](../src/pymoo_gui/viz/pareto_dialogs.py#L170).
- `PyQtGraphParetoDialog.set_grid(self, visible: bool, spacing: float=0.0) -> None` — metoda; [wiersz 177](../src/pymoo_gui/viz/pareto_dialogs.py#L177).
- `PyQtGraphParetoDialog.export_png(self, path: str) -> None` — metoda; [wiersz 183](../src/pymoo_gui/viz/pareto_dialogs.py#L183).
- `PyQtGraphParetoDialog.set_auto_scale(self, enabled: bool) -> None` — metoda; [wiersz 190](../src/pymoo_gui/viz/pareto_dialogs.py#L190).
- `PyQtGraphParetoDialog.reset_view_limits(self) -> None` — metoda; [wiersz 194](../src/pymoo_gui/viz/pareto_dialogs.py#L194).
- `PyQtGraphParetoDialog._reference_limits_signature(self, ref_arr: Optional[np.ndarray]) -> Optional[Tuple[int, float, float, float, float]]` — metoda; [wiersz 200](../src/pymoo_gui/viz/pareto_dialogs.py#L200).
- `PyQtGraphParetoDialog._set_fixed_limits(self, mins: np.ndarray, maxs: np.ndarray) -> None` — metoda; [wiersz 212](../src/pymoo_gui/viz/pareto_dialogs.py#L212).
- `PyQtGraphParetoDialog._apply_fixed_limits(self, ref_arr: Optional[np.ndarray], front_arr: Optional[np.ndarray], pop_arr: Optional[np.ndarray]) -> None` — metoda; [wiersz 221](../src/pymoo_gui/viz/pareto_dialogs.py#L221).
- `PyQtGraphParetoDialog.get_axis_limits(self) -> Optional[Tuple[float, float, float, float]]` — metoda; [wiersz 246](../src/pymoo_gui/viz/pareto_dialogs.py#L246).
- `PyQtGraphParetoDialog.update_points(self, pop_F: Optional[np.ndarray], front_F: Optional[np.ndarray], ref_F: Optional[np.ndarray], gen: Optional[int]=None) -> None` — metoda; [wiersz 256](../src/pymoo_gui/viz/pareto_dialogs.py#L256).
- `PyQtGraphParetoDialog.update_points._finite_rows(data: Optional[np.ndarray]) -> Optional[np.ndarray]` — funkcja zagnieżdżona; [wiersz 264](../src/pymoo_gui/viz/pareto_dialogs.py#L264).
- `PyQtGraphParetoDialog.update_points._as_2d(arr: Optional[np.ndarray]) -> Optional[np.ndarray]` — funkcja zagnieżdżona; [wiersz 271](../src/pymoo_gui/viz/pareto_dialogs.py#L271).
- `_MatplotlibPlotControls._add_legend(self) -> None` — metoda; [wiersz 309](../src/pymoo_gui/viz/pareto_dialogs.py#L309).
- `_MatplotlibPlotControls._style_axes(self) -> None` — metoda; [wiersz 322](../src/pymoo_gui/viz/pareto_dialogs.py#L322).
- `_MatplotlibPlotControls._plot_axes(self)` — metoda; [wiersz 332](../src/pymoo_gui/viz/pareto_dialogs.py#L332).
- `_MatplotlibPlotControls.set_grid(self, visible: bool, spacing: float=0.0) -> None` — metoda; [wiersz 338](../src/pymoo_gui/viz/pareto_dialogs.py#L338).
- `_MatplotlibPlotControls.export_png(self, path: str) -> None` — metoda; [wiersz 344](../src/pymoo_gui/viz/pareto_dialogs.py#L344).
- `MatplotlibParetoDialog.__init__(self, ideal_front: np.ndarray, parent=None, equal_aspect: bool=False, axis_labels: Optional[Sequence[str]]=None, title: Optional[str]=None, point_label: str='Population', front_label: str='Nondominated solutions', ref_label: str='Reference PF')` — metoda; [wiersz 351](../src/pymoo_gui/viz/pareto_dialogs.py#L351).
- `MatplotlibParetoDialog._apply_equal_aspect(self) -> None` — metoda; [wiersz 441](../src/pymoo_gui/viz/pareto_dialogs.py#L441).
- `MatplotlibParetoDialog.reset_view_limits(self) -> None` — metoda; [wiersz 448](../src/pymoo_gui/viz/pareto_dialogs.py#L448).
- `MatplotlibParetoDialog.update_points(self, pop_F: Optional[np.ndarray], front_F: Optional[np.ndarray], ref_F: Optional[np.ndarray], gen: Optional[int]=None) -> None` — metoda; [wiersz 452](../src/pymoo_gui/viz/pareto_dialogs.py#L452).
- `MatplotlibParetoDialog.update_points._finite_rows(data: Optional[np.ndarray]) -> Optional[np.ndarray]` — funkcja zagnieżdżona; [wiersz 460](../src/pymoo_gui/viz/pareto_dialogs.py#L460).
- `MatplotlibParetoDialog.update_points._as_dim(arr: Optional[np.ndarray]) -> Optional[np.ndarray]` — funkcja zagnieżdżona; [wiersz 467](../src/pymoo_gui/viz/pareto_dialogs.py#L467).
- `MatplotlibParetoDialog.set_auto_scale(self, enabled: bool) -> None` — metoda; [wiersz 568](../src/pymoo_gui/viz/pareto_dialogs.py#L568).
- `MatplotlibParetoDialog.get_axis_limits(self) -> Optional[Tuple[float, ...]]` — metoda; [wiersz 572](../src/pymoo_gui/viz/pareto_dialogs.py#L572).
- `OneDParetoDialog.__init__(self, ideal_front: np.ndarray, parent=None, axis_labels: Optional[Sequence[str]]=None, title: Optional[str]=None, point_label: str='Population', front_label: str='Nondominated solutions', ref_label: str='Reference PF')` — metoda; [wiersz 588](../src/pymoo_gui/viz/pareto_dialogs.py#L588).
- `OneDParetoDialog.set_auto_scale(self, enabled: bool) -> None` — metoda; [wiersz 644](../src/pymoo_gui/viz/pareto_dialogs.py#L644).
- `OneDParetoDialog.reset_view_limits(self) -> None` — metoda; [wiersz 648](../src/pymoo_gui/viz/pareto_dialogs.py#L648).
- `OneDParetoDialog.get_axis_limits(self) -> Optional[Tuple[float, float, float, float]]` — metoda; [wiersz 652](../src/pymoo_gui/viz/pareto_dialogs.py#L652).
- `OneDParetoDialog.update_points(self, pop_F: Optional[np.ndarray], front_F: Optional[np.ndarray], ref_F: Optional[np.ndarray], gen: Optional[int]=None) -> None` — metoda; [wiersz 661](../src/pymoo_gui/viz/pareto_dialogs.py#L661).
- `OneDParetoDialog.update_points._finite_rows(data: Optional[np.ndarray]) -> Optional[np.ndarray]` — funkcja zagnieżdżona; [wiersz 669](../src/pymoo_gui/viz/pareto_dialogs.py#L669).
- `OneDParetoDialog.update_points._as_1d(arr: Optional[np.ndarray]) -> Optional[np.ndarray]` — funkcja zagnieżdżona; [wiersz 676](../src/pymoo_gui/viz/pareto_dialogs.py#L676).
- `UnifiedParetoDialog.__init__(self, ideal_front: np.ndarray, parent=None, equal_aspect: bool=False, objective_names: Optional[Sequence[str]]=None)` — metoda; [wiersz 774](../src/pymoo_gui/viz/pareto_dialogs.py#L774).
- `UnifiedParetoDialog.show(self) -> None` — metoda; [wiersz 840](../src/pymoo_gui/viz/pareto_dialogs.py#L840).
- `UnifiedParetoDialog.set_auto_scale(self, enabled: bool) -> None` — metoda; [wiersz 844](../src/pymoo_gui/viz/pareto_dialogs.py#L844).
- `UnifiedParetoDialog.get_axis_limits(self) -> Optional[Tuple[float, ...]]` — metoda; [wiersz 849](../src/pymoo_gui/viz/pareto_dialogs.py#L849).
- `UnifiedParetoDialog.update_points(self, pop_F: Optional[np.ndarray], front_F: Optional[np.ndarray], ref_F: Optional[np.ndarray], gen: Optional[int]=None) -> None` — metoda; [wiersz 855](../src/pymoo_gui/viz/pareto_dialogs.py#L855).
- `UnifiedParetoDialog.update_points._reduce(arr: Optional[np.ndarray]) -> Optional[np.ndarray]` — funkcja zagnieżdżona; [wiersz 863](../src/pymoo_gui/viz/pareto_dialogs.py#L863).
- `UnifiedParetoDialog.__getattr__(self, name)` — metoda; [wiersz 879](../src/pymoo_gui/viz/pareto_dialogs.py#L879).
- `PyQtGraphParetoWidget.__init__(self, *args, **kwargs)` — metoda; [wiersz 887](../src/pymoo_gui/viz/pareto_dialogs.py#L887).
- `MatplotlibParetoWidget.__init__(self, *args, **kwargs)` — metoda; [wiersz 896](../src/pymoo_gui/viz/pareto_dialogs.py#L896).
- `OneDParetoWidget.__init__(self, *args, **kwargs)` — metoda; [wiersz 905](../src/pymoo_gui/viz/pareto_dialogs.py#L905).
- `UnifiedParetoWidget.__init__(self, ideal_front: np.ndarray, parent=None, equal_aspect: bool=False, objective_names: Optional[Sequence[str]]=None)` — metoda; [wiersz 915](../src/pymoo_gui/viz/pareto_dialogs.py#L915).
- `UnifiedParetoWidget.set_auto_scale(self, enabled: bool) -> None` — metoda; [wiersz 997](../src/pymoo_gui/viz/pareto_dialogs.py#L997).
- `UnifiedParetoWidget.set_show_population(self, enabled: bool) -> None` — metoda; [wiersz 1002](../src/pymoo_gui/viz/pareto_dialogs.py#L1002).
- `UnifiedParetoWidget.get_axis_limits(self) -> Optional[Tuple[float, ...]]` — metoda; [wiersz 1010](../src/pymoo_gui/viz/pareto_dialogs.py#L1010).
- `UnifiedParetoWidget._reduce_points(self, arr: Optional[np.ndarray]) -> Optional[np.ndarray]` — metoda; [wiersz 1016](../src/pymoo_gui/viz/pareto_dialogs.py#L1016).
- `UnifiedParetoWidget._snapshot_points(self, arr: Optional[np.ndarray]) -> Optional[np.ndarray]` — metoda; [wiersz 1027](../src/pymoo_gui/viz/pareto_dialogs.py#L1027).
- `UnifiedParetoWidget._shape_of(self, arr: Optional[np.ndarray]) -> Optional[Tuple[int, ...]]` — metoda; [wiersz 1039](../src/pymoo_gui/viz/pareto_dialogs.py#L1039).
- `UnifiedParetoWidget._render_points(self) -> None` — metoda; [wiersz 1043](../src/pymoo_gui/viz/pareto_dialogs.py#L1043).
- `UnifiedParetoWidget.render_snapshot(self) -> dict` — metoda; [wiersz 1055](../src/pymoo_gui/viz/pareto_dialogs.py#L1055).
- `UnifiedParetoWidget.update_points(self, pop_F: Optional[np.ndarray], front_F: Optional[np.ndarray], ref_F: Optional[np.ndarray], gen: Optional[int]=None) -> None` — metoda; [wiersz 1065](../src/pymoo_gui/viz/pareto_dialogs.py#L1065).
- `UnifiedParetoWidget.__getattr__(self, name)` — metoda; [wiersz 1079](../src/pymoo_gui/viz/pareto_dialogs.py#L1079).

### `tests/conftest.py`

Brak deklaracji funkcji i wyrażeń `lambda`.

### `tests/test_article_alignment_corrections.py`

- `_state(X: np.ndarray, F: np.ndarray, CV: np.ndarray) -> PopulationState` — funkcja modułowa; [wiersz 19](../tests/test_article_alignment_corrections.py#L19).
- `test_epsilon_moea_uses_population_and_archive_parents(monkeypatch) -> None` — funkcja modułowa; [wiersz 24](../tests/test_article_alignment_corrections.py#L24).
- `test_epsilon_moea_uses_population_and_archive_parents.fake_sbx(X, parent_pairs, *args, **kwargs)` — funkcja zagnieżdżona; [wiersz 40](../tests/test_article_alignment_corrections.py#L40).
- `test_gde3_has_no_pymoo_sorting_dependency() -> None` — funkcja modułowa; [wiersz 49](../tests/test_article_alignment_corrections.py#L49).
- `test_moead_external_archive_contains_only_nondominated_points() -> None` — funkcja modułowa; [wiersz 55](../tests/test_article_alignment_corrections.py#L55).
- `test_moead_iepsilon_initial_level_uses_descending_violation_order() -> None` — funkcja modułowa; [wiersz 63](../tests/test_article_alignment_corrections.py#L63).
- `test_rnsga3_projects_shrunken_lattice_around_aspiration_point() -> None` — funkcja modułowa; [wiersz 74](../tests/test_article_alignment_corrections.py#L74).
- `test_rvea_uses_actual_termination_horizon() -> None` — funkcja modułowa; [wiersz 83](../tests/test_article_alignment_corrections.py#L83).
- `test_tea_uses_internal_dace_style_kriging() -> None` — funkcja modułowa; [wiersz 90](../tests/test_article_alignment_corrections.py#L90).

### `tests/test_cmoea_cd_cmobr.py`

- `test_algorithm_is_registered_with_header_and_without_ready_algorithm_imports(key: str) -> None` — funkcja modułowa; [wiersz 22](../tests/test_cmoea_cd_cmobr.py#L22).
- `test_constraint_pareto_relation_preserves_objective_incomparable_points() -> None` — funkcja modułowa; [wiersz 33](../tests/test_cmoea_cd_cmobr.py#L33).
- `test_cmoea_cd_runtime_archives_and_callback() -> None` — funkcja modułowa; [wiersz 40](../tests/test_cmoea_cd_cmobr.py#L40).
- `test_cmobr_push_pull_transition_and_evaluation_accounting() -> None` — funkcja modułowa; [wiersz 53](../tests/test_cmoea_cd_cmobr.py#L53).
- `test_cmobr_helpers() -> None` — funkcja modułowa; [wiersz 64](../tests/test_cmoea_cd_cmobr.py#L64).
- `test_algorithms_require_constraints(key: str) -> None` — funkcja modułowa; [wiersz 72](../tests/test_cmoea_cd_cmobr.py#L72).
- `test_short_runs_are_reproducible(factory, kwargs) -> None` — funkcja modułowa; [wiersz 78](../tests/test_cmoea_cd_cmobr.py#L78).
- `lambda` — wyrażenie anonimowe; [wiersz 44](../tests/test_cmoea_cd_cmobr.py#L44).

### `tests/test_custom_algorithm_runtime.py`

- `test_ibea_runtime_on_schaffer() -> None` — funkcja modułowa; [wiersz 14](../tests/test_custom_algorithm_runtime.py#L14).
- `test_gde3_runtime_on_schaffer() -> None` — funkcja modułowa; [wiersz 27](../tests/test_custom_algorithm_runtime.py#L27).
- `test_piea_runtime_on_schaffer() -> None` — funkcja modułowa; [wiersz 40](../tests/test_custom_algorithm_runtime.py#L40).
- `test_tea_runtime_on_schaffer() -> None` — funkcja modułowa; [wiersz 60](../tests/test_custom_algorithm_runtime.py#L60).
- `test_tea_preserves_individual_problem_constraints() -> None` — funkcja modułowa; [wiersz 79](../tests/test_custom_algorithm_runtime.py#L79).
- `test_ssde_runtime_on_schaffer() -> None` — funkcja modułowa; [wiersz 93](../tests/test_custom_algorithm_runtime.py#L93).

### `tests/test_delta.py`

- `test_classical_delta_keeps_endpoint_and_spacing_penalties() -> None` — funkcja modułowa; [wiersz 13](../tests/test_delta.py#L13).
- `test_generalized_delta_penalizes_missing_extremes(n_obj: int) -> None` — funkcja modułowa; [wiersz 26](../tests/test_delta.py#L26).
- `test_generalized_delta_measures_nonuniform_spacing() -> None` — funkcja modułowa; [wiersz 34](../tests/test_delta.py#L34).
- `test_delta_requires_valid_reference_and_enough_feasible_points(n_obj: int) -> None` — funkcja modułowa; [wiersz 46](../tests/test_delta.py#L46).
- `test_generation_callback_computes_delta_for_every_algorithm(algorithm_key, n_obj: int) -> None` — funkcja modułowa; [wiersz 60](../tests/test_delta.py#L60).

### `tests/test_dssea_pimd_umaoea.py`

- `test_new_algorithm_is_registered_as_standalone(key: str) -> None` — funkcja modułowa; [wiersz 23](../tests/test_dssea_pimd_umaoea.py#L23).
- `test_new_algorithm_does_not_import_ready_algorithm_package(key: str) -> None` — funkcja modułowa; [wiersz 31](../tests/test_dssea_pimd_umaoea.py#L31).
- `test_dssea_epsilon_fitness_prefers_feasibility() -> None` — funkcja modułowa; [wiersz 46](../tests/test_dssea_pimd_umaoea.py#L46).
- `test_dssea_runtime_includes_aldva_evaluations() -> None` — funkcja modułowa; [wiersz 53](../tests/test_dssea_pimd_umaoea.py#L53).
- `test_pimd_shape_estimate_and_runtime() -> None` — funkcja modułowa; [wiersz 71](../tests/test_dssea_pimd_umaoea.py#L71).
- `test_pimd_rejects_constrained_problem_before_run() -> None` — funkcja modułowa; [wiersz 84](../tests/test_dssea_pimd_umaoea.py#L84).
- `test_umaoea_reference_weights_merge_and_runtime() -> None` — funkcja modułowa; [wiersz 91](../tests/test_dssea_pimd_umaoea.py#L91).
- `test_new_algorithms_are_reproducible_for_short_runs() -> None` — funkcja modułowa; [wiersz 116](../tests/test_dssea_pimd_umaoea.py#L116).
- `lambda` — wyrażenie anonimowe; [wiersz 62](../tests/test_dssea_pimd_umaoea.py#L62).
- `lambda` — wyrażenie anonimowe; [wiersz 107](../tests/test_dssea_pimd_umaoea.py#L107).

### `tests/test_dtlz_pareto_fronts.py`

- `_dtlz_front(problem_key: str, n_obj: int=3) -> np.ndarray` — funkcja modułowa; [wiersz 9](../tests/test_dtlz_pareto_fronts.py#L9).
- `test_dtlz_fronts_are_dense_finite_and_three_dimensional(problem_key: str) -> None` — funkcja modułowa; [wiersz 18](../tests/test_dtlz_pareto_fronts.py#L18).
- `test_dtlz_fronts_follow_their_expected_geometry() -> None` — funkcja modułowa; [wiersz 27](../tests/test_dtlz_pareto_fronts.py#L27).
- `test_dtlz7_front_uses_only_the_disconnected_optimal_intervals() -> None` — funkcja modułowa; [wiersz 40](../tests/test_dtlz_pareto_fronts.py#L40).

### `tests/test_dvcea_dssea_import.py`

- `test_dvcea_is_registered_and_dssea_is_not_duplicated() -> None` — funkcja modułowa; [wiersz 20](../tests/test_dvcea_dssea_import.py#L20).
- `test_modules_have_project_header_and_no_ready_algorithm_import(key: str) -> None` — funkcja modułowa; [wiersz 28](../tests/test_dvcea_dssea_import.py#L28).
- `test_kmeans_centroids_is_deterministic_and_dimensionally_correct() -> None` — funkcja modułowa; [wiersz 37](../tests/test_dvcea_dssea_import.py#L37).
- `test_improved_survival_prioritizes_epsilon_feasible_pool() -> None` — funkcja modułowa; [wiersz 45](../tests/test_dvcea_dssea_import.py#L45).
- `test_dvcea_runtime_classification_cost_two_stages_and_callback() -> None` — funkcja modułowa; [wiersz 54](../tests/test_dvcea_dssea_import.py#L54).
- `test_dvcea_requires_constrained_problem() -> None` — funkcja modułowa; [wiersz 66](../tests/test_dvcea_dssea_import.py#L66).
- `test_dvcea_short_run_is_reproducible() -> None` — funkcja modułowa; [wiersz 71](../tests/test_dvcea_dssea_import.py#L71).
- `lambda` — wyrażenie anonimowe; [wiersz 58](../tests/test_dvcea_dssea_import.py#L58).

### `tests/test_empty_benchmark_template.py`

- `test_empty_benchmark_template_evaluates_vectorized_objectives() -> None` — funkcja modułowa; [wiersz 14](../tests/test_empty_benchmark_template.py#L14).
- `test_empty_benchmark_template_validates_configuration() -> None` — funkcja modułowa; [wiersz 27](../tests/test_empty_benchmark_template.py#L27).
- `test_empty_benchmark_template_exposes_registration_contract() -> None` — funkcja modułowa; [wiersz 36](../tests/test_empty_benchmark_template.py#L36).

### `tests/test_expanded_benchmark_capabilities.py`

- `_make(key: str)` — funkcja modułowa; [wiersz 21](../tests/test_expanded_benchmark_capabilities.py#L21).
- `test_every_problem_and_algorithm_declares_capabilities() -> None` — funkcja modułowa; [wiersz 32](../tests/test_expanded_benchmark_capabilities.py#L32).
- `test_local_constrained_families_have_finite_objectives_and_constraints(key: str) -> None` — funkcja modułowa; [wiersz 42](../tests/test_expanded_benchmark_capabilities.py#L42).
- `test_local_mw_objectives_and_constraints(key: str) -> None` — funkcja modułowa; [wiersz 54](../tests/test_expanded_benchmark_capabilities.py#L54).
- `test_new_known_fronts_are_finite_and_dimensionally_correct(key: str) -> None` — funkcja modułowa; [wiersz 65](../tests/test_expanded_benchmark_capabilities.py#L65).
- `test_zdt5_is_local_binary_and_only_encoding_aware_algorithms_are_allowed() -> None` — funkcja modułowa; [wiersz 74](../tests/test_expanded_benchmark_capabilities.py#L74).
- `test_binary_operators_never_create_fractional_values() -> None` — funkcja modułowa; [wiersz 85](../tests/test_expanded_benchmark_capabilities.py#L85).
- `test_dynamic_problem_advances_and_population_is_reevaluated() -> None` — funkcja modułowa; [wiersz 94](../tests/test_expanded_benchmark_capabilities.py#L94).
- `test_dynamic_and_encoding_incompatibilities_have_explicit_reasons() -> None` — funkcja modułowa; [wiersz 102](../tests/test_expanded_benchmark_capabilities.py#L102).
- `test_multimodal_and_dynamic_metrics() -> None` — funkcja modułowa; [wiersz 110](../tests/test_expanded_benchmark_capabilities.py#L110).

### `tests/test_kktpm.py`

- `test_kktpm_includes_variable_bounds_for_zdt1_pareto_points() -> None` — funkcja modułowa; [wiersz 12](../tests/test_kktpm.py#L12).
- `test_kktpm_does_not_duplicate_preconverted_bound_constraints() -> None` — funkcja modułowa; [wiersz 27](../tests/test_kktpm.py#L27).
- `test_kktpm_preserves_problem_constraints_when_adding_bounds() -> None` — funkcja modułowa; [wiersz 40](../tests/test_kktpm.py#L40).
- `test_default_numerical_step_is_stable_near_zdt1_endpoint() -> None` — funkcja modułowa; [wiersz 53](../tests/test_kktpm.py#L53).

### `tests/test_lmoea_ds_runtime.py`

- `test_lmoea_ds_runtime_on_schaffer() -> None` — funkcja modułowa; [wiersz 8](../tests/test_lmoea_ds_runtime.py#L8).

### `tests/test_metric_trajectories.py`

- `test_metric_trajectories_store_finite_generation_values() -> None` — funkcja modułowa; [wiersz 17](../tests/test_metric_trajectories.py#L17).
- `test_spread_delta_and_kktpm_axes_show_unscaled_decimal_values() -> None` — funkcja modułowa; [wiersz 40](../tests/test_metric_trajectories.py#L40).
- `test_main_run_updates_and_resets_metric_trajectories() -> None` — funkcja modułowa; [wiersz 54](../tests/test_metric_trajectories.py#L54).
- `test_delta_trajectory_is_visible_and_updates_for_every_algorithm() -> None` — funkcja modułowa; [wiersz 98](../tests/test_metric_trajectories.py#L98).
- `test_clear_button_clears_console_and_visual_charts() -> None` — funkcja modułowa; [wiersz 119](../tests/test_metric_trajectories.py#L119).

### `tests/test_multi.py`

- `test_default_entry_params_returns_independent_values() -> None` — funkcja modułowa; [wiersz 26](../tests/test_multi.py#L26).
- `test_build_multi_run_specs_creates_problem_major_cartesian_product() -> None` — funkcja modułowa; [wiersz 43](../tests/test_multi.py#L43).
- `test_metrics_table_data_preserves_generation_history() -> None` — funkcja modułowa; [wiersz 57](../tests/test_multi.py#L57).
- `test_solution_table_data_exports_objectives_and_decisions() -> None` — funkcja modułowa; [wiersz 71](../tests/test_multi.py#L71).
- `test_solution_table_data_keeps_headers_for_an_empty_front() -> None` — funkcja modułowa; [wiersz 84](../tests/test_multi.py#L84).
- `test_multi_worker_runs_and_exports_each_result(tmp_path: Path) -> None` — funkcja modułowa; [wiersz 91](../tests/test_multi.py#L91).
- `test_multi_worker_skips_incompatible_algorithm_problem_pair(tmp_path: Path) -> None` — funkcja modułowa; [wiersz 120](../tests/test_multi.py#L120).
- `test_main_window_exposes_main_and_multi_tabs() -> None` — funkcja modułowa; [wiersz 140](../tests/test_multi.py#L140).
- `test_hv_reference_point_is_scaled_from_the_known_front() -> None` — funkcja modułowa; [wiersz 161](../tests/test_multi.py#L161).
- `test_main_auto_hv_reference_uses_selected_problem_front() -> None` — funkcja modułowa; [wiersz 169](../tests/test_multi.py#L169).

### `tests/test_package_exports.py`

- `test_top_level_exports_match_active_modules() -> None` — funkcja modułowa; [wiersz 8](../tests/test_package_exports.py#L8).
- `test_historical_algoritms_alias_still_imports() -> None` — funkcja modułowa; [wiersz 13](../tests/test_package_exports.py#L13).

### `tests/test_pareto_labels.py`

- `test_pareto_reference_layer_label_does_not_use_known() -> None` — funkcja modułowa; [wiersz 16](../tests/test_pareto_labels.py#L16).

### `tests/test_plot_controls.py`

- `app()` — funkcja modułowa; [wiersz 22](../tests/test_plot_controls.py#L22).
- `wait_until(app, predicate, timeout=10)` — funkcja modułowa; [wiersz 26](../tests/test_plot_controls.py#L26).
- `make_worker(*, step_mode=False, n_gen=3)` — funkcja modułowa; [wiersz 35](../tests/test_plot_controls.py#L35).
- `test_steps_match_continuous_run_and_do_not_advance_while_paused(app)` — funkcja modułowa; [wiersz 42](../tests/test_plot_controls.py#L42).
- `test_stop_wakes_unlimited_worker_paused_after_epoch_one(app)` — funkcja modułowa; [wiersz 72](../tests/test_plot_controls.py#L72).
- `test_browse_epochs_preserves_snapshots_and_keeps_metrics_history(app)` — funkcja modułowa; [wiersz 89](../tests/test_plot_controls.py#L89).
- `test_grid_and_complete_png_export_preserve_current_view(app, tmp_path, dim)` — funkcja modułowa; [wiersz 116](../tests/test_plot_controls.py#L116).
- `test_step_button_advances_from_history_and_stop_exports(app, tmp_path, monkeypatch)` — funkcja modułowa; [wiersz 159](../tests/test_plot_controls.py#L159).
- `test_closing_window_wakes_paused_worker(app, tmp_path, monkeypatch)` — funkcja modułowa; [wiersz 188](../tests/test_plot_controls.py#L188).
- `test_default_window_is_square_and_console_is_shallow(app)` — funkcja modułowa; [wiersz 208](../tests/test_plot_controls.py#L208).
- `lambda` — wyrażenie anonimowe; [wiersz 55](../tests/test_plot_controls.py#L55).
- `lambda` — wyrażenie anonimowe; [wiersz 61](../tests/test_plot_controls.py#L61).
- `lambda` — wyrażenie anonimowe; [wiersz 79](../tests/test_plot_controls.py#L79).
- `lambda` — wyrażenie anonimowe; [wiersz 81](../tests/test_plot_controls.py#L81).
- `lambda` — wyrażenie anonimowe; [wiersz 160](../tests/test_plot_controls.py#L160).
- `lambda` — wyrażenie anonimowe; [wiersz 169](../tests/test_plot_controls.py#L169).
- `lambda` — wyrażenie anonimowe; [wiersz 171](../tests/test_plot_controls.py#L171).
- `lambda` — wyrażenie anonimowe; [wiersz 174](../tests/test_plot_controls.py#L174).
- `lambda` — wyrażenie anonimowe; [wiersz 176](../tests/test_plot_controls.py#L176).
- `lambda` — wyrażenie anonimowe; [wiersz 189](../tests/test_plot_controls.py#L189).
- `lambda` — wyrażenie anonimowe; [wiersz 197](../tests/test_plot_controls.py#L197).
- `lambda` — wyrażenie anonimowe; [wiersz 199](../tests/test_plot_controls.py#L199).

### `tests/test_recent_algorithms.py`

- `test_recent_algorithm_registry_entries_document_provenance(algorithm_key: str) -> None` — funkcja modułowa; [wiersz 37](../tests/test_recent_algorithms.py#L37).
- `test_probability_and_dominance_mechanisms() -> None` — funkcja modułowa; [wiersz 46](../tests/test_recent_algorithms.py#L46).
- `test_disk_density_and_constrained_probability_order() -> None` — funkcja modułowa; [wiersz 59](../tests/test_recent_algorithms.py#L59).
- `test_tspp_phase_two_prioritizes_feasibility() -> None` — funkcja modułowa; [wiersz 73](../tests/test_recent_algorithms.py#L73).
- `test_ported_kriging_interpolates_linear_trend() -> None` — funkcja modułowa; [wiersz 85](../tests/test_recent_algorithms.py#L85).
- `test_new_surrogate_algorithm_runtime(factory, problem, extra) -> None` — funkcja modułowa; [wiersz 107](../tests/test_recent_algorithms.py#L107).
- `test_new_surrogate_algorithm_runtime.callback(current) -> None` — funkcja zagnieżdżona; [wiersz 117](../tests/test_recent_algorithms.py#L117).
- `test_constrained_only_algorithms_are_rejected_before_factory_execution() -> None` — funkcja modułowa; [wiersz 139](../tests/test_recent_algorithms.py#L139).
- `test_stage_one_recent_algorithms_are_reproducible(factory, kwargs) -> None` — funkcja modułowa; [wiersz 163](../tests/test_recent_algorithms.py#L163).

### `tests/test_registry_integrity.py`

- `test_algorithm_registry_has_required_structure() -> None` — funkcja modułowa; [wiersz 12](../tests/test_registry_integrity.py#L12).
- `test_problem_registry_has_required_structure() -> None` — funkcja modułowa; [wiersz 21](../tests/test_registry_integrity.py#L21).
- `test_known_fronts_are_finite_unique_and_nondominated() -> None` — funkcja modułowa; [wiersz 30](../tests/test_registry_integrity.py#L30).
- `test_wfg3_2d_reference_front_stays_inside_analytical_objective_ranges() -> None` — funkcja modułowa; [wiersz 54](../tests/test_registry_integrity.py#L54).

### `tests/test_rewritten_article_algorithms.py`

- `test_rewritten_algorithms_do_not_import_ready_algorithm_packages() -> None` — funkcja modułowa; [wiersz 33](../tests/test_rewritten_article_algorithms.py#L33).
- `SwitchingProblem.__init__(self) -> None` — metoda; [wiersz 48](../tests/test_rewritten_article_algorithms.py#L48).
- `SwitchingProblem._evaluate(self, X, out, *args, **kwargs) -> None` — metoda; [wiersz 52](../tests/test_rewritten_article_algorithms.py#L52).
- `test_epsilon_nsga2_performs_connected_run_restart() -> None` — funkcja modułowa; [wiersz 59](../tests/test_rewritten_article_algorithms.py#L59).
- `test_diskplus_cdipd_and_runtime_are_constraint_aware() -> None` — funkcja modułowa; [wiersz 77](../tests/test_rewritten_article_algorithms.py#L77).
- `test_learning_edmo_trains_central_model_and_transfers_between_dimensions() -> None` — funkcja modułowa; [wiersz 102](../tests/test_rewritten_article_algorithms.py#L102).
- `test_maotspp_penalty_prioritizes_feasibility_and_runs() -> None` — funkcja modułowa; [wiersz 117](../tests/test_rewritten_article_algorithms.py#L117).
- `test_rnn_guided_dmo_detects_changes_and_trains_weights_online() -> None` — funkcja modułowa; [wiersz 138](../tests/test_rewritten_article_algorithms.py#L138).
- `test_ts_nsga_implements_spd_lpd_and_stage_switch() -> None` — funkcja modułowa; [wiersz 162](../tests/test_rewritten_article_algorithms.py#L162).

### `tests/test_runtime_paths.py`

- `test_source_results_stay_in_project(monkeypatch)` — funkcja modułowa; [wiersz 7](../tests/test_runtime_paths.py#L7).
- `test_frozen_results_survive_bundle_cleanup(monkeypatch, tmp_path)` — funkcja modułowa; [wiersz 12](../tests/test_runtime_paths.py#L12).

### `tests/test_standalone_classic_algorithms.py`

- `test_registered_algorithm_does_not_import_ready_algorithm(algorithm_key: str) -> None` — funkcja modułowa; [wiersz 43](../tests/test_standalone_classic_algorithms.py#L43).
- `test_registered_standalone_algorithm_completes_two_generations(algorithm_key: str) -> None` — funkcja modułowa; [wiersz 59](../tests/test_standalone_classic_algorithms.py#L59).

### `tests/test_version.py`

- `test_public_version_and_window_title() -> None` — funkcja modułowa; [wiersz 7](../tests/test_version.py#L7).
