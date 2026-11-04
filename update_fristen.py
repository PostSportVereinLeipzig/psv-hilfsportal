#!/usr/bin/env python3
"""Gleicht die wiederkehrenden Fristen in daten/fristen.json mit der Fristenseite des SSB Leipzig ab
(https://www.ssb-leipzig.de/leistungen/vereinsberatung/fristen-1/) und passt sie bei Änderungen an.

Läuft wöchentlich als GitHub Action (.github/workflows/fristen.yml), lässt sich aber auch lokal starten:
    python3 update_fristen.py

Was das Skript tut
- Nur Monat und Tag zählen. Das Jahr auf der SSB-Seite wird ignoriert, die Fristen wiederholen sich jährlich.
- Jede Frist mit ssb_match wird in der SSB-Tabelle gesucht. Weicht Monat oder Tag ab, wird sie angepasst.
- Neue Zeilen der SSB-Tabelle, die zu keiner Frist passen, werden als neue Frist ergänzt (auto: true).
- Fristen, die auf der SSB-Seite nicht mehr stehen, bleiben stehen und werden nur gemeldet.
- Texte (Titel, Hinweise) ändert das Skript nie. Die Änderungen stehen in daten/.fristen_aenderungen.txt.
- Endet mit Fehlercode 2, wenn die Seite nicht gelesen werden kann. Dann bleibt alles unverändert.
"""
import html
import json
import re
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATEI = ROOT / "daten" / "fristen.json"
CHANGES = ROOT / "daten" / ".fristen_aenderungen.txt"
URL = "https://www.ssb-leipzig.de/leistungen/vereinsberatung/fristen-1/"
UA = "Foerderportal-PSV-Update (Postsportverein Leipzig e.V.; woechentlicher Abruf)"
MONATE = {m: i + 1 for i, m in enumerate(
    "Januar Februar März April Mai Juni Juli August September Oktober November Dezember".split())}


def get(url):
    last = None
    for versuch in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=30) as r:
                return r.read().decode("utf-8", errors="replace")
        except Exception as e:  # noqa: BLE001
            last = e
            time.sleep(2 * (versuch + 1))
    raise RuntimeError(f"{url}: {last}")


def text(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s))).strip()


def ssb_zeilen():
    """-> Liste (jahr, monat, tag, text) aus der Fristentabelle, neueste Jahre zuerst."""
    seite = get(URL)
    tab = re.search(r"<table[\s\S]*?</table>", seite)
    if not tab:
        raise ValueError("Fristentabelle nicht gefunden (Seite umgebaut?)")
    out = []
    for row in re.findall(r"<tr[^>]*>([\s\S]*?)</tr>", tab.group(0)):
        zellen = [text(c) for c in re.findall(r"<td[^>]*>([\s\S]*?)</td>", row)]
        if len(zellen) < 2 or not zellen[1]:
            continue
        m = re.search(rf"(\d{{1,2}})\.\s*({'|'.join(MONATE)})\s*(\d{{4}})", zellen[0])
        if not m:
            continue  # 'unterjährig' usw. werden nicht abgeglichen
        out.append((int(m.group(3)), MONATE[m.group(2)], int(m.group(1)), zellen[1]))
    if len(out) < 5:
        raise ValueError(f"Nur {len(out)} Fristen erkannt, erwartet mehr (Seite umgebaut?)")
    return sorted(out, key=lambda z: (-z[0], z[1], z[2]))


def passt(txt, woerter):
    t = txt.lower()
    return all(w in t for w in woerter)


def quelle_von(txt):
    t = txt.lower()
    if any(k in t for k in ("landessportbund", "lsb", "vereinsportal")):
        return "LSB"
    if any(k in t for k in ("amt für", "stadt leipzig", "stadtbezirk")):
        return "Stadt"
    if any(k in t for k in ("bürgerstiftung", "wir für sachsen")):
        return "Dritte"
    return "SSB"


def main():
    daten = json.loads(DATEI.read_text(encoding="utf-8"))
    fristen = daten["fristen"]
    try:
        zeilen = ssb_zeilen()
    except Exception as e:  # noqa: BLE001
        print(f"FEHLER: {e}  (Fristen bleiben unverändert)", file=sys.stderr)
        return 2

    neuestes = max(z[0] for z in zeilen)
    benutzt, meldungen = set(), []
    for f in fristen:
        regeln = f.get("ssb_match")
        if not regeln:
            continue
        treffer = []
        for woerter in regeln:
            # neuestes Jahr zuerst, sonst das nächstältere (Jahreswechsel, wenn die neue Tabelle noch unvollständig ist)
            z = next((z for z in zeilen if passt(z[3], woerter)), None)
            if z:
                treffer.append(z)
                benutzt.add(z)
        if not treffer:
            meldungen.append(f"Nicht mehr auf der SSB-Seite gefunden (bleibt stehen): {f['t']} ({f['d']:02d}.{f['m']:02d}.)")
            continue
        daten_set = {(z[1], z[2]) for z in treffer}
        if len(daten_set) > 1:
            meldungen.append(f"Uneinheitliche Daten auf der SSB-Seite für: {f['t']}: " + ", ".join(f"{d:02d}.{m:02d}." for m, d in sorted(daten_set)) + " (nicht geändert, bitte prüfen)")
            continue
        m, d = next(iter(daten_set))
        if (f["m"], f["d"]) != (m, d):
            meldungen.append(f"Geändert: {f['t']}: {f['d']:02d}.{f['m']:02d}. -> {d:02d}.{m:02d}.")
            f["m"], f["d"] = m, d

    # neue Zeilen (nur aus dem neuesten Jahr), die zu keiner Frist passen
    for z in zeilen:
        if z[0] != neuestes or z in benutzt:
            continue
        if any(f.get("ssb_match") and any(passt(z[3], w) for w in f["ssb_match"]) for f in fristen):
            continue
        titel = re.sub(r"\s+", " ", z[3]).strip()
        fristen.append({"m": z[1], "d": z[2], "t": titel, "s": quelle_von(titel), "w": "siehe SSB-Fristenseite",
                        "h": "Automatisch vom SSB übernommen, bitte Text prüfen.", "ssb_match": [[w.lower() for w in re.findall(r"[\wäöüß]{6,}", titel)[:2]]], "auto": True})
        meldungen.append(f"Neu auf der SSB-Seite (ergänzt): {z[2]:02d}.{z[1]:02d}. {titel}")

    fristen.sort(key=lambda f: (f["m"], f["d"]))
    CHANGES.write_text("\n".join(meldungen), encoding="utf-8")
    DATEI.write_text(json.dumps(daten, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"SSB-Fristenseite gelesen: {len(zeilen)} Zeilen, {len(meldungen)} Meldungen.")
    for m in meldungen:
        print(" -", m)
    return 0


if __name__ == "__main__":
    sys.exit(main())
