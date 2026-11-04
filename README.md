# Förderportal PSV

Öffentliches Informationsportal des **Postsportvereins Leipzig e.V.**: Förderungen, Fristen, Termine und Formulare an einem Ort, durchsuchbar, am Handy und am Computer nutzbar.

**Zur Seite:** https://postsportvereinleipzig.github.io/psv-hilfsportal/

Kein Login, kein Upload, keine Cookies. Alle Inhalte sind öffentlich.

## Für Mitglieder
Kurzanleitung (Suche, Download, Symbol auf dem Handy): [ANLEITUNG_Mitglieder.md](ANLEITUNG_Mitglieder.md)

## Für den Vorstand
Termine, Fristen, Kontakte und Formulare pflegen, Zugang sichern: [ANLEITUNG_Pflege.md](ANLEITUNG_Pflege.md)

Kurzfassung: Datei in `daten/` direkt auf GitHub bearbeiten (Stift-Symbol), speichern. Die Seite baut sich selbst neu und ist nach ein bis zwei Minuten aktualisiert.

## Aufbau

| Pfad | Zweck |
|---|---|
| `index.html` | Fertige Seite (wird automatisch erzeugt, nicht von Hand ändern) |
| `tpl.html` | Vorlage mit Aussehen und Programmlogik (CSS und JavaScript inline) |
| `build.py` | Baut `index.html` aus Vorlage und Daten |
| `daten/termine.json` | Termine und jährlich wiederkehrende Vereinsfristen |
| `daten/kontakte.json` | Kontakt-E-Mail-Adressen (keine Telefonnummern) |
| `daten/downloads.json` | Titel und Gruppen der Downloads |
| `daten/dokumente.json` | Such-Index der Richtlinien und Formulare |
| `quellen/` | Neue Texte für die Suche als Markdown |
| `downloads/` | Formulare und Vorlagen (PDF, XLSX, XLS) |
| `manifest.webmanifest`, `icons/` | App-Installation auf dem Handy (PWA) |
| `.github/workflows/build.yml` | Automatisches Bauen bei jeder Änderung |

## Lokal bauen
Voraussetzung: Python 3 (keine weiteren Pakete).

```bash
python3 build.py
```

Danach `index.html` im Browser öffnen. Veröffentlicht wird mit `git push`; GitHub Pages liefert die Seite vom Zweig `main` aus.

## Technik
- Statische Seite ohne Server, gehostet über GitHub Pages
- Hash-Navigation (`#suche`, `#foerderungen`, `#fristen`, `#termine`, `#formulare`)
- Responsives Layout für Handy, Tablet und Desktop, helles und dunkles Farbschema
- Volltextsuche im Browser über rund 800 Textabschnitte

## Hinweise
Beträge und Fristen sind ohne Gewähr. Maßgeblich sind der jeweilige Bescheid und die Originalquellen der Stadt Leipzig, des LSB Sachsen und des SSB Leipzig. Die Stadt aktualisiert ihre Formulare jährlich.
