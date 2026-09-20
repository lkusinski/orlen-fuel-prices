# Changelog

> Format: `## vX.Y.Z (RRRR-MM-DD) — Tytuł`, najnowsze na górze.
> Sekcje z emoji: 🚀 nowości, 🐛 poprawki, 🛠️ zmiany techniczne, ✅ testy/weryfikacja,
> ⚠️ breaking, 🔒 bezpieczeństwo/PII.

## v0.1.0-beta.1 (2026-09-20) — pierwsze wydanie testowe

Wydanie **pre-release** (nie stabilne). Pierwsza wersja integracji
**Ceny Paliw Orlen**: pobiera publiczne, nieoficjalne hurtowe ceny paliw ORLEN
i wystawia sensory netto/brutto/brutto z marżą. **NIE promowano do stabilnej**
do czasu przejścia protokołu akceptacyjnego (laby + produkcja).

- 🚀 Katalog produktów silnikowych z `/api/wholesalefuelprices/` (Pb95, Pb98,
  ON Ekodiesel, ON Arktyczny 2, ON Miejski Super, ON Ekoterm, BIO 100).
- 🚀 Poprawny VAT: tabela **CPN 2026** (okna 8%) z zachowaniem 23% dla olejów
  opałowych oraz tryb stałej stawki (`fixed`).
- 🚀 **Encja z marżą** (`..._brutto_z_marza`), domyślnie **0%** — równa cenie
  brutto; marża uwzględniana w obliczeniach `brutto × (1 + marża/100)`.
- 🚀 Data obowiązywania ceny (`effectiveDate`) jako osobny sensor.
- 🚀 Opcjonalne LPG per województwo (`/api/autogasprices`).
- 🚀 Usługa `orlen_fuel_prices.get_prices` (`SupportsResponse.ONLY`).
- 🛠️ Coordinator z interwałem 1 h–24 h, mapowaniem WAF/timeoutów na `UpdateFailed`.
- 🛠️ Diagnostyka z maskowaniem danych wrażliwych.
- 🛠️ CI: `tests.yml` (pytest + coverage + ruff), hassfest, HACS validation,
  workflow release jako pre-release dla tagów `-beta`.
- 🔒 Brak sekretów — API nie wymaga logowania; brak PII w diagnostyce/logach.
- ✅ Testy: `61 passed`; `ruff` czysty.

## v0.1.0 (planowane) — pierwsze stabilne wydanie

Wydanie **stabilne** po akceptacji pre-release na labach i produkcji.
