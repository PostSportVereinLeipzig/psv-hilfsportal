# Förderportal PSV: Anleitung zur Pflege (Vorstand)

Die Seite liegt öffentlich auf GitHub und wird dort kostenlos ausgeliefert.

- **Seite:** https://postsportvereinleipzig.github.io/psv-hilfsportal/
- **Repository (Dateien):** https://github.com/PostSportVereinLeipzig/psv-hilfsportal
- **GitHub-Konto:** PostSportVereinLeipzig

## Aufbau

| Datei / Ordner | Zweck |
|---|---|
| `daten/termine.json` | Termine (einmalig) und Vereinsfristen (jährlich wiederkehrend) |
| `daten/kontakte.json` | Kontakt-E-Mail-Adressen (nur E-Mail, keine Telefonnummern) |
| `daten/downloads.json` | Titel und Gruppe der Formulare im Reiter „Formulare“ |
| `downloads/` | Die Formular-Dateien selbst (PDF, XLSX, XLS) |
| `quellen/` | Neue Texte für die Suche als `.md`-Dateien |
| `daten/dokumente.json` | Bestehender Such-Index. Nicht von Hand ändern. |
| `tpl.html` | Vorlage von Aussehen und Programmierung. Nur bei Designänderungen. |
| `build.py` | Baut aus allem die fertige `index.html`. |
| `index.html` | Fertige Seite. **Nie von Hand bearbeiten**, sie wird überschrieben. |
| `.github/workflows/build.yml` | Automatik: baut `index.html` nach jeder Änderung auf GitHub. |

## Einfachster Weg: direkt im Browser ändern
Die Seite baut sich selbst neu, sobald eine Datei in `daten/`, `quellen/`, `downloads/` oder `tpl.html` geändert wird.

1. Auf https://github.com/PostSportVereinLeipzig/psv-hilfsportal mit dem Vereinskonto anmelden.
2. Zum Beispiel `daten/termine.json` öffnen, oben rechts auf den **Stift** (Edit) klicken, ändern.
3. Oben rechts **Commit changes…** klicken, kurz beschreiben, bestätigen.
4. Unter dem Reiter **Actions** läuft „Portal bauen“ (grüner Haken nach etwa 30 Sekunden). Danach ist die Seite nach ein bis zwei Minuten aktualisiert.
5. Neue Formulare: **Add file → Upload files** im Ordner `downloads/`, danach `daten/downloads.json` ergänzen.
6. Rot markierter Lauf in **Actions**: Meist ein Tippfehler im JSON. Auf den Lauf klicken, die Fehlermeldung nennt die Zeile.

Wer lokal arbeitet, holt vorher den neuesten Stand mit `git pull`, weil die Automatik `index.html` im Repository ändert.

## Alternativ: lokal bauen und veröffentlichen
1. Datei ändern (siehe unten).
2. Im Ordner `Portal` ausführen: `python3 build.py`
3. Lesen, was das Skript meldet. Bei „FEHLER“ oder „WARNUNG“ zuerst beheben.
4. `index.html` im Browser öffnen und prüfen.
5. Veröffentlichen:
   ```
   git add -A
   git commit -m "Termine aktualisiert"
   git push
   ```
6. Nach ein bis zwei Minuten ist die Änderung online. Gegebenenfalls Seite neu laden (am Handy: Tab schließen und neu öffnen).

Voraussetzungen auf dem Rechner: Python 3, Git, angemeldet bei GitHub (`gh auth login`).

## Termine ändern (`daten/termine.json`)
Einmalige Termine stehen unter `"termine"`, Datum als `JJJJ-MM-TT`:
```json
{ "datum": "2026-12-10", "titel": "Verwaltungsratssitzung", "art": "Gremium", "ort": "Kultursaal, Am Sportforum 3, 04105 Leipzig" }
```
Vergangene Termine wandern automatisch in „Vergangene Termine“. Zum Hinzufügen den Block kopieren und anpassen. Zwischen Blöcken steht ein Komma, nach dem letzten nicht.

## Vereinsfristen ändern (`vereinsfristen` in derselben Datei)
Sie wiederholen sich jährlich, deshalb nur `monat` und `tag`:
```json
{ "titel": "Übungsleiter-Abrechnung 1. Halbjahr", "monat": 7, "tag": 15, "wer": "Vorstand", "hinweis": "Abrechnungszeitraum 01.01. bis 30.06." }
```
Aktuelle Fristen: Grundbeiträge 1. Halbjahr 31.03.; Mitgliedermeldung 30.06. und 31.12.; ÜL-Abrechnung 15.07. und 15.01.

## Kontakte ändern (`daten/kontakte.json`)
Felder je Eintrag: `gruppe`, `rolle`, `mail`, `anliegen`. Nur Funktionspostfächer, keine Telefonnummern. Einträge ohne E-Mail (z. B. Gymnastik-Ansprechpartner) bleiben draußen.

## Neues Formular bereitstellen
1. Datei in `downloads/` legen. Dateinamen ohne Leerzeichen und Sonderzeichen, z. B. `Antrag-Beispiel-2027.pdf`.
2. In `daten/downloads.json` einen Eintrag ergänzen:
   ```json
   { "g": "0", "grp": "PSV-Vorlagen", "t": "Anzeigename des Formulars", "f": "downloads/Antrag-Beispiel-2027.pdf" }
   ```
   `grp` bestimmt die Überschrift, `g` die Reihenfolge der Gruppen (`0` kommt zuerst).
3. Formular entfernen: Eintrag löschen und Datei aus `downloads/` löschen.
4. Dateigröße und Dateityp setzt `build.py` selbst.

Auf dem Mac werden Umlaute in Dateinamen manchmal anders gespeichert (Unicode). Darum Dateinamen am besten ohne Umlaute wählen.

## Neue Texte für die Suche
Textdatei als `quellen/Name.md` anlegen:
```
# Titel, der in den Treffern erscheint
Kategorie: Info
Link: https://… (optional, wird als „Original“ angezeigt)

Hier folgt der Text. Absätze durch Leerzeilen trennen.
```
Bei PDFs: erst in Markdown oder Text umwandeln und einfügen. Nach `python3 build.py` ist der Text durchsuchbar.

## Typische Fehler
| Meldung | Ursache und Lösung |
|---|---|
| `ist kein gültiges JSON (Zeile …)` | Komma, Anführungszeichen oder Klammer fehlt. Bei der genannten Zeile suchen. Hilfreich: https://jsonlint.com |
| `WARNUNG: … fehlt im Ordner downloads/` | Dateiname in `downloads.json` stimmt nicht mit der Datei überein. |
| Änderung nicht sichtbar | Erst `python3 build.py`, dann `git push`. Warten und Seite neu laden. |
| `git push` verlangt Anmeldung | `gh auth login` erneut ausführen. |
| Alles kaputt | Vorherigen Stand holen: `git log --oneline`, dann `git revert <Nummer>` und `git push`. |

## Zugang und Sicherung
Das Konto **PostSportVereinLeipzig** gehört dem Verein, nicht einer Person.

1. **Zwei-Faktor-Authentifizierung (2FA)** aktivieren: GitHub → Settings → Password and authentication.
2. **Wiederherstellungscodes** (Recovery codes) herunterladen und ausgedruckt an einem sicheren Ort aufbewahren, z. B. beim Vorstandsvorsitz und beim Schatzmeister. Ohne sie ist das Konto bei Verlust des Telefons gesperrt.
3. **Zweite Admin-Person:** Repository → Settings → Collaborators → Add people. Eine zweite Person mit eigenem GitHub-Konto einladen und ihr Schreibrechte geben. So bleibt der Zugang bei Vorstandswechsel erhalten.
4. **Vorstandswechsel:** Neue Person einladen, ausscheidende Person entfernen. Die E-Mail-Adresse des Kontos auf eine Funktionsadresse legen, nicht auf eine Privatadresse.
5. **Sicherung:** Das Repository ist selbst die Sicherung des Standes. Zusätzlich einmal im Jahr über „Code → Download ZIP“ eine Kopie ablegen.
6. Es gibt keinen Upload und keinen Passwortschutz. Nichts ins Repository legen, was nicht öffentlich sein darf (Verträge mit Personen, Bescheide, Bankdaten).

## Hinweise
- § 9 im Übungsleitervertrag zitiert „§ 5 BDSG“. Das sollte rechtlich geprüft werden.
- Termine für das Folgejahr sind nach dem Muster des Vorjahres berechnet und müssen jedes Jahr geprüft werden.
