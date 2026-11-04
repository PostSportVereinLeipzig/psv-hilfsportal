#!/usr/bin/env python3
"""Baut index.html aus tpl.html und den Daten im Ordner daten/ und quellen/.

Aufruf:  python3 build.py
Danach index.html im Browser prüfen und mit git veröffentlichen.
"""
import json, re, sys, unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATEN, QUELLEN, DOWNLOADS = ROOT / "daten", ROOT / "quellen", ROOT / "downloads"
MAXLEN = 1000  # maximale Länge eines Such-Abschnitts in Zeichen


def lade(name):
    try:
        return json.loads((DATEN / name).read_text(encoding="utf-8"))
    except FileNotFoundError:
        sys.exit(f"FEHLER: daten/{name} fehlt.")
    except json.JSONDecodeError as e:
        sys.exit(f"FEHLER: daten/{name} ist kein gültiges JSON (Zeile {e.lineno}, Spalte {e.colno}): {e.msg}\n"
                 "Meist fehlt ein Komma oder ein Anführungszeichen in der Nähe dieser Stelle.")


def abschnitte(text):
    """Zerlegt Markdown-Text in Abschnitte bis MAXLEN Zeichen, an Absatzgrenzen."""
    out, cur = [], ""
    for para in re.split(r"\n\s*\n", text):
        para = re.sub(r"\s+", " ", para).strip()
        if not para:
            continue
        while len(para) > MAXLEN:  # sehr lange Absätze an Satzende/Leerzeichen trennen
            cut = max(para.rfind(". ", 0, MAXLEN), para.rfind(" ", 0, MAXLEN))
            cut = cut if cut > 200 else MAXLEN
            if cur:
                out.append(cur); cur = ""
            out.append(para[:cut + 1].strip()); para = para[cut + 1:].strip()
        if cur and len(cur) + len(para) + 1 > MAXLEN:
            out.append(cur); cur = ""
        cur = f"{cur} {para}".strip()
    if cur:
        out.append(cur)
    return out


def md_quellen(docs, chunks):
    """Jede quellen/*.md wird ein eigenes Dokument der Suche.
    Kopfzeilen (optional): '# Titel', 'Kategorie: Info', 'Link: https://...'"""
    for p in sorted(QUELLEN.glob("*.md")):
        zeilen = unicodedata.normalize("NFC", p.read_text(encoding="utf-8")).splitlines()
        titel, kat, link, i = p.stem, "Info", None, 0
        while i < len(zeilen):
            z = zeilen[i].strip()
            if z.startswith("# ") and titel == p.stem:
                titel = z[2:].strip()
            elif z.lower().startswith("kategorie:"):
                kat = z.split(":", 1)[1].strip() or kat
            elif z.lower().startswith("link:"):
                link = z.split(":", 1)[1].strip() or None
            elif z:
                break
            i += 1
        docs.append({"t": titel, "k": kat, "h": link})
        n = len(docs) - 1
        chunks.extend([n, a] for a in abschnitte("\n".join(zeilen[i:])))
        print(f"  Quelle: {p.name} -> {len(chunks) and sum(1 for c in chunks if c[0] == n)} Abschnitte")


def downloads_liste():
    out = []
    for x in lade("downloads.json")["downloads"]:
        f = DOWNLOADS / Path(x["f"]).name
        if not f.exists():
            print(f"  WARNUNG: {x['f']} fehlt im Ordner downloads/ und wird weggelassen.")
            continue
        out.append({**x, "ext": f.suffix[1:].upper(), "kb": max(1, round(f.stat().st_size / 1024))})
    return out


def main():
    ref = lade("dokumente.json")
    docs, chunks = list(ref["docs"]), [list(c) for c in ref["chunks"]]
    md_quellen(docs, chunks)
    data = {"docs": docs, "chunks": chunks, "downloads": downloads_liste(), "fmap": ref["fmap"],
            "termine": lade("termine.json"), "kontakte": lade("kontakte.json")}
    # Nur Dateien aus fmap prüfen, die es wirklich nicht gibt
    for v in ref["fmap"].values():
        if v and not (ROOT / v).exists():
            print(f"  WARNUNG: {v} (fmap) fehlt.")
    js = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    tpl = (ROOT / "tpl.html").read_text(encoding="utf-8")
    if "__DATA__" not in tpl:
        sys.exit("FEHLER: Platzhalter __DATA__ fehlt in tpl.html.")
    (ROOT / "index.html").write_text(tpl.replace("__DATA__", js), encoding="utf-8")
    print(f"index.html gebaut: {len(docs)} Dokumente, {len(chunks)} Abschnitte, {len(data['downloads'])} Downloads.")


if __name__ == "__main__":
    main()
