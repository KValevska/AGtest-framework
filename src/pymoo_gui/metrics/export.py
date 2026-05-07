"""
EN:
Helpers for building safe metrics export paths and writing a minimal XLSX workbook.

PL:
Pomaga zapisac historie metryk do pliku Excel w bezpiecznie nazwanym katalogu.
"""

# ------------------------------------------------------------------------------------
# File: export.py
# Contents: metrics export path builders, filename sanitizers and minimal XLSX writer.
# What happens here: metric-table rows are converted into worksheet XML and stored as an .xlsx archive.
# Role in the framework: persists dissertation experiment metrics in spreadsheet form for later analysis.
# Author: mgr inż. Kristina Valevska
# ------------------------------------------------------------------------------------

from __future__ import annotations

from datetime import datetime
from pathlib import Path
import re
import zipfile
from typing import Sequence
from xml.sax.saxutils import escape


EXPORT_DIR_NAME = "Tabeli_metryk"
SOLUTIONS_EXPORT_DIR_NAME = "Tabeli_rozwiązań"
# Znaki niedozwolone w nazwach plikow Windows.
INVALID_FILENAME_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]+')


def safe_filename_part(value: object, fallback: str) -> str:
    """
    EN:
    Sanitize a single filename segment for Windows-compatible metric exports.

    PL:
    Czysci fragment nazwy pliku, aby usunac znaki niedozwolone w Windows.
    """
    # Keep filenames readable while preventing characters rejected by common file systems.
    text = str(value or "").strip() or str(fallback)
    text = INVALID_FILENAME_CHARS.sub("_", text)
    text = re.sub(r"\s+", "_", text)
    text = text.strip("._ ")
    return text or str(fallback)


def timestamp_for_filename(now: datetime | None = None) -> str:
    """
    EN:
    Format a timestamp using only filename-safe characters.

    PL:
    Zwraca date i czas w formacie, ktory mozna bezpiecznie wstawic do nazwy pliku.
    """
    return (now or datetime.now()).strftime("%Y-%m-%d_%H-%M-%S")


def date_for_filename(now: datetime | None = None) -> str:
    """
    EN:
    Format only the current date for solution-table filenames.

    PL:
    Zwraca sama date w formacie wymaganym dla tabeli rozwiazan.
    """
    return (now or datetime.now()).strftime("%Y-%m-%d")


def metrics_export_path(
    project_root: Path,
    algorithm_name: object,
    problem_name: object,
    now: datetime | None = None,
) -> Path:
    """
    EN:
    Build the output path for a metrics spreadsheet for one algorithm/problem run.

    PL:
    Tworzy pelna sciezke pliku z metrykami dla konkretnego algorytmu i problemu.
    """
    export_dir = Path(project_root) / EXPORT_DIR_NAME
    filename = (
        f"{safe_filename_part(algorithm_name, 'Algorytm')}_"
        f"{safe_filename_part(problem_name, 'Problem')}_"
        f"{timestamp_for_filename(now)}.xlsx"
    )
    return export_dir / filename


def solutions_export_path(
    project_root: Path,
    algorithm_name: object,
    problem_name: object,
    now: datetime | None = None,
) -> Path:
    """
    EN:
    Build the output path for nondominated solution points from one run.

    PL:
    Tworzy sciezke pliku z punktami niezdominowanymi dla jednego uruchomienia.
    """
    export_dir = Path(project_root) / SOLUTIONS_EXPORT_DIR_NAME
    filename = (
        f"{safe_filename_part(algorithm_name, 'Algorytm')}_"
        f"{safe_filename_part(problem_name, 'Problem')}_"
        f"{date_for_filename(now)}.xlsx"
    )
    return export_dir / filename


def next_available_export_path(path: Path) -> Path:
    """
    EN:
    Return the first non-existing path by appending `_1`, `_2`, ... to the stem.

    PL:
    Zwraca pierwsza wolna sciezke, dopinajac `_1`, `_2`, ... do nazwy pliku.
    """
    candidate = Path(path)
    if not candidate.exists():
        return candidate
    stem = candidate.stem
    suffix = candidate.suffix
    parent = candidate.parent
    counter = 1
    while True:
        variant = parent / f"{stem}_{counter}{suffix}"
        if not variant.exists():
            return variant
        counter += 1


def _safe_sheet_name(value: object) -> str:
    """
    EN:
    Return an Excel-compatible worksheet name.

    PL:
    Zwraca nazwe arkusza zgodna z ograniczeniami Excela.
    """
    text = str(value or "").strip() or "Arkusz1"
    text = re.sub(r"[\[\]:*?/\\]+", "_", text).strip("'")
    return (text or "Arkusz1")[:31]


def _column_name(index: int) -> str:
    """
    EN:
    Convert a zero-based column index to an Excel column label.

    PL:
    Zamienia numer kolumny na oznaczenie Excela, np. 0 na A.
    """
    name = ""
    index += 1
    while index:
        index, rem = divmod(index - 1, 26)
        name = chr(65 + rem) + name
    return name


def _cell_xml(row_idx: int, col_idx: int, value: object) -> str:
    """
    EN:
    Serialize one worksheet cell as inline string or numeric XML.

    PL:
    Tworzy zapis XML jednej komorki arkusza, jako tekst albo liczbe.
    """
    ref = f"{_column_name(col_idx)}{row_idx}"
    if value is None:
        text = ""
    else:
        text = str(value).strip()
    if text in {"", "-"}:
        return f'<c r="{ref}" t="inlineStr"><is><t>{escape(text)}</t></is></c>'
    try:
        # Liczby zapisujemy jako liczby :)
        number = float(text)
    except ValueError:
        return f'<c r="{ref}" t="inlineStr"><is><t>{escape(text)}</t></is></c>'
    return f'<c r="{ref}"><v>{number:.15g}</v></c>'


def _worksheet_xml(headers: Sequence[str], rows: Sequence[Sequence[object]]) -> str:
    """
    EN:
    Build worksheet XML with one header row and metric data rows.

    PL:
    Sklada arkusz XML: pierwszy wiersz to naglowki, kolejne wiersze to wyniki.
    """
    sheet_rows = []
    header_cells = "".join(_cell_xml(1, col, header) for col, header in enumerate(headers))
    sheet_rows.append(f'<row r="1">{header_cells}</row>')
    for row_offset, row in enumerate(rows, start=2):
        cells = "".join(_cell_xml(row_offset, col, value) for col, value in enumerate(row))
        sheet_rows.append(f'<row r="{row_offset}">{cells}</row>')
    last_col = _column_name(max(len(headers), 1) - 1)
    last_row = max(len(rows) + 1, 1)
    dimension = f"A1:{last_col}{last_row}"
    # Zamrazamy pierwszy wiersz, aby naglowki byly widoczne przy przewijaniu.
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        f'<dimension ref="{dimension}"/>'
        "<sheetViews><sheetView workbookViewId=\"0\"><pane ySplit=\"1\" topLeftCell=\"A2\" "
        'activePane="bottomLeft" state="frozen"/></sheetView></sheetViews>'
        "<sheetData>"
        + "".join(sheet_rows)
        + "</sheetData></worksheet>"
    )


def _deduplicate_sheet_names(names: Sequence[object]) -> list[str]:
    """
    EN:
    Return Excel-safe worksheet names with deterministic suffixes for duplicates.

    PL:
    Zwraca poprawne nazwy arkuszy Excela i rozroznia ewentualne duplikaty.
    """
    seen: dict[str, int] = {}
    out: list[str] = []
    for raw_name in names:
        base_name = _safe_sheet_name(raw_name)
        candidate = base_name
        counter = seen.get(base_name, 0)
        while candidate in seen:
            counter += 1
            suffix = f"_{counter}"
            candidate = f"{base_name[: max(0, 31 - len(suffix))]}{suffix}" or f"Arkusz{counter}"
        seen[base_name] = counter
        seen[candidate] = 0
        out.append(candidate)
    return out


def write_xlsx_workbook(
    path: Path,
    sheets: Sequence[tuple[object, Sequence[str], Sequence[Sequence[object]]]],
) -> Path:
    """
    EN:
    Write a simple `.xlsx` workbook with one or more worksheets.

    PL:
    Zapisuje prosty skoroszyt `.xlsx` z jednym albo wieloma arkuszami.
    """
    if not sheets:
        raise ValueError("sheets must not be empty")
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    sheet_names = _deduplicate_sheet_names([sheet_name for sheet_name, _headers, _rows in sheets])
    for _sheet_name, headers, _rows in sheets:
        if not headers:
            raise ValueError("headers must not be empty")

    content_types_parts = [
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">',
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>',
        '<Default Extension="xml" ContentType="application/xml"/>',
        '<Override PartName="/xl/workbook.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>',
    ]
    for index in range(len(sheets)):
        content_types_parts.append(
            f'<Override PartName="/xl/worksheets/sheet{index + 1}.xml" '
            'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
        )
    content_types_parts.append("</Types>")
    content_types = "".join(content_types_parts)

    root_rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" '
        'Target="xl/workbook.xml"/>'
        "</Relationships>"
    )

    workbook_sheet_parts = []
    workbook_rels_parts = [
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">',
    ]
    for index, sheet_name in enumerate(sheet_names, start=1):
        safe_sheet_name_xml = escape(sheet_name, {'"': "&quot;"})
        workbook_sheet_parts.append(
            f'<sheet name="{safe_sheet_name_xml}" sheetId="{index}" r:id="rId{index}"/>'
        )
        workbook_rels_parts.append(
            f'<Relationship Id="rId{index}" '
            'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" '
            f'Target="worksheets/sheet{index}.xml"/>'
        )
    workbook_rels_parts.append("</Relationships>")
    workbook = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        f"<sheets>{''.join(workbook_sheet_parts)}</sheets></workbook>"
    )
    workbook_rels = "".join(workbook_rels_parts)

    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", content_types)
        zf.writestr("_rels/.rels", root_rels)
        zf.writestr("xl/workbook.xml", workbook)
        zf.writestr("xl/_rels/workbook.xml.rels", workbook_rels)
        for index, (_sheet_name, headers, rows) in enumerate(sheets, start=1):
            zf.writestr(f"xl/worksheets/sheet{index}.xml", _worksheet_xml(headers, rows))
    return path


def write_xlsx_table(
    path: Path,
    headers: Sequence[str],
    rows: Sequence[Sequence[object]],
    sheet_name: object = "Metryki",
) -> Path:
    """
    EN:
    Write a simple `.xlsx` workbook with one worksheet and a header row.

    PL:
    Zapisuje tabele metryk do pliku Excel. Funkcja uzywa tylko standardowej
    biblioteki Pythona, wiec nie wymaga dodatkowych pakietow do eksportu.

    Args:
        path (Path): EN: Destination workbook path.
                     PL: Miejsce zapisania pliku.
        headers (Sequence[str]): EN: Column labels for the first row.
                                 PL: Naglowki kolumn.
        rows (Sequence[Sequence[object]]): EN: Table rows to serialize.
                                           PL: Wiersze danych do zapisania.
        sheet_name (object): EN: Worksheet name.
                             PL: Nazwa arkusza.

    Returns:
        Path: EN: Path to the written workbook.
              PL: Sciezka do utworzonego pliku.

    Raises:
        ValueError: EN: If `headers` is empty.
                    PL: Gdy nie podano zadnych naglowkow.
        OSError: EN: If the destination cannot be created or written.
                 PL: Gdy system nie pozwala utworzyc albo zapisac pliku.
    """
    return write_xlsx_workbook(path, [(sheet_name, headers, rows)])
