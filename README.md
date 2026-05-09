# Audyt licencji

**Autor:** Dawid Glinkowski, nr indeksu: 266509

**Temat:** 1 — Audyt licencji w repozytorium

**Kurs:** Aspekty prawne, społeczne i etyczne w AI, PWr 2025/2026

> Lista tematów: [Zasady zaliczenia — Menu mini-projektów](https://github.com/laugustyniak/ai-ethics-law-course/blob/main/Zasady%20zaliczenia.md#menu-mini-projekt%C3%B3w)

---

## Quick Start

```bash
uv sync                        # zainstaluj zależności
cp .env.example .env           # skopiuj wzór zmiennych środowiskowych
# uzupełnij klucze API w .env (opcjonalnie dla przykładów LLM)

# Uruchomienie audytu dla bieżącego projektu
uv run src/license_scanner.py --browser wyniki/graph.html --out wyniki/licenses.txt
```

---

## Cel projektu

Projekt służy do automatycznego audytu licencji bibliotek Python w drzewie zależności. Kluczowe cele to:
- **Identyfikacja ryzyk prawnych**: Wykrywanie licencji typu Copyleft (np. GPL), które mogą wymuszać udostępnienie kodu źródłowego projektu.
- **Wizualizacja zależności**: Tworzenie grafów (statycznych i interaktywnych) obrazujących strukturę projektu i powiązane z nią licencje.
- **Klasyfikacja automatyczna**: Przypisywanie licencji do kategorii (Permissive, Copyleft, Weak Copyleft, Unknown) na podstawie metadanych PyPI i słownika SPDX.
- **Opcjonalna AI explain**: Umowzliwia wstepne wyjasnienie warningu z uzyciem AI   

## Powiązanie z projektem grupowym

Mini-projekt jest luźno powiązany z projektem. Temat licencji uwazam za istotny ze względu na multum bilbliotek w pythonie i coraz popularniejszy vibe coding, który sprawia, ze ludzie traca kontrole nad kodem i agenci (badz inni kontrybutorzy) moga dodac zaleznosci, ktorych licencja jest nieodpowiednia
## Wymagania

Projekt korzysta z [uv](https://docs.astral.sh/uv/) — szybkiego menedżera pakietów Python.

```bash
# Instalacja uv (jeśli nie masz)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Instalacja zależności
uv sync
```

## Uruchomienie

Skrypt `src/license_scanner.py` oferuje bogaty interfejs CLI (oparty o bibliotekę `click`):

```bash
# Podstawowy audyt (głębokość 2)
uv run src/license_scanner.py

# Pełny audyt (wszystkie zależności przechodnie) z interaktywnym grafem
uv run src/license_scanner.py --depth max --browser wyniki/pnw.html

# Audyt konkretnego katalogu i zapis do JSONL
uv run src/license_scanner.py /sciezka/do/projektu --out wyniki/audit.jsonl --out-type jsonl
```

**Dostępne flagi:**
- `--depth [int|max]`: Głębokość rekurencji (domyślnie 2).
- `--browser FILE`: Generuje interaktywny graf HTML (pyvis).
- `--output FILE`: Zapisuje statyczny graf PNG (matplotlib).
- `--out FILE`: Zapisuje tabelę wyników do pliku.
- `--out-type [pretty|jsonl]`: Format zapisu tabeli.
- `--layout [shell|spring|...]`: Algorytm ułożenia grafu.

## Wyniki

Przykładowe wyniki audytu dla projektu naukowo-wdrozeniowego:

1. **Raport Tekstowy**: [wyniki/pnw.txt](wyniki/pnw.txt)
2. **Interaktywny Graf**: [wyniki/graph.html](wyniki/graph.html) (należy otworzyć w przeglądarce)
3. **Statyczna Wizualizacja**:
   ![Graf licencji](wyniki/licencje_graf.png)
4. **GH actions**
   ![GH actions](wyniki/wyniki-ci-cd.png)

## Wnioski merytoryczne

Na podstawie przeprowadzonego audytu (plik `wyniki/pnw.txt`) wyciągnięto następujące wnioski:

1. **Dominacja licencji Permissive**: Większość bibliotek (np. `anthropic`, `openai`, `pandas`) korzysta z licencji MIT, Apache 2.0 lub BSD, co jest bezpieczne dla projektów komercyjnych i naukowych.
2. **Wykrycie ryzyk (Copyleft)**: Zidentyfikowano bibliotekę `grandalf` z licencją `GPLv2 | EPLv1`. W przypadku dystrybucji projektu jako oprogramowania (nie SaaS), może to wymagać udostępnienia kodu źródłowego.
3. **Słaba jakość metadanych (Unknown)**: Znaczna liczba pakietów (ok. 20-30% w zależności od głębokości) zwraca licencję `Unknown`. Wynika to z faktu, że autorzy na PyPI często wpisują nazwę licencji w polu `description` zamiast w dedykowanym polu `license`, lub używają niestandardowych formatów. Wymaga to ręcznej weryfikacji dla krytycznych komponentów.
4. **Złożone zależności**: Interaktywny graf pokazuje, że pojedyncza biblioteka (np. `dvc`) potrafi wprowadzić kilkadziesiąt zależności przechodnich, z których każda niesie własne ryzyko licencyjne.

## Ograniczenia

- **Ekosystem**: Obsługuje wyłącznie pakiety Python (PyPI). Brak wsparcia dla npm, cargo itp.
- **Zależność od PyPI**: Jeśli serwer PyPI jest niedostępny lub pakiet nie ma metadanych, skrypt nie może pobrać licencji.
- **Brak analizy kodu**: Skrypt polega na zadeklarowanych metadanych, nie skanuje plików `LICENSE` wewnątrz paczek (co byłoby wolniejsze, ale pewniejsze).

## Źródła

- [PyPI JSON API](https://warehouse.pypa.io/api-reference/json.html) — źródło metadanych.
- [SPDX License List](https://spdx.org/licenses/) — podstawa klasyfikacji.
- [NetworkX](https://networkx.org/) & [Pyvis](https://pyvis.readthedocs.io/) — silniki wizualizacji.
