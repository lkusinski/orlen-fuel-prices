# Dane, jednostki i VAT

## 1. Źródło

Publiczna strona **Hurtowe ceny paliw** ORLEN:
<https://www.orlen.pl/pl/dla-biznesu/hurtowe-ceny-paliw>

Endpointy (nieoficjalne, bez klucza, za WAF-em):

| Endpoint | Zawartość |
|---|---|
| `GET /api/wholesalefuelprices/` | bieżący snapshot paliw silnikowych |
| `GET /api/wholesalefuelprices/Products` | katalog produktów |
| `GET /api/autogasprices` | bieżące LPG per województwo |

Wymagane nagłówki (inaczej WAF zwraca HTTP 200 + HTML `Request Rejected`):
`User-Agent`, `Referer` strony publicznej, `Accept: application/json`.

## 2. Jednostki

- Paliwa silnikowe: `value` w **PLN za 1000 l (m³)** →
  `netto_zł/l = value / 1000`.
- LPG: `value` już w **zł/l** (pole `unit` = `null`, ale wartość ~2,6–2,7 jest
  jednoznacznie zł/l).
- Cena netto zawiera akcyzę i opłatę paliwową (poza olejem opałowym).
- Pole `effectiveDate` to dzień obowiązywania cennika (nie czas pobrania).

## 3. VAT

Domyślnie `brutto = netto × (1 + VAT)`.

Tabela okresów (program **CPN 2026**, zakres `[start, end)`), wyłącznie paliwa
silnikowe:

| Okres | VAT |
|---|---|
| 2026-03-31 – 2026-06-30 | 8% |
| 2026-07-01 – 2026-08-16 | 23% |
| 2026-08-17 – 2026-08-31 | 8% |
| od 2026-09-01 | 23% |

Zasady:

- **Oleje opałowe/grzewcze** (`OnEkoterm`, `HeatingC3`, `HeatingC3LowSulfur`)
  **zawsze 23%** — obniżka ich nie obejmowała.
- Data wyliczenia = `effectiveDate` ceny, a nie „dziś”.
- Tryb `fixed` w opcjach wymusza stałą stawkę na wszystkich produktach.

## 4. Marża

`cena z marżą = brutto × (1 + marża/100)`, domyślnie **marża = 0%**, więc encja
`sensor.orlen_<slug>_cena_z_marza` jest równa cenie brutto. Marża jest sterowana
encją **`number.orlen_marza`** (0–1000%, krok 0,1) albo polem w opcjach
integracji i nie jest zgadywana — służy użytkownikom, którzy chcą doliczyć
własną narzutę.

## 5. Atrybucja i zastrzeżenia

- Dane mają charakter informacyjny i nie stanowią oferty handlowej.
- Integracja nie jest oficjalnym produktem ORLEN S.A.
- Pobieranie jest oszczędne (interwał 1 h–24 h, jedna instancja), ale API nie ma
  gwarancji SLA i może się zmienić bez ostrzeżenia.
