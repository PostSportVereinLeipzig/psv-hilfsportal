# Förderportal PSV: Anleitung zur Pflege (Vorstand)

Die Seite liegt öffentlich auf GitHub und wird dort kostenlos ausgeliefert.

- **Seite:** https://postsportvereinleipzig.github.io/psv-hilfsportal/
- **Repository (Dateien):** https://github.com/PostSportVereinLeipzig/psv-hilfsportal
- **GitHub-Konto:** PostSportVereinLeipzig

## Aufbau

| Datei / Ordner | Zweck |
|---|---|
| `daten/termine.json` | Termine (einmalig, mit Jahr) und Vereinsfristen (jährlich wiederkehrend, ohne Jahr) |
| `daten/fristen.json` | Fristen der Stadt, des LSB, des SSB und Dritter. Wiederkehrend, ohne Jahr. Wird jede Woche mit der SSB-Seite abgeglichen. |
| `update_fristen.py` | Gleicht `fristen.json` mit der Fristenseite des SSB ab |
| `daten/kontakte.json` | Kontakt-E-Mail-Adressen (nur E-Mail, keine Telefonnummern) |
| `daten/veranstaltungen.json` | Von Hand: Hinweise zu Veranstaltungen, eigene Ergänzungen, Infotext „Angebot anmelden“ |
| `daten/veranstaltungen_auto.json` | Automatisch gelesen (jede Woche). Nicht von Hand ändern. |
| `update_veranstaltungen.py` | Liest die Veranstaltungen von den Seiten des SSB und LSB |
| `daten/bildung.json` | Inhalte des Reiters „Weiterbildung“ (Lizenzregeln, Schritte, Kontakt, Links) |
| `daten/downloads.json` | Titel und Gruppe der Formulare im Reiter „Formulare“ |
| `downloads/` | Die Formular-Dateien selbst (PDF, XLSX, XLS) |
| `quellen/` | Neue Texte für die Suche als `.md`-Dateien |
| `daten/dokumente.json` | Bestehender Such-Index. Nicht von Hand ändern. |
| `tpl.html` | Vorlage von Aussehen und Programmierung. Nur bei Designänderungen. |
| `build.py` | Baut aus allem die fertige `index.html`. |
| `index.html` | Fertige Seite. **Nie von Hand bearbeiten**, sie wird überschrieben. |
| `.github/workflows/build.yml` | Automatik: baut `index.html` nach jeder Änderung auf GitHub. |
| `.github/workflows/fristen.yml` | Automatik: gleicht dienstags die Fristen mit der SSB-Seite ab. |
| `.github/workflows/termine-erinnerung.yml` | Automatik: erinnert zum Jahresende an die Termine für das nächste Jahr. |
| `.github/workflows/veranstaltungen.yml` | Automatik: liest montags die Veranstaltungen und baut die Seite neu. |

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

## Fristen (`daten/fristen.json`) und Abgleich mit dem SSB
Die Fristen gelten jedes Jahr, deshalb stehen nur Monat (`m`) und Tag (`d`) darin, kein Jahr. Im Portal erscheinen sie als „31.03. jährlich“ mit der Zahl der Tage bis zur nächsten Fälligkeit.

**Automatischer Abgleich (dienstags):** GitHub vergleicht die Fristen mit der [Fristenseite des SSB](https://www.ssb-leipzig.de/leistungen/vereinsberatung/fristen-1/).
- Weicht Monat oder Tag ab, wird die Frist angepasst.
- Steht dort eine neue Frist, wird sie ergänzt (mit dem Hinweis „bitte Text prüfen“).
- Fehlt eine Frist auf der SSB-Seite, bleibt sie stehen und wird nur gemeldet.
- Titel und Hinweise ändert die Automatik nie.
- Bei jeder Änderung legt GitHub unter **Issues** einen Hinweis an und schickt eine E-Mail, damit jemand kurz draufschaut.
- Fristen ohne `ssb_match` in der Datei (z. B. „Ehrenamt stärken“) stehen nicht auf der SSB-Seite und werden von Hand gepflegt.

**Jetzt sofort abgleichen:** Repository → **Actions** → „Fristen abgleichen“ → **Run workflow**.

## Termine ändern (`daten/termine.json`)
Einmalige Termine stehen unter `"termine"`, Datum als `JJJJ-MM-TT`:
```json
{ "datum": "2026-12-10", "titel": "Verwaltungsratssitzung", "art": "Gremium", "ort": "Kultursaal, Am Sportforum 3, 04105 Leipzig" }
```
Vergangene Termine des laufenden Jahres wandern automatisch in „Vergangene Termine“. Neue Termine (Verwaltungsratssitzungen, Delegiertenversammlung, Feiern und sonstiges) werden am Jahresende für das nächste Jahr eingetragen. Dazu erinnert GitHub am 1. November, 1. Dezember, 15. Dezember und 5. Januar per Hinweis (Issue) und E-Mail, solange für das Zieljahr noch nichts eingetragen ist. Zum Hinzufügen den Block kopieren und anpassen. Zwischen Blöcken steht ein Komma, nach dem letzten nicht.

## Vereinsfristen ändern (`vereinsfristen` in derselben Datei)
Sie wiederholen sich jährlich, deshalb nur `monat` und `tag`:
```json
{ "titel": "Übungsleiter-Abrechnung 1. Halbjahr", "monat": 7, "tag": 15, "wer": "Vorstand", "hinweis": "Abrechnungszeitraum 01.01. bis 30.06." }
```
Aktuelle Fristen: Grundbeiträge 1. Halbjahr 31.03.; Mitgliedermeldung 30.06. und 31.12.; ÜL-Abrechnung 15.07. und 15.01.

## Kontakte ändern (`daten/kontakte.json`)
Felder je Eintrag: `gruppe`, `rolle`, `mail`, `anliegen`. Nur Funktionspostfächer, keine Telefonnummern. Einträge ohne E-Mail (z. B. Gymnastik-Ansprechpartner) bleiben draußen.

## Reiter „Weiterbildung“ pflegen (`daten/bildung.json`)
Die Inhalte stammen von der SSB-Seite „Häufig gestellte Fragen“ (Link und Stand stehen in der Datei). Ändern sich dort Zahlen oder Regeln, die Datei anpassen:
- `kennzahlen`: die drei Kacheln oben
- `erwerb`: Weg zur Lizenz mit `schritte` (Grundlehrgang, Erste Hilfe, ÜL-C-Lehrgang mit Lerneinheiten und Kosten), `voraussetzungen`, `anmeldung`, `foerderung`
- `quellen`: die SSB-Seiten, aus denen die Angaben stammen
- `verlaengern`: die Schritte zur Verlängerung
- `abgelaufen`: Tabelle für abgelaufene Lizenzen. `bis_jahre` ist die Obergrenze in Jahren nach Ablauf und steuert den Lizenz-Check
- `psv`: Hinweise, die nur für den PSV gelten (Vertrag, Honorar)
- `kontakt`, `kurse`, `links`: Ansprechpartner und Verweise
- `stand`: Datum der letzten Prüfung gegen die SSB-Seite, bitte mit anpassen

Kurse, Termine und Anmeldebeginne stehen bewusst nicht im Portal, sondern nur als Link auf den Jahresplan des SSB. So kann nichts veralten.

## Reiter „Veranstaltungen“
**Was automatisch läuft:** Jeden Montag liest GitHub die Jahrespläne des SSB Leipzig (Veranstaltungen und Aus-/Weiterbildung), die Kurstabellen mit Anmeldebeginn (Grundlehrgang, Erste Hilfe, ÜL-C) und die Landesjugendspiele des LSB. Neue, geänderte und abgesagte Termine stehen danach im Portal. Was sich geändert hat, steht in der Commit-Meldung unter dem Reiter **Commits**.

**Jetzt sofort aktualisieren:** Repository → **Actions** → „Veranstaltungen aktualisieren“ → **Run workflow**.

**Wenn der Lauf rot wird:** Der SSB oder LSB hat eine Seite umgebaut oder sie war nicht erreichbar. Das Portal zeigt den letzten bekannten Stand und weist darauf hin. GitHub schickt eine E-Mail. In diesem Fall bitte melden, dann wird das Skript `update_veranstaltungen.py` angepasst.

**Von Hand ergänzen (`daten/veranstaltungen.json`):**
- `anpassungen`: Zusatzangaben zu einer automatisch gelesenen Veranstaltung. `match` ist ein Stück des Titels, z. B.:
  ```json
  {"match": "SommerSportWoche", "anmeldung_bis": "2026-06-15", "hinweis": "PSV meldet Angebot bis 10.05.", "vereinsangebot": true}
  ```
  Mögliche Felder: `anmeldung_ab`, `anmeldung_bis` (JJJJ-MM-TT), `hinweis`, `vereinsangebot`, `anmeldung_url`, `ausblenden` (true blendet den Eintrag aus), `jahr` (wenn der Titel in mehreren Jahren vorkommt).
- `ergaenzungen`: Eigene Einträge, z. B. LSB-Termine oder Einladungen per E-Mail:
  ```json
  {"titel": "Sächsische Sportgala", "von": "2026-11-21", "veranstalter": "LSB Sachsen", "url": "https://www.sport-fuer-sachsen.de/veranstaltungen/saechsische-sportgala", "hinweis": "Einladung per Mail erhalten"}
  ```
  Pflicht sind `titel` und `von` (JJJJ-MM-TT). Optional `bis`, `anmeldung_ab`, `anmeldung_bis`, `kategorie` (Veranstaltung oder Bildung).
- `angebot_melden`: Der Text im Aufklapper „Eigenes Angebot bei einer Veranstaltung anbieten“. Im PSV entscheidet jede Abteilung selbst.

Manuelle Einträge bleiben bestehen, die automatische Aktualisierung überschreibt sie nie.

## Satzung und Geschäftsordnung austauschen
Beide stehen als PDF in `downloads/` und als Text in `quellen/` (damit die Suche sie findet):
1. Neue PDF nach `downloads/` legen, z. B. `Geschaeftsordnung-Postsportverein-Leipzig-2027-01-15.pdf`.
2. In `daten/downloads.json` den Eintrag der Gruppe „Vereinsdokumente“ auf den neuen Dateinamen und Titel (mit Stand) ändern.
3. In `quellen/Geschaeftsordnung.md` bzw. `quellen/Satzung.md` den Text ersetzen und die `Link:`-Zeile auf die neue PDF setzen.
4. Alte PDF löschen, dann speichern. Die Seite baut sich selbst neu.

Veröffentlicht wird nur, was beschlossen ist. Entwürfe (z. B. die Beitragsordnung) gehören nicht ins öffentliche Repository. Die GO wird ohne Anlagen veröffentlicht, damit sie keine Kontaktdaten enthält.

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
