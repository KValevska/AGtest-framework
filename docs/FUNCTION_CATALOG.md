# Katalog funkcji AGtest-framework v0.1

Dokument jest generowany z aktualnych drzew składniowych AST poleceniem
`python scripts/generate_function_catalog.py`. Obejmuje kod aplikacji, testy, metody,
funkcje zagnieżdżone i wyrażenia `lambda`; nie obejmuje symboli importowanych.

## Wynik analizy

- Przeanalizowano **71** plików Python.
- Kod uruchomieniowy zawiera **580** deklaracji funkcji i metod.
- Testy zawierają **49** deklaracji funkcji i metod.
- Łącznie znaleziono **629** deklaracji, **82** klas i **40** wyrażeń `lambda`.

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
| `src/pymoo_gui/algorithms/__init__.py` | 1 | 0 | 0 |
| `src/pymoo_gui/algorithms/age.py` | 14 | 2 | 0 |
| `src/pymoo_gui/algorithms/common.py` | 14 | 2 | 0 |
| `src/pymoo_gui/algorithms/empty_algorithm_template.py` | 7 | 1 | 0 |
| `src/pymoo_gui/algorithms/eps_moea.py` | 2 | 0 | 0 |
| `src/pymoo_gui/algorithms/eps_nsga2.py` | 2 | 0 | 0 |
| `src/pymoo_gui/algorithms/gde3.py` | 9 | 1 | 0 |
| `src/pymoo_gui/algorithms/hype.py` | 26 | 2 | 0 |
| `src/pymoo_gui/algorithms/ibea.py` | 10 | 1 | 0 |
| `src/pymoo_gui/algorithms/learning_edmo.py` | 6 | 1 | 0 |
| `src/pymoo_gui/algorithms/lmoea_ds.py` | 18 | 1 | 0 |
| `src/pymoo_gui/algorithms/moead.py` | 4 | 0 | 0 |
| `src/pymoo_gui/algorithms/nsga2.py` | 2 | 0 | 0 |
| `src/pymoo_gui/algorithms/nsga3.py` | 4 | 0 | 0 |
| `src/pymoo_gui/algorithms/platypus_common.py` | 15 | 3 | 0 |
| `src/pymoo_gui/algorithms/platypus_moead.py` | 2 | 0 | 0 |
| `src/pymoo_gui/algorithms/research_common.py` | 53 | 3 | 0 |
| `src/pymoo_gui/algorithms/rnn_guided_dmo.py` | 7 | 1 | 0 |
| `src/pymoo_gui/algorithms/rnsga3.py` | 5 | 0 | 0 |
| `src/pymoo_gui/algorithms/rvea.py` | 9 | 1 | 0 |
| `src/pymoo_gui/algorithms/spea2.py` | 6 | 2 | 0 |
| `src/pymoo_gui/algorithms/ts_nsga.py` | 3 | 1 | 0 |
| `src/pymoo_gui/algoritms/__init__.py` | 0 | 0 | 0 |
| `src/pymoo_gui/app.py` | 145 | 7 | 4 |
| `src/pymoo_gui/metrics/__init__.py` | 0 | 0 | 0 |
| `src/pymoo_gui/metrics/export.py` | 13 | 0 | 0 |
| `src/pymoo_gui/metrics/quality.py` | 22 | 1 | 0 |
| `src/pymoo_gui/multi.py` | 13 | 3 | 0 |
| `src/pymoo_gui/packaging_smoke.py` | 2 | 0 | 0 |
| `src/pymoo_gui/parallel.py` | 12 | 1 | 0 |
| `src/pymoo_gui/problems/__init__.py` | 0 | 0 | 0 |
| `src/pymoo_gui/problems/binh2.py` | 2 | 1 | 0 |
| `src/pymoo_gui/problems/constrex.py` | 2 | 1 | 0 |
| `src/pymoo_gui/problems/empty_benchmark_template.py` | 4 | 1 | 0 |
| `src/pymoo_gui/problems/fonseca.py` | 2 | 1 | 0 |
| `src/pymoo_gui/problems/golinski.py` | 2 | 1 | 0 |
| `src/pymoo_gui/problems/kursawe.py` | 2 | 1 | 0 |
| `src/pymoo_gui/problems/lz09.py` | 16 | 10 | 0 |
| `src/pymoo_gui/problems/osyczka2.py` | 2 | 1 | 0 |
| `src/pymoo_gui/problems/registry.py` | 18 | 0 | 24 |
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
| `tests/test_custom_algorithm_runtime.py` | 2 | 0 | 0 |
| `tests/test_delta.py` | 5 | 0 | 0 |
| `tests/test_dtlz_pareto_fronts.py` | 4 | 0 | 0 |
| `tests/test_empty_benchmark_template.py` | 3 | 0 | 0 |
| `tests/test_kktpm.py` | 4 | 0 | 0 |
| `tests/test_lmoea_ds_runtime.py` | 1 | 0 | 0 |
| `tests/test_metric_trajectories.py` | 5 | 0 | 0 |
| `tests/test_multi.py` | 7 | 0 | 0 |
| `tests/test_package_exports.py` | 2 | 0 | 0 |
| `tests/test_pareto_labels.py` | 1 | 0 | 0 |
| `tests/test_plot_controls.py` | 10 | 0 | 12 |
| `tests/test_registry_integrity.py` | 2 | 0 | 0 |
| `tests/test_runtime_paths.py` | 2 | 0 | 0 |
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

- `minimize(problem: Any, algorithm: Any, termination: Any, **kwargs: Any) -> Any` — funkcja modułowa; [wiersz 63](../src/pymoo_gui/algorithms/__init__.py#L63).

### `src/pymoo_gui/algorithms/age.py`

- `_parse_positive_int(value: Any, field_name: str) -> int` — funkcja modułowa; [wiersz 29](../src/pymoo_gui/algorithms/age.py#L29).
- `_parse_optional_positive_int(value: Any, field_name: str) -> Optional[int]` — funkcja modułowa; [wiersz 40](../src/pymoo_gui/algorithms/age.py#L40).
- `point_2_line_distance(points: np.ndarray, start: np.ndarray, end: np.ndarray) -> np.ndarray` — funkcja modułowa; [wiersz 47](../src/pymoo_gui/algorithms/age.py#L47).
- `find_corner_solutions(front: np.ndarray) -> np.ndarray` — funkcja modułowa; [wiersz 60](../src/pymoo_gui/algorithms/age.py#L60).
- `normalize(front: np.ndarray, extreme: np.ndarray) -> tuple[np.ndarray, np.ndarray]` — funkcja modułowa; [wiersz 79](../src/pymoo_gui/algorithms/age.py#L79).
- `AGEMOEASurvival.__init__(self) -> None` — metoda; [wiersz 107](../src/pymoo_gui/algorithms/age.py#L107).
- `AGEMOEASurvival._do(self, problem, pop, *args, n_survive=None, **kwargs)` — metoda; [wiersz 112](../src/pymoo_gui/algorithms/age.py#L112).
- `AGEMOEASurvival.survival_score(self, front: np.ndarray, ideal_point: np.ndarray) -> tuple[np.ndarray, float, np.ndarray]` — metoda; [wiersz 145](../src/pymoo_gui/algorithms/age.py#L145).
- `AGEMOEASurvival.compute_geometry(front: np.ndarray, extreme: np.ndarray, n_obj: int) -> float` — metoda; [wiersz 193](../src/pymoo_gui/algorithms/age.py#L193).
- `AGEMOEASurvival.pairwise_distances(front: np.ndarray, p: float) -> np.ndarray` — metoda; [wiersz 210](../src/pymoo_gui/algorithms/age.py#L210).
- `AGEMOEASurvival.minkowski_distances(A: np.ndarray, B: np.ndarray, p: float) -> np.ndarray` — metoda; [wiersz 219](../src/pymoo_gui/algorithms/age.py#L219).
- `AGE.__init__(self, pop_size: int=100, sampling=FloatRandomSampling(), selection=TournamentSelection(func_comp=binary_tournament), crossover=SBX(eta=15, prob=0.9), mutation=PM(eta=20), eliminate_duplicates: bool=True, n_offsprings: Optional[int]=None, output=MultiObjectiveOutput(), **kwargs)` — metoda; [wiersz 233](../src/pymoo_gui/algorithms/age.py#L233).
- `AGE._set_optimum(self, **kwargs)` — metoda; [wiersz 262](../src/pymoo_gui/algorithms/age.py#L262).
- `make_age(pop_size: int=100, n_offsprings: Optional[int]=None) -> AGE` — funkcja modułowa; [wiersz 270](../src/pymoo_gui/algorithms/age.py#L270).

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

### `src/pymoo_gui/algorithms/empty_algorithm_template.py`

- `EmptyAlgorithmTemplate.__init__(self, population_size: int=100, archive_size: int=100, crossover_rate: float=0.9, mutation_rate: float=0.1, template_bias: float=0.5, seed: int=1) -> None` — metoda; [wiersz 26](../src/pymoo_gui/algorithms/empty_algorithm_template.py#L26).
- `EmptyAlgorithmTemplate.after_initialize(self) -> None` — metoda; [wiersz 52](../src/pymoo_gui/algorithms/empty_algorithm_template.py#L52).
- `EmptyAlgorithmTemplate.guided_candidates(self) -> np.ndarray` — metoda; [wiersz 57](../src/pymoo_gui/algorithms/empty_algorithm_template.py#L57).
- `EmptyAlgorithmTemplate.create_offspring(self) -> np.ndarray` — metoda; [wiersz 64](../src/pymoo_gui/algorithms/empty_algorithm_template.py#L64).
- `EmptyAlgorithmTemplate.environmental_selection(self, X: np.ndarray, F: np.ndarray, CV: np.ndarray, n_survive: int) -> PopulationState` — metoda; [wiersz 76](../src/pymoo_gui/algorithms/empty_algorithm_template.py#L76).
- `EmptyAlgorithmTemplate.after_generation(self, previous: PopulationState, current: PopulationState) -> None` — metoda; [wiersz 96](../src/pymoo_gui/algorithms/empty_algorithm_template.py#L96).
- `make_empty_algorithm_template(population_size: int=100, archive_size: int=100, crossover_rate: float=0.9, mutation_rate: float=0.1, template_bias: float=0.5, seed: int=1) -> EmptyAlgorithmTemplate` — funkcja modułowa; [wiersz 106](../src/pymoo_gui/algorithms/empty_algorithm_template.py#L106).

### `src/pymoo_gui/algorithms/eps_moea.py`

- `make_eps_moea(problem: Any, population_size: int=100, epsilons: Any=0.01) -> PlatypusAlgorithmAdapter` — funkcja modułowa; [wiersz 23](../src/pymoo_gui/algorithms/eps_moea.py#L23).
- `make_eps_moea._factory(platypus_problem: Any) -> Any` — funkcja zagnieżdżona; [wiersz 42](../src/pymoo_gui/algorithms/eps_moea.py#L42).

### `src/pymoo_gui/algorithms/eps_nsga2.py`

- `make_eps_nsga2(problem: Any, population_size: int=100, epsilons: Any=0.01) -> PlatypusAlgorithmAdapter` — funkcja modułowa; [wiersz 23](../src/pymoo_gui/algorithms/eps_nsga2.py#L23).
- `make_eps_nsga2._factory(platypus_problem: Any) -> Any` — funkcja zagnieżdżona; [wiersz 42](../src/pymoo_gui/algorithms/eps_nsga2.py#L42).

### `src/pymoo_gui/algorithms/gde3.py`

- `_dominates(lhs: np.ndarray, rhs: np.ndarray) -> bool` — funkcja modułowa; [wiersz 32](../src/pymoo_gui/algorithms/gde3.py#L32).
- `_weakly_constraint_dominates(lhs_f: np.ndarray, lhs_cv: float, rhs_f: np.ndarray, rhs_cv: float) -> bool` — funkcja modułowa; [wiersz 37](../src/pymoo_gui/algorithms/gde3.py#L37).
- `_parse_de_weight(value: Any, field_name: str) -> float` — funkcja modułowa; [wiersz 50](../src/pymoo_gui/algorithms/gde3.py#L50).
- `GDE3.__init__(self, pop_size: int=100, f_weight: float=0.5, crossover_rate: float=0.3, seed: int=1) -> None` — metoda; [wiersz 61](../src/pymoo_gui/algorithms/gde3.py#L61).
- `GDE3._trial_population(self) -> np.ndarray` — metoda; [wiersz 77](../src/pymoo_gui/algorithms/gde3.py#L77).
- `GDE3._pruning_crowding(self, F: np.ndarray, n_survive: int) -> np.ndarray` — metoda; [wiersz 97](../src/pymoo_gui/algorithms/gde3.py#L97).
- `GDE3._reduce_population(self, X: np.ndarray, F: np.ndarray, CV: np.ndarray, n_survive: int) -> PopulationState` — metoda; [wiersz 112](../src/pymoo_gui/algorithms/gde3.py#L112).
- `GDE3.step(self) -> None` — metoda; [wiersz 148](../src/pymoo_gui/algorithms/gde3.py#L148).
- `make_gde3(pop_size: int=100, f_weight: float=0.5, crossover_rate: float=0.3, seed: int=1) -> GDE3` — funkcja modułowa; [wiersz 204](../src/pymoo_gui/algorithms/gde3.py#L204).

### `src/pymoo_gui/algorithms/hype.py`

- `_parse_positive_int(value: Any, field_name: str) -> int` — funkcja modułowa; [wiersz 30](../src/pymoo_gui/algorithms/hype.py#L30).
- `_rng_int(rng: Optional[np.random.Generator], high: int, size: Optional[int | tuple[int, ...]]=None)` — funkcja modułowa; [wiersz 43](../src/pymoo_gui/algorithms/hype.py#L43).
- `_rng_random(rng: Optional[np.random.Generator]) -> float` — funkcja modułowa; [wiersz 52](../src/pymoo_gui/algorithms/hype.py#L52).
- `_clean_reference(value: Any) -> Any` — funkcja modułowa; [wiersz 59](../src/pymoo_gui/algorithms/hype.py#L59).
- `_auto_reference_point(problem: Any, n_obj: int) -> np.ndarray` — funkcja modułowa; [wiersz 76](../src/pymoo_gui/algorithms/hype.py#L76).
- `_reference_values(n_obj: int, problem: Any=None, reference_point: Any=None, reference_set: Any=None) -> np.ndarray` — funkcja modułowa; [wiersz 90](../src/pymoo_gui/algorithms/hype.py#L90).
- `prepare_reference_set(n_obj: int, reference_point: Sequence[float] | None=None, reference_set: Sequence[Sequence[float]] | None=None) -> np.ndarray` — funkcja modułowa; [wiersz 109](../src/pymoo_gui/algorithms/hype.py#L109).
- `fast_non_dominated_sort(objectives: np.ndarray) -> List[List[int]]` — funkcja modułowa; [wiersz 132](../src/pymoo_gui/algorithms/hype.py#L132).
- `_alpha(n: int, k: int, i: int) -> float` — funkcja modułowa; [wiersz 154](../src/pymoo_gui/algorithms/hype.py#L154).
- `_axis_edges(F: np.ndarray, R: np.ndarray) -> list[np.ndarray]` — funkcja modułowa; [wiersz 164](../src/pymoo_gui/algorithms/hype.py#L164).
- `exact_hype_fitness(objectives: np.ndarray, reference_set: np.ndarray, k: int) -> np.ndarray` — funkcja modułowa; [wiersz 175](../src/pymoo_gui/algorithms/hype.py#L175).
- `estimated_hype_fitness(objectives: np.ndarray, reference_set: np.ndarray, k: int, n_samples: int, rng: Optional[np.random.Generator]=None) -> np.ndarray` — funkcja modułowa; [wiersz 210](../src/pymoo_gui/algorithms/hype.py#L210).
- `hype_fitness(objectives: np.ndarray, reference_set: np.ndarray, k: int, n_samples: int, rng: Optional[np.random.Generator]=None) -> np.ndarray` — funkcja modułowa; [wiersz 253](../src/pymoo_gui/algorithms/hype.py#L253).
- `mating_selection(population: np.ndarray, n_obj: int, reference_set: np.ndarray, n_offspring: int, n_samples: int, rng: Optional[np.random.Generator]=None) -> np.ndarray` — funkcja modułowa; [wiersz 266](../src/pymoo_gui/algorithms/hype.py#L266).
- `_eval_objectives(x: np.ndarray, functions: Sequence[ObjectiveFn]) -> np.ndarray` — funkcja modułowa; [wiersz 291](../src/pymoo_gui/algorithms/hype.py#L291).
- `_new_population(size: int, min_values: np.ndarray, max_values: np.ndarray, functions: Sequence[ObjectiveFn], rng: np.random.Generator) -> np.ndarray` — funkcja modułowa; [wiersz 296](../src/pymoo_gui/algorithms/hype.py#L296).
- `crossover(parents: np.ndarray, min_values: Sequence[float], max_values: Sequence[float], functions: Sequence[ObjectiveFn], size: int, mu: float=20.0, rng: Optional[np.random.Generator]=None) -> np.ndarray` — funkcja modułowa; [wiersz 309](../src/pymoo_gui/algorithms/hype.py#L309).
- `mutation(offspring: np.ndarray, min_values: Sequence[float], max_values: Sequence[float], functions: Sequence[ObjectiveFn], mutation_rate: float=0.1, eta: float=20.0, rng: Optional[np.random.Generator]=None) -> np.ndarray` — funkcja modułowa; [wiersz 361](../src/pymoo_gui/algorithms/hype.py#L361).
- `environmental_selection(population: np.ndarray, population_size: int, n_obj: int, reference_set: np.ndarray, n_samples: int, rng: Optional[np.random.Generator]=None) -> np.ndarray` — funkcja modułowa; [wiersz 402](../src/pymoo_gui/algorithms/hype.py#L402).
- `hype_tournament(pop, P, random_state=None, **kwargs)` — funkcja modułowa; [wiersz 435](../src/pymoo_gui/algorithms/hype.py#L435).
- `HypESurvival.__init__(self, reference_point: Any='auto', reference_set: Any=None, n_samples: int=1000)` — metoda; [wiersz 467](../src/pymoo_gui/algorithms/hype.py#L467).
- `HypESurvival._do(self, problem, pop, *args, n_survive=None, **kwargs)` — metoda; [wiersz 474](../src/pymoo_gui/algorithms/hype.py#L474).
- `HypE.__init__(self, pop_size: int=40, reference_point: Any='auto', reference_set: Any=None, n_samples: int=1000, sampling=FloatRandomSampling(), selection=TournamentSelection(func_comp=hype_tournament), crossover=SBX(eta=15, prob=0.9), mutation=PM(eta=20), output=MultiObjectiveOutput(), **kwargs)` — metoda; [wiersz 507](../src/pymoo_gui/algorithms/hype.py#L507).
- `HypE.reference_values(self, n_obj: int) -> np.ndarray` — metoda; [wiersz 537](../src/pymoo_gui/algorithms/hype.py#L537).
- `hype(min_values: Sequence[float], max_values: Sequence[float], functions: Sequence[ObjectiveFn], population_size: int=100, generations: int=50, reference_point: Sequence[float] | None=None, reference_set: Sequence[Sequence[float]] | None=None, n_samples: int=1000, mutation_rate: float=0.1, mu: float=20.0, eta: float=20.0, rng: Optional[np.random.Generator]=None) -> np.ndarray` — funkcja modułowa; [wiersz 542](../src/pymoo_gui/algorithms/hype.py#L542).
- `make_hype(problem: Any=None, pop_size: int=40, reference_point: Any='auto', reference_set: Any=None, n_samples: int=1000) -> HypE` — funkcja modułowa; [wiersz 581](../src/pymoo_gui/algorithms/hype.py#L581).

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

- `LearningAcrossProblemsEDMO.__init__(self, population_size: int=100, archive_size: int=100, crossover_rate: float=0.9, mutation_rate: float=0.1, transfer_fraction: float=0.2, memory_size: int=8, seed: int=1) -> None` — metoda; [wiersz 25](../src/pymoo_gui/algorithms/learning_edmo.py#L25).
- `LearningAcrossProblemsEDMO.make_signature(self) -> str` — metoda; [wiersz 46](../src/pymoo_gui/algorithms/learning_edmo.py#L46).
- `LearningAcrossProblemsEDMO.warm_start_candidates(self) -> np.ndarray | None` — metoda; [wiersz 51](../src/pymoo_gui/algorithms/learning_edmo.py#L51).
- `LearningAcrossProblemsEDMO.guided_candidates(self) -> np.ndarray` — metoda; [wiersz 62](../src/pymoo_gui/algorithms/learning_edmo.py#L62).
- `LearningAcrossProblemsEDMO.after_generation(self, previous, current) -> None` — metoda; [wiersz 78](../src/pymoo_gui/algorithms/learning_edmo.py#L78).
- `make_learning_edmo(population_size: int=100, archive_size: int=100, crossover_rate: float=0.9, mutation_rate: float=0.1, transfer_fraction: float=0.2, memory_size: int=8, seed: int=1) -> LearningAcrossProblemsEDMO` — funkcja modułowa; [wiersz 89](../src/pymoo_gui/algorithms/learning_edmo.py#L89).

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

### `src/pymoo_gui/algorithms/moead.py`

- `_parse_positive_int(value: Any, field_name: str) -> int` — funkcja modułowa; [wiersz 18](../src/pymoo_gui/algorithms/moead.py#L18).
- `_parse_probability(value: Any, field_name: str) -> float` — funkcja modułowa; [wiersz 35](../src/pymoo_gui/algorithms/moead.py#L35).
- `_problem_n_obj(problem: Any) -> int` — funkcja modułowa; [wiersz 53](../src/pymoo_gui/algorithms/moead.py#L53).
- `make_moead(problem: Any, n_partitions: int=12, n_neighbors: int=15, prob_neighbor_mating: float=0.7) -> MOEAD` — funkcja modułowa; [wiersz 69](../src/pymoo_gui/algorithms/moead.py#L69).

### `src/pymoo_gui/algorithms/nsga2.py`

- `_parse_positive_int(value: Any, field_name: str) -> int` — funkcja modułowa; [wiersz 18](../src/pymoo_gui/algorithms/nsga2.py#L18).
- `make_nsga2(pop_size: int=100) -> NSGA2` — funkcja modułowa; [wiersz 36](../src/pymoo_gui/algorithms/nsga2.py#L36).

### `src/pymoo_gui/algorithms/nsga3.py`

- `_parse_positive_int(value: Any, field_name: str) -> int` — funkcja modułowa; [wiersz 24](../src/pymoo_gui/algorithms/nsga3.py#L24).
- `_problem_n_obj(problem: Any) -> int` — funkcja modułowa; [wiersz 42](../src/pymoo_gui/algorithms/nsga3.py#L42).
- `_ref_dir_count(n_obj: int, n_partitions: int) -> int` — funkcja modułowa; [wiersz 58](../src/pymoo_gui/algorithms/nsga3.py#L58).
- `make_nsga3(problem: Any, pop_size: int=DEFAULT_NSGA3_POP_SIZE, n_partitions: int=DEFAULT_NSGA3_N_PARTITIONS) -> NSGA3` — funkcja modułowa; [wiersz 63](../src/pymoo_gui/algorithms/nsga3.py#L63).

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

### `src/pymoo_gui/algorithms/platypus_moead.py`

- `make_platypus_moead(problem: Any, population_size: int=100, neighborhood_size: int=10, delta: float=0.8, eta: int=1) -> PlatypusAlgorithmAdapter` — funkcja modułowa; [wiersz 23](../src/pymoo_gui/algorithms/platypus_moead.py#L23).
- `make_platypus_moead._factory(platypus_problem: Any) -> Any` — funkcja zagnieżdżona; [wiersz 48](../src/pymoo_gui/algorithms/platypus_moead.py#L48).

### `src/pymoo_gui/algorithms/research_common.py`

- `parse_positive_int(value: Any, field_name: str) -> int` — funkcja modułowa; [wiersz 31](../src/pymoo_gui/algorithms/research_common.py#L31).
- `parse_optional_positive_int(value: Any, field_name: str) -> Optional[int]` — funkcja modułowa; [wiersz 42](../src/pymoo_gui/algorithms/research_common.py#L42).
- `parse_positive_float(value: Any, field_name: str) -> float` — funkcja modułowa; [wiersz 49](../src/pymoo_gui/algorithms/research_common.py#L49).
- `parse_probability(value: Any, field_name: str) -> float` — funkcja modułowa; [wiersz 60](../src/pymoo_gui/algorithms/research_common.py#L60).
- `parse_reference_directions(value: Any, n_obj: int) -> Optional[np.ndarray]` — funkcja modułowa; [wiersz 71](../src/pymoo_gui/algorithms/research_common.py#L71).
- `problem_bounds(problem: Any) -> tuple[np.ndarray, np.ndarray, int]` — funkcja modułowa; [wiersz 85](../src/pymoo_gui/algorithms/research_common.py#L85).
- `problem_n_obj(problem: Any) -> int` — funkcja modułowa; [wiersz 101](../src/pymoo_gui/algorithms/research_common.py#L101).
- `project_to_bounds(X: np.ndarray, xl: np.ndarray, xu: np.ndarray) -> np.ndarray` — funkcja modułowa; [wiersz 106](../src/pymoo_gui/algorithms/research_common.py#L106).
- `evaluate_problem(problem: Any, X: np.ndarray) -> tuple[np.ndarray, np.ndarray]` — funkcja modułowa; [wiersz 111](../src/pymoo_gui/algorithms/research_common.py#L111).
- `feasible_mask(cv: np.ndarray) -> np.ndarray` — funkcja modułowa; [wiersz 141](../src/pymoo_gui/algorithms/research_common.py#L141).
- `crowding_distance(F: np.ndarray) -> np.ndarray` — funkcja modułowa; [wiersz 146](../src/pymoo_gui/algorithms/research_common.py#L146).
- `assign_rank_and_crowding(F: np.ndarray, CV: np.ndarray) -> tuple[np.ndarray, np.ndarray]` — funkcja modułowa; [wiersz 167](../src/pymoo_gui/algorithms/research_common.py#L167).
- `stable_survivor_order(rank: np.ndarray, crowding: np.ndarray, cv: np.ndarray) -> np.ndarray` — funkcja modułowa; [wiersz 197](../src/pymoo_gui/algorithms/research_common.py#L197).
- `select_survivors_nsga2(X: np.ndarray, F: np.ndarray, CV: np.ndarray, n_survive: int) -> 'PopulationState'` — funkcja modułowa; [wiersz 205](../src/pymoo_gui/algorithms/research_common.py#L205).
- `tournament_indices(rank: np.ndarray, crowding: np.ndarray, cv: np.ndarray, n_parents: int, rng: np.random.Generator) -> np.ndarray` — funkcja modułowa; [wiersz 218](../src/pymoo_gui/algorithms/research_common.py#L218).
- `sbx_crossover(X: np.ndarray, parent_pairs: np.ndarray, xl: np.ndarray, xu: np.ndarray, eta: float, prob: float, rng: np.random.Generator) -> np.ndarray` — funkcja modułowa; [wiersz 257](../src/pymoo_gui/algorithms/research_common.py#L257).
- `polynomial_mutation(X: np.ndarray, xl: np.ndarray, xu: np.ndarray, eta: float, prob: float, rng: np.random.Generator, strength: float=1.0) -> np.ndarray` — funkcja modułowa; [wiersz 309](../src/pymoo_gui/algorithms/research_common.py#L309).
- `gaussian_mutation(X: np.ndarray, xl: np.ndarray, xu: np.ndarray, prob: float, sigma: float, rng: np.random.Generator) -> np.ndarray` — funkcja modułowa; [wiersz 350](../src/pymoo_gui/algorithms/research_common.py#L350).
- `de_crossover(X: np.ndarray, xl: np.ndarray, xu: np.ndarray, F_weight: np.ndarray, CR: np.ndarray, rng: np.random.Generator) -> np.ndarray` — funkcja modułowa; [wiersz 368](../src/pymoo_gui/algorithms/research_common.py#L368).
- `sample_reference_directions(n_obj: int, population_size: int, n_partitions: int, rng: np.random.Generator, reference_directions: Optional[np.ndarray]=None) -> np.ndarray` — funkcja modułowa; [wiersz 395](../src/pymoo_gui/algorithms/research_common.py#L395).
- `normalized_objectives(F: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]` — funkcja modułowa; [wiersz 421](../src/pymoo_gui/algorithms/research_common.py#L421).
- `associate_to_reference_directions(F: np.ndarray, ref_dirs: np.ndarray) -> tuple[np.ndarray, np.ndarray]` — funkcja modułowa; [wiersz 430](../src/pymoo_gui/algorithms/research_common.py#L430).
- `tchebycheff_scores(F: np.ndarray, ref_dirs: np.ndarray) -> np.ndarray` — funkcja modułowa; [wiersz 446](../src/pymoo_gui/algorithms/research_common.py#L446).
- `shifted_density(F: np.ndarray) -> np.ndarray` — funkcja modułowa; [wiersz 455](../src/pymoo_gui/algorithms/research_common.py#L455).
- `PopulationState.feasible(self) -> np.ndarray` — metoda; [wiersz 481](../src/pymoo_gui/algorithms/research_common.py#L481).
- `ArrayPopulationView.__init__(self, state: Optional[PopulationState])` — metoda; [wiersz 490](../src/pymoo_gui/algorithms/research_common.py#L490).
- `ArrayPopulationView.get(self, name: str) -> Optional[np.ndarray]` — metoda; [wiersz 494](../src/pymoo_gui/algorithms/research_common.py#L494).
- `ResearchMOOAlgorithm.__init__(self, population_size: int=100, archive_size: int=100, crossover_rate: float=0.9, mutation_rate: float=0.1, crossover_eta: float=15.0, mutation_eta: float=20.0, epsilon: float=0.05, n_neighbors: int=15, n_partitions: int=12, reference_directions: Any=None, seed: int=1) -> None` — metoda; [wiersz 513](../src/pymoo_gui/algorithms/research_common.py#L513).
- `ResearchMOOAlgorithm.setup_rng(self, seed: Optional[int]) -> None` — metoda; [wiersz 554](../src/pymoo_gui/algorithms/research_common.py#L554).
- `ResearchMOOAlgorithm.initialize(self, problem: Any) -> None` — metoda; [wiersz 561](../src/pymoo_gui/algorithms/research_common.py#L561).
- `ResearchMOOAlgorithm.after_initialize(self) -> None` — metoda; [wiersz 589](../src/pymoo_gui/algorithms/research_common.py#L589).
- `ResearchMOOAlgorithm.sample_initial_population(self) -> np.ndarray` — metoda; [wiersz 593](../src/pymoo_gui/algorithms/research_common.py#L593).
- `ResearchMOOAlgorithm.warm_start_candidates(self) -> Optional[np.ndarray]` — metoda; [wiersz 597](../src/pymoo_gui/algorithms/research_common.py#L597).
- `ResearchMOOAlgorithm.evaluate(self, X: np.ndarray) -> tuple[np.ndarray, np.ndarray]` — metoda; [wiersz 601](../src/pymoo_gui/algorithms/research_common.py#L601).
- `ResearchMOOAlgorithm.select(self) -> np.ndarray` — metoda; [wiersz 607](../src/pymoo_gui/algorithms/research_common.py#L607).
- `ResearchMOOAlgorithm.crossover(self, parent_pairs: np.ndarray) -> np.ndarray` — metoda; [wiersz 618](../src/pymoo_gui/algorithms/research_common.py#L618).
- `ResearchMOOAlgorithm.mutation(self, offspring: np.ndarray) -> np.ndarray` — metoda; [wiersz 631](../src/pymoo_gui/algorithms/research_common.py#L631).
- `ResearchMOOAlgorithm.guided_candidates(self) -> np.ndarray` — metoda; [wiersz 642](../src/pymoo_gui/algorithms/research_common.py#L642).
- `ResearchMOOAlgorithm.create_offspring(self) -> np.ndarray` — metoda; [wiersz 646](../src/pymoo_gui/algorithms/research_common.py#L646).
- `ResearchMOOAlgorithm.environmental_selection(self, X: np.ndarray, F: np.ndarray, CV: np.ndarray, n_survive: int) -> PopulationState` — metoda; [wiersz 651](../src/pymoo_gui/algorithms/research_common.py#L651).
- `ResearchMOOAlgorithm.build_archive(self, state: PopulationState) -> PopulationState` — metoda; [wiersz 661](../src/pymoo_gui/algorithms/research_common.py#L661).
- `ResearchMOOAlgorithm.archive_elites(self, count: int) -> np.ndarray` — metoda; [wiersz 673](../src/pymoo_gui/algorithms/research_common.py#L673).
- `ResearchMOOAlgorithm.state_centroid(self, state: Optional[PopulationState]=None, elite_fraction: float=0.25) -> np.ndarray` — metoda; [wiersz 680](../src/pymoo_gui/algorithms/research_common.py#L680).
- `ResearchMOOAlgorithm.state_spread(self, state: Optional[PopulationState]=None, elite_fraction: float=0.25) -> np.ndarray` — metoda; [wiersz 688](../src/pymoo_gui/algorithms/research_common.py#L688).
- `ResearchMOOAlgorithm.diversity_score(self, state: Optional[PopulationState]=None) -> float` — metoda; [wiersz 698](../src/pymoo_gui/algorithms/research_common.py#L698).
- `ResearchMOOAlgorithm.progress_score(self, previous: PopulationState, current: PopulationState) -> float` — metoda; [wiersz 708](../src/pymoo_gui/algorithms/research_common.py#L708).
- `ResearchMOOAlgorithm.after_generation(self, previous: PopulationState, current: PopulationState) -> None` — metoda; [wiersz 718](../src/pymoo_gui/algorithms/research_common.py#L718).
- `ResearchMOOAlgorithm._remember_state(self) -> None` — metoda; [wiersz 722](../src/pymoo_gui/algorithms/research_common.py#L722).
- `ResearchMOOAlgorithm._update_population_view(self) -> None` — metoda; [wiersz 739](../src/pymoo_gui/algorithms/research_common.py#L739).
- `ResearchMOOAlgorithm.step(self) -> None` — metoda; [wiersz 743](../src/pymoo_gui/algorithms/research_common.py#L743).
- `ResearchMOOAlgorithm.run(self, n_generations: int, callback: Any=None) -> None` — metoda; [wiersz 766](../src/pymoo_gui/algorithms/research_common.py#L766).
- `ResearchMOOAlgorithm.finalize_result(self) -> Result` — metoda; [wiersz 773](../src/pymoo_gui/algorithms/research_common.py#L773).
- `ResearchMOOAlgorithm.gui_minimize(self, *, problem: Any, termination: Any, seed: Optional[int]=None, callback: Any=None, **kwargs: Any) -> Result` — metoda; [wiersz 783](../src/pymoo_gui/algorithms/research_common.py#L783).

### `src/pymoo_gui/algorithms/rnn_guided_dmo.py`

- `RNNGuidedDMO.__init__(self, population_size: int=100, archive_size: int=100, crossover_rate: float=0.9, mutation_rate: float=0.1, hidden_size: int=16, guided_fraction: float=0.2, prediction_scale: float=0.35, seed: int=1) -> None` — metoda; [wiersz 23](../src/pymoo_gui/algorithms/rnn_guided_dmo.py#L23).
- `RNNGuidedDMO.after_initialize(self) -> None` — metoda; [wiersz 49](../src/pymoo_gui/algorithms/rnn_guided_dmo.py#L49).
- `RNNGuidedDMO._update_hidden(self, centroid: np.ndarray) -> None` — metoda; [wiersz 59](../src/pymoo_gui/algorithms/rnn_guided_dmo.py#L59).
- `RNNGuidedDMO.predict_center(self) -> np.ndarray` — metoda; [wiersz 63](../src/pymoo_gui/algorithms/rnn_guided_dmo.py#L63).
- `RNNGuidedDMO.guided_candidates(self) -> np.ndarray` — metoda; [wiersz 70](../src/pymoo_gui/algorithms/rnn_guided_dmo.py#L70).
- `RNNGuidedDMO.after_generation(self, previous, current) -> None` — metoda; [wiersz 80](../src/pymoo_gui/algorithms/rnn_guided_dmo.py#L80).
- `make_rnn_guided_dmo(population_size: int=100, archive_size: int=100, crossover_rate: float=0.9, mutation_rate: float=0.1, hidden_size: int=16, guided_fraction: float=0.2, prediction_scale: float=0.35, seed: int=1) -> RNNGuidedDMO` — funkcja modułowa; [wiersz 85](../src/pymoo_gui/algorithms/rnn_guided_dmo.py#L85).

### `src/pymoo_gui/algorithms/rnsga3.py`

- `_problem_n_obj(problem: Any) -> int` — funkcja modułowa; [wiersz 22](../src/pymoo_gui/algorithms/rnsga3.py#L22).
- `_parse_positive_int(value: Any, field_name: str) -> int` — funkcja modułowa; [wiersz 40](../src/pymoo_gui/algorithms/rnsga3.py#L40).
- `_parse_non_negative_float(value: Any, field_name: str) -> float` — funkcja modułowa; [wiersz 57](../src/pymoo_gui/algorithms/rnsga3.py#L57).
- `_normalize_ref_points(ref_points: Any, n_obj: int) -> np.ndarray` — funkcja modułowa; [wiersz 75](../src/pymoo_gui/algorithms/rnsga3.py#L75).
- `make_rnsga3(problem: Any, ref_points: Any=None, pop_per_ref_point: int=50, mu: float=0.1) -> RNSGA3` — funkcja modułowa; [wiersz 101](../src/pymoo_gui/algorithms/rnsga3.py#L101).

### `src/pymoo_gui/algorithms/rvea.py`

- `_RveaRanTermination._update(self, algorithm: Any) -> float` — metoda; [wiersz 27](../src/pymoo_gui/algorithms/rvea.py#L27).
- `_parse_positive_int(value: Any, field_name: str) -> int` — funkcja modułowa; [wiersz 38](../src/pymoo_gui/algorithms/rvea.py#L38).
- `_parse_positive_float(value: Any, field_name: str) -> float` — funkcja modułowa; [wiersz 49](../src/pymoo_gui/algorithms/rvea.py#L49).
- `_parse_optional_positive_int(value: Any, field_name: str) -> Optional[int]` — funkcja modułowa; [wiersz 62](../src/pymoo_gui/algorithms/rvea.py#L62).
- `_problem_n_obj(problem: Any) -> int` — funkcja modułowa; [wiersz 69](../src/pymoo_gui/algorithms/rvea.py#L69).
- `_is_no_termination(termination: Any) -> bool` — funkcja modułowa; [wiersz 82](../src/pymoo_gui/algorithms/rvea.py#L82).
- `_rvea_gui_termination(termination: Any) -> Any` — funkcja modułowa; [wiersz 87](../src/pymoo_gui/algorithms/rvea.py#L87).
- `make_rvea(problem: Any, pop_size: Optional[int]=100, n_partitions: int=99, alpha: float=2.0, adapt_freq: float=0.1) -> RVEA` — funkcja modułowa; [wiersz 94](../src/pymoo_gui/algorithms/rvea.py#L94).
- `make_rvea.gui_minimize(*, problem: Any, termination: Any, **kwargs: Any) -> Any` — funkcja zagnieżdżona; [wiersz 125](../src/pymoo_gui/algorithms/rvea.py#L125).

### `src/pymoo_gui/algorithms/spea2.py`

- `_parse_positive_int(value: Any, field_name: str) -> int` — funkcja modułowa; [wiersz 28](../src/pymoo_gui/algorithms/spea2.py#L28).
- `binary_tournament(pop, P, algorithm, **kwargs)` — funkcja modułowa; [wiersz 41](../src/pymoo_gui/algorithms/spea2.py#L41).
- `RankAndCrowdingSurvival.__init__(self, nds=None, crowding_func: str='cd')` — metoda; [wiersz 104](../src/pymoo_gui/algorithms/spea2.py#L104).
- `SPEA2.__init__(self, pop_size=100, sampling=FloatRandomSampling(), selection=TournamentSelection(func_comp=binary_tournament), crossover=SBX(eta=15, prob=0.9), mutation=PM(eta=20), survival=RankAndCrowdingSurvival(), output=MultiObjectiveOutput(), **kwargs)` — metoda; [wiersz 113](../src/pymoo_gui/algorithms/spea2.py#L113).
- `SPEA2._set_optimum(self, **kwargs)` — metoda; [wiersz 146](../src/pymoo_gui/algorithms/spea2.py#L146).
- `make_spea2(pop_size: int=100) -> SPEA2` — funkcja modułowa; [wiersz 157](../src/pymoo_gui/algorithms/spea2.py#L157).

### `src/pymoo_gui/algorithms/ts_nsga.py`

- `TSNSGA.__init__(self, population_size: int=100, archive_size: int=100, crossover_rate: float=0.9, mutation_rate: float=0.1, stage_fraction: float=0.3, local_search_scale: float=0.15, seed: int=1) -> None` — metoda; [wiersz 28](../src/pymoo_gui/algorithms/ts_nsga.py#L28).
- `TSNSGA.guided_candidates(self) -> np.ndarray` — metoda; [wiersz 48](../src/pymoo_gui/algorithms/ts_nsga.py#L48).
- `make_ts_nsga(population_size: int=100, archive_size: int=100, crossover_rate: float=0.9, mutation_rate: float=0.1, stage_fraction: float=0.3, local_search_scale: float=0.15, seed: int=1) -> TSNSGA` — funkcja modułowa; [wiersz 62](../src/pymoo_gui/algorithms/ts_nsga.py#L62).

### `src/pymoo_gui/algoritms/__init__.py`

Brak deklaracji funkcji i wyrażeń `lambda`.

### `src/pymoo_gui/app.py`

- `NoTermination.__init__(self)` — metoda; [wiersz 66](../src/pymoo_gui/app.py#L66).
- `NoTermination.update(self, algorithm)` — metoda; [wiersz 71](../src/pymoo_gui/app.py#L71).
- `NoTermination.has_terminated(self)` — metoda; [wiersz 76](../src/pymoo_gui/app.py#L76).
- `NoTermination.do_continue(self)` — metoda; [wiersz 80](../src/pymoo_gui/app.py#L80).
- `translate_ui_text(text: Any) -> str` — funkcja modułowa; [wiersz 264](../src/pymoo_gui/app.py#L264).
- `pl_param_label(name: str) -> str` — funkcja modułowa; [wiersz 322](../src/pymoo_gui/app.py#L322).
- `callable_signature(obj: Any) -> inspect.Signature` — funkcja modułowa; [wiersz 327](../src/pymoo_gui/app.py#L327).
- `filter_callable_kwargs(fn: Any, params: Mapping[str, Any]) -> Dict[str, Any]` — funkcja modułowa; [wiersz 332](../src/pymoo_gui/app.py#L332).
- `_literal_or_str(value: str) -> Any` — funkcja modułowa; [wiersz 344](../src/pymoo_gui/app.py#L344).
- `should_save_nondominated_solutions_for_epoch(epoch: Any, mode: str, step: int=1, *, is_final: bool=False) -> bool` — funkcja modułowa; [wiersz 355](../src/pymoo_gui/app.py#L355).
- `_specs(raw_specs: Optional[Any]) -> list[FieldSpec]` — funkcja modułowa; [wiersz 401](../src/pymoo_gui/app.py#L401).
- `ParamForm.__init__(self, title: str, parent=None)` — metoda; [wiersz 437](../src/pymoo_gui/app.py#L437).
- `ParamForm.clear(self) -> None` — metoda; [wiersz 446](../src/pymoo_gui/app.py#L446).
- `ParamForm.binding(self, name: str) -> Optional[WidgetBinding]` — metoda; [wiersz 452](../src/pymoo_gui/app.py#L452).
- `ParamForm.bindings(self) -> Sequence[WidgetBinding]` — metoda; [wiersz 456](../src/pymoo_gui/app.py#L456).
- `ParamForm.build_for_callable(self, fn: Any, extra_fields: Optional[Any]=None) -> None` — metoda; [wiersz 460](../src/pymoo_gui/app.py#L460).
- `ParamForm.build_for_signature(self, sig: inspect.Signature, extra_fields: Optional[Any]=None) -> None` — metoda; [wiersz 464](../src/pymoo_gui/app.py#L464).
- `ParamForm.build_from_specs(self, raw_specs: Optional[Any]) -> None` — metoda; [wiersz 479](../src/pymoo_gui/app.py#L479).
- `ParamForm._kind(self, annotation: Any, default: Any) -> str` — metoda; [wiersz 485](../src/pymoo_gui/app.py#L485).
- `ParamForm._bounds(self, spec: FieldSpec) -> Tuple[float, float]` — metoda; [wiersz 497](../src/pymoo_gui/app.py#L497).
- `ParamForm._apply_read_only(self, widget: Any, spec: FieldSpec) -> None` — metoda; [wiersz 516](../src/pymoo_gui/app.py#L516).
- `ParamForm._add_field(self, spec: FieldSpec) -> None` — metoda; [wiersz 529](../src/pymoo_gui/app.py#L529).
- `ParamForm.values(self) -> Dict[str, Any]` — metoda; [wiersz 571](../src/pymoo_gui/app.py#L571).
- `OptimizationWorker.__init__(self, problem_key: str, alg_key: str, problem_params: Mapping[str, Any], algorithm_params: Mapping[str, Any], n_gen: Optional[int], seed: int, verbose: bool, hv_ref_point: Optional[list[float]], parallel_eval: bool=False, parallel_workers: int=1, parallel_backend: str='process', parent=None, step_mode: bool=False)` — metoda; [wiersz 605](../src/pymoo_gui/app.py#L605).
- `OptimizationWorker.request_cancel(self) -> None` — metoda; [wiersz 640](../src/pymoo_gui/app.py#L640).
- `OptimizationWorker.request_next_epoch(self) -> bool` — metoda; [wiersz 647](../src/pymoo_gui/app.py#L647).
- `OptimizationWorker._cancel_pending(self) -> bool` — metoda; [wiersz 656](../src/pymoo_gui/app.py#L656).
- `OptimizationWorker._emit_generation(self, payload: dict) -> None` — metoda; [wiersz 660](../src/pymoo_gui/app.py#L660).
- `OptimizationWorker.run(self) -> None` — metoda; [wiersz 676](../src/pymoo_gui/app.py#L676).
- `MainWindow.__init__(self)` — metoda; [wiersz 728](../src/pymoo_gui/app.py#L728).
- `MainWindow._apply_default_window_geometry(self) -> None` — metoda; [wiersz 766](../src/pymoo_gui/app.py#L766).
- `MainWindow.showEvent(self, event) -> None` — metoda; [wiersz 774](../src/pymoo_gui/app.py#L774).
- `MainWindow._make_window_square(self) -> None` — metoda; [wiersz 781](../src/pymoo_gui/app.py#L781).
- `MainWindow._build_ui(self) -> None` — metoda; [wiersz 786](../src/pymoo_gui/app.py#L786).
- `MainWindow._build_checkable_registry_list(self, registry: Mapping[str, Dict[str, Any]]) -> QListWidget` — metoda; [wiersz 817](../src/pymoo_gui/app.py#L817).
- `MainWindow._build_multi_selection_group(self, title: str, widget: QListWidget) -> QGroupBox` — metoda; [wiersz 829](../src/pymoo_gui/app.py#L829).
- `MainWindow._build_multi_panel(self) -> QWidget` — metoda; [wiersz 844](../src/pymoo_gui/app.py#L844).
- `MainWindow._apply_english_ui_texts(self) -> None` — metoda; [wiersz 929](../src/pymoo_gui/app.py#L929).
- `MainWindow._build_controls_panel(self) -> QWidget` — metoda; [wiersz 949](../src/pymoo_gui/app.py#L949).
- `MainWindow._build_results_panel(self) -> QWidget` — metoda; [wiersz 961](../src/pymoo_gui/app.py#L961).
- `MainWindow._build_problem_controls(self) -> None` — metoda; [wiersz 1024](../src/pymoo_gui/app.py#L1024).
- `MainWindow._build_hv_controls(self) -> None` — metoda; [wiersz 1043](../src/pymoo_gui/app.py#L1043).
- `MainWindow._build_run_controls(self) -> None` — metoda; [wiersz 1062](../src/pymoo_gui/app.py#L1062).
- `MainWindow._build_console(self) -> None` — metoda; [wiersz 1111](../src/pymoo_gui/app.py#L1111).
- `MainWindow._connect_signals(self) -> None` — metoda; [wiersz 1121](../src/pymoo_gui/app.py#L1121).
- `MainWindow._configure_placeholders(self) -> None` — metoda; [wiersz 1160](../src/pymoo_gui/app.py#L1160).
- `MainWindow._set_all_multi_items(self, widget: QListWidget, checked: bool) -> None` — metoda; [wiersz 1176](../src/pymoo_gui/app.py#L1176).
- `MainWindow._checked_multi_keys(self, widget: QListWidget) -> list[str]` — metoda; [wiersz 1189](../src/pymoo_gui/app.py#L1189).
- `MainWindow._update_multi_selection_state(self, *_args: Any) -> None` — metoda; [wiersz 1200](../src/pymoo_gui/app.py#L1200).
- `MainWindow._set_multi_running_state(self, running: bool) -> None` — metoda; [wiersz 1213](../src/pymoo_gui/app.py#L1213).
- `MainWindow._multi_row_key(self, payload: Mapping[str, Any]) -> tuple[str, str]` — metoda; [wiersz 1229](../src/pymoo_gui/app.py#L1229).
- `MainWindow._set_multi_table_value(self, row: int, column: int, value: Any) -> None` — metoda; [wiersz 1233](../src/pymoo_gui/app.py#L1233).
- `MainWindow._on_multi_run_started(self, payload: Mapping[str, Any]) -> None` — metoda; [wiersz 1240](../src/pymoo_gui/app.py#L1240).
- `MainWindow._on_multi_run_progress(self, payload: Mapping[str, Any]) -> None` — metoda; [wiersz 1264](../src/pymoo_gui/app.py#L1264).
- `MainWindow._on_multi_run_finished(self, payload: Mapping[str, Any]) -> None` — metoda; [wiersz 1283](../src/pymoo_gui/app.py#L1283).
- `MainWindow.start_multi_experiment(self) -> None` — metoda; [wiersz 1309](../src/pymoo_gui/app.py#L1309).
- `MainWindow.stop_multi_experiment(self) -> None` — metoda; [wiersz 1360](../src/pymoo_gui/app.py#L1360).
- `MainWindow._finish_multi_experiment(self, status: str, results: Sequence[Mapping[str, Any]]) -> None` — metoda; [wiersz 1370](../src/pymoo_gui/app.py#L1370).
- `MainWindow._on_multi_experiment_done(self, results: Sequence[Mapping[str, Any]]) -> None` — metoda; [wiersz 1386](../src/pymoo_gui/app.py#L1386).
- `MainWindow._on_multi_experiment_cancelled(self, results: Sequence[Mapping[str, Any]]) -> None` — metoda; [wiersz 1390](../src/pymoo_gui/app.py#L1390).
- `MainWindow._on_multi_experiment_failed(self, error: str) -> None` — metoda; [wiersz 1394](../src/pymoo_gui/app.py#L1394).
- `MainWindow._entry(self, combo: QComboBox, registry: Mapping[str, Dict[str, Any]]) -> Dict[str, Any]` — metoda; [wiersz 1402](../src/pymoo_gui/app.py#L1402).
- `MainWindow._known_pf_for_problem(self, entry: Mapping[str, Any], problem: Any) -> Optional[np.ndarray]` — metoda; [wiersz 1407](../src/pymoo_gui/app.py#L1407).
- `MainWindow._instantiate_selected_problem(self, params: Optional[Mapping[str, Any]]=None) -> Tuple[Optional[Any], Optional[str]]` — metoda; [wiersz 1428](../src/pymoo_gui/app.py#L1428).
- `MainWindow._connect_problem_form_signals(self) -> None` — metoda; [wiersz 1443](../src/pymoo_gui/app.py#L1443).
- `MainWindow._ensure_plot_widget(self) -> UnifiedParetoWidget` — metoda; [wiersz 1456](../src/pymoo_gui/app.py#L1456).
- `MainWindow._reset_plot_axes(self) -> None` — metoda; [wiersz 1481](../src/pymoo_gui/app.py#L1481).
- `MainWindow._set_plot_message(self, text: str) -> None` — metoda; [wiersz 1486](../src/pymoo_gui/app.py#L1486).
- `MainWindow._reset_plot_run_data(self) -> None` — metoda; [wiersz 1494](../src/pymoo_gui/app.py#L1494).
- `MainWindow._update_epoch_controls(self) -> None` — metoda; [wiersz 1502](../src/pymoo_gui/app.py#L1502).
- `MainWindow._remember_epoch(self, payload: Mapping[str, Any]) -> None` — metoda; [wiersz 1515](../src/pymoo_gui/app.py#L1515).
- `MainWindow._show_epoch(self, epoch: int) -> None` — metoda; [wiersz 1527](../src/pymoo_gui/app.py#L1527).
- `MainWindow._move_epoch(self, direction: int) -> None` — metoda; [wiersz 1536](../src/pymoo_gui/app.py#L1536).
- `MainWindow._show_latest_epoch(self) -> None` — metoda; [wiersz 1542](../src/pymoo_gui/app.py#L1542).
- `MainWindow._apply_grid_options(self, *_args: Any) -> None` — metoda; [wiersz 1546](../src/pymoo_gui/app.py#L1546).
- `MainWindow._export_window_screenshot(self) -> None` — metoda; [wiersz 1551](../src/pymoo_gui/app.py#L1551).
- `MainWindow._export_plot_png(self) -> None` — metoda; [wiersz 1567](../src/pymoo_gui/app.py#L1567).
- `MainWindow._run_next_epoch(self) -> None` — metoda; [wiersz 1583](../src/pymoo_gui/app.py#L1583).
- `MainWindow._reset_run_result_state(self) -> None` — metoda; [wiersz 1592](../src/pymoo_gui/app.py#L1592).
- `MainWindow._update_run_form_state(self) -> None` — metoda; [wiersz 1598](../src/pymoo_gui/app.py#L1598).
- `MainWindow._current_nd_save_mode(self) -> str` — metoda; [wiersz 1622](../src/pymoo_gui/app.py#L1622).
- `MainWindow._update_nd_save_controls_state(self) -> None` — metoda; [wiersz 1627](../src/pymoo_gui/app.py#L1627).
- `MainWindow._collect_nd_save_args(self) -> Tuple[Optional[dict], Optional[str]]` — metoda; [wiersz 1631](../src/pymoo_gui/app.py#L1631).
- `MainWindow._set_run_state(self, status_text: str, running: bool) -> None` — metoda; [wiersz 1641](../src/pymoo_gui/app.py#L1641).
- `MainWindow._apply_generation_payload(self, payload: Mapping[str, Any]) -> None` — metoda; [wiersz 1657](../src/pymoo_gui/app.py#L1657).
- `MainWindow._apply_problem_preview_state(self, problem: Any) -> None` — metoda; [wiersz 1666](../src/pymoo_gui/app.py#L1666).
- `MainWindow._refresh_problem_plot(self) -> None` — metoda; [wiersz 1676](../src/pymoo_gui/app.py#L1676).
- `MainWindow._render_plot(self) -> None` — metoda; [wiersz 1690](../src/pymoo_gui/app.py#L1690).
- `MainWindow._rebuild_problem_form(self) -> None` — metoda; [wiersz 1707](../src/pymoo_gui/app.py#L1707).
- `MainWindow._rebuild_alg_form(self) -> None` — metoda; [wiersz 1718](../src/pymoo_gui/app.py#L1718).
- `MainWindow._connect_problem_param_signals(self) -> None` — metoda; [wiersz 1724](../src/pymoo_gui/app.py#L1724).
- `MainWindow._on_n_obj_changed(self, _value: int) -> None` — metoda; [wiersz 1741](../src/pymoo_gui/app.py#L1741).
- `MainWindow._on_problem_form_changed(self, *_args: Any) -> None` — metoda; [wiersz 1746](../src/pymoo_gui/app.py#L1746).
- `MainWindow._on_show_population_toggled(self, checked: bool) -> None` — metoda; [wiersz 1750](../src/pymoo_gui/app.py#L1750).
- `MainWindow._on_hide_pareto_front_toggled(self, checked: bool) -> None` — metoda; [wiersz 1755](../src/pymoo_gui/app.py#L1755).
- `MainWindow._on_auto_scale_toggled(self, checked: bool) -> None` — metoda; [wiersz 1762](../src/pymoo_gui/app.py#L1762).
- `MainWindow._on_nd_save_mode_changed(self, _index: int) -> None` — metoda; [wiersz 1771](../src/pymoo_gui/app.py#L1771).
- `MainWindow._on_ran_toggled(self, checked: bool) -> None` — metoda; [wiersz 1775](../src/pymoo_gui/app.py#L1775).
- `MainWindow._on_parallel_eval_toggled(self, checked: bool) -> None` — metoda; [wiersz 1780](../src/pymoo_gui/app.py#L1780).
- `MainWindow._toggle_console_dock(self) -> None` — metoda; [wiersz 1785](../src/pymoo_gui/app.py#L1785).
- `MainWindow._on_console_visibility_changed(self, visible: bool) -> None` — metoda; [wiersz 1789](../src/pymoo_gui/app.py#L1789).
- `MainWindow._log(self, msg: str) -> None` — metoda; [wiersz 1793](../src/pymoo_gui/app.py#L1793).
- `MainWindow._warn(self, title: str, message: str, log_message: Optional[str]=None) -> None` — metoda; [wiersz 1799](../src/pymoo_gui/app.py#L1799).
- `MainWindow._current_n_obj(self) -> int` — metoda; [wiersz 1805](../src/pymoo_gui/app.py#L1805).
- `MainWindow._parse_float_token(self, token: str) -> Optional[float]` — metoda; [wiersz 1818](../src/pymoo_gui/app.py#L1818).
- `MainWindow._parse_ref_point_text(self, text: str) -> Tuple[Optional[list[float]], Optional[str]]` — metoda; [wiersz 1836](../src/pymoo_gui/app.py#L1836).
- `MainWindow._auto_hv_ref_point(self) -> list[float]` — metoda; [wiersz 1857](../src/pymoo_gui/app.py#L1857).
- `MainWindow._hv_ref_point_state(self) -> Tuple[bool, Optional[list[float]], str, Optional[str]]` — metoda; [wiersz 1861](../src/pymoo_gui/app.py#L1861).
- `MainWindow._validate_hv_manual_ref_point(self) -> bool` — metoda; [wiersz 1876](../src/pymoo_gui/app.py#L1876).
- `MainWindow._update_hv_ref_point_label(self) -> None` — metoda; [wiersz 1887](../src/pymoo_gui/app.py#L1887).
- `MainWindow._on_hv_mode_changed(self, _checked: bool) -> None` — metoda; [wiersz 1897](../src/pymoo_gui/app.py#L1897).
- `MainWindow._on_hv_manual_changed(self, _text: str) -> None` — metoda; [wiersz 1906](../src/pymoo_gui/app.py#L1906).
- `MainWindow._on_live_updates_toggled(self, checked: bool) -> None` — metoda; [wiersz 1911](../src/pymoo_gui/app.py#L1911).
- `MainWindow._update_run_button_state(self) -> None` — metoda; [wiersz 1916](../src/pymoo_gui/app.py#L1916).
- `MainWindow._update_plot_status(self, payload: Optional[dict]=None, message: Optional[str]=None) -> None` — metoda; [wiersz 1926](../src/pymoo_gui/app.py#L1926).
- `MainWindow._fmt_int(self, value: Optional[int]) -> str` — metoda; [wiersz 1942](../src/pymoo_gui/app.py#L1942).
- `MainWindow._fmt_metric(self, value: Optional[float]) -> str` — metoda; [wiersz 1949](../src/pymoo_gui/app.py#L1949).
- `MainWindow._update_metrics_label(self, payload: Optional[dict]) -> None` — metoda; [wiersz 1956](../src/pymoo_gui/app.py#L1956).
- `MainWindow._metrics_label_text(self, payload: Mapping[str, Any]) -> str` — metoda; [wiersz 1960](../src/pymoo_gui/app.py#L1960).
- `MainWindow._clear_table(self) -> None` — metoda; [wiersz 1966](../src/pymoo_gui/app.py#L1966).
- `MainWindow._should_scroll_table(self) -> bool` — metoda; [wiersz 1971](../src/pymoo_gui/app.py#L1971).
- `MainWindow._append_generation_row(self, payload: dict) -> None` — metoda; [wiersz 1976](../src/pymoo_gui/app.py#L1976).
- `MainWindow._append_last_payload_once(self, payload: Mapping[str, Any]) -> None` — metoda; [wiersz 1999](../src/pymoo_gui/app.py#L1999).
- `MainWindow._metrics_table_data(self) -> Tuple[list[str], list[list[str]]]` — metoda; [wiersz 2007](../src/pymoo_gui/app.py#L2007).
- `MainWindow._export_metrics_table(self) -> None` — metoda; [wiersz 2023](../src/pymoo_gui/app.py#L2023).
- `MainWindow._xlsx_value(self, value: Any) -> object` — metoda; [wiersz 2042](../src/pymoo_gui/app.py#L2042).
- `MainWindow._solution_table_data(self, payload: Mapping[str, Any]) -> Tuple[list[str], list[list[object]]]` — metoda; [wiersz 2054](../src/pymoo_gui/app.py#L2054).
- `MainWindow._export_solution_table(self, payload: Mapping[str, Any]) -> None` — metoda; [wiersz 2095](../src/pymoo_gui/app.py#L2095).
- `MainWindow._export_nondominated_solutions_for_epoch(self, payload: Mapping[str, Any]) -> None` — metoda; [wiersz 2124](../src/pymoo_gui/app.py#L2124).
- `MainWindow._export_nondominated_solutions_for_final_epoch(self, payload: Mapping[str, Any]) -> None` — metoda; [wiersz 2144](../src/pymoo_gui/app.py#L2144).
- `MainWindow._validated_int(self, value: Any, label: str, minimum: int) -> Tuple[Optional[int], Optional[str]]` — metoda; [wiersz 2169](../src/pymoo_gui/app.py#L2169).
- `MainWindow._collect_run_args(self) -> Tuple[Optional[dict], Optional[str]]` — metoda; [wiersz 2181](../src/pymoo_gui/app.py#L2181).
- `MainWindow._collect_algorithm_args(self) -> Tuple[Optional[dict], Optional[str]]` — metoda; [wiersz 2209](../src/pymoo_gui/app.py#L2209).
- `MainWindow._collect_problem_args(self) -> Tuple[dict, Optional[str]]` — metoda; [wiersz 2219](../src/pymoo_gui/app.py#L2219).
- `MainWindow._prepare_run_visuals(self) -> None` — metoda; [wiersz 2223](../src/pymoo_gui/app.py#L2223).
- `MainWindow._finish_run(self, status_text: str, last_payload: Optional[dict]) -> None` — metoda; [wiersz 2237](../src/pymoo_gui/app.py#L2237).
- `MainWindow._on_generation(self, payload: dict) -> None` — metoda; [wiersz 2256](../src/pymoo_gui/app.py#L2256).
- `MainWindow.start_run(self, _checked: bool=False, *, step_mode: bool=False) -> None` — metoda; [wiersz 2279](../src/pymoo_gui/app.py#L2279).
- `MainWindow.stop_run(self) -> None` — metoda; [wiersz 2381](../src/pymoo_gui/app.py#L2381).
- `MainWindow._on_run_done(self, last_payload: dict) -> None` — metoda; [wiersz 2392](../src/pymoo_gui/app.py#L2392).
- `MainWindow._on_run_cancelled(self, last_payload: dict) -> None` — metoda; [wiersz 2396](../src/pymoo_gui/app.py#L2396).
- `MainWindow._on_run_failed(self, err: str) -> None` — metoda; [wiersz 2401](../src/pymoo_gui/app.py#L2401).
- `MainWindow._clear_console_and_visuals(self) -> None` — metoda; [wiersz 2410](../src/pymoo_gui/app.py#L2410).
- `MainWindow.closeEvent(self, event) -> None` — metoda; [wiersz 2423](../src/pymoo_gui/app.py#L2423).
- `main() -> None` — funkcja modułowa; [wiersz 2437](../src/pymoo_gui/app.py#L2437).
- `lambda` — wyrażenie anonimowe; [wiersz 837](../src/pymoo_gui/app.py#L837).
- `lambda` — wyrażenie anonimowe; [wiersz 838](../src/pymoo_gui/app.py#L838).
- `lambda` — wyrażenie anonimowe; [wiersz 1135](../src/pymoo_gui/app.py#L1135).
- `lambda` — wyrażenie anonimowe; [wiersz 1136](../src/pymoo_gui/app.py#L1136).

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
- `_safe_float(x) -> Optional[float]` — funkcja modułowa; [wiersz 62](../src/pymoo_gui/metrics/quality.py#L62).
- `_as_2d(arr: Optional[np.ndarray], n_obj: Optional[int]=None) -> Optional[np.ndarray]` — funkcja modułowa; [wiersz 70](../src/pymoo_gui/metrics/quality.py#L70).
- `_as_decision_matrix(values: Optional[np.ndarray], n_var: Optional[int]=None) -> Optional[np.ndarray]` — funkcja modułowa; [wiersz 89](../src/pymoo_gui/metrics/quality.py#L89).
- `_finite_rows(arr: np.ndarray) -> np.ndarray` — funkcja modułowa; [wiersz 106](../src/pymoo_gui/metrics/quality.py#L106).
- `_safe_solve(A: np.ndarray, b: np.ndarray) -> Optional[np.ndarray]` — funkcja modułowa; [wiersz 112](../src/pymoo_gui/metrics/quality.py#L112).
- `_problem_n_ieq_constr(problem: Any) -> int` — funkcja modułowa; [wiersz 123](../src/pymoo_gui/metrics/quality.py#L123).
- `_problem_bounds(problem: Any, n_var: int) -> tuple[np.ndarray, np.ndarray]` — funkcja modułowa; [wiersz 135](../src/pymoo_gui/metrics/quality.py#L135).
- `_problem_bounds._bound(name: str, fill: float) -> np.ndarray` — funkcja zagnieżdżona; [wiersz 137](../src/pymoo_gui/metrics/quality.py#L137).
- `_evaluate_fg(problem: Any, X: np.ndarray) -> Optional[tuple[np.ndarray, np.ndarray]]` — funkcja modułowa; [wiersz 156](../src/pymoo_gui/metrics/quality.py#L156).
- `_valid_derivative(values: Any, expected_shape: tuple[int, int, int]) -> Optional[np.ndarray]` — funkcja modułowa; [wiersz 180](../src/pymoo_gui/metrics/quality.py#L180).
- `_finite_difference_derivatives(problem: Any, X: np.ndarray, F: np.ndarray, G: np.ndarray, eps: float=FINITE_DIFF_EPS) -> tuple[Optional[np.ndarray], Optional[np.ndarray]]` — funkcja modułowa; [wiersz 191](../src/pymoo_gui/metrics/quality.py#L191).
- `_evaluate_kktpm_inputs(X: np.ndarray, problem: Any, finite_diff_eps: float=FINITE_DIFF_EPS) -> Optional[tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]]` — funkcja modułowa; [wiersz 253](../src/pymoo_gui/metrics/quality.py#L253).
- `_append_bound_constraints(problem: Any, X: np.ndarray, G: np.ndarray, dG: np.ndarray) -> tuple[np.ndarray, np.ndarray]` — funkcja modułowa; [wiersz 291](../src/pymoo_gui/metrics/quality.py#L291).
- `_calc_cv(G: np.ndarray) -> np.ndarray` — funkcja modułowa; [wiersz 334](../src/pymoo_gui/metrics/quality.py#L334).
- `compute_spread(F: np.ndarray) -> Optional[float]` — funkcja modułowa; [wiersz 341](../src/pymoo_gui/metrics/quality.py#L341).
- `compute_delta(F: np.ndarray, pareto_front: np.ndarray) -> Optional[float]` — funkcja modułowa; [wiersz 371](../src/pymoo_gui/metrics/quality.py#L371).
- `compute_kktpm(X: np.ndarray, problem: Any, ideal: Optional[np.ndarray]=None, utopian_eps: float=0.0001, rho: float=0.001, finite_diff_eps: float=FINITE_DIFF_EPS) -> Optional[np.ndarray]` — funkcja modułowa; [wiersz 417](../src/pymoo_gui/metrics/quality.py#L417).
- `_feasibility_mask_from_cv(cv: Optional[np.ndarray]) -> Optional[np.ndarray]` — funkcja modułowa; [wiersz 534](../src/pymoo_gui/metrics/quality.py#L534).
- `compute_metrics(F: np.ndarray, pareto_front: Optional[np.ndarray], cv: Optional[np.ndarray]=None, ref_point: Optional[np.ndarray]=None, n_obj: Optional[int]=None, X: Optional[np.ndarray]=None, problem: Any=None, kktpm_ideal: Optional[np.ndarray]=None, delta_supported: bool=True) -> MetricResult` — funkcja modułowa; [wiersz 549](../src/pymoo_gui/metrics/quality.py#L549).
- `get_hv_ref_point(problem_name: Optional[str], n_obj: Optional[int]) -> Optional[np.ndarray]` — funkcja modułowa; [wiersz 681](../src/pymoo_gui/metrics/quality.py#L681).
- `fixed_ref_point_for_problem(problem_name: Optional[str], n_obj: Optional[int]) -> Optional[np.ndarray]` — funkcja modułowa; [wiersz 697](../src/pymoo_gui/metrics/quality.py#L697).

### `src/pymoo_gui/multi.py`

- `default_entry_params(entry: Mapping[str, Any]) -> dict[str, Any]` — funkcja modułowa; [wiersz 45](../src/pymoo_gui/multi.py#L45).
- `filter_callable_kwargs(fn: Any, params: Mapping[str, Any]) -> dict[str, Any]` — funkcja modułowa; [wiersz 59](../src/pymoo_gui/multi.py#L59).
- `build_multi_run_specs(problem_keys: Sequence[str], algorithm_keys: Sequence[str]) -> list[MultiRunSpec]` — funkcja modułowa; [wiersz 71](../src/pymoo_gui/multi.py#L71).
- `metrics_table_data(history: Sequence[Mapping[str, Any]]) -> tuple[list[str], list[list[object]]]` — funkcja modułowa; [wiersz 96](../src/pymoo_gui/multi.py#L96).
- `_xlsx_value(value: Any) -> object` — funkcja modułowa; [wiersz 111](../src/pymoo_gui/multi.py#L111).
- `solution_table_data(payload: Mapping[str, Any], n_obj: int) -> tuple[list[str], list[list[object]]]` — funkcja modułowa; [wiersz 124](../src/pymoo_gui/multi.py#L124).
- `MultiExperimentWorker.__init__(self, specs: Sequence[MultiRunSpec], n_gen: int, seed: int, project_root: Path, parent=None) -> None` — metoda; [wiersz 182](../src/pymoo_gui/multi.py#L182).
- `MultiExperimentWorker.request_cancel(self) -> None` — metoda; [wiersz 201](../src/pymoo_gui/multi.py#L201).
- `MultiExperimentWorker._cancel_pending(self) -> bool` — metoda; [wiersz 206](../src/pymoo_gui/multi.py#L206).
- `MultiExperimentWorker._write_result_files(self, spec: MultiRunSpec, history: Sequence[Mapping[str, Any]], last_payload: Mapping[str, Any], n_obj: int) -> tuple[Optional[Path], Optional[Path], list[str]]` — metoda; [wiersz 210](../src/pymoo_gui/multi.py#L210).
- `MultiExperimentWorker._execute_spec(self, spec: MultiRunSpec, index: int, total: int) -> dict[str, Any]` — metoda; [wiersz 239](../src/pymoo_gui/multi.py#L239).
- `MultiExperimentWorker._execute_spec.on_generation(payload: Mapping[str, Any]) -> None` — funkcja zagnieżdżona; [wiersz 277](../src/pymoo_gui/multi.py#L277).
- `MultiExperimentWorker.run(self) -> None` — metoda; [wiersz 362](../src/pymoo_gui/multi.py#L362).

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

### `src/pymoo_gui/problems/constrex.py`

- `ConstrExProblem.__init__(self)` — metoda; [wiersz 22](../src/pymoo_gui/problems/constrex.py#L22).
- `ConstrExProblem._evaluate(self, X, out, *args, **kwargs)` — metoda; [wiersz 31](../src/pymoo_gui/problems/constrex.py#L31).

### `src/pymoo_gui/problems/empty_benchmark_template.py`

- `EmptyBenchmarkTemplate.__init__(self, n_var: int=10, n_obj: int=2, lower_bound: float=-1.0, upper_bound: float=1.0) -> None` — metoda; [wiersz 26](../src/pymoo_gui/problems/empty_benchmark_template.py#L26).
- `EmptyBenchmarkTemplate._evaluate(self, X, out, *args, **kwargs) -> None` — metoda; [wiersz 61](../src/pymoo_gui/problems/empty_benchmark_template.py#L61).
- `empty_benchmark_known_pf(problem: EmptyBenchmarkTemplate, n_points: int=200) -> Optional[np.ndarray]` — funkcja modułowa; [wiersz 89](../src/pymoo_gui/problems/empty_benchmark_template.py#L89).
- `make_empty_benchmark_template(n_var: int=10, n_obj: int=2, lower_bound: float=-1.0, upper_bound: float=1.0) -> EmptyBenchmarkTemplate` — funkcja modułowa; [wiersz 104](../src/pymoo_gui/problems/empty_benchmark_template.py#L104).

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

### `src/pymoo_gui/problems/osyczka2.py`

- `Osyczka2Problem.__init__(self)` — metoda; [wiersz 22](../src/pymoo_gui/problems/osyczka2.py#L22).
- `Osyczka2Problem._evaluate(self, X, out, *args, **kwargs)` — metoda; [wiersz 31](../src/pymoo_gui/problems/osyczka2.py#L31).

### `src/pymoo_gui/problems/registry.py`

- `_problem_entry(label: str, factory: Any, form_fields: Dict[str, Dict[str, Any]], form_note: str, known_pf_factory: Any=None) -> Dict[str, Any]` — funkcja modułowa; [wiersz 60](../src/pymoo_gui/problems/registry.py#L60).
- `_normalize_pf(values: Any, expected_n_obj: int | None=None) -> np.ndarray | None` — funkcja modułowa; [wiersz 77](../src/pymoo_gui/problems/registry.py#L77).
- `_load_pf_file(filename: str, expected_n_obj: int | None=None) -> np.ndarray | None` — funkcja modułowa; [wiersz 98](../src/pymoo_gui/problems/registry.py#L98).
- `_pf_file_loader(filename: str, expected_n_obj: int)` — funkcja modułowa; [wiersz 110](../src/pymoo_gui/problems/registry.py#L110).
- `_zdt_known_pf(problem: Any) -> np.ndarray | None` — funkcja modułowa; [wiersz 115](../src/pymoo_gui/problems/registry.py#L115).
- `_dtlz_reference_directions(n_obj: int, target_points: int) -> np.ndarray` — funkcja modułowa; [wiersz 127](../src/pymoo_gui/problems/registry.py#L127).
- `_dtlz_degenerate_known_pf(n_obj: int, n_points: int=1000) -> np.ndarray` — funkcja modułowa; [wiersz 136](../src/pymoo_gui/problems/registry.py#L136).
- `_dtlz7_known_pf(n_obj: int, target_points: int=2000) -> np.ndarray` — funkcja modułowa; [wiersz 155](../src/pymoo_gui/problems/registry.py#L155).
- `_dtlz_known_pf(problem: Any, target_points: int=2000) -> np.ndarray | None` — funkcja modułowa; [wiersz 175](../src/pymoo_gui/problems/registry.py#L175).
- `_readonly_n_obj_field(label: str, n_obj: int) -> Dict[str, Any]` — funkcja modułowa; [wiersz 198](../src/pymoo_gui/problems/registry.py#L198).
- `_n_var_field(label: str, default: int, minimum: int=1) -> Dict[str, Any]` — funkcja modułowa; [wiersz 207](../src/pymoo_gui/problems/registry.py#L207).
- `_zdt_entry(name: str, default_n_var: int) -> Dict[str, Any]` — funkcja modułowa; [wiersz 216](../src/pymoo_gui/problems/registry.py#L216).
- `_dtlz_entry(name: str, default_n_var: int, default_n_obj: int=3) -> Dict[str, Any]` — funkcja modułowa; [wiersz 231](../src/pymoo_gui/problems/registry.py#L231).
- `_local_entry(key_label: str, factory: Any, n_obj: int, pf_filename: str, n_var_default: int | None=None, n_var_minimum: int=1, form_note: str | None=None) -> Dict[str, Any]` — funkcja modułowa; [wiersz 255](../src/pymoo_gui/problems/registry.py#L255).
- `_wfg_entry(problem_name: str, n_obj: int) -> Dict[str, Any]` — funkcja modułowa; [wiersz 279](../src/pymoo_gui/problems/registry.py#L279).
- `make_kursawe(n_var: int=3) -> KursaweProblem` — funkcja modułowa; [wiersz 304](../src/pymoo_gui/problems/registry.py#L304).
- `make_schaffer() -> SchafferProblem` — funkcja modułowa; [wiersz 308](../src/pymoo_gui/problems/registry.py#L308).
- `make_zdt5()` — funkcja modułowa; [wiersz 312](../src/pymoo_gui/problems/registry.py#L312).
- `lambda` — wyrażenie anonimowe; [wiersz 112](../src/pymoo_gui/problems/registry.py#L112).
- `lambda` — wyrażenie anonimowe; [wiersz 221](../src/pymoo_gui/problems/registry.py#L221).
- `lambda` — wyrażenie anonimowe; [wiersz 236](../src/pymoo_gui/problems/registry.py#L236).
- `lambda` — wyrażenie anonimowe; [wiersz 285](../src/pymoo_gui/problems/registry.py#L285).
- `lambda` — wyrażenie anonimowe; [wiersz 336](../src/pymoo_gui/problems/registry.py#L336).
- `lambda` — wyrażenie anonimowe; [wiersz 369](../src/pymoo_gui/problems/registry.py#L369).
- `lambda` — wyrażenie anonimowe; [wiersz 376](../src/pymoo_gui/problems/registry.py#L376).
- `lambda` — wyrażenie anonimowe; [wiersz 383](../src/pymoo_gui/problems/registry.py#L383).
- `lambda` — wyrażenie anonimowe; [wiersz 390](../src/pymoo_gui/problems/registry.py#L390).
- `lambda` — wyrażenie anonimowe; [wiersz 397](../src/pymoo_gui/problems/registry.py#L397).
- `lambda` — wyrażenie anonimowe; [wiersz 404](../src/pymoo_gui/problems/registry.py#L404).
- `lambda` — wyrażenie anonimowe; [wiersz 411](../src/pymoo_gui/problems/registry.py#L411).
- `lambda` — wyrażenie anonimowe; [wiersz 418](../src/pymoo_gui/problems/registry.py#L418).
- `lambda` — wyrażenie anonimowe; [wiersz 425](../src/pymoo_gui/problems/registry.py#L425).
- `lambda` — wyrażenie anonimowe; [wiersz 430](../src/pymoo_gui/problems/registry.py#L430).
- `lambda` — wyrażenie anonimowe; [wiersz 431](../src/pymoo_gui/problems/registry.py#L431).
- `lambda` — wyrażenie anonimowe; [wiersz 432](../src/pymoo_gui/problems/registry.py#L432).
- `lambda` — wyrażenie anonimowe; [wiersz 433](../src/pymoo_gui/problems/registry.py#L433).
- `lambda` — wyrażenie anonimowe; [wiersz 434](../src/pymoo_gui/problems/registry.py#L434).
- `lambda` — wyrażenie anonimowe; [wiersz 435](../src/pymoo_gui/problems/registry.py#L435).
- `lambda` — wyrażenie anonimowe; [wiersz 436](../src/pymoo_gui/problems/registry.py#L436).
- `lambda` — wyrażenie anonimowe; [wiersz 437](../src/pymoo_gui/problems/registry.py#L437).
- `lambda` — wyrażenie anonimowe; [wiersz 438](../src/pymoo_gui/problems/registry.py#L438).
- `lambda` — wyrażenie anonimowe; [wiersz 439](../src/pymoo_gui/problems/registry.py#L439).

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

### `tests/test_custom_algorithm_runtime.py`

- `test_ibea_runtime_on_schaffer() -> None` — funkcja modułowa; [wiersz 9](../tests/test_custom_algorithm_runtime.py#L9).
- `test_gde3_runtime_on_schaffer() -> None` — funkcja modułowa; [wiersz 22](../tests/test_custom_algorithm_runtime.py#L22).

### `tests/test_delta.py`

- `test_classical_delta_keeps_endpoint_and_spacing_penalties() -> None` — funkcja modułowa; [wiersz 13](../tests/test_delta.py#L13).
- `test_generalized_delta_penalizes_missing_extremes(n_obj: int) -> None` — funkcja modułowa; [wiersz 26](../tests/test_delta.py#L26).
- `test_generalized_delta_measures_nonuniform_spacing() -> None` — funkcja modułowa; [wiersz 34](../tests/test_delta.py#L34).
- `test_delta_requires_valid_reference_and_enough_feasible_points(n_obj: int) -> None` — funkcja modułowa; [wiersz 46](../tests/test_delta.py#L46).
- `test_generation_callback_computes_delta_for_every_algorithm(algorithm_key, n_obj: int) -> None` — funkcja modułowa; [wiersz 60](../tests/test_delta.py#L60).

### `tests/test_dtlz_pareto_fronts.py`

- `_dtlz_front(problem_key: str, n_obj: int=3) -> np.ndarray` — funkcja modułowa; [wiersz 9](../tests/test_dtlz_pareto_fronts.py#L9).
- `test_dtlz_fronts_are_dense_finite_and_three_dimensional(problem_key: str) -> None` — funkcja modułowa; [wiersz 18](../tests/test_dtlz_pareto_fronts.py#L18).
- `test_dtlz_fronts_follow_their_expected_geometry() -> None` — funkcja modułowa; [wiersz 27](../tests/test_dtlz_pareto_fronts.py#L27).
- `test_dtlz7_front_uses_only_the_disconnected_optimal_intervals() -> None` — funkcja modułowa; [wiersz 40](../tests/test_dtlz_pareto_fronts.py#L40).

### `tests/test_empty_benchmark_template.py`

- `test_empty_benchmark_template_evaluates_vectorized_objectives() -> None` — funkcja modułowa; [wiersz 14](../tests/test_empty_benchmark_template.py#L14).
- `test_empty_benchmark_template_validates_configuration() -> None` — funkcja modułowa; [wiersz 27](../tests/test_empty_benchmark_template.py#L27).
- `test_empty_benchmark_template_exposes_registration_contract() -> None` — funkcja modułowa; [wiersz 36](../tests/test_empty_benchmark_template.py#L36).

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

- `test_default_entry_params_returns_independent_values() -> None` — funkcja modułowa; [wiersz 25](../tests/test_multi.py#L25).
- `test_build_multi_run_specs_creates_problem_major_cartesian_product() -> None` — funkcja modułowa; [wiersz 42](../tests/test_multi.py#L42).
- `test_metrics_table_data_preserves_generation_history() -> None` — funkcja modułowa; [wiersz 56](../tests/test_multi.py#L56).
- `test_solution_table_data_exports_objectives_and_decisions() -> None` — funkcja modułowa; [wiersz 70](../tests/test_multi.py#L70).
- `test_solution_table_data_keeps_headers_for_an_empty_front() -> None` — funkcja modułowa; [wiersz 83](../tests/test_multi.py#L83).
- `test_multi_worker_runs_and_exports_each_result(tmp_path: Path) -> None` — funkcja modułowa; [wiersz 90](../tests/test_multi.py#L90).
- `test_main_window_exposes_main_and_multi_tabs() -> None` — funkcja modułowa; [wiersz 119](../tests/test_multi.py#L119).

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

### `tests/test_registry_integrity.py`

- `test_algorithm_registry_has_required_structure() -> None` — funkcja modułowa; [wiersz 7](../tests/test_registry_integrity.py#L7).
- `test_problem_registry_has_required_structure() -> None` — funkcja modułowa; [wiersz 16](../tests/test_registry_integrity.py#L16).

### `tests/test_runtime_paths.py`

- `test_source_results_stay_in_project(monkeypatch)` — funkcja modułowa; [wiersz 7](../tests/test_runtime_paths.py#L7).
- `test_frozen_results_survive_bundle_cleanup(monkeypatch, tmp_path)` — funkcja modułowa; [wiersz 12](../tests/test_runtime_paths.py#L12).

### `tests/test_version.py`

- `test_public_version_and_window_title() -> None` — funkcja modułowa; [wiersz 7](../tests/test_version.py#L7).
