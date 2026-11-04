#!/usr/bin/env python3
"""Liest Veranstaltungen und Kurse von den Seiten des SSB Leipzig (und des LSB Sachsen)
und schreibt sie nach daten/veranstaltungen_auto.json.

Läuft wöchentlich als GitHub Action (.github/workflows/veranstaltungen.yml), lässt sich aber
auch lokal starten:  python3 update_veranstaltungen.py

Grundsätze
- Nur lesen, je Woche ein Abruf pro Seite, mit Namen des Vereins im User-Agent.
- Nur Angaben übernehmen, die klar erkennbar sind. Sonst bleibt das Feld leer.
- Schlägt eine Quelle fehl (Seite umgebaut, nicht erreichbar), bleiben ihre bisherigen Einträge
  stehen und das Skript endet mit Fehlercode 2. Die Action meldet das per E-Mail von GitHub.
- Von Hand gepflegtes steht in daten/veranstaltungen.json und wird hier nie angefasst.
"""
import datetime as dt
import html
import json
import re
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
AUTO = ROOT / "daten" / "veranstaltungen_auto.json"
CHANGES = ROOT / "daten" / ".aenderungen.txt"
BASE = "https://www.ssb-leipzig.de"
UA = "Foerderportal-PSV-Update (Postsportverein Leipzig e.V.; woechentlicher Abruf)"
BILDUNGSPORTAL = "https://bildungsportal.sport-fuer-sachsen.de/vasuche.html?client_id=38"
MONATE = {m: i + 1 for i, m in enumerate(
    "Januar Februar März April Mai Juni Juli August September Oktober November Dezember".split())}
MON_RE = "|".join(MONATE)

_cache = {}


def get(url):
    if url in _cache:
        return _cache[url]
    last = None
    for versuch in range(3):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=30) as r:
                _cache[url] = r.read().decode("utf-8", errors="replace")
                return _cache[url]
        except Exception as e:  # noqa: BLE001
            last = e
            time.sleep(2 * (versuch + 1))
    raise RuntimeError(f"{url}: {last}")


def text(html_src):
    s = re.sub(r"<(script|style)[\s\S]*?</\1>", " ", html_src)
    s = re.sub(r"<[^>]+>", " ", s)
    return re.sub(r"\s+", " ", html.unescape(s)).strip()


def absurl(u):
    return u if u.startswith("http") else BASE + (u if u.startswith("/") else "/" + u)


def slug(s):
    s = s.lower()
    for a, b in (("ä", "ae"), ("ö", "oe"), ("ü", "ue"), ("ß", "ss")):
        s = s.replace(a, b)
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")[:60]


def iso(d):
    return d.isoformat() if d else None


def dm(s, jahr):
    t, m = re.match(r"(\d{2})\.(\d{2})\.", s).groups()
    return dt.date(jahr, int(m), int(t))


def dmy(s):
    t, m, y = re.match(r"(\d{2})\.(\d{2})\.(\d{4})", s).groups()
    return dt.date(int(y), int(m), int(t))


def parse_datum(txt, jahr):
    """'6./7. Februar', '30. Mai - 28. Juni*', 'ab 13. März' -> (von, bis, ab)"""
    ab = txt.strip().lower().startswith("ab ")
    toks = re.findall(rf"(\d{{1,2}})\.\s*(?:({MON_RE}))?", txt)
    if not toks:
        raise ValueError(f"Datum nicht lesbar: {txt!r}")
    monate, nxt = [], None
    for tag, mon in reversed(toks):
        nxt = MONATE[mon] if mon else nxt
        if nxt is None:
            raise ValueError(f"Monat fehlt: {txt!r}")
        monate.append((int(tag), nxt))
    monate.reverse()
    (t1, m1), (t2, m2) = monate[0], monate[-1]
    von, bis = dt.date(jahr, m1, t1), dt.date(jahr, m2, t2)
    return von, (bis if bis != von else None), ab


def tabellenzeilen(html_src):
    """Gibt (jahr, [zellen-html, ...]) je Zeile zurück. Jahreszeilen wie '2027' schalten das Jahr um."""
    m = re.search(r"JAHRESPLAN\s*(\d{4})", html_src)
    jahr = int(m.group(1)) if m else dt.date.today().year
    t = re.search(r"JAHRESPLAN[\s\S]*?<table[\s\S]*?</table>", html_src)
    if not t:
        raise ValueError("Tabelle des Jahresplans nicht gefunden")
    for row in re.findall(r"<tr[^>]*>([\s\S]*?)</tr>", t.group(0)):
        cells = re.findall(r"<td[^>]*>([\s\S]*?)</td>", row)
        if not cells:
            continue
        first = text(cells[0])
        if re.fullmatch(r"\d{4}", first):
            jahr = int(first)
            continue
        if not first:
            continue
        yield jahr, cells


def eintrag(**kw):
    e = {"id": "", "titel": "", "von": None, "bis": None, "ab": False, "veranstalter": "SSB Leipzig",
         "kategorie": "Veranstaltung", "url": None, "le": None, "abgesagt": False,
         "anmeldung_ab": None, "anmeldung_bis": None, "anmeldung_url": None, "quelle": ""}
    e.update(kw)
    return e


# ---------- Quellen ----------

def quelle_veranstaltungen():
    url = f"{BASE}/leistungen/veranstaltungen/jahresplan-1/"
    out = []
    for jahr, cells in tabellenzeilen(get(url)):
        if len(cells) < 2:
            continue
        von, bis, ab = parse_datum(text(cells[0]), jahr)
        titel = text(cells[1])
        link = re.search(r'href="([^"]+)"', cells[1])
        u = absurl(html.unescape(link.group(1))) if link else None
        veranst = "SSB Leipzig"
        if titel.endswith("Sportjugend Leipzig") or (u and "/sportjugend/" in u):
            veranst = "Sportjugend Leipzig"
        titel = re.sub(r"\s*(Sportjugend Leipzig|Stadtsportbund Leipzig e\.V\.|Stadtsportbund)\s*$", "", titel)
        titel = re.sub(r"\s*Leipzig e\.V\.$", "", titel).strip(" *")
        out.append(eintrag(id=f"{slug(titel)}-{jahr}", titel=titel, von=iso(von), bis=iso(bis), ab=ab,
                           veranstalter=veranst, url=u, quelle="ssb-veranstaltungen"))
    return out


def kurs_id(titel, jahr):
    m = re.search(r"Grundlehrgang\s*(\d)/(\d{4})", titel)
    if m:
        return f"glg-{m.group(1)}-{m.group(2)}"
    m = re.search(r"Erste[\s-]*Hilfe[\s-]*Kurs\s*(\d)/(\d{4})", titel)
    if m:
        return f"ehk-{m.group(1)}-{m.group(2)}"
    if "Übungsleiter" in titel and "-C" in titel:
        return f"uelc-{jahr}"
    return f"{slug(titel)}-{jahr}"


def quelle_bildung():
    url = f"{BASE}/leistungen/aus-und-weiterbildung/jahresplan-1/"
    out = []
    for jahr, cells in tabellenzeilen(get(url)):
        if len(cells) < 2:
            continue
        von, bis, ab = parse_datum(text(cells[0]), jahr)
        link = re.search(r'href="([^"]+)"', cells[1])
        u = absurl(html.unescape(link.group(1))) if link else None
        titel = re.sub(r"\s*-?\s*ABSAGE!?\s*$", "", text(cells[1]), flags=re.I).strip(" |")
        titel = re.sub(r"\s*-?\s*jetzt anmelden!?\s*$", "", titel, flags=re.I)
        titel = re.sub(r"\s+", " ", titel).strip(" -")
        abgesagt = "ABSAGE" in text(cells[1]).upper()
        le = text(cells[2]) if len(cells) > 2 and text(cells[2]) else None
        anm = u if (u and "bildungsportal" in u) else None
        out.append(eintrag(id=kurs_id(titel, jahr), titel=titel, von=iso(von), bis=iso(bis), ab=ab,
                           kategorie="Bildung", url=u, le=le, abgesagt=abgesagt,
                           anmeldung_url=anm or BILDUNGSPORTAL, quelle="ssb-bildung"))
    return out


def quelle_kurstabellen():
    """Kurstermine mit Anmeldebeginn aus den Tabellen der Kursseiten (Grundlehrgang, Erste Hilfe, ÜL-C)."""
    out = []
    p = f"{BASE}/leistungen/aus-und-weiterbildung/"
    # Grundlehrgang
    t = text(get(p + "sportartuebergreifender-grundlehrgang/"))
    for m in re.finditer(r"GLG (\d)/(\d{4})[^\d]{0,40}?((?:\d{2}\.\d{2}\.\s+){5}\d{2}\.\d{2}\.)\s+(\d{2}\.\d{2}\.\d{4})", t):
        n, y, daten, anm = m.groups()
        ds = sorted(dm(x, int(y)) for x in re.findall(r"\d{2}\.\d{2}\.", daten))
        out.append(eintrag(id=f"glg-{n}-{y}", titel=f"Sportartübergreifender Grundlehrgang {n}/{y}", von=iso(ds[0]),
                           bis=iso(ds[-1]), kategorie="Bildung", le="32 LE", url=p + "sportartuebergreifender-grundlehrgang/",
                           anmeldung_ab=iso(dmy(anm)), anmeldung_url=BILDUNGSPORTAL, quelle="ssb-kurstabellen"))
    # Erste Hilfe
    t = text(get(p + "kurs-erste-hilfe/"))
    for m in re.finditer(r"EHK (\d)/(\d{4})\s+Fr\.\s*\|\s*(\d{2}\.\d{2}\.)\s*Sa\.\s*\|\s*(\d{2}\.\d{2}\.)\s*(\d{2}\.\d{2}\.\d{4})", t):
        n, y, d1, d2, anm = m.groups()
        out.append(eintrag(id=f"ehk-{n}-{y}", titel=f"Erste-Hilfe-Kurs {n}/{y}", von=iso(dm(d1, int(y))), bis=iso(dm(d2, int(y))),
                           kategorie="Bildung", le="9 LE", url=p + "kurs-erste-hilfe/",
                           anmeldung_ab=iso(dmy(anm)), anmeldung_url=BILDUNGSPORTAL, quelle="ssb-kurstabellen"))
    # ÜL-C
    t = text(get(p + "lehrgang-uebungsleiterin-c-breitensport/"))
    for m in re.finditer(r"ÜL-C BS (\d{4})\s+Fr\.\s*\|\s*(\d{2}\.\d{2}\.).*?Di\.\s*\|\s*(\d{2}\.\d{2}\.)\s*(\d{2}\.\d{2}\.\d{4})", t):
        y, d1, d2, anm = m.groups()
        out.append(eintrag(id=f"uelc-{y}", titel=f"Lehrgang Übungsleiter*in-C Breitensport {y} (kompakt)", von=iso(dm(d1, int(y))),
                           bis=iso(dm(d2, int(y))), kategorie="Bildung", le="90 LE",
                           url=p + "lehrgang-uebungsleiterin-c-breitensport/", anmeldung_ab=iso(dmy(anm)),
                           anmeldung_url=BILDUNGSPORTAL, quelle="ssb-kurstabellen"))
    return out


def quelle_lsb():
    url = "https://www.sport-fuer-sachsen.de/veranstaltungen/landesjugendspiele"
    t = text(get(url))
    m = re.search(r"Kommende Termine\s+(.*?)\s+(?:Impressionen|R[üu]ckblick)", t)
    if not m:
        raise ValueError("Abschnitt 'Kommende Termine' nicht gefunden")
    out = []
    for mm in re.finditer(rf"(Landesjugendspiele[^:]*):\s*(\d{{1,2}})\.\s*(?:({MON_RE})\s*)?bis\s*(\d{{1,2}})\.\s*({MON_RE})\s*(\d{{4}})\s*in\s*(\w+)", m.group(1)):
        name, d1, m1, d2, m2, y, ort = mm.groups()
        von = dt.date(int(y), MONATE[m1 or m2], int(d1))
        bis = dt.date(int(y), MONATE[m2], int(d2))
        titel = f"Sparkassen {name.strip()} ({ort})"
        out.append(eintrag(id=f"{slug(name)}-{y}", titel=titel, von=iso(von), bis=iso(bis), veranstalter="LSB Sachsen",
                           url=url, quelle="lsb-landesjugendspiele"))
    return out


def anmeldung_aus_seite(e):
    """Sucht auf der Detailseite einer Veranstaltung des SSB nach klar benannten Anmeldedaten."""
    u = e.get("url")
    if not u or not u.startswith(BASE) or "/leistungen/aus-und-weiterbildung/" in u:
        return
    try:
        t = text(get(u))
    except Exception:  # noqa: BLE001
        return
    m = re.search(r"Anmeldung[^|]{0,200}?ab dem (\d{2}\.\d{2}\.\d{4})", t) or re.search(r"Anmeldebeginn:?\s*(\d{2}\.\d{2}\.\d{4})", t)
    if m and not e["anmeldung_ab"]:
        d = dmy(m.group(1))
        if e["von"] and d.isoformat() < e["von"]:
            e["anmeldung_ab"] = d.isoformat()
    m = re.search(r"(?:Anmeldeschluss|Anmeldefrist|Meldeschluss)\D{0,40}(\d{2}\.\d{2}\.\d{4})", t)
    if m and not e["anmeldung_bis"]:
        e["anmeldung_bis"] = dmy(m.group(1)).isoformat()


QUELLEN = [
    ("ssb-veranstaltungen", "SSB Leipzig: Jahresplan Veranstaltungen", f"{BASE}/leistungen/veranstaltungen/jahresplan-1/", quelle_veranstaltungen),
    ("ssb-bildung", "SSB Leipzig: Jahresplan Aus- und Weiterbildung", f"{BASE}/leistungen/aus-und-weiterbildung/jahresplan-1/", quelle_bildung),
    ("ssb-kurstabellen", "SSB Leipzig: Kurstermine und Anmeldebeginn", f"{BASE}/leistungen/aus-und-weiterbildung/", quelle_kurstabellen),
    ("lsb-landesjugendspiele", "LSB Sachsen: Landesjugendspiele", "https://www.sport-fuer-sachsen.de/veranstaltungen/landesjugendspiele", quelle_lsb),
]


def zusammenfuehren(eintraege):
    """Gleiche id: Angaben ergänzen, vorhandene nicht überschreiben (Kurstabelle liefert Anmeldebeginn)."""
    out = {}
    for e in eintraege:
        a = out.get(e["id"])
        if not a:
            out[e["id"]] = e
            continue
        for k, v in e.items():
            if v not in (None, "", False) and a.get(k) in (None, "", False):
                a[k] = v
        if e["quelle"] == "ssb-kurstabellen":  # Termin der Kurstabelle ist genauer
            a["von"], a["bis"] = e["von"] or a["von"], e["bis"] or a["bis"]
    return sorted(out.values(), key=lambda e: (e["von"] or "9999", e["titel"]))


def main():
    alt = json.loads(AUTO.read_text(encoding="utf-8")) if AUTO.exists() else {"eintraege": []}
    alt_nach_quelle = {}
    for e in alt.get("eintraege", []):
        alt_nach_quelle.setdefault(e["quelle"], []).append(e)

    neu, status, fehler = [], [], 0
    for key, name, url, fn in QUELLEN:
        try:
            items = fn()
            if not items:
                raise ValueError("keine Einträge erkannt (Seite umgebaut?)")
            neu += items
            status.append({"quelle": key, "name": name, "url": url, "ok": True, "anzahl": len(items)})
            print(f"OK     {name}: {len(items)} Einträge")
        except Exception as e:  # noqa: BLE001
            fehler += 1
            neu += alt_nach_quelle.get(key, [])
            status.append({"quelle": key, "name": name, "url": url, "ok": False, "fehler": str(e)[:200],
                           "anzahl": len(alt_nach_quelle.get(key, []))})
            print(f"FEHLER {name}: {e}  (bisherige Einträge bleiben erhalten)", file=sys.stderr)

    neu = zusammenfuehren(neu)
    for e in neu:
        if e["quelle"] == "ssb-veranstaltungen":
            anmeldung_aus_seite(e)

    # Änderungen für die Commit-Meldung
    a = {e["id"]: e for e in alt.get("eintraege", [])}
    b = {e["id"]: e for e in neu}
    zeilen = [f"Neu: {b[i]['titel']} ({b[i]['von']})" for i in b if i not in a]
    zeilen += [f"Entfallen: {a[i]['titel']} ({a[i]['von']})" for i in a if i not in b]
    for i in b:
        if i in a:
            for k, bez in (("von", "Beginn"), ("bis", "Ende"), ("anmeldung_ab", "Anmeldebeginn"), ("anmeldung_bis", "Anmeldefrist"), ("abgesagt", "Absage")):
                if a[i].get(k) != b[i].get(k):
                    zeilen.append(f"Geändert: {b[i]['titel']}: {bez} {a[i].get(k)} -> {b[i].get(k)}")
    CHANGES.write_text("\n".join(zeilen), encoding="utf-8")

    heute = dt.date.today().isoformat()
    ausgabe = {"hinweis": "Wird automatisch von update_veranstaltungen.py erzeugt. Nicht von Hand ändern, Ergänzungen bitte in veranstaltungen.json.",
               "stand": heute if not fehler else alt.get("stand", heute), "quellen": status, "eintraege": neu}
    if not zeilen and AUTO.exists() and not fehler:
        ausgabe["stand"] = alt.get("stand", heute)  # keine Änderung, kein unnötiger Commit
    AUTO.write_text(json.dumps(ausgabe, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"{len(neu)} Einträge, {len(zeilen)} Änderungen, {fehler} fehlerhafte Quellen.")
    return 2 if fehler else 0


if __name__ == "__main__":
    sys.exit(main())
