from __future__ import annotations

from datetime import date
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    KeepTogether,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs" / "Raport_poprawek_po_recenzji.pdf"

NAVY = colors.HexColor("#17365D")
BLUE = colors.HexColor("#2F75B5")
LIGHT_BLUE = colors.HexColor("#D9EAF7")
LIGHT_GREY = colors.HexColor("#F2F4F7")
MID_GREY = colors.HexColor("#64748B")
GREEN = colors.HexColor("#2E7D32")
AMBER = colors.HexColor("#B26A00")
RED = colors.HexColor("#B3261E")
WHITE = colors.white


def register_fonts() -> None:
    pdfmetrics.registerFont(TTFont("Arial", r"C:\Windows\Fonts\arial.ttf"))
    pdfmetrics.registerFont(TTFont("Arial-Bold", r"C:\Windows\Fonts\arialbd.ttf"))


def page_decor(canvas, doc) -> None:
    canvas.saveState()
    width, height = A4
    canvas.setStrokeColor(colors.HexColor("#D6DEE8"))
    canvas.setLineWidth(0.5)
    canvas.line(18 * mm, height - 15 * mm, width - 18 * mm, height - 15 * mm)
    canvas.setFont("Arial", 8)
    canvas.setFillColor(MID_GREY)
    canvas.drawString(18 * mm, height - 11.5 * mm, "AGtest-framework — raport odpowiedzi na uwagi recenzenta")
    canvas.drawRightString(width - 18 * mm, 10 * mm, f"Strona {doc.page}")
    canvas.restoreState()


def status_cell(text: str, color: colors.Color, style: ParagraphStyle) -> Paragraph:
    return Paragraph(f'<font color="{color.hexval()}"><b>{text}</b></font>', style)


def build_pdf() -> Path:
    register_fonts()
    styles = getSampleStyleSheet()
    normal = ParagraphStyle(
        "NormalPL",
        parent=styles["BodyText"],
        fontName="Arial",
        fontSize=9.4,
        leading=13.2,
        textColor=colors.HexColor("#1F2937"),
        spaceAfter=5,
    )
    small = ParagraphStyle(
        "SmallPL",
        parent=normal,
        fontSize=8.2,
        leading=10.8,
        spaceAfter=2,
    )
    title = ParagraphStyle(
        "TitlePL",
        parent=normal,
        fontName="Arial-Bold",
        fontSize=24,
        leading=29,
        alignment=TA_CENTER,
        textColor=NAVY,
        spaceAfter=10,
    )
    subtitle = ParagraphStyle(
        "SubtitlePL",
        parent=normal,
        fontSize=11.5,
        leading=16,
        alignment=TA_CENTER,
        textColor=MID_GREY,
        spaceAfter=10,
    )
    h1 = ParagraphStyle(
        "H1PL",
        parent=normal,
        fontName="Arial-Bold",
        fontSize=15,
        leading=19,
        textColor=NAVY,
        spaceBefore=10,
        spaceAfter=7,
        keepWithNext=True,
    )
    h2 = ParagraphStyle(
        "H2PL",
        parent=normal,
        fontName="Arial-Bold",
        fontSize=11.2,
        leading=14,
        textColor=BLUE,
        spaceBefore=7,
        spaceAfter=4,
        keepWithNext=True,
    )
    bullet = ParagraphStyle(
        "BulletPL",
        parent=normal,
        leftIndent=11,
        firstLineIndent=-7,
        bulletIndent=3,
        spaceAfter=2.5,
    )
    table_text = ParagraphStyle(
        "TableText",
        parent=small,
        fontSize=7.7,
        leading=10.2,
        spaceAfter=0,
    )
    table_header = ParagraphStyle(
        "TableHeader",
        parent=table_text,
        fontName="Arial-Bold",
        textColor=WHITE,
        alignment=TA_LEFT,
    )
    callout = ParagraphStyle(
        "Callout",
        parent=normal,
        fontSize=9.5,
        leading=13.5,
        textColor=NAVY,
        borderColor=BLUE,
        borderWidth=0.8,
        borderPadding=7,
        backColor=colors.HexColor("#EEF6FC"),
        spaceBefore=5,
        spaceAfter=8,
    )

    doc = BaseDocTemplate(
        str(OUTPUT),
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=20 * mm,
        bottomMargin=17 * mm,
        title="Raport poprawek po uwagach recenzenta — AGtest-framework",
        author="AGtest-framework",
        subject="Stan realizacji uwag recenzenta i sposób wprowadzenia poprawek",
    )
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="main")
    doc.addPageTemplates([PageTemplate(id="report", frames=[frame], onPage=page_decor)])

    story = []
    story.append(Spacer(1, 25 * mm))
    story.append(Paragraph("Raport poprawek po uwagach recenzenta", title))
    story.append(Paragraph("AGtest-framework — stan implementacji, sposób naprawy i weryfikacja", subtitle))
    story.append(Spacer(1, 7 * mm))
    story.append(
        Table(
            [
                [Paragraph("Dokument źródłowy", table_header), Paragraph("Analiza_uwag_recenzenta.pdf", table_text)],
                [Paragraph("Zakres", table_header), Paragraph("8 uwag recenzenta, kod, dokumentacja, testy i eksport", table_text)],
                [Paragraph("Data kontroli", table_header), Paragraph(str(date.today()), table_text)],
                [Paragraph("Stan testów", table_header), Paragraph("280/280 testów zakończonych powodzeniem", table_text)],
                [Paragraph("Kontrola integracyjna", table_header), Paragraph("31/31 algorytmów, 116/116 fabryk problemów, GUI, eksport oraz backendy thread/process", table_text)],
            ],
            colWidths=[45 * mm, 115 * mm],
            style=TableStyle(
                [
                    ("BACKGROUND", (0, 0), (0, -1), NAVY),
                    ("BACKGROUND", (1, 0), (1, -1), LIGHT_GREY),
                    ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#CBD5E1")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 7),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ]
            ),
        )
    )
    story.append(Spacer(1, 12 * mm))
    story.append(
        Paragraph(
            "Wniosek ogólny: najpoważniejsze problemy metodologiczne z nazwami algorytmów, punktem HV, definicją metryki Spread oraz reprodukcją eksportów zostały usunięte. Rozszerzenia katalogu algorytmów i benchmarków są znaczne, lecz pełna walidacja publikacyjna nadal wymaga wieloseedowych eksperymentów statystycznych i porównania wybranych portów z implementacjami referencyjnymi.",
            callout,
        )
    )
    story.append(PageBreak())

    story.append(Paragraph("1. Podsumowanie statusu uwag", h1))
    summary_rows = [
        [Paragraph("Lp.", table_header), Paragraph("Uwaga", table_header), Paragraph("Status", table_header), Paragraph("Wynik", table_header)],
        [Paragraph("1", table_text), Paragraph("Zbyt mało współczesnych algorytmów", table_text), status_cell("CZĘŚCIOWO", AMBER, table_text), Paragraph("Dodano szeroki zestaw nowych metod i metadane pochodzenia; brak pełnej walidacji PlatEMO i statystyki wielu seedów.", table_text)],
        [Paragraph("2", table_text), Paragraph("Niewystarczający zakres benchmarków", table_text), status_cell("CZĘŚCIOWO", AMBER, table_text), Paragraph("Rejestr rozszerzono do 116 problemów i dodano macierz możliwości; nadal niewielka liczba problemów multimodalnych i dyskretnych.", table_text)],
        [Paragraph("3", table_text), Paragraph("Niejasny wkład ponad pymoo", table_text), status_cell("CZĘŚCIOWO", AMBER, table_text), Paragraph("Pochodzenie oznaczono w plikach i rejestrze; narrację i tabelę porównawczą trzeba konsekwentnie przenieść do finalnego manuskryptu.", table_text)],
        [Paragraph("4", table_text), Paragraph("Nazwy nie odpowiadają implementacjom", table_text), status_cell("POPRAWIONO", GREEN, table_text), Paragraph("Rozdzielono standardowy MOEA/D od MOEA/D-IEpsilon; MOEA/D-RNN otrzymał rzeczywiste uczenie online i ostrożne oznaczenie adapted port.", table_text)],
        [Paragraph("5", table_text), Paragraph("Niepoprawny automatyczny punkt HV", table_text), status_cell("POPRAWIONO", GREEN, table_text), Paragraph("Wspólny resolver zamraża ideal, nadir, normalizację i punkt odniesienia przed eksperymentem.", table_text)],
        [Paragraph("6", table_text), Paragraph("Niejasne definicje wskaźników", table_text), status_cell("POPRAWIONO", GREEN, table_text), Paragraph("Spread przemianowano na Pairwise objective-space spread; Delta i HV opisano zgodnie z rzeczywistą interpretacją.", table_text)],
        [Paragraph("7", table_text), Paragraph("Niespójny przykład i słaba walidacja", table_text), status_cell("TECHNICZNIE WDROŻONO", BLUE, table_text), Paragraph("Dodano wspólny run_id i testy macierzy przypadków. Finalny manuskrypt musi jeszcze użyć jednego wybranego archiwum wyników.", table_text)],
        [Paragraph("8", table_text), Paragraph("Eksport nie zapewnia reprodukcji", table_text), status_cell("POPRAWIONO", GREEN, table_text), Paragraph("Każdy workbook ma Configuration; Multi tworzy manifest JSON, runs.xlsx i osobne wyniki każdego przebiegu.", table_text)],
    ]
    story.append(
        Table(
            summary_rows,
            colWidths=[9 * mm, 43 * mm, 31 * mm, 77 * mm],
            repeatRows=1,
            style=TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), NAVY),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT_GREY]),
                    ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#C7D0DB")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 5),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ]
            ),
        )
    )

    def add_bullets(items: list[str]) -> None:
        for item in items:
            story.append(Paragraph(f"• {item}", bullet))

    def add_section(number: int, heading: str, status: str, status_color, diagnosis: str, changes: list[str], evidence: list[str], remaining: list[str]) -> None:
        story.append(Paragraph(f"{number}. {heading}", h1))
        story.append(Paragraph(f'<b>Status:</b> <font color="{status_color.hexval()}"><b>{status}</b></font>', normal))
        story.append(Paragraph("Ocena", h2))
        story.append(Paragraph(diagnosis, normal))
        story.append(Paragraph("Co poprawiono i w jaki sposób", h2))
        add_bullets(changes)
        story.append(Paragraph("Dowody w aktualnym frameworku", h2))
        add_bullets(evidence)
        if remaining:
            story.append(Paragraph("Co pozostaje do wykonania", h2))
            add_bullets(remaining)
        story.append(Spacer(1, 2 * mm))

    story.append(PageBreak())
    add_section(
        1,
        "Zbyt mało współczesnych algorytmów",
        "częściowo poprawiono",
        AMBER,
        "Uwaga została potraktowana jako problem jakości i weryfikacji, a nie wyłącznie liczby pozycji w rejestrze. Framework zawiera obecnie 31 algorytmów, w tym nowe metody surrogate-assisted, constrained, large-scale, dynamic i micro-population.",
        [
            "Dodano m.in. PIEA, PIMD, TEA, SSDE, DISK, DISK+, PEA+, TSPP, MaO-TSP+, DSSEA, μMaOEA, CMOEA-CD, CMOBR i DVCEA.",
            "Dla wpisów algorytmów wprowadzono pola implementation_type, reference, source_commit i verified_against.",
            "Dodano dokument RECENT_ALGORITHMS.md opisujący pochodzenie, parametry, ograniczenia oraz zakres weryfikacji nowych metod.",
            "Dodano testy mechanizmów artykułowych, krótkich deterministycznych przebiegów i integracji GUI/Multi.",
        ],
        [
            "Smoke test wykonał 31/31 algorytmów przez dwa pokolenia bez błędu.",
            "Testy m.in. test_recent_algorithms.py, test_rewritten_article_algorithms.py, test_standalone_classic_algorithms.py oraz test_article_alignment_corrections.py.",
            "Rejestr jawnie zastrzega brak roszczenia o statystyczną równoważność tam, gdzie wykonano tylko testy mechanizmów.",
        ],
        [
            "Wykonać porównanie wybranych 5–8 portów z kodem referencyjnym PlatEMO dla wielu seedów.",
            "Uzupełnić source_commit konkretnym hashem upstream albo wartością not applicable wraz z uzasadnieniem; obecnie pole istnieje, lecz wszystkie wpisy mają wartość pustą.",
            "Dodać mediany, IQR i testy statystyczne przed deklaracją zgodności numerycznej z publikacjami.",
        ],
    )

    add_section(
        2,
        "Niewystarczający zakres benchmarków",
        "znacznie rozszerzono, nadal częściowe",
        AMBER,
        "Katalog został rozszerzony z dominacji klasycznych rodzin do 116 problemów. Zawiera już problemy constrained, dynamiczne, large-scale, binarne, całkowitoliczbowe i mieszane, lecz pokrycie multimodalne oraz dyskretne nadal jest małe.",
        [
            "Dodano rodziny MW (14), C-DTLZ (11), DAS-CMOP (9), DF (9) i large-scale DTLZ (8), a także problem MMF oraz przykłady discrete i mixed.",
            "Rejestr problemów zawiera capabilities: typ zmiennych, rodzinę, ograniczenia, dynamikę, multimodalność, large-scale i dostępność frontu referencyjnego.",
            "Walidacja algorytm–problem blokuje kombinacje niezgodne z typem zmiennych, ograniczeniami lub wymaganiami benchmarku.",
        ],
        [
            "Aktualne zestawienie: 116 problemów; 36 constrained, 9 dynamicznych, 8 large-scale i 1 multimodalny.",
            "Typy zmiennych: 113 real, 1 binary, 1 integer i 1 mixed.",
            "Testy test_expanded_benchmark_capabilities.py i test_registry_integrity.py sprawdzają metadane oraz zgodność kombinacji.",
        ],
        [
            "Rozszerzyć benchmarki multimodalne i dyskretne, jeżeli te klasy mają być istotną częścią deklarowanego zakresu pracy.",
            "Nie deklarować pełnego pokrycia frontem referencyjnym: 70 wpisów ma obecnie status reference_front=unavailable.",
        ],
    )

    add_section(
        3,
        "Niejasny wkład ponad pymoo",
        "częściowo poprawiono",
        AMBER,
        "Kod i dokumentacja lepiej rozdzielają pochodzenie elementów, lecz ostateczne rozróżnienie musi zostać przedstawione także w manuskrypcie. Wartość frameworku należy opisywać jako warstwę zarządzania eksperymentem, a nie zamiennik pymoo.",
        [
            "Dodano nagłówki plików algorytmów i problemów wskazujące bibliotekę lub publikację bazową.",
            "Rejestr algorytmów przechowuje typ implementacji, źródło, zakres weryfikacji i opcjonalny commit źródłowy.",
            "README opisuje GUI, dynamiczne formularze, worker, historię epok, Multi, automatyczne metryki, eksport i reprodukcję jako wkład AGtest-framework.",
        ],
        [
            "Metadane są walidowane przez test_registry_integrity.py.",
            "Konfiguracja eksportowana do XLSX zawiera implementation type, source/reference, source commit i verified against.",
        ],
        [
            "Dodać do manuskryptu tabelę pymoo bezpośrednio vs AGtest-framework oraz jednoznaczny diagram odpowiedzialności.",
            "Nie nazywać integracji bibliotecznej własną implementacją, jeśli jest adapterem; zachować spójność pomiędzy kodem, rejestrem i tekstem publikacji.",
        ],
    )

    story.append(PageBreak())
    add_section(
        4,
        "Nazwy algorytmów nie odpowiadają implementacjom",
        "poprawiono",
        GREEN,
        "Pierwotna uwaga była zasadna. Standardowy Platypus.MOEAD nie może być opisywany jako MOEA/D-IEpsilon, a losowy predyktor rekurencyjny nie może być przedstawiany jako wyuczony RNN.",
        [
            "Standardowy adapter Platypus otrzymał jednoznaczne oznaczenie MOEA/D (Platypus), a prawdziwy MOEA/D-IEpsilon został wydzielony jako osobna adaptowana implementacja.",
            "MOEA/D-IEpsilon implementuje sterowanie poziomem epsilon zależne od udziału rozwiązań dopuszczalnych, mechanizmy artykułu i DE/polynomial mutation.",
            "MOEA/D-RNN ma obecnie uczenie online: loss, aktualizację wag gradientem, change detection, adaptive response oraz MOEA/D-DE.",
            "Nazwy obu metod zawierają dopisek adapted port, a verified_against nie deklaruje statystycznej równoważności.",
        ],
        [
            "Pliki moead_iepsilon.py i rnn_guided_dmo.py zawierają publikacje bazowe i opis implementacji.",
            "Test test_article_alignment_corrections.py weryfikuje uczenie wag RNN i mechanizmy MOEA/D-IEpsilon.",
            "RECENT_ALGORITHMS.md opisuje ograniczenia i zakres zgodności.",
        ],
        [
            "Dla pełnej zgodności publikacyjnej nadal potrzebne są wieloseedowe porównania z implementacjami referencyjnymi.",
        ],
    )

    add_section(
        5,
        "Niepoprawny automatyczny punkt HV",
        "poprawiono",
        GREEN,
        "Usunięto metodologicznie błędne stosowanie stałego [1.1,…,1.1] w surowej przestrzeni celów niezależnie od problemu.",
        [
            "Wprowadzono wspólny resolve_hv_config używany przez Main i Multi.",
            "Dla wiarygodnego frontu referencyjnego przed startem wyznaczane i zamrażane są ideal oraz nadir; cele są normalizowane stałym przekształceniem, a punkt efektywny wynosi [1.1,…,1.1].",
            "Bez wiarygodnego frontu tryb automatyczny jest niedostępny: Main wymaga ręcznego punktu w surowej przestrzeni, a Multi raportuje HV jako N/A.",
            "Konfiguracja HV jest zapisywana do arkuszy Configuration i HV Configuration.",
            "Obliczenie HV wymaga, aby zamrożony punkt odniesienia był gorszy od wszystkich analizowanych punktów.",
        ],
        [
            "test_hypervolume_configuration.py sprawdza stałość normalizacji między generacjami, walidację punktu i brak niebezpiecznego fallbacku.",
            "Smoke test potwierdził eksport ideal, nadir, raw reference point oraz effective reference point.",
        ],
        [],
    )

    add_section(
        6,
        "Niejasne definicje wskaźników",
        "poprawiono",
        GREEN,
        "Kod nie obliczał standardowego Deb’s Spread. Zamiast zmieniać matematykę bez uzasadnienia, metrykę uczciwie przemianowano i opisano zgodnie z jej rzeczywistą definicją.",
        [
            "Widoczna nazwa została zmieniona na Pairwise objective-space spread w GUI, wykresach i XLSX.",
            "Dodano jawnie nazwaną funkcję compute_mean_normalized_pairwise_separation; compute_spread pozostaje aliasem zgodności wstecznej.",
            "Dokumentacja wyjaśnia, że większa wartość oznacza większą średnią separację, a nie równomierność, i że skala jest wyznaczana z aktualnego zbioru.",
            "Delta pozostaje osobną metryką: niższa wartość jest lepsza, zero oznacza równomierne odstępy i pokrycie ekstremów, a metryka wymaga frontu referencyjnego.",
            "HV opisano jako miarę zbieżności i pokrycia zdominowanej przestrzeni, częściowo wrażliwą na różnorodność, ale nie jako czystą miarę równomierności.",
        ],
        [
            "test_pairwise_separation.py sprawdza wzór, normalizację, przypadki zdegenerowane i widoczną etykietę.",
            "test_delta.py sprawdza klasyczne Delta 2D i generalized spread dla większej liczby celów.",
        ],
        [],
    )

    story.append(PageBreak())
    add_section(
        7,
        "Niespójny przykład i zbyt słaba walidacja",
        "warstwa techniczna wdrożona; finalny przykład publikacyjny pozostaje do wykonania",
        BLUE,
        "Framework zapewnia już techniczne powiązanie artefaktów jednego przebiegu, ale spójność rysunków i tabel w publikacji zależy od użycia jednego konkretnego archiwum przy składzie manuskryptu.",
        [
            "Każdy przebieg otrzymuje unikalny UTC run_id zawierający algorytm, problem i seed.",
            "Ten sam run_id jest widoczny w GUI i Multi oraz używany w nazwach metryk, rozwiązań, screenshotu konfiguracji i wykresu Pareto.",
            "Testy pokrywają przypadki continuous 2D, constrained, binary, 3D/many-objective, large-scale i Multi.",
            "Automatyczne testy otwierają wygenerowane XLSX i porównują ich Configuration z uruchomieniem.",
        ],
        [
            "Smoke test: 31/31 algorytmów, 116/116 fabryk problemów, 49 plików frontów oraz oba backendy równoległe.",
            "test_plot_controls.py sprawdza wspólny run_id w workbookach Main; test_multi.py sprawdza zgodność konfiguracji metryk i rozwiązań.",
        ],
        [
            "Wykonać jeden finalny eksperyment publikacyjny i z jego run_id wygenerować wszystkie rysunki, tabele i opis w tekście.",
            "Zarchiwizować ten przebieg jako niezmienny pakiet oraz podać run_id w podpisach tabel i rysunków.",
        ],
    )

    add_section(
        8,
        "Eksport nie zapewnia reprodukcji",
        "poprawiono",
        GREEN,
        "Eksport został przebudowany tak, aby workbook nie był samą tabelą wyników, lecz kompletnym zapisem konfiguracji i środowiska przebiegu.",
        [
            "Każdy workbook metryk i rozwiązań zawiera angielski arkusz Configuration.",
            "Zapisywane są: run_id, framework i wersja, commit Git, czas UTC, problem key/label i parametry, algorithm key/label i parametry, typ i źródło implementacji, seed, termination, n_gen, final n_eval, pełna konfiguracja HV, wersje Python/pymoo/NumPy/SciPy/Platypus/scikit-learn, status oraz backend równoległy.",
            "Multi tworzy multi_experiments/&lt;experiment_id&gt;/experiment_manifest.json i runs.xlsx z jednym wierszem na kombinację.",
            "Manifest jest aktualizowany po każdym przebiegu i zachowywany także przy anulowaniu; każdy wynik zachowuje kopię pełnej konfiguracji.",
        ],
        [
            "test_experiment_configuration.py sprawdza format run_id, nazwy plików oraz angielskie pola Configuration.",
            "test_multi.py sprawdza identyczną konfigurację w workbookach metryk i rozwiązań, manifest JSON, runs.xlsx oraz przypadek anulowania.",
            "W pełnym smoke teście wszystkie 31 par plików XLSX zostało otwartych jako poprawne archiwa.",
        ],
        [
            "Przed eksperymentami publikacyjnymi zatwierdzić wszystkie zmiany i oznaczyć wersję tagiem; bieżący katalog roboczy zawiera niezacommitowane zmiany, których sam hash HEAD nie opisuje.",
            "Uzupełnić source_commit dla portów posiadających kod upstream albo jawnie zapisać not applicable — article-based implementation.",
        ],
    )

    story.append(PageBreak())
    story.append(Paragraph("9. Zakres wykonanej weryfikacji", h1))
    verification = [
        [Paragraph("Kontrola", table_header), Paragraph("Wynik", table_header), Paragraph("Znaczenie", table_header)],
        [Paragraph("pytest", table_text), Paragraph("280/280 passed", table_text), Paragraph("Brak regresji w testach jednostkowych, integracyjnych, GUI, metryk, rejestrów i eksportu.", table_text)],
        [Paragraph("compileall", table_text), Paragraph("passed", table_text), Paragraph("Wszystkie moduły src i bootstrap run_gui.py są składniowo poprawne.", table_text)],
        [Paragraph("GUI offscreen", table_text), Paragraph("passed", table_text), Paragraph("Okno główne tworzy się, zawiera wymagane zakładki i zamyka bez błędu.", table_text)],
        [Paragraph("Fabryki problemów", table_text), Paragraph("116/116", table_text), Paragraph("Każdy zarejestrowany problem został utworzony i obliczył cele dla próbki wejściowej.", table_text)],
        [Paragraph("Algorytmy", table_text), Paragraph("31/31", table_text), Paragraph("Każdy algorytm ukończył dwupokoleniowy przebieg na zgodnym benchmarku.", table_text)],
        [Paragraph("Fronty referencyjne", table_text), Paragraph("49 plików", table_text), Paragraph("Pliki .pf obecne w pakiecie zostały odczytane bez pobierania danych z sieci.", table_text)],
        [Paragraph("Równoległość", table_text), Paragraph("thread + process", table_text), Paragraph("Oba backendy dały wyniki zgodne z oceną sekwencyjną.", table_text)],
        [Paragraph("Eksport", table_text), Paragraph("passed", table_text), Paragraph("XLSX, Configuration, HV Configuration, manifest JSON i runs.xlsx zostały utworzone i otwarte.", table_text)],
    ]
    story.append(
        Table(
            verification,
            colWidths=[35 * mm, 33 * mm, 92 * mm],
            repeatRows=1,
            style=TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), NAVY),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT_GREY]),
                    ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#C7D0DB")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 5),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ]
            ),
        )
    )
    story.append(Paragraph("Ograniczenie interpretacji", h2))
    story.append(
        Paragraph(
            "Dwupokoleniowy smoke test potwierdza działanie kodu, przepływ danych i eksport, ale nie dowodzi jakości optymalizacji ani statystycznej zgodności z wynikami publikacji. Takie twierdzenie wymaga wielu niezależnych seedów, ustalonego budżetu ocen, benchmarków reprezentatywnych dla domeny, median/IQR oraz właściwych testów statystycznych.",
            callout,
        )
    )

    story.append(Paragraph("10. Rekomendowane następne kroki przed wysłaniem manuskryptu", h1))
    recommendations = [
        "Zatwierdzić aktualny kod w Git, oznaczyć wersję tagiem i wykonać finalne eksperymenty wyłącznie z czystego drzewa roboczego.",
        "Wybrać jeden run_id jako źródło wszystkich ilustracji i tabel przykładowego eksperymentu.",
        "Dla 5–8 najważniejszych nowych algorytmów wykonać 20–30 seedów oraz porównanie z PlatEMO lub inną implementacją referencyjną.",
        "Uzupełnić source_commit albo jawne uzasadnienie not applicable dla każdego wpisu rejestru.",
        "W manuskrypcie dodać tabelę pymoo/Platypus/AGtest-framework oraz tabelę statusu implementacji: adapter, adapted port, faithful port lub framework variant.",
        "Nie przedstawiać punktów 1, 2, 3 i 7 jako całkowicie zamkniętych, dopóki nie zostanie wykonana walidacja statystyczna i złożony spójny przykład publikacyjny.",
    ]
    add_bullets(recommendations)

    story.append(Paragraph("11. Konkluzja", h1))
    story.append(
        Paragraph(
            "Framework jest funkcjonalnie spójny po poprawkach i przeszedł pełny dostępny zestaw testów oraz kontrolę integracyjną wszystkich zarejestrowanych algorytmów. Krytyczne uwagi 4, 5, 6 i 8 zostały rozwiązane w kodzie. Dalsza praca dotyczy przede wszystkim jakości dowodu naukowego — nie kolejnych napraw wykonawczych: czystego wydania Git, jednego archiwum publikacyjnego, źródłowych commitów portów oraz wieloseedowej walidacji statystycznej.",
            callout,
        )
    )

    doc.build(story)
    return OUTPUT


if __name__ == "__main__":
    print(build_pdf())
