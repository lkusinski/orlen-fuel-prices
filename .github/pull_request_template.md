## Opis

<!-- Krótko: co zmienia ten PR i dlaczego. -->

## Typ zmiany

- [ ] 🚀 Nowa funkcja (`feat`)
- [ ] 🐛 Poprawka (`fix`)
- [ ] 📝 Dokumentacja (`docs`)
- [ ] 🛠️ Refaktor / CI (`refactor` / `ci`)
- [ ] 🎨 Release (`release`)

## Checklist

- [ ] `python -m pytest tests/ -v` — zielone
- [ ] `ruff check custom_components/ tests/ --select E,F,I --ignore E501,E402` — czysto
- [ ] Zaktualizowane `CHANGELOG.md` (i `manifest.version` przy release)
- [ ] Brak sekretów/PII w kodzie, testach i logach
- [ ] Nowy kod ma testy (happy path + błąd)

## Powiązane zgłoszenia

<!-- np. Closes #12 -->
