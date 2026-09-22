"""Generate the repository function catalog directly from Python syntax trees."""

from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs" / "FUNCTION_CATALOG.md"
SKIPPED_PARTS = {".git", ".venv", ".venv-build", "build", "dist", "__pycache__"}


@dataclass(frozen=True)
class Declaration:
    qualified_name: str
    signature: str
    line: int
    kind: str


class CatalogVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.scope: list[tuple[str, str]] = []
        self.declarations: list[Declaration] = []
        self.classes = 0
        self.lambdas: list[int] = []

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self.classes += 1
        self.scope.append((node.name, "class"))
        self.generic_visit(node)
        self.scope.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._record_function(node, async_function=False)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._record_function(node, async_function=True)

    def _record_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef, *, async_function: bool) -> None:
        prefix = ".".join(name for name, _ in self.scope)
        qualified = f"{prefix}.{node.name}" if prefix else node.name
        if self.scope and self.scope[-1][1] == "class":
            kind = "metoda"
        elif self.scope:
            kind = "funkcja zagnieżdżona"
        else:
            kind = "funkcja modułowa"
        return_annotation = f" -> {ast.unparse(node.returns)}" if node.returns is not None else ""
        signature = f"{node.name}({ast.unparse(node.args)}){return_annotation}"
        self.declarations.append(Declaration(qualified, signature, node.lineno, kind))
        self.scope.append((node.name, "function"))
        self.generic_visit(node)
        self.scope.pop()

    def visit_Lambda(self, node: ast.Lambda) -> None:
        self.lambdas.append(node.lineno)
        self.generic_visit(node)


def python_files() -> list[Path]:
    return sorted(
        path for path in ROOT.rglob("*.py")
        if not any(part in SKIPPED_PARTS or part.startswith("pytest-cache-files-") for part in path.parts)
    )


def analyze(path: Path) -> CatalogVisitor:
    visitor = CatalogVisitor()
    visitor.visit(ast.parse(path.read_text(encoding="utf-8"), filename=str(path)))
    return visitor


def main() -> None:
    analyses = [(path, analyze(path)) for path in python_files()]
    runtime = [(path, data) for path, data in analyses if "tests" not in path.relative_to(ROOT).parts]
    tests = [(path, data) for path, data in analyses if "tests" in path.relative_to(ROOT).parts]
    total_declarations = sum(len(data.declarations) for _, data in analyses)
    total_classes = sum(data.classes for _, data in analyses)
    total_lambdas = sum(len(data.lambdas) for _, data in analyses)
    runtime_declarations = sum(len(data.declarations) for _, data in runtime)
    test_declarations = sum(len(data.declarations) for _, data in tests)

    lines = [
        "# Katalog funkcji AGtest-framework v0.1",
        "",
        "Dokument jest generowany z aktualnych drzew składniowych AST poleceniem",
        "`python scripts/generate_function_catalog.py`. Obejmuje kod aplikacji, testy, metody,",
        "funkcje zagnieżdżone i wyrażenia `lambda`; nie obejmuje symboli importowanych.",
        "",
        "## Wynik analizy",
        "",
        f"- Przeanalizowano **{len(analyses)}** plików Python.",
        f"- Kod uruchomieniowy zawiera **{runtime_declarations}** deklaracji funkcji i metod.",
        f"- Testy zawierają **{test_declarations}** deklaracji funkcji i metod.",
        f"- Łącznie znaleziono **{total_declarations}** deklaracji, **{total_classes}** klas i **{total_lambdas}** wyrażeń `lambda`.",
        "",
        "## Aktualny przepływ sterowania",
        "",
        "1. `run_gui.py` uruchamia aplikację lub samodzielny test pakietu EXE.",
        "2. `MainWindow` buduje trzy zakładki z rejestrów `PROBLEMS` i `ALGORITHMS`.",
        "3. `OptimizationWorker` prowadzi obliczenia poza wątkiem GUI, również w trybie `RAN step`.",
        "4. Callback generacyjny oblicza metryki i przekazuje migawki populacji do historii epok.",
        "5. Widoki Pareto i trajektorii prezentują dane, a warstwa eksportu zapisuje PNG i XLSX.",
        "6. `MultiExperimentWorker` wykonuje wybrane kombinacje problem–algorytm bez renderowania wykresów.",
        "",
        "## Zestawienie modułów",
        "",
        "| Plik | Deklaracje | Klasy | Lambda |",
        "|---|---:|---:|---:|",
    ]
    for path, data in analyses:
        relative = path.relative_to(ROOT).as_posix()
        lines.append(f"| `{relative}` | {len(data.declarations)} | {data.classes} | {len(data.lambdas)} |")

    lines.extend(["", "## Pełny indeks deklaracji", ""])
    for path, data in analyses:
        relative = path.relative_to(ROOT).as_posix()
        lines.extend([f"### `{relative}`", ""])
        if not data.declarations and not data.lambdas:
            lines.append("Brak deklaracji funkcji i wyrażeń `lambda`.")
        for declaration in data.declarations:
            link = f"../{relative}#L{declaration.line}"
            lines.append(
                f"- `{declaration.qualified_name}{declaration.signature[declaration.signature.find('('):]}` — "
                f"{declaration.kind}; [wiersz {declaration.line}]({link})."
            )
        for line in data.lambdas:
            lines.append(f"- `lambda` — wyrażenie anonimowe; [wiersz {line}](../{relative}#L{line}).")
        lines.append("")

    OUTPUT.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
