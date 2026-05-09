# Dokumentacja procesu

Ten plik dokumentuje **jak** pracowałem/am nad mini-projektem — jakie narzędzia AI wykorzystałem, jakie prompty pisałem, jakie decyzje podjąłem i co nie zadziałało.

> **PROCESS.md jest tak samo ważny jak kod.** Prowadzący ocenia świadome korzystanie z narzędzi AI — to jest kurs o aspektach AI.

---

## Narzędzia AI

[Lista narzędzi AI użytych w projekcie]

| Narzędzie | Do czego używałem |
|-----------|-------------------|
| Claude Code Sonnet 4.6 | Generowanie szkieletu skryptu |
| Gemini CLI | Zmiany w kodzie, Podstawowa analiza  |
| GitHub Copilot | Autouzupełnianie kodu w VS Code |
| Context7 | MCP do dokumentacji kodu |
| Gemini 2.5 Flash (API) | Wyjaśnianie ostrzeżeń licencyjnych w `--ai-explain` |

## Prompty

> Nie wklejaj outputu z AI — tylko prompty, które wpisywałeś/aś.

### Generowanie kodu i refaktoryzacja

```
Napisz skrypt skanujący zależności projektu (requirements.txt, package.json, itp.) i sprawdzający ich licencje.
Skrypt wypisuje listę zależności z licencjami. Tabelka wyników. Wyświetlanie w postaci grafu, skanując zaleności rekurencyjne 
od określonej głębokości domyślnie 2
```

**Kontekst:** Utworzenie backbone (struktury) skryptu, w ramach pierwszej iteracji nad problemem (Claude).

```
Seperate src/license_scanner.py to functionality based file so its more readable
```

**Kontekst:** Modularyzacja monolitycznego skryptu. Rozdzielenie logiki parsowania, pobierania danych z PyPI, budowania grafu i raportowania do osobnych modułów w pakiecie `src/scanner/`.

```
Create license type Enum having all known licenses. Explicitly Enum for MIT and other well known licenses
```

**Kontekst:** Wprowadzenie typu wyliczeniowego dla kategorii licencji (Permissive, Copyleft itp.) w celu poprawy bezpieczeństwa typów i czytelności kodu.


```
How can we make classification method more based
```

**Kontekst:** Ulepszenie metody klasyfikacji licencji w `src/scanner/classifier.py`. Poprzednia implementacja używała naiwnego dopasowywania podciągów z błędną kolejnością sprawdzeń (LGPL było klasyfikowane jako GPL). Wprowadzono trzypoziomowe dopasowanie: (1) dokładne dopasowanie identyfikatorów SPDX przez słownik `SPDX_MAP`, (2) obsługa złożonych licencji z operatorami OR/AND, (3) fallback substring z poprawioną kolejnością (agpl → lgpl → gpl). Dodano również trzy nowe wartości enum (`PERMISSIVE_OTHER`, `COPYLEFT_OTHER`, `WEAK_COPYLEFT_OTHER`) pokrywające licencje takie jak CC0, Unlicense, EUPL, EPL.

```
instead of arg parser let's use click
```

**Kontekst:** Zamiana standardowej biblioteki `argparse` na `click` w celu uzyskania czytelniejszego, bardziej deklaratywnego CLI. Click oferuje automatyczną walidację typów (np. `click.Path(exists=True)`), wbudowaną obsługę `--help` i niestandardowe typy parametrów (np. własny `DepthType`).

```
Allow depth to be "max which would go in BFS fashion"
```

**Kontekst:** Dodanie obsługi wartości `max` dla parametru `--depth`, która wyłącza limit głębokości i pozwala na pełne przejście BFS przez całe drzewo zależności. Zaimplementowano przez własny typ Click (`DepthType`) i zmianę sygnatury `build_graph` na `depth: int | None`.

```
Add column with depth info of table, and its usages
```

**Kontekst:** Rozszerzenie tabeli wyników o kolumnę `D` (głębokość BFS), aby użytkownik widział, czy pakiet jest zależnością bezpośrednią (głębokość 1) czy przechodnią. `build_graph` zwraca teraz dodatkowo słownik `depths: dict[str, int]`, który jest przekazywany do `print_table` i `draw_graph`.

```
Make networkx have different layout
```

**Kontekst:** Zastąpienie layoutu graphviz (`dot`) układem koncentrycznym (`shell_layout`) pogrupowanym według głębokości BFS — projekt w centrum, kolejne pierścienie to kolejne poziomy zależności. Dodano też parametr `--layout` (click.Choice) umożliwiający wybór spośród: `shell`, `spring`, `kamada_kawai`, `spectral`, `circular`.

```
Add --out arg which outputs formatted table
```

**Kontekst:** Dodanie flagi `--out <plik>` zapisującej tabelę wyników do pliku, niezależnie od wydruku na stdout. Wymagało refaktoryzacji `print_table` — zamiast bezpośrednich wywołań `print()` wprowadzono lokalną funkcję `out()` przyjmującą parametr `file`.

```
add --out-type pretty | csv. pretty is current one csv outputs to csv file
```

**Kontekst:** Pierwsza wersja wspierała tylko format tekstowy. Dodano opcję `--out-type` (pretty/csv) w celu umożliwienia maszynowego przetwarzania wyników. Ponieważ licencje z PyPI często zawierają pełny tekst licencji (wieloliniowy), biblioteka `csv` obsługuje poprawne cytowanie takich pól.

```
Instead of csv let's use jsonl
```

**Kontekst:** Zmiana formatu eksportu z CSV na JSONL (JSON Lines), gdzie każdy pakiet to oddzielna linia z obiektem JSON. Format JSONL jest bardziej naturalny dla danych o nieregularnej strukturze (np. wieloliniowe teksty licencji) i łatwiej go przetwarzać strumieniowo (`jq`, pandas, etc.).

```
Proposed Technical Implementation (Phase 1: Dynamic Graph)
We can add a --browser flag that uses pyvis to export the networkx graph to an HTML file.
```

**Kontekst:** Dodanie flagi `--browser <plik.html>` eksportującej interaktywny graf jako samodzielny plik HTML przy użyciu biblioteki `pyvis`. Graf umożliwia przeciąganie węzłów, zoom oraz tooltip z pełnymi informacjami o pakiecie (licencja, kategoria, głębokość). Rozmiar węzła skaluje się odwrotnie z głębokością. Kolor węzłów odpowiada tej samej konwencji co w widoku matplotlib.

```
Extend current script with --ai-explain arg which uses gemini (throws error if GOOGLE_API_KEY is not set) to explain why the warning was raised and what does it mean to the project
```

**Kontekst:** Dodanie flagi `--ai-explain` integrującej API Gemini (`gemini-2.5-flash`) z modułem `src/scanner/explain.py`. Skaner zbiera ostrzeżenia licencyjne (copyleft, weak copyleft, proprietary, unknown) i wysyła je do Gemini z system instruction nakazującym wyjaśnienie po polsku w kontekście prawnym (AI Act, RODO, IP). Brak zmiennej `GOOGLE_API_KEY` skutkuje błędem z instrukcją konfiguracji. Użyto biblioteki `google-genai` (już w zależnościach projektu).

### Debugowanie i poprawki

```
<br> tags doesn't work
```

**Kontekst:** Tooltips w `pyvis` nie renderują HTML — znaczniki `<br>` były wyświetlane jako tekst. Zamieniono na znaki nowej linii `\n`, które pyvis interpretuje poprawnie w oknie podpowiedzi.

## Decyzje

1. **Modularyzacja do pakietu `src/scanner/`** — Monolityczny skrypt stał się nieczytelny po dodaniu parsowania, grafu i raportowania. Podział na moduły (`parsers`, `graph`, `reporting`, `visualization`, `classifier`, `constants`, `pypi`) ułatwia testowanie i rozbudowę.

2. **SPDX jako podstawa klasyfikacji** — Zamiast polegać wyłącznie na heurystyce podciągów, wprowadzono słownik `SPDX_MAP` z ponad 40 identyfikatorami. Poprzednia kolejność sprawdzeń powodowała błąd: LGPL było klasyfikowane jako GPL.

3. **`depth=None` jako sentinel dla BFS bez limitu** — Zamiast dodawać osobny boolean `--no-limit`, wartość `None` dla głębokości jest semantycznie czytelna i nie wymaga zmian w logice grafu poza jednym warunkiem `if depth is None or level < depth`.

4. **JSONL zamiast CSV** — Pola licencji z PyPI często zawierają pełny tekst licencji z podziałami wierszy. JSONL naturalnie obsługuje takie dane bez ucieczek, a format jest bezpośrednio przetwarzalny przez `jq`, pandas czy narzędzia LLM.

5. **pyvis zamiast d3.js / plotly** — Biblioteka pyvis generuje samodzielny plik HTML bez potrzeby serwera i bez pisania JavaScript. Wystarczy otworzyć plik w przeglądarce.

6. **Gemini do wyjaśniania ostrzeżeń** — Zamiast statycznych komunikatów, `--ai-explain` wysyła zebrane ostrzeżenia do LLM, który wyjaśnia implikacje prawne w kontekście AI Act i RODO. Wybrano Gemini 2.5 Flash (szybki, tani) zamiast GPT/Claude, ponieważ `google-genai` było już w zależnościach projektu.

## Co nie zadziałało

1. **W przypadku wielu paczek graf w postaci png jest nieczytelny** — Rozszerzenie skryptu o argument umozliwiajacy dependencji output w postaci interaktywnego html, umozliwienie ograniczenia rekurencji skryptu

## Iteracje

1. **v1 — Monolityczny skrypt** — Jeden plik `src/license_scanner.py` z argparse, pobieraniem PyPI, budowaniem grafu i wizualizacją. Działał, ale był nieczytelny.

2. **v2 — Modularyzacja** — Podział na pakiet `src/scanner/` z osobnymi modułami. Wprowadzenie Enum dla licencji i kategorii.

3. **v3 — Lepsza klasyfikacja** — Słownik SPDX, obsługa złożonych licencji (OR/AND), poprawiona kolejność heurystyki, nowe kategorie (`PERMISSIVE_OTHER`, etc.).

4. **v4 — Rozbudowane CLI (click)** — Zamiana argparse na click, `--depth max`, kolumna głębokości w tabeli, wybór layoutu grafu, eksport tabeli (`--out`, `--out-type`).

5. **v5 — Interaktywny graf** — Dodanie `--browser` z pyvis, samodzielny plik HTML z możliwością eksploracji grafu zależności w przeglądarce.

6. **v6 — AI-powered wyjaśnienia** — Dodanie `--ai-explain` z integracją Gemini API. Nowy moduł `src/scanner/explain.py` zbiera ostrzeżenia i wysyła je do modelu z promptem systemowym ukierunkowanym na aspekty prawne i etyczne.
