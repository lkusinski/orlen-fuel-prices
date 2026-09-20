# AGENTS.md — reguły dla agenta AI pracującego nad tą integracją

> Plik nadrzędny wobec „dobrej woli” agenta. Podręcznik procesu poza repo:
> katalog `ORLEN` (m.in. `PROCES_PRACY_Z_AI.md`, `STYL.md`, `TESTY_I_JAKOSC.md`).

## 🔒 Sekrety i dane

- **Nigdy** nie commituj ani nie wypisuj w logach/odpowiedziach haseł, tokenów, PAT,
  kluczy, danych kont i PII.
- Sekrety leżą wyłącznie w `CREDENTIALS.md` **poza repozytorium** (i innych plikach
  ignorowanych przez git). Nie kopiuj ich treści.
- W diagnostyce/logach maskuj dane wrażliwe (`**REDACTED**`, `a***@d***`).

## 🚀 Release

- Release tworzy **wyłącznie workflow** `release.yml` na push tagu `v*`.
- **NIE twórz release'ów ręcznie przez API/UI** — powoduje konflikt `already exists`.
- Bety jako **pre-release** (`vX.Y.Z-beta.N`, `-rc.N`, `-alpha.N`).
- Promocja do stabilnej (`vX.Y.Z`, `make_latest`) dopiero po testach i akceptacji.
- `manifest.version` musi odpowiadać tagowi (podbij w tym samym commicie).

## ✍️ Commity

- Autor: `lkusinski <lkusinski@gmail.com>`.
- Konwencja: `feat:`, `fix:`, `docs:`, `ci:`, `refactor:`, `release:`, `chore:`.
- Przed commitem: **testy (`pytest`) + `ruff` muszą być czyste**.
- Nie pushuj bez wyraźnego polecenia. Nie rób `--force` na wydanych tagach.

## 🧪 Jakość

- Uruchamiaj: `python -m pytest tests/ -v` oraz
  `ruff check custom_components/ tests/ --select E,F,I --ignore E501,E402`.
- Każdy bug → najpierw test regresyjny, potem fix.
- Defensywność: timeouty, `ConfigEntryNotReady`, brak blokowania pętli, brak
  `except Exception: pass` bez logu.

## 🖥️ Środowiska

- **Jedno środowisko testowe naraz** (limity RAM homelabów).
- `onboot=0`, `discard=on`; okresowo `fstrim`.
- **Backup POZA `custom_components`** — kopia tej samej domeny w `custom_components`
  zawiesza start HA (duplikat domeny).

## 🎨 Styl

- PL w `README`/`CHANGELOG`/`docs`; EN w docstringach i kodzie; komentarze tylko gdy
  wnoszą wartość.
- Nazewnictwo encji: `<domain>_<id>_<slug>`; `unique_id` stabilny.
- Tłumaczenia PL/EN utrzymuj spójne w trzech plikach (`strings.json` + `translations/`).
