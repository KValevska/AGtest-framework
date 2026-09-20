# Katalog wszystkich funkcji frameworka

Ten dokument jest statycznym katalogiem deklaracji znajdujących się w repozytorium. Obejmuje kod aplikacji, metody klas, funkcje zagnieżdżone, funkcje testowe i anonimowe funkcje `lambda`. Nie obejmuje funkcji importowanych z bibliotek zewnętrznych ani obiektów wywoływalnych utworzonych dynamicznie.

## Wynik analizy

- Kod uruchomieniowy zawiera **540** deklaracji `def` w **47** plikach oraz **77** klas.
- Testy zawierają **25** funkcji testowych lub pomocniczych.
- Łącznie znaleziono **565** deklaracji: **224** funkcje modułowe, **328** metod i **13** funkcji zagnieżdżonych.
- Kod zawiera dodatkowo **26** anonimowych funkcji `lambda`, wyszczególnionych w osobnym rozdziale.
- W kodzie nie ma deklaracji `async def`. Przetwarzanie w tle realizują `QThread` oraz pule procesów lub wątków.

## Architektura i przepływ sterowania

1. `run_gui.py` przygotowuje ścieżkę importów i wywołuje `pymoo_gui.app.main`.
2. `MainWindow` buduje interfejs z metadanych `PROBLEMS` i `ALGORITHMS`; formularze parametrów powstają z sygnatur fabryk i jawnych `form_fields`.
3. `OptimizationWorker` tworzy problem i algorytm, opcjonalnie opakowuje problem w `ParallelProblem`, a następnie uruchamia wspólny dispatcher `algorithms.minimize`.
4. Algorytmy natywne dla pymoo korzystają z `pymoo.optimize.minimize`; adaptery i algorytmy badawcze udostępniają własne `gui_minimize`.
5. Callback z `algorithms.common` normalizuje dane generacji, wybiera rozwiązania dopuszczalne i niezdominowane oraz wywołuje obliczanie metryk.
6. GUI aktualizuje widok Pareto i tabelę historii; warstwa `metrics.export` zapisuje dane do skoroszytów XLSX.
7. Karta `Multi` buduje iloczyn wybranych problemów i algorytmów, a `MultiExperimentWorker` wykonuje kombinacje kolejno, bez renderowania wykresów, zapisując osobne skoroszyty wynikowe.
8. Karta `Metric trajectories` odbiera wyłącznie dane bieżącego eksperymentu z `Main` i rysuje osobny przebieg wartości względem generacji dla każdej metryki; brak dostępnej wartości jest oznaczany jako `N/A`.

Największym węzłem zależności jest `app.py` (130 deklaracji), ponieważ łączy budowę GUI, walidację, orkiestrację przebiegu, aktualizację wykresów i eksport. Wspólna baza `ResearchMOOAlgorithm` skupia cykl życia trzech algorytmów badawczych, natomiast `common.py` skupia logikę monitorowania współdzieloną przez pozostałe algorytmy. Implementacje problemów są celowo małe: zwykle składają się z konstruktora oraz `_evaluate`.

## Uwagi utrzymaniowe

- Tylko `metrics/export.py` ma docstringi funkcji; pozostałe role są opisywane komentarzami lub wynikają z nazw. Ten katalog zapewnia pełny indeks, ale nie zastępuje kontraktów wejścia/wyjścia w docstringach.
- `app.py` ma wiele odpowiedzialności. Naturalne granice przyszłego podziału to: formularze, kontroler uruchomienia, prezentacja metryk oraz eksport.
- Istnieją równolegle katalogi `algorithms` i historycznie błędnie zapisany `algoritms`; drugi działa wyłącznie jako alias zgodności wstecznej.
- W kilku komentarzach i tekstach źródłowych widać uszkodzone kodowanie polskich znaków; aplikacja częściowo kompensuje je przez `translate_ui_text`.
- Fabryki i rejestry są właściwym publicznym punktem rozszerzeń. Metody i funkcje zaczynające się od `_` należy traktować jako szczegóły implementacyjne.

## Zestawienie modułów

| Plik | Funkcje modułowe | Metody | Zagnieżdżone | Klasy | Lambda |
|---|---:|---:|---:|---:|---:|
| `run_gui.py` | 2 | 0 | 0 | 0 | 0 |
| `src/pymoo_gui/algorithms/__init__.py` | 1 | 0 | 0 | 0 | 0 |
| `src/pymoo_gui/algorithms/age.py` | 6 | 8 | 0 | 2 | 0 |
| `src/pymoo_gui/algorithms/common.py` | 13 | 1 | 0 | 2 | 0 |
| `src/pymoo_gui/algorithms/empty_algorithm_template.py` | 1 | 6 | 0 | 1 | 0 |
| `src/pymoo_gui/algorithms/eps_moea.py` | 1 | 0 | 1 | 0 | 0 |
| `src/pymoo_gui/algorithms/eps_nsga2.py` | 1 | 0 | 1 | 0 | 0 |
| `src/pymoo_gui/algorithms/gde3.py` | 4 | 5 | 0 | 1 | 0 |
| `src/pymoo_gui/algorithms/hype.py` | 22 | 4 | 0 | 2 | 0 |
| `src/pymoo_gui/algorithms/ibea.py` | 5 | 5 | 0 | 1 | 0 |
| `src/pymoo_gui/algorithms/learning_edmo.py` | 1 | 5 | 0 | 1 | 0 |
| `src/pymoo_gui/algorithms/lmoea_ds.py` | 6 | 12 | 0 | 1 | 0 |
| `src/pymoo_gui/algorithms/moead.py` | 4 | 0 | 0 | 0 | 0 |
| `src/pymoo_gui/algorithms/nsga2.py` | 2 | 0 | 0 | 0 | 0 |
| `src/pymoo_gui/algorithms/nsga3.py` | 4 | 0 | 0 | 0 | 0 |
| `src/pymoo_gui/algorithms/platypus_common.py` | 7 | 8 | 0 | 3 | 0 |
| `src/pymoo_gui/algorithms/platypus_moead.py` | 1 | 0 | 1 | 0 | 0 |
| `src/pymoo_gui/algorithms/research_common.py` | 24 | 29 | 0 | 3 | 0 |
| `src/pymoo_gui/algorithms/rnn_guided_dmo.py` | 1 | 6 | 0 | 1 | 0 |
| `src/pymoo_gui/algorithms/rnsga3.py` | 5 | 0 | 0 | 0 | 0 |
| `src/pymoo_gui/algorithms/rvea.py` | 7 | 1 | 1 | 1 | 0 |
| `src/pymoo_gui/algorithms/spea2.py` | 3 | 3 | 0 | 2 | 0 |
| `src/pymoo_gui/algorithms/ts_nsga.py` | 1 | 2 | 0 | 1 | 0 |
| `src/pymoo_gui/app.py` | 8 | 123 | 0 | 7 | 2 |
| `src/pymoo_gui/metrics/export.py` | 13 | 0 | 0 | 0 | 0 |
| `src/pymoo_gui/metrics/quality.py` | 19 | 0 | 1 | 1 | 0 |
| `src/pymoo_gui/multi.py` | 6 | 6 | 1 | 3 | 0 |
| `src/pymoo_gui/parallel.py` | 6 | 6 | 0 | 1 | 0 |
| `src/pymoo_gui/problems/binh2.py` | 0 | 2 | 0 | 1 | 0 |
| `src/pymoo_gui/problems/constrex.py` | 0 | 2 | 0 | 1 | 0 |
| `src/pymoo_gui/problems/empty_benchmark_template.py` | 2 | 2 | 0 | 1 | 0 |
| `src/pymoo_gui/problems/fonseca.py` | 0 | 2 | 0 | 1 | 0 |
| `src/pymoo_gui/problems/golinski.py` | 0 | 2 | 0 | 1 | 0 |
| `src/pymoo_gui/problems/kursawe.py` | 0 | 2 | 0 | 1 | 0 |
| `src/pymoo_gui/problems/lz09.py` | 0 | 16 | 0 | 10 | 0 |
| `src/pymoo_gui/problems/osyczka2.py` | 0 | 2 | 0 | 1 | 0 |
| `src/pymoo_gui/problems/registry.py` | 18 | 0 | 0 | 0 | 24 |
| `src/pymoo_gui/problems/schaffer.py` | 0 | 2 | 0 | 1 | 0 |
| `src/pymoo_gui/problems/srinivas.py` | 0 | 2 | 0 | 1 | 0 |
| `src/pymoo_gui/problems/tanaka.py` | 0 | 2 | 0 | 1 | 0 |
| `src/pymoo_gui/problems/uf.py` | 2 | 13 | 0 | 11 | 0 |
| `src/pymoo_gui/problems/viennet2.py` | 0 | 2 | 0 | 1 | 0 |
| `src/pymoo_gui/problems/viennet3.py` | 0 | 2 | 0 | 1 | 0 |
| `src/pymoo_gui/problems/water.py` | 0 | 2 | 0 | 1 | 0 |
| `src/pymoo_gui/problems/wfg.py` | 2 | 0 | 0 | 0 | 0 |
| `src/pymoo_gui/viz/metric_trajectories.py` | 0 | 4 | 0 | 1 | 0 |
| `src/pymoo_gui/viz/pareto_dialogs.py` | 1 | 39 | 7 | 8 | 0 |
| `tests/test_custom_algorithm_runtime.py` | 2 | 0 | 0 | 0 | 0 |
| `tests/test_dtlz_pareto_fronts.py` | 4 | 0 | 0 | 0 | 0 |
| `tests/test_empty_benchmark_template.py` | 3 | 0 | 0 | 0 | 0 |
| `tests/test_lmoea_ds_runtime.py` | 1 | 0 | 0 | 0 | 0 |
| `tests/test_metric_trajectories.py` | 3 | 0 | 0 | 0 | 0 |
| `tests/test_multi.py` | 7 | 0 | 0 | 0 | 0 |
| `tests/test_package_exports.py` | 2 | 0 | 0 | 0 | 0 |
| `tests/test_pareto_labels.py` | 1 | 0 | 0 | 0 | 0 |
| `tests/test_registry_integrity.py` | 2 | 0 | 0 | 0 | 0 |

## Katalog kodu uruchomieniowego

Sygnatury są zapisane dokładnie na podstawie drzewa składniowego Pythona. Nazwa kwalifikowana pokazuje klasę lub funkcję nadrzędną. Dekoratory są podane w nawiasach kwadratowych.

### `run_gui.py`

- `_ensure_src_on_path() -> None` — funkcja modułowa; [wiersz 17](../run_gui.py#L17).
- `main() -> None` — funkcja modułowa; [wiersz 27](../run_gui.py#L27).

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
- `AGEMOEASurvival.compute_geometry(front: np.ndarray, extreme: np.ndarray, n_obj: int) -> float` — metoda; dekoratory: `staticmethod`; [wiersz 193](../src/pymoo_gui/algorithms/age.py#L193).
- `AGEMOEASurvival.pairwise_distances(front: np.ndarray, p: float) -> np.ndarray` — metoda; dekoratory: `staticmethod`; [wiersz 210](../src/pymoo_gui/algorithms/age.py#L210).
- `AGEMOEASurvival.minkowski_distances(A: np.ndarray, B: np.ndarray, p: float) -> np.ndarray` — metoda; dekoratory: `staticmethod`; [wiersz 219](../src/pymoo_gui/algorithms/age.py#L219).
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

- `EmptyAlgorithmTemplate.__init__(self, population_size: int=100, archive_size: int=100, crossover_rate: float=0.9, mutation_rate: float=0.1, template_bias: float=0.5, seed: int=1) -> None` — metoda; [wiersz 28](../src/pymoo_gui/algorithms/empty_algorithm_template.py#L28).
- `EmptyAlgorithmTemplate.after_initialize(self) -> None` — metoda; [wiersz 54](../src/pymoo_gui/algorithms/empty_algorithm_template.py#L54).
- `EmptyAlgorithmTemplate.guided_candidates(self) -> np.ndarray` — metoda; [wiersz 59](../src/pymoo_gui/algorithms/empty_algorithm_template.py#L59).
- `EmptyAlgorithmTemplate.create_offspring(self) -> np.ndarray` — metoda; [wiersz 66](../src/pymoo_gui/algorithms/empty_algorithm_template.py#L66).
- `EmptyAlgorithmTemplate.environmental_selection(self, X: np.ndarray, F: np.ndarray, CV: np.ndarray, n_survive: int) -> PopulationState` — metoda; [wiersz 78](../src/pymoo_gui/algorithms/empty_algorithm_template.py#L78).
- `EmptyAlgorithmTemplate.after_generation(self, previous: PopulationState, current: PopulationState) -> None` — metoda; [wiersz 98](../src/pymoo_gui/algorithms/empty_algorithm_template.py#L98).
- `make_empty_algorithm_template(population_size: int=100, archive_size: int=100, crossover_rate: float=0.9, mutation_rate: float=0.1, template_bias: float=0.5, seed: int=1) -> EmptyAlgorithmTemplate` — funkcja modułowa; [wiersz 108](../src/pymoo_gui/algorithms/empty_algorithm_template.py#L108).

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
- `PopulationState.feasible(self) -> np.ndarray` — metoda; dekoratory: `property`; [wiersz 481](../src/pymoo_gui/algorithms/research_common.py#L481).
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

### `src/pymoo_gui/app.py`

- `NoTermination.__init__(self)` — metoda; [wiersz 63](../src/pymoo_gui/app.py#L63).
- `NoTermination.update(self, algorithm)` — metoda; [wiersz 68](../src/pymoo_gui/app.py#L68).
- `NoTermination.has_terminated(self)` — metoda; [wiersz 73](../src/pymoo_gui/app.py#L73).
- `NoTermination.do_continue(self)` — metoda; [wiersz 77](../src/pymoo_gui/app.py#L77).
- `translate_ui_text(text: Any) -> str` — funkcja modułowa; [wiersz 257](../src/pymoo_gui/app.py#L257).
- `pl_param_label(name: str) -> str` — funkcja modułowa; [wiersz 315](../src/pymoo_gui/app.py#L315).
- `callable_signature(obj: Any) -> inspect.Signature` — funkcja modułowa; [wiersz 320](../src/pymoo_gui/app.py#L320).
- `filter_callable_kwargs(fn: Any, params: Mapping[str, Any]) -> Dict[str, Any]` — funkcja modułowa; [wiersz 325](../src/pymoo_gui/app.py#L325).
- `_literal_or_str(value: str) -> Any` — funkcja modułowa; [wiersz 337](../src/pymoo_gui/app.py#L337).
- `should_save_nondominated_solutions_for_epoch(epoch: Any, mode: str, step: int=1, *, is_final: bool=False) -> bool` — funkcja modułowa; [wiersz 348](../src/pymoo_gui/app.py#L348).
- `_specs(raw_specs: Optional[Any]) -> list[FieldSpec]` — funkcja modułowa; [wiersz 394](../src/pymoo_gui/app.py#L394).
- `ParamForm.__init__(self, title: str, parent=None)` — metoda; [wiersz 430](../src/pymoo_gui/app.py#L430).
- `ParamForm.clear(self) -> None` — metoda; [wiersz 439](../src/pymoo_gui/app.py#L439).
- `ParamForm.binding(self, name: str) -> Optional[WidgetBinding]` — metoda; [wiersz 445](../src/pymoo_gui/app.py#L445).
- `ParamForm.bindings(self) -> Sequence[WidgetBinding]` — metoda; [wiersz 449](../src/pymoo_gui/app.py#L449).
- `ParamForm.build_for_callable(self, fn: Any, extra_fields: Optional[Any]=None) -> None` — metoda; [wiersz 453](../src/pymoo_gui/app.py#L453).
- `ParamForm.build_for_signature(self, sig: inspect.Signature, extra_fields: Optional[Any]=None) -> None` — metoda; [wiersz 457](../src/pymoo_gui/app.py#L457).
- `ParamForm.build_from_specs(self, raw_specs: Optional[Any]) -> None` — metoda; [wiersz 472](../src/pymoo_gui/app.py#L472).
- `ParamForm._kind(self, annotation: Any, default: Any) -> str` — metoda; [wiersz 478](../src/pymoo_gui/app.py#L478).
- `ParamForm._bounds(self, spec: FieldSpec) -> Tuple[float, float]` — metoda; [wiersz 490](../src/pymoo_gui/app.py#L490).
- `ParamForm._apply_read_only(self, widget: Any, spec: FieldSpec) -> None` — metoda; [wiersz 509](../src/pymoo_gui/app.py#L509).
- `ParamForm._add_field(self, spec: FieldSpec) -> None` — metoda; [wiersz 522](../src/pymoo_gui/app.py#L522).
- `ParamForm.values(self) -> Dict[str, Any]` — metoda; [wiersz 564](../src/pymoo_gui/app.py#L564).
- `OptimizationWorker.__init__(self, problem_key: str, alg_key: str, problem_params: Mapping[str, Any], algorithm_params: Mapping[str, Any], n_gen: Optional[int], seed: int, verbose: bool, hv_ref_point: Optional[list[float]], parallel_eval: bool=False, parallel_workers: int=1, parallel_backend: str='process', parent=None)` — metoda; [wiersz 598](../src/pymoo_gui/app.py#L598).
- `OptimizationWorker.request_cancel(self) -> None` — metoda; [wiersz 629](../src/pymoo_gui/app.py#L629).
- `OptimizationWorker._cancel_pending(self) -> bool` — metoda; [wiersz 634](../src/pymoo_gui/app.py#L634).
- `OptimizationWorker._emit_generation(self, payload: dict) -> None` — metoda; [wiersz 638](../src/pymoo_gui/app.py#L638).
- `OptimizationWorker.run(self) -> None` — metoda; [wiersz 647](../src/pymoo_gui/app.py#L647).
- `MainWindow.__init__(self)` — metoda; [wiersz 699](../src/pymoo_gui/app.py#L699).
- `MainWindow._build_ui(self) -> None` — metoda; [wiersz 733](../src/pymoo_gui/app.py#L733).
- `MainWindow._build_checkable_registry_list(self, registry: Mapping[str, Dict[str, Any]]) -> QListWidget` — metoda; [wiersz 759](../src/pymoo_gui/app.py#L759).
- `MainWindow._build_multi_selection_group(self, title: str, widget: QListWidget) -> QGroupBox` — metoda; [wiersz 771](../src/pymoo_gui/app.py#L771).
- `MainWindow._build_multi_panel(self) -> QWidget` — metoda; [wiersz 786](../src/pymoo_gui/app.py#L786).
- `MainWindow._apply_english_ui_texts(self) -> None` — metoda; [wiersz 871](../src/pymoo_gui/app.py#L871).
- `MainWindow._build_controls_panel(self) -> QWidget` — metoda; [wiersz 891](../src/pymoo_gui/app.py#L891).
- `MainWindow._build_results_panel(self) -> QWidget` — metoda; [wiersz 903](../src/pymoo_gui/app.py#L903).
- `MainWindow._build_problem_controls(self) -> None` — metoda; [wiersz 933](../src/pymoo_gui/app.py#L933).
- `MainWindow._build_hv_controls(self) -> None` — metoda; [wiersz 952](../src/pymoo_gui/app.py#L952).
- `MainWindow._build_run_controls(self) -> None` — metoda; [wiersz 971](../src/pymoo_gui/app.py#L971).
- `MainWindow._build_console(self) -> None` — metoda; [wiersz 1018](../src/pymoo_gui/app.py#L1018).
- `MainWindow._connect_signals(self) -> None` — metoda; [wiersz 1028](../src/pymoo_gui/app.py#L1028).
- `MainWindow._configure_placeholders(self) -> None` — metoda; [wiersz 1057](../src/pymoo_gui/app.py#L1057).
- `MainWindow._set_all_multi_items(self, widget: QListWidget, checked: bool) -> None` — metoda; [wiersz 1072](../src/pymoo_gui/app.py#L1072).
- `MainWindow._checked_multi_keys(self, widget: QListWidget) -> list[str]` — metoda; [wiersz 1085](../src/pymoo_gui/app.py#L1085).
- `MainWindow._update_multi_selection_state(self, *_args: Any) -> None` — metoda; [wiersz 1096](../src/pymoo_gui/app.py#L1096).
- `MainWindow._set_multi_running_state(self, running: bool) -> None` — metoda; [wiersz 1109](../src/pymoo_gui/app.py#L1109).
- `MainWindow._multi_row_key(self, payload: Mapping[str, Any]) -> tuple[str, str]` — metoda; [wiersz 1123](../src/pymoo_gui/app.py#L1123).
- `MainWindow._set_multi_table_value(self, row: int, column: int, value: Any) -> None` — metoda; [wiersz 1127](../src/pymoo_gui/app.py#L1127).
- `MainWindow._on_multi_run_started(self, payload: Mapping[str, Any]) -> None` — metoda; [wiersz 1134](../src/pymoo_gui/app.py#L1134).
- `MainWindow._on_multi_run_progress(self, payload: Mapping[str, Any]) -> None` — metoda; [wiersz 1158](../src/pymoo_gui/app.py#L1158).
- `MainWindow._on_multi_run_finished(self, payload: Mapping[str, Any]) -> None` — metoda; [wiersz 1177](../src/pymoo_gui/app.py#L1177).
- `MainWindow.start_multi_experiment(self) -> None` — metoda; [wiersz 1203](../src/pymoo_gui/app.py#L1203).
- `MainWindow.stop_multi_experiment(self) -> None` — metoda; [wiersz 1254](../src/pymoo_gui/app.py#L1254).
- `MainWindow._finish_multi_experiment(self, status: str, results: Sequence[Mapping[str, Any]]) -> None` — metoda; [wiersz 1264](../src/pymoo_gui/app.py#L1264).
- `MainWindow._on_multi_experiment_done(self, results: Sequence[Mapping[str, Any]]) -> None` — metoda; [wiersz 1280](../src/pymoo_gui/app.py#L1280).
- `MainWindow._on_multi_experiment_cancelled(self, results: Sequence[Mapping[str, Any]]) -> None` — metoda; [wiersz 1284](../src/pymoo_gui/app.py#L1284).
- `MainWindow._on_multi_experiment_failed(self, error: str) -> None` — metoda; [wiersz 1288](../src/pymoo_gui/app.py#L1288).
- `MainWindow._entry(self, combo: QComboBox, registry: Mapping[str, Dict[str, Any]]) -> Dict[str, Any]` — metoda; [wiersz 1296](../src/pymoo_gui/app.py#L1296).
- `MainWindow._known_pf_for_problem(self, entry: Mapping[str, Any], problem: Any) -> Optional[np.ndarray]` — metoda; [wiersz 1301](../src/pymoo_gui/app.py#L1301).
- `MainWindow._instantiate_selected_problem(self, params: Optional[Mapping[str, Any]]=None) -> Tuple[Optional[Any], Optional[str]]` — metoda; [wiersz 1322](../src/pymoo_gui/app.py#L1322).
- `MainWindow._connect_problem_form_signals(self) -> None` — metoda; [wiersz 1337](../src/pymoo_gui/app.py#L1337).
- `MainWindow._ensure_plot_widget(self) -> UnifiedParetoWidget` — metoda; [wiersz 1350](../src/pymoo_gui/app.py#L1350).
- `MainWindow._reset_plot_axes(self) -> None` — metoda; [wiersz 1373](../src/pymoo_gui/app.py#L1373).
- `MainWindow._set_plot_message(self, text: str) -> None` — metoda; [wiersz 1378](../src/pymoo_gui/app.py#L1378).
- `MainWindow._reset_plot_run_data(self) -> None` — metoda; [wiersz 1385](../src/pymoo_gui/app.py#L1385).
- `MainWindow._reset_run_result_state(self) -> None` — metoda; [wiersz 1391](../src/pymoo_gui/app.py#L1391).
- `MainWindow._update_run_form_state(self) -> None` — metoda; [wiersz 1397](../src/pymoo_gui/app.py#L1397).
- `MainWindow._current_nd_save_mode(self) -> str` — metoda; [wiersz 1421](../src/pymoo_gui/app.py#L1421).
- `MainWindow._update_nd_save_controls_state(self) -> None` — metoda; [wiersz 1426](../src/pymoo_gui/app.py#L1426).
- `MainWindow._collect_nd_save_args(self) -> Tuple[Optional[dict], Optional[str]]` — metoda; [wiersz 1430](../src/pymoo_gui/app.py#L1430).
- `MainWindow._set_run_state(self, status_text: str, running: bool) -> None` — metoda; [wiersz 1440](../src/pymoo_gui/app.py#L1440).
- `MainWindow._apply_generation_payload(self, payload: Mapping[str, Any]) -> None` — metoda; [wiersz 1451](../src/pymoo_gui/app.py#L1451).
- `MainWindow._apply_problem_preview_state(self, problem: Any) -> None` — metoda; [wiersz 1460](../src/pymoo_gui/app.py#L1460).
- `MainWindow._refresh_problem_plot(self) -> None` — metoda; [wiersz 1470](../src/pymoo_gui/app.py#L1470).
- `MainWindow._render_plot(self) -> None` — metoda; [wiersz 1484](../src/pymoo_gui/app.py#L1484).
- `MainWindow._rebuild_problem_form(self) -> None` — metoda; [wiersz 1501](../src/pymoo_gui/app.py#L1501).
- `MainWindow._rebuild_alg_form(self) -> None` — metoda; [wiersz 1512](../src/pymoo_gui/app.py#L1512).
- `MainWindow._connect_problem_param_signals(self) -> None` — metoda; [wiersz 1518](../src/pymoo_gui/app.py#L1518).
- `MainWindow._on_n_obj_changed(self, _value: int) -> None` — metoda; [wiersz 1535](../src/pymoo_gui/app.py#L1535).
- `MainWindow._on_problem_form_changed(self, *_args: Any) -> None` — metoda; [wiersz 1540](../src/pymoo_gui/app.py#L1540).
- `MainWindow._on_show_population_toggled(self, checked: bool) -> None` — metoda; [wiersz 1544](../src/pymoo_gui/app.py#L1544).
- `MainWindow._on_hide_pareto_front_toggled(self, checked: bool) -> None` — metoda; [wiersz 1549](../src/pymoo_gui/app.py#L1549).
- `MainWindow._on_auto_scale_toggled(self, checked: bool) -> None` — metoda; [wiersz 1556](../src/pymoo_gui/app.py#L1556).
- `MainWindow._on_nd_save_mode_changed(self, _index: int) -> None` — metoda; [wiersz 1565](../src/pymoo_gui/app.py#L1565).
- `MainWindow._on_ran_toggled(self, checked: bool) -> None` — metoda; [wiersz 1569](../src/pymoo_gui/app.py#L1569).
- `MainWindow._on_parallel_eval_toggled(self, checked: bool) -> None` — metoda; [wiersz 1574](../src/pymoo_gui/app.py#L1574).
- `MainWindow._toggle_console_dock(self) -> None` — metoda; [wiersz 1579](../src/pymoo_gui/app.py#L1579).
- `MainWindow._on_console_visibility_changed(self, visible: bool) -> None` — metoda; [wiersz 1583](../src/pymoo_gui/app.py#L1583).
- `MainWindow._log(self, msg: str) -> None` — metoda; [wiersz 1587](../src/pymoo_gui/app.py#L1587).
- `MainWindow._warn(self, title: str, message: str, log_message: Optional[str]=None) -> None` — metoda; [wiersz 1593](../src/pymoo_gui/app.py#L1593).
- `MainWindow._current_n_obj(self) -> int` — metoda; [wiersz 1599](../src/pymoo_gui/app.py#L1599).
- `MainWindow._parse_float_token(self, token: str) -> Optional[float]` — metoda; [wiersz 1612](../src/pymoo_gui/app.py#L1612).
- `MainWindow._parse_ref_point_text(self, text: str) -> Tuple[Optional[list[float]], Optional[str]]` — metoda; [wiersz 1630](../src/pymoo_gui/app.py#L1630).
- `MainWindow._auto_hv_ref_point(self) -> list[float]` — metoda; [wiersz 1651](../src/pymoo_gui/app.py#L1651).
- `MainWindow._hv_ref_point_state(self) -> Tuple[bool, Optional[list[float]], str, Optional[str]]` — metoda; [wiersz 1655](../src/pymoo_gui/app.py#L1655).
- `MainWindow._validate_hv_manual_ref_point(self) -> bool` — metoda; [wiersz 1670](../src/pymoo_gui/app.py#L1670).
- `MainWindow._update_hv_ref_point_label(self) -> None` — metoda; [wiersz 1681](../src/pymoo_gui/app.py#L1681).
- `MainWindow._on_hv_mode_changed(self, _checked: bool) -> None` — metoda; [wiersz 1691](../src/pymoo_gui/app.py#L1691).
- `MainWindow._on_hv_manual_changed(self, _text: str) -> None` — metoda; [wiersz 1700](../src/pymoo_gui/app.py#L1700).
- `MainWindow._on_live_updates_toggled(self, checked: bool) -> None` — metoda; [wiersz 1705](../src/pymoo_gui/app.py#L1705).
- `MainWindow._update_run_button_state(self) -> None` — metoda; [wiersz 1710](../src/pymoo_gui/app.py#L1710).
- `MainWindow._update_plot_status(self, payload: Optional[dict]=None, message: Optional[str]=None) -> None` — metoda; [wiersz 1718](../src/pymoo_gui/app.py#L1718).
- `MainWindow._fmt_int(self, value: Optional[int]) -> str` — metoda; [wiersz 1734](../src/pymoo_gui/app.py#L1734).
- `MainWindow._fmt_metric(self, value: Optional[float]) -> str` — metoda; [wiersz 1741](../src/pymoo_gui/app.py#L1741).
- `MainWindow._update_metrics_label(self, payload: Optional[dict]) -> None` — metoda; [wiersz 1748](../src/pymoo_gui/app.py#L1748).
- `MainWindow._metrics_label_text(self, payload: Mapping[str, Any]) -> str` — metoda; [wiersz 1752](../src/pymoo_gui/app.py#L1752).
- `MainWindow._clear_table(self) -> None` — metoda; [wiersz 1758](../src/pymoo_gui/app.py#L1758).
- `MainWindow._should_scroll_table(self) -> bool` — metoda; [wiersz 1763](../src/pymoo_gui/app.py#L1763).
- `MainWindow._append_generation_row(self, payload: dict) -> None` — metoda; [wiersz 1768](../src/pymoo_gui/app.py#L1768).
- `MainWindow._append_last_payload_once(self, payload: Mapping[str, Any]) -> None` — metoda; [wiersz 1791](../src/pymoo_gui/app.py#L1791).
- `MainWindow._metrics_table_data(self) -> Tuple[list[str], list[list[str]]]` — metoda; [wiersz 1799](../src/pymoo_gui/app.py#L1799).
- `MainWindow._export_metrics_table(self) -> None` — metoda; [wiersz 1815](../src/pymoo_gui/app.py#L1815).
- `MainWindow._xlsx_value(self, value: Any) -> object` — metoda; [wiersz 1834](../src/pymoo_gui/app.py#L1834).
- `MainWindow._solution_table_data(self, payload: Mapping[str, Any]) -> Tuple[list[str], list[list[object]]]` — metoda; [wiersz 1846](../src/pymoo_gui/app.py#L1846).
- `MainWindow._export_solution_table(self, payload: Mapping[str, Any]) -> None` — metoda; [wiersz 1887](../src/pymoo_gui/app.py#L1887).
- `MainWindow._export_nondominated_solutions_for_epoch(self, payload: Mapping[str, Any]) -> None` — metoda; [wiersz 1916](../src/pymoo_gui/app.py#L1916).
- `MainWindow._export_nondominated_solutions_for_final_epoch(self, payload: Mapping[str, Any]) -> None` — metoda; [wiersz 1936](../src/pymoo_gui/app.py#L1936).
- `MainWindow._validated_int(self, value: Any, label: str, minimum: int) -> Tuple[Optional[int], Optional[str]]` — metoda; [wiersz 1961](../src/pymoo_gui/app.py#L1961).
- `MainWindow._collect_run_args(self) -> Tuple[Optional[dict], Optional[str]]` — metoda; [wiersz 1973](../src/pymoo_gui/app.py#L1973).
- `MainWindow._collect_algorithm_args(self) -> Tuple[Optional[dict], Optional[str]]` — metoda; [wiersz 2001](../src/pymoo_gui/app.py#L2001).
- `MainWindow._collect_problem_args(self) -> Tuple[dict, Optional[str]]` — metoda; [wiersz 2011](../src/pymoo_gui/app.py#L2011).
- `MainWindow._prepare_run_visuals(self) -> None` — metoda; [wiersz 2015](../src/pymoo_gui/app.py#L2015).
- `MainWindow._finish_run(self, status_text: str, last_payload: Optional[dict]) -> None` — metoda; [wiersz 2026](../src/pymoo_gui/app.py#L2026).
- `MainWindow._on_generation(self, payload: dict) -> None` — metoda; [wiersz 2043](../src/pymoo_gui/app.py#L2043).
- `MainWindow.start_run(self) -> None` — metoda; [wiersz 2057](../src/pymoo_gui/app.py#L2057).
- `MainWindow.stop_run(self) -> None` — metoda; [wiersz 2153](../src/pymoo_gui/app.py#L2153).
- `MainWindow._on_run_done(self, last_payload: dict) -> None` — metoda; [wiersz 2163](../src/pymoo_gui/app.py#L2163).
- `MainWindow._on_run_cancelled(self, last_payload: dict) -> None` — metoda; [wiersz 2167](../src/pymoo_gui/app.py#L2167).
- `MainWindow._on_run_failed(self, err: str) -> None` — metoda; [wiersz 2178](../src/pymoo_gui/app.py#L2178).
- `MainWindow._clear_console_and_visuals(self) -> None` — metoda; [wiersz 2187](../src/pymoo_gui/app.py#L2187).
- `main() -> None` — funkcja modułowa; [wiersz 2201](../src/pymoo_gui/app.py#L2201).

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

- `_safe_float(x) -> Optional[float]` — funkcja modułowa; [wiersz 52](../src/pymoo_gui/metrics/quality.py#L52).
- `_as_2d(arr: Optional[np.ndarray], n_obj: Optional[int]=None) -> Optional[np.ndarray]` — funkcja modułowa; [wiersz 60](../src/pymoo_gui/metrics/quality.py#L60).
- `_as_decision_matrix(values: Optional[np.ndarray], n_var: Optional[int]=None) -> Optional[np.ndarray]` — funkcja modułowa; [wiersz 79](../src/pymoo_gui/metrics/quality.py#L79).
- `_finite_rows(arr: np.ndarray) -> np.ndarray` — funkcja modułowa; [wiersz 96](../src/pymoo_gui/metrics/quality.py#L96).
- `_safe_solve(A: np.ndarray, b: np.ndarray) -> Optional[np.ndarray]` — funkcja modułowa; [wiersz 102](../src/pymoo_gui/metrics/quality.py#L102).
- `_problem_n_ieq_constr(problem: Any) -> int` — funkcja modułowa; [wiersz 113](../src/pymoo_gui/metrics/quality.py#L113).
- `_problem_bounds(problem: Any, n_var: int) -> tuple[np.ndarray, np.ndarray]` — funkcja modułowa; [wiersz 125](../src/pymoo_gui/metrics/quality.py#L125).
- `_problem_bounds._bound(name: str, fill: float) -> np.ndarray` — funkcja zagnieżdżona; [wiersz 127](../src/pymoo_gui/metrics/quality.py#L127).
- `_evaluate_fg(problem: Any, X: np.ndarray) -> Optional[tuple[np.ndarray, np.ndarray]]` — funkcja modułowa; [wiersz 146](../src/pymoo_gui/metrics/quality.py#L146).
- `_valid_derivative(values: Any, expected_shape: tuple[int, int, int]) -> Optional[np.ndarray]` — funkcja modułowa; [wiersz 170](../src/pymoo_gui/metrics/quality.py#L170).
- `_finite_difference_derivatives(problem: Any, X: np.ndarray, F: np.ndarray, G: np.ndarray, eps: float=FINITE_DIFF_EPS) -> tuple[Optional[np.ndarray], Optional[np.ndarray]]` — funkcja modułowa; [wiersz 181](../src/pymoo_gui/metrics/quality.py#L181).
- `_evaluate_kktpm_inputs(X: np.ndarray, problem: Any, finite_diff_eps: float=FINITE_DIFF_EPS) -> Optional[tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]]` — funkcja modułowa; [wiersz 243](../src/pymoo_gui/metrics/quality.py#L243).
- `_calc_cv(G: np.ndarray) -> np.ndarray` — funkcja modułowa; [wiersz 280](../src/pymoo_gui/metrics/quality.py#L280).
- `compute_spread(F: np.ndarray) -> Optional[float]` — funkcja modułowa; [wiersz 287](../src/pymoo_gui/metrics/quality.py#L287).
- `compute_delta(F: np.ndarray, pareto_front: np.ndarray) -> Optional[float]` — funkcja modułowa; [wiersz 317](../src/pymoo_gui/metrics/quality.py#L317).
- `compute_kktpm(X: np.ndarray, problem: Any, ideal: Optional[np.ndarray]=None, utopian_eps: float=0.0001, rho: float=0.001, finite_diff_eps: float=FINITE_DIFF_EPS) -> Optional[np.ndarray]` — funkcja modułowa; [wiersz 343](../src/pymoo_gui/metrics/quality.py#L343).
- `_feasibility_mask_from_cv(cv: Optional[np.ndarray]) -> Optional[np.ndarray]` — funkcja modułowa; [wiersz 460](../src/pymoo_gui/metrics/quality.py#L460).
- `compute_metrics(F: np.ndarray, pareto_front: Optional[np.ndarray], cv: Optional[np.ndarray]=None, ref_point: Optional[np.ndarray]=None, n_obj: Optional[int]=None, X: Optional[np.ndarray]=None, problem: Any=None, kktpm_ideal: Optional[np.ndarray]=None, delta_supported: bool=False) -> MetricResult` — funkcja modułowa; [wiersz 475](../src/pymoo_gui/metrics/quality.py#L475).
- `get_hv_ref_point(problem_name: Optional[str], n_obj: Optional[int]) -> Optional[np.ndarray]` — funkcja modułowa; [wiersz 607](../src/pymoo_gui/metrics/quality.py#L607).
- `fixed_ref_point_for_problem(problem_name: Optional[str], n_obj: Optional[int]) -> Optional[np.ndarray]` — funkcja modułowa; [wiersz 623](../src/pymoo_gui/metrics/quality.py#L623).

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

### `src/pymoo_gui/viz/metric_trajectories.py`

- `MetricTrajectoriesWidget.__init__(self, parent=None) -> None` — metoda; [wiersz 29](../src/pymoo_gui/viz/metric_trajectories.py#L29).
- `MetricTrajectoriesWidget.reset(self, algorithm_name: Optional[str]=None, problem_name: Optional[str]=None) -> None` — metoda; [wiersz 89](../src/pymoo_gui/viz/metric_trajectories.py#L89).
- `MetricTrajectoriesWidget.append_payload(self, payload: Mapping[str, Any]) -> None` — metoda; [wiersz 111](../src/pymoo_gui/viz/metric_trajectories.py#L111).
- `MetricTrajectoriesWidget.history(self) -> dict[str, list[tuple[int, float]]]` — metoda; [wiersz 137](../src/pymoo_gui/viz/metric_trajectories.py#L137).

### `src/pymoo_gui/viz/pareto_dialogs.py`

- `_compute_stable_limits(ref_arr: Optional[np.ndarray], front_arr: Optional[np.ndarray], pop_arr: Optional[np.ndarray]) -> Optional[Tuple[np.ndarray, np.ndarray]]` — funkcja modułowa; [wiersz 27](../src/pymoo_gui/viz/pareto_dialogs.py#L27).
- `PyQtGraphParetoDialog.__init__(self, ideal_front: np.ndarray, parent=None, axis_labels: Optional[Sequence[str]]=None, title: Optional[str]=None, point_label: str='Population', front_label: str='Nondominated solutions', ref_label: str='Reference PF')` — metoda; [wiersz 66](../src/pymoo_gui/viz/pareto_dialogs.py#L66).
- `PyQtGraphParetoDialog.set_auto_scale(self, enabled: bool) -> None` — metoda; [wiersz 148](../src/pymoo_gui/viz/pareto_dialogs.py#L148).
- `PyQtGraphParetoDialog.reset_view_limits(self) -> None` — metoda; [wiersz 152](../src/pymoo_gui/viz/pareto_dialogs.py#L152).
- `PyQtGraphParetoDialog._reference_limits_signature(self, ref_arr: Optional[np.ndarray]) -> Optional[Tuple[int, float, float, float, float]]` — metoda; [wiersz 158](../src/pymoo_gui/viz/pareto_dialogs.py#L158).
- `PyQtGraphParetoDialog._set_fixed_limits(self, mins: np.ndarray, maxs: np.ndarray) -> None` — metoda; [wiersz 170](../src/pymoo_gui/viz/pareto_dialogs.py#L170).
- `PyQtGraphParetoDialog._apply_fixed_limits(self, ref_arr: Optional[np.ndarray], front_arr: Optional[np.ndarray], pop_arr: Optional[np.ndarray]) -> None` — metoda; [wiersz 179](../src/pymoo_gui/viz/pareto_dialogs.py#L179).
- `PyQtGraphParetoDialog.get_axis_limits(self) -> Optional[Tuple[float, float, float, float]]` — metoda; [wiersz 204](../src/pymoo_gui/viz/pareto_dialogs.py#L204).
- `PyQtGraphParetoDialog.update_points(self, pop_F: Optional[np.ndarray], front_F: Optional[np.ndarray], ref_F: Optional[np.ndarray], gen: Optional[int]=None) -> None` — metoda; [wiersz 214](../src/pymoo_gui/viz/pareto_dialogs.py#L214).
- `PyQtGraphParetoDialog.update_points._finite_rows(data: Optional[np.ndarray]) -> Optional[np.ndarray]` — funkcja zagnieżdżona; [wiersz 222](../src/pymoo_gui/viz/pareto_dialogs.py#L222).
- `PyQtGraphParetoDialog.update_points._as_2d(arr: Optional[np.ndarray]) -> Optional[np.ndarray]` — funkcja zagnieżdżona; [wiersz 229](../src/pymoo_gui/viz/pareto_dialogs.py#L229).
- `MatplotlibParetoDialog.__init__(self, ideal_front: np.ndarray, parent=None, equal_aspect: bool=False, axis_labels: Optional[Sequence[str]]=None, title: Optional[str]=None, point_label: str='Population', front_label: str='Nondominated solutions', ref_label: str='Reference PF')` — metoda; [wiersz 269](../src/pymoo_gui/viz/pareto_dialogs.py#L269).
- `MatplotlibParetoDialog._apply_equal_aspect(self) -> None` — metoda; [wiersz 357](../src/pymoo_gui/viz/pareto_dialogs.py#L357).
- `MatplotlibParetoDialog.reset_view_limits(self) -> None` — metoda; [wiersz 364](../src/pymoo_gui/viz/pareto_dialogs.py#L364).
- `MatplotlibParetoDialog.update_points(self, pop_F: Optional[np.ndarray], front_F: Optional[np.ndarray], ref_F: Optional[np.ndarray], gen: Optional[int]=None) -> None` — metoda; [wiersz 368](../src/pymoo_gui/viz/pareto_dialogs.py#L368).
- `MatplotlibParetoDialog.update_points._finite_rows(data: Optional[np.ndarray]) -> Optional[np.ndarray]` — funkcja zagnieżdżona; [wiersz 376](../src/pymoo_gui/viz/pareto_dialogs.py#L376).
- `MatplotlibParetoDialog.update_points._as_dim(arr: Optional[np.ndarray]) -> Optional[np.ndarray]` — funkcja zagnieżdżona; [wiersz 383](../src/pymoo_gui/viz/pareto_dialogs.py#L383).
- `MatplotlibParetoDialog.set_auto_scale(self, enabled: bool) -> None` — metoda; [wiersz 484](../src/pymoo_gui/viz/pareto_dialogs.py#L484).
- `MatplotlibParetoDialog.get_axis_limits(self) -> Optional[Tuple[float, ...]]` — metoda; [wiersz 488](../src/pymoo_gui/viz/pareto_dialogs.py#L488).
- `OneDParetoDialog.__init__(self, ideal_front: np.ndarray, parent=None, axis_labels: Optional[Sequence[str]]=None, title: Optional[str]=None, point_label: str='Population', front_label: str='Nondominated solutions', ref_label: str='Reference PF')` — metoda; [wiersz 504](../src/pymoo_gui/viz/pareto_dialogs.py#L504).
- `OneDParetoDialog.set_auto_scale(self, enabled: bool) -> None` — metoda; [wiersz 559](../src/pymoo_gui/viz/pareto_dialogs.py#L559).
- `OneDParetoDialog.reset_view_limits(self) -> None` — metoda; [wiersz 563](../src/pymoo_gui/viz/pareto_dialogs.py#L563).
- `OneDParetoDialog.get_axis_limits(self) -> Optional[Tuple[float, float, float, float]]` — metoda; [wiersz 567](../src/pymoo_gui/viz/pareto_dialogs.py#L567).
- `OneDParetoDialog.update_points(self, pop_F: Optional[np.ndarray], front_F: Optional[np.ndarray], ref_F: Optional[np.ndarray], gen: Optional[int]=None) -> None` — metoda; [wiersz 576](../src/pymoo_gui/viz/pareto_dialogs.py#L576).
- `OneDParetoDialog.update_points._finite_rows(data: Optional[np.ndarray]) -> Optional[np.ndarray]` — funkcja zagnieżdżona; [wiersz 584](../src/pymoo_gui/viz/pareto_dialogs.py#L584).
- `OneDParetoDialog.update_points._as_1d(arr: Optional[np.ndarray]) -> Optional[np.ndarray]` — funkcja zagnieżdżona; [wiersz 591](../src/pymoo_gui/viz/pareto_dialogs.py#L591).
- `UnifiedParetoDialog.__init__(self, ideal_front: np.ndarray, parent=None, equal_aspect: bool=False, objective_names: Optional[Sequence[str]]=None)` — metoda; [wiersz 689](../src/pymoo_gui/viz/pareto_dialogs.py#L689).
- `UnifiedParetoDialog.show(self) -> None` — metoda; [wiersz 755](../src/pymoo_gui/viz/pareto_dialogs.py#L755).
- `UnifiedParetoDialog.set_auto_scale(self, enabled: bool) -> None` — metoda; [wiersz 759](../src/pymoo_gui/viz/pareto_dialogs.py#L759).
- `UnifiedParetoDialog.get_axis_limits(self) -> Optional[Tuple[float, ...]]` — metoda; [wiersz 764](../src/pymoo_gui/viz/pareto_dialogs.py#L764).
- `UnifiedParetoDialog.update_points(self, pop_F: Optional[np.ndarray], front_F: Optional[np.ndarray], ref_F: Optional[np.ndarray], gen: Optional[int]=None) -> None` — metoda; [wiersz 770](../src/pymoo_gui/viz/pareto_dialogs.py#L770).
- `UnifiedParetoDialog.update_points._reduce(arr: Optional[np.ndarray]) -> Optional[np.ndarray]` — funkcja zagnieżdżona; [wiersz 778](../src/pymoo_gui/viz/pareto_dialogs.py#L778).
- `UnifiedParetoDialog.__getattr__(self, name)` — metoda; [wiersz 794](../src/pymoo_gui/viz/pareto_dialogs.py#L794).
- `PyQtGraphParetoWidget.__init__(self, *args, **kwargs)` — metoda; [wiersz 802](../src/pymoo_gui/viz/pareto_dialogs.py#L802).
- `MatplotlibParetoWidget.__init__(self, *args, **kwargs)` — metoda; [wiersz 811](../src/pymoo_gui/viz/pareto_dialogs.py#L811).
- `OneDParetoWidget.__init__(self, *args, **kwargs)` — metoda; [wiersz 820](../src/pymoo_gui/viz/pareto_dialogs.py#L820).
- `UnifiedParetoWidget.__init__(self, ideal_front: np.ndarray, parent=None, equal_aspect: bool=False, objective_names: Optional[Sequence[str]]=None)` — metoda; [wiersz 830](../src/pymoo_gui/viz/pareto_dialogs.py#L830).
- `UnifiedParetoWidget.set_auto_scale(self, enabled: bool) -> None` — metoda; [wiersz 912](../src/pymoo_gui/viz/pareto_dialogs.py#L912).
- `UnifiedParetoWidget.set_show_population(self, enabled: bool) -> None` — metoda; [wiersz 917](../src/pymoo_gui/viz/pareto_dialogs.py#L917).
- `UnifiedParetoWidget.get_axis_limits(self) -> Optional[Tuple[float, ...]]` — metoda; [wiersz 925](../src/pymoo_gui/viz/pareto_dialogs.py#L925).
- `UnifiedParetoWidget._reduce_points(self, arr: Optional[np.ndarray]) -> Optional[np.ndarray]` — metoda; [wiersz 931](../src/pymoo_gui/viz/pareto_dialogs.py#L931).
- `UnifiedParetoWidget._snapshot_points(self, arr: Optional[np.ndarray]) -> Optional[np.ndarray]` — metoda; [wiersz 942](../src/pymoo_gui/viz/pareto_dialogs.py#L942).
- `UnifiedParetoWidget._shape_of(self, arr: Optional[np.ndarray]) -> Optional[Tuple[int, ...]]` — metoda; [wiersz 954](../src/pymoo_gui/viz/pareto_dialogs.py#L954).
- `UnifiedParetoWidget._render_points(self) -> None` — metoda; [wiersz 958](../src/pymoo_gui/viz/pareto_dialogs.py#L958).
- `UnifiedParetoWidget.render_snapshot(self) -> dict` — metoda; [wiersz 970](../src/pymoo_gui/viz/pareto_dialogs.py#L970).
- `UnifiedParetoWidget.update_points(self, pop_F: Optional[np.ndarray], front_F: Optional[np.ndarray], ref_F: Optional[np.ndarray], gen: Optional[int]=None) -> None` — metoda; [wiersz 980](../src/pymoo_gui/viz/pareto_dialogs.py#L980).
- `UnifiedParetoWidget.__getattr__(self, name)` — metoda; [wiersz 994](../src/pymoo_gui/viz/pareto_dialogs.py#L994).

## Anonimowe funkcje `lambda`

Anonimowe funkcje obejmują fabryki problemów wpisane do `PROBLEMS` oraz krótkie procedury obsługi przycisków GUI.

- `lambda ` — [wiersz 779](../src/pymoo_gui/app.py#L779).
- `lambda ` — [wiersz 780](../src/pymoo_gui/app.py#L780).
- `lambda _problem, pf_name=filename, n_obj=expected_n_obj` — [wiersz 112](../src/pymoo_gui/problems/registry.py#L112).
- `lambda n_var=default_n_var, problem_name=name` — [wiersz 221](../src/pymoo_gui/problems/registry.py#L221).
- `lambda n_var=default_n_var, n_obj=default_n_obj, problem_name=name` — [wiersz 236](../src/pymoo_gui/problems/registry.py#L236).
- `lambda n_var=default_n_var, p_name=problem_name, objective_count=n_obj` — [wiersz 285](../src/pymoo_gui/problems/registry.py#L285).
- `lambda n_var=3` — [wiersz 336](../src/pymoo_gui/problems/registry.py#L336).
- `lambda n_var=10` — [wiersz 369](../src/pymoo_gui/problems/registry.py#L369).
- `lambda n_var=30` — [wiersz 376](../src/pymoo_gui/problems/registry.py#L376).
- `lambda n_var=30` — [wiersz 383](../src/pymoo_gui/problems/registry.py#L383).
- `lambda n_var=30` — [wiersz 390](../src/pymoo_gui/problems/registry.py#L390).
- `lambda n_var=30` — [wiersz 397](../src/pymoo_gui/problems/registry.py#L397).
- `lambda n_var=10` — [wiersz 404](../src/pymoo_gui/problems/registry.py#L404).
- `lambda n_var=10` — [wiersz 411](../src/pymoo_gui/problems/registry.py#L411).
- `lambda n_var=10` — [wiersz 418](../src/pymoo_gui/problems/registry.py#L418).
- `lambda n_var=30` — [wiersz 425](../src/pymoo_gui/problems/registry.py#L425).
- `lambda n_var=30` — [wiersz 430](../src/pymoo_gui/problems/registry.py#L430).
- `lambda n_var=30` — [wiersz 431](../src/pymoo_gui/problems/registry.py#L431).
- `lambda n_var=30` — [wiersz 432](../src/pymoo_gui/problems/registry.py#L432).
- `lambda n_var=30` — [wiersz 433](../src/pymoo_gui/problems/registry.py#L433).
- `lambda n_var=30` — [wiersz 434](../src/pymoo_gui/problems/registry.py#L434).
- `lambda n_var=30` — [wiersz 435](../src/pymoo_gui/problems/registry.py#L435).
- `lambda n_var=30` — [wiersz 436](../src/pymoo_gui/problems/registry.py#L436).
- `lambda n_var=30` — [wiersz 437](../src/pymoo_gui/problems/registry.py#L437).
- `lambda n_var=30` — [wiersz 438](../src/pymoo_gui/problems/registry.py#L438).
- `lambda n_var=30` — [wiersz 439](../src/pymoo_gui/problems/registry.py#L439).

## Funkcje testowe

### `tests/test_custom_algorithm_runtime.py`

- `test_ibea_runtime_on_schaffer() -> None` — funkcja modułowa; [wiersz 9](../tests/test_custom_algorithm_runtime.py#L9).
- `test_gde3_runtime_on_schaffer() -> None` — funkcja modułowa; [wiersz 22](../tests/test_custom_algorithm_runtime.py#L22).

### `tests/test_dtlz_pareto_fronts.py`

- `_dtlz_front(problem_key: str, n_obj: int=3) -> np.ndarray` — funkcja modułowa; [wiersz 9](../tests/test_dtlz_pareto_fronts.py#L9).
- `test_dtlz_fronts_are_dense_finite_and_three_dimensional(problem_key: str) -> None` — funkcja modułowa; [wiersz 18](../tests/test_dtlz_pareto_fronts.py#L18).
- `test_dtlz_fronts_follow_their_expected_geometry() -> None` — funkcja modułowa; [wiersz 27](../tests/test_dtlz_pareto_fronts.py#L27).
- `test_dtlz7_front_uses_only_the_disconnected_optimal_intervals() -> None` — funkcja modułowa; [wiersz 40](../tests/test_dtlz_pareto_fronts.py#L40).

### `tests/test_empty_benchmark_template.py`

- `test_empty_benchmark_template_evaluates_vectorized_objectives() -> None` — funkcja modułowa; [wiersz 14](../tests/test_empty_benchmark_template.py#L14).
- `test_empty_benchmark_template_validates_configuration() -> None` — funkcja modułowa; [wiersz 27](../tests/test_empty_benchmark_template.py#L27).
- `test_empty_benchmark_template_exposes_registration_contract() -> None` — funkcja modułowa; [wiersz 36](../tests/test_empty_benchmark_template.py#L36).

### `tests/test_lmoea_ds_runtime.py`

- `test_lmoea_ds_runtime_on_schaffer() -> None` — funkcja modułowa; [wiersz 8](../tests/test_lmoea_ds_runtime.py#L8).

### `tests/test_metric_trajectories.py`

- `test_metric_trajectories_store_finite_generation_values() -> None` — funkcja modułowa; [wiersz 16](../tests/test_metric_trajectories.py#L16).
- `test_main_run_updates_and_resets_metric_trajectories() -> None` — funkcja modułowa; [wiersz 38](../tests/test_metric_trajectories.py#L38).
- `test_clear_button_clears_console_and_visual_charts() -> None` — funkcja modułowa; [wiersz 73](../tests/test_metric_trajectories.py#L73).

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

### `tests/test_registry_integrity.py`

- `test_algorithm_registry_has_required_structure() -> None` — funkcja modułowa; [wiersz 7](../tests/test_registry_integrity.py#L7).
- `test_problem_registry_has_required_structure() -> None` — funkcja modułowa; [wiersz 16](../tests/test_registry_integrity.py#L16).

## Jak aktualizować katalog

Po dodaniu lub usunięciu funkcji należy ponownie przeskanować `run_gui.py`, `src/**/*.py` i `tests/**/*.py`. Kontrolne liczby z tego dokumentu powinny zgadzać się z liczbą węzłów `ast.FunctionDef`, `ast.AsyncFunctionDef` i `ast.Lambda` w tych plikach.
