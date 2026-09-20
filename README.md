<div align="center">
  <img src="logo.png" alt="Ceny Paliw Orlen" width="320"/>
</div>

<h1 align="center">Ceny Paliw Orlen for Home Assistant</h1>

![GitHub Release](https://img.shields.io/github/v/release/lkusinski/orlen-fuel-prices)
[![HACS](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
![API](https://img.shields.io/badge/data_source-REST_API-blue)
![Tests](https://img.shields.io/badge/tests-61_passed-lightgrey)

**Najnowsze wydanie: [v0.1.0-beta.1](https://github.com/lkusinski/orlen-fuel-prices/releases)** (pre-release).

> [!NOTE]
> Repozytorium niestandardowe HACS (prywatne). Instalacja przez
> **HACS → Integracje → Repozytoria niestandardowe** (kategoria: Integracja)
> albo ręcznie. Integracja korzysta z **publicznego, nieoficjalnego** API
> hurtowych cen paliw ORLEN i nie jest w żaden sposób powiązana z ORLEN S.A.

---

## ✨ Główne możliwości

* ⛽ **Hurtowe ceny paliw ORLEN** (netto, PLN/m³ → zł/l): Pb95, Pb98, ON Ekodiesel,
  ON Arktyczny 2, ON Miejski Super, ON grzewczy Ekoterm, BIO 100.
* 🧮 **Poprawny VAT** — automatyczna tabela okresów **CPN 2026** (8% w oknach
  obniżki dla paliw silnikowych) z zachowaniem 23% dla olejów opałowych,
  albo **stała stawka** wymuszona przez użytkownika.
* ➕ **Encja z marżą** — `..._brutto_z_marza`, domyślnie **0%** (równa cenie
  brutto). Marża jest w pełni konfigurowalna i uwzględniana w obliczeniach.
* 🗓️ **Data obowiązywania ceny** (`effectiveDate`) jako osobna encja — wiadomo,
  kiedy cennik faktycznie się zmienił (weekendy bywają z piątku).
* 🛢️ **LPG** opcjonalnie, per województwo (`/api/autogasprices`).
* 🧩 **Usługa `get_prices`** zwracająca pełny cennik przez `return_response`.
* 🛡️ Odporne na WAF (HTML „Request Rejected” zamiast JSON), timeouty, 5xx.

---

## 📦 Instalacja

### Metoda 1: HACS (Repozytorium Niestandardowe — zalecana)

1. HACS → Integracje.
2. Menu (3 kropki) → **Repozytoria niestandardowe**.
3. URL: `https://github.com/lkusinski/orlen-fuel-prices` → kategoria **Integracja**.
4. Dodaj, znajdź **Ceny Paliw Orlen**, wybierz **Pobierz**.
5. Zrestartuj Home Assistant.

> Dla repozytorium **prywatnego** HACS wymaga skonfigurowanego tokenu GitHub
> o dostępie do tego repo.

### Metoda 2: ręcznie

Skopiuj `custom_components/orlen_fuel_prices/` do
`<config>/custom_components/orlen_fuel_prices/` i zrestartuj HA.

---

## ⚙️ Konfiguracja

1. Ustawienia → Urządzenia i usługi → **Dodaj integrację** → **Ceny Paliw Orlen**.
2. Wybierz **produkty paliwowe**, tryb VAT, marżę i interwał odświeżania.
3. Gotowe — encje pojawią się na urządzeniu **ORLEN**.

| Opcja | Domyślnie | Znaczenie |
|---|---|---|
| `products` | Pb95, Pb98, ON Ekodiesel, ON Arktyczny 2, ON Ekoterm | Katalog produktów silnikowych. |
| `vat_mode` | `auto` | `auto` = tabela CPN 2026; `fixed` = zawsze stała stawka. |
| `vat_rate` | `23` | Stawka używana w trybie `fixed`. |
| `margin` | `0` | Marża (%) doliczana do brutto: `brutto × (1 + marża/100)`. |
| `show_netto` | `true` | Dodatkowe sensory netto (do faktur). |
| `lpg_regions` | `[]` | Województwa LPG (brak = bez LPG). |
| `scan_interval` | `3600` | Interwał odświeżania w sekundach (3600–86400). |

---

## 🧩 Encje

Dla każdego wybranego produktu (`<sym>` = np. `pb95`):

| Encja | Typ | Opis |
|---|---|---|
| `sensor.orlen_<sym>_netto` | sensor | Cena hurtowa netto, zł/l. |
| `sensor.orlen_<sym>_brutto` | sensor | Cena brutto (netto × (1 + VAT)). |
| `sensor.orlen_<sym>_brutto_z_marza` | sensor | Brutto z marżą (domyślnie 0% = brutto). |
| `sensor.orlen_<sym>_data_obowiazywania` | sensor | Timestamp `effectiveDate`. |

Globalne:

| Encja | Opis |
|---|---|
| `sensor.orlen_aktualna_stawka_vat` | Aktualnie stosowana stawka VAT (%). |
| `sensor.orlen_marza` | Skonfigurowana marża (%). |
| `sensor.orlen_ostatnia_aktualizacja` | Czas ostatniego udanego pobrania. |

LPG (gdy wybrano regiony): `sensor.orlen_lpg_<woj>_netto`,
`sensor.orlen_lpg_<woj>_brutto`, `sensor.orlen_lpg_<woj>_brutto_z_marza`.

Atrybuty każdego sensora ceny: `product_symbol`, `effective_date`, `vat_rate`,
`margin`, `stale`, `source`.

> **Marża:** domyślnie `0%`, więc `brutto_z_marza == brutto`. To celowe —
> Orlen publikuje cenę **hurtową netto**, a marża detaliczna jest pojęciem
> odrębnym i jej nie zgadujemy. Encja istnieje dla użytkowników, którzy chcą
> doliczyć własną marżę.

## 🔧 Usługi

| Usługa | Pola | Opis |
|---|---|---|
| `orlen_fuel_prices.get_prices` | `entry_id` (opcjonalne) | Zwraca pełny cennik (`motor`, `lpg`, `vat_rate`, `margin`). Wywołaj z `return_response: true`. |

---

## 🐞 Rozwiązywanie problemów

- Sprawdź Ustawienia → System → **Logi**, filtruj po `orlen_fuel_prices`.
- **WAF / `Request Rejected`:** API ORLEN jest chronione; przy zbyt częstych
  żądaniach może odrzucać połączenia. Zmniejsz częstotliwość (interwał ≥ 1 h).
- **`stale: true`:** brak świeżych danych (sieć/WAF) — encje pokazują ostatnią
  znaną wartość.
- Zgłoś problem przez [Issues](https://github.com/lkusinski/orlen-fuel-prices/issues)
  z wersją HA i integracji oraz logami.

---

## ⚖️ Źródło danych i zastrzeżenia

- Dane: publiczna strona **Hurtowe ceny paliw** —
  <https://www.orlen.pl/pl/dla-biznesu/hurtowe-ceny-paliw>
  (endpoint `https://tool.orlen.pl/api/...`, nieoficjalny, bez klucza).
- Ceny są **hurtowe, netto, w PLN/m³ (za 1000 l)** i ważne dziennie od 00:00.
  Cena netto zawiera akcyzę i opłatę paliwową (poza olejem opałowym).
- Dane mają charakter **informacyjny** i nie stanowią oferty handlowej.
- Integracja **nie jest** oficjalnym produktem ORLEN S.A.
- Pobieranie jest oszczędne (cache/interwał), ale nie ma gwarancji SLA API.

---

## 📄 Licencja

MIT — patrz [LICENSE.md](LICENSE.md).
