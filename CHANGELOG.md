# Changelog

> Format: `## vX.Y.Z (RRRR-MM-DD) — Tytuł`, najnowsze na górze.
> Sekcje z emoji: 🚀 nowości, 🐛 poprawki, 🛠️ zmiany techniczne, ✅ testy/weryfikacja,
> ⚠️ breaking, 🔒 bezpieczeństwo/PII.

## v1.0.0 (2026-09-21) — pierwsze stabilne wydanie

Wydanie **stabilne** po serii `v0.1.0-beta.1 … beta.3`. Zawiera pełną
funkcjonalność: hurtowe ceny paliw ORLEN (netto/brutto), poprawny VAT CPN 2026,
marżę sterowaną z UI, datę ceny i opcjonalne LPG.

Promocja do stabilnej po testach (`64 passed`, `ruff` czysto), zielonym CI
(Tests, hassfest, HACS) oraz weryfikacji na labie `warzywna` (VM125, HA 2026.9.1).

- 🚀 Wszystkie funkcje z `v0.1.0-beta.3`.
- 🛠️ Minimalna wersja HA (`2024.6.0`) zadeklarowana w `hacs.json`; dodano
  `CONFIG_SCHEMA` (`config_entry_only_config_schema`).
- 🛠️ Repozytorium **publiczne** — HACS instaluje bez tokenu GitHub.
- ✅ Testy: `64 passed`; `ruff` czysty.

## v0.1.0-beta.3 (2026-09-21) — marża w UI, czytelne nazwy i ikony encji

Wydanie **pre-release**. Sterowanie marżą przeniesione do UI oraz przebudowa
nazewnictwa/ikon encji. **NIE promowano do stabilnej.**

- 🚀 **`number.orlen_marza`** — marża ustawialna bezpośrednio z UI (0–1000%,
  krok 0,1%): zapis do opcji wpisu i automatyczne przeliczenie cen na encjach.
  Domyślnie **0%**.
- 🚀 Czytelne nazwy encji: „**Pb95 – cena netto/brutto/z marżą**”,
  „**ON Ekodiesel – …**”, „**… – data ceny**”, „**LPG mazowieckie – …**”.
- 🚀 Ikony: netto `mdi:cash-minus`, brutto `mdi:cash`, z marżą `mdi:cash-plus`,
  data `mdi:calendar-clock`, LPG `mdi:gas-cylinder`, VAT `mdi:percent`,
  marża `mdi:percent-box`.
- 🛠️ Spójne `entity_id`: `sensor.orlen_<slug>_cena_<netto|brutto|z_marza>`,
  `sensor.orlen_<slug>_data_ceny`, `sensor.orlen_lpg_<woj>_cena_*`,
  `number.orlen_marza`.
- ⚠️ Zmiana `unique_id` względem `beta.2` — po aktualizacji encje utworzą się na
  nowo; w rejestrze encji mogą zostać osierocone wpisy do usunięcia.
- ✅ Testy: `64 passed`; `ruff` czysty.

## v0.1.0-beta.2 (2026-09-21) — poprawka encji marży (wykryta na labie)

Wydanie **pre-release**. Weryfikacja na labie **warzywna** (VM125, HA 2026.9.1)
wykryła błąd: sensor marży miał `EntityCategory.CONFIG`, czego Home Assistant nie
pozwala dla encji typu sensor („Entity sensor.orlen_marza cannot be added as the
entity category is set to config”). Naprawione + test regresyjny.
**NIE promowano do stabilnej.**

- 🐛 `sensor.orlen_marza` był niedostępny — usunięto kategorię `config`.
- 🛠️ Mocki testowe `multi_select` zgodne z HA (wymaga **listy**, nie dict) —
  wykryte przez onboarding na labie przez REST.
- ✅ Testy: `62 passed`; `ruff` czysty.
- ✅ Lab warzywna (VM125): wpis `loaded`, 18/18 encji dostępnych; marża 5% →
  Pb95 `8.193 zł/l`, powrót 0% → `7.803 zł/l`; usługa `get_prices` → 200.

## v0.1.0-beta.1 (2026-09-20) — pierwsze wydanie testowe

Wydanie **pre-release** (nie stabilne). Pierwsza wersja integracji
**Ceny Paliw Orlen**: pobiera publiczne, nieoficjalne hurtowe ceny paliw ORLEN
i wystawia sensory netto/brutto/brutto z marżą. **NIE promowano do stabilnej**
do czasu przejścia protokołu akceptacyjnego (laby + produkcja).

- 🚀 Katalog produktów silnikowych z `/api/wholesalefuelprices/` (Pb95, Pb98,
  ON Ekodiesel, ON Arktyczny 2, ON Miejski Super, ON Ekoterm, BIO 100).
- 🚀 Poprawny VAT: tabela **CPN 2026** (okna 8%) z zachowaniem 23% dla olejów
  opałowych oraz tryb stałej stawki (`fixed`).
- 🚀 **Encja z marżą** (cena brutto × (1 + marża)), domyślnie **0%** — równa
  cenie brutto; marża uwzględniana w obliczeniach.
- 🚀 Data obowiązywania ceny (`effectiveDate`) jako osobny sensor.
- 🚀 Opcjonalne LPG per województwo (`/api/autogasprices`).
- 🚀 Usługa `orlen_fuel_prices.get_prices` (`SupportsResponse.ONLY`).
- 🛠️ Coordinator z interwałem 1 h–24 h, mapowaniem WAF/timeoutów na `UpdateFailed`.
- 🛠️ Diagnostyka z maskowaniem danych wrażliwych.
- 🛠️ CI: `tests.yml` (pytest + coverage + ruff), hassfest, HACS validation,
  workflow release jako pre-release dla tagów `-beta`.
- 🔒 Brak sekretów — API nie wymaga logowania; brak PII w diagnostyce/logach.
- ✅ Testy: `61 passed`; `ruff` czysty.
