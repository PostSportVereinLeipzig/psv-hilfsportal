# Übergabe: Förderportal PSV (für Claude Code)

## Ziel
Statische Web-Seite (GitHub Pages, kostenlos, öffentlich) für den Postsportverein Leipzig e.V. Muss auf **Desktop und Smartphone** gut nutzbar sein (responsive, ein Layout, optional PWA/App-Symbol).

## Aktueller Stand (lokal)
- `tpl.html`: Vorlage mit Platzhalter `__DATA__` (CSS und JS inline, Hash-Routing #suche #foerderungen #fristen #termine #formulare).
- `index.html`: gebaute Seite (Daten eingebettet, Volltextsuche über ca. 805 Abschnitte).
- `daten/termine.json`: Termine und jährlich wiederkehrende Vereinsfristen (monat, tag).
- `daten/kontakte.json`: nur E-Mail-Adressen, keine Telefonnummern.
- `downloads/`: Formulare und Vorlagen (PDF, XLSX, XLS).
- Offen: Der Build-Schritt (Daten + Volltext-Chunks aus den md-Dateien in `../1_Quellen_fuer_Markdown`) lief bisher über temporäre Skripte. Als dauerhaftes `build.py` im Repo neu anlegen (Quelle: md-Dateien, termine.json, kontakte.json, downloads).

## Aufgaben
1. Mobile Ansicht: `@media`-Regeln für schmale Bildschirme (Navigation, Karten, Suche, Downloads), Tippflächen, kein horizontales Scrollen. Test mit Handy.
2. Optional PWA (manifest, Icon).
3. Repo anlegen (neuer GitHub-Account über Vorstands-Mailadresse), GitHub Pages aktivieren, ersten Push.
4. `build.py` + kurze Anleitung zur Pflege von Terminen und Fristen (JSON editieren, bauen, pushen).

## Startreihenfolge in Claude Code
0. GitHub-Account (Vorstands-Mailadresse) ist angelegt. Zuerst die Verknüpfung herstellen (`gh auth login` oder Git-Zugang), dann Repository anlegen.
1. Repo + GitHub Pages einrichten, ersten Stand veröffentlichen.
2. Mobile Ansicht und Build-Skript (siehe Aufgaben).
3. Zwei Anleitungen als Markdown im Repo schreiben:
   - `ANLEITUNG_Pflege.md` für den Vorstand: Termine/Fristen/Kontakte in den JSON-Dateien ändern, neue Formulare und md-Quellen ablegen, bauen, veröffentlichen, Fehler beheben, Zugang und Sicherung (2FA, Wiederherstellungscodes, zweite Admin-Person).
   - `ANLEITUNG_Mitglieder.md` (eine Seite): Link, Suche, Download, Handy-Symbol.
4. Alle Mitglieder sollen zugreifen: öffentlich, ohne Login.

## Hinweise
- Alles darf öffentlich sein, es gibt keinen Upload und keinen Passwortschutz.
- Dateinamen auf macOS: Unicode normalisieren (NFC).
- § 9 im ÜL-Vertrag zitiert "§ 5 BDSG" und sollte rechtlich geprüft werden.
- Frist Grundbeiträge 1. HJ: 31.03. Mitgliedermeldung: 30.06./31.12. ÜL-Abrechnung: 15.07./15.01.
- Gymnastik-Ansprechpartner (Blumberg Böhm, Vocke): bisher ohne E-Mail, nicht im Kontaktblock.
