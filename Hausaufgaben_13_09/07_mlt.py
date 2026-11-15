"""
Das Script prüft, ob ein Request Handler /mlt existiert. Ist dies nicht der Fall, legt das Script diesen an. Existiert dieser schon,
dann erfolgt eine entsprechende Rückmeldung ("Request Handler '/mlt' existiert bereits.")
Danach werden Funktionien für die Ein- und Ausgaben aufbereitet. 
Es folgt die Suche. Das Ergebnis gibt zunächst das erste EBook aus, dann die drei ähnlichen Titel und dann die "interessanten" Therme aus dem
Ausgangsdokument.
Für eine bessere Nutzung wurde sich dafür entschieden, dass die Suche nicht nach einer Anfrage abgebrochen wird, sondern aktiv durch die Eingabe von
'q' oder einer leeren Suchanfrage abgebrochen werden muss. 



authors: Beata Lakeberg, Christin Seegert, Martina Schildt, Elena Torlopova
license: MIT License
version: 1.0
date: 2026-11-08  

"""

"""

Ablauf:
  1. Request Handler /mlt im Core anlegen (nur falls noch nicht vorhanden).
  2. Suchanfrage vom Benutzer einlesen, Top-1-Dokument ermitteln und ausgeben.
  3. ID des Top-1-Dokuments an /mlt schicken -> bis zu 3 ähnliche E-Books
     sowie die "interessantesten" Terme (interestingTerms) ausgeben.

MLT-Parameter lassen sich pro Aufruf überschreiben, z.B.:
    python 07_mlt.py --param mlt.mintf=1 --param mlt.mindf=2 --param mlt.maxqt=50
"""

#!/usr/bin/env python3
"""07_mlt.py - MoreLikeThis (Ähnlichkeitssuche) auf dem Solr-Core pg_fulltexts.

Ablauf:
  1. Request Handler /mlt im Core anlegen (nur falls noch nicht vorhanden).
  2. Suchanfrage vom Benutzer einlesen, Top-1-Dokument ermitteln und ausgeben.
  3. ID des Top-1-Dokuments an /mlt schicken -> bis zu 3 ähnliche E-Books
     sowie die "interessantesten" Terme (interestingTerms) ausgeben.

MLT-Parameter lassen sich pro Aufruf überschreiben, z.B.:
    python 07_mlt.py --param mlt.mintf=1 --param mlt.mindf=2 --param mlt.maxqt=50
"""

import argparse

import pysolr
import requests

SOLR_BASE_URL = "http://localhost:8983/solr"
CORE = "pg_fulltexts"
CORE_URL = f"{SOLR_BASE_URL}/{CORE}"
HANDLER_NAME = "/mlt"

# Namen der Metadatenfelder, die ausgegeben werden sollen
ID_FIELD = "id"
TITLE_FIELD = "title"
AUTHOR_FIELD = "author"

NUM_SIMILAR = 3

# in Aufgabenstellung vorgegeben
MLT_HANDLER_DEFAULTS = {
    "mlt.fl": "fulltext",
    # Das Feld, aus dem die Terme des Ausgangsdokuments stammen und in dem nach ähnlichen Dokumenten gesucht wird. 
    "mlt.mintf": 2,
    # Minimale Term Frequency im Ausgangsdokument. Ein Term muss dort mindestens 2-mal vorkommen.
    "mlt.mindf": 5,
    # Minimale Document Frequency im Index. Ein Term muss in mindestens 5 Dokumenten vorkommen.
    "mlt.minwl": 5,
    # Minimale Wortlänge. Terme mit weniger als 5 Zeichen werden ignoriert. 
    "mlt.maxdfpct": 25,
    # Maximale Document Frequency in Prozent. Terme, die in mehr als 25 % aller Dokumente stehen, fallen weg.
    "mlt.interestingTerms": "list",
    # das Ausgangsdokument selbst soll nicht in der Trefferliste erscheinen
    "mlt.match.include": "false",
    "mlt.boost": "true",
}


# ---------------------------------------------------------------------------
# Request Handler
# ---------------------------------------------------------------------------
def handler_exists() -> bool:
    """Prüft per HTTP-GET, ob /mlt in der Konfiguration des Cores existiert."""
    resp = requests.get(f"{CORE_URL}/config", params={"wt": "json"}, timeout=30)
    resp.raise_for_status()
    handlers = resp.json().get("config", {}).get("requestHandler", {})
    return HANDLER_NAME in handlers


def create_handler() -> None:
    """Legt den Request Handler /mlt über die Config API an."""
    payload = {
        "add-requesthandler": {
            "name": HANDLER_NAME,
            "class": "solr.MoreLikeThisHandler",
            "defaults": MLT_HANDLER_DEFAULTS,
        }
    }
    resp = requests.post(f"{CORE_URL}/config", json=payload, timeout=30)
    resp.raise_for_status()
    body = resp.json()
    if "errorMessages" in body or "error" in body:
        raise RuntimeError(f"Handler konnte nicht angelegt werden: {body}")
    print(f"Request Handler '{HANDLER_NAME}' wurde angelegt.")


def ensure_handler() -> None:
    if handler_exists():
        print(f"Request Handler '{HANDLER_NAME}' existiert bereits.")
    else:
        create_handler()


# ---------------------------------------------------------------------------
# Funktionien für Ein- und Ausgaben
# ---------------------------------------------------------------------------
def first(value):
    """Solr liefert Felder je nach Schema als Liste oder Einzelwert."""
    if isinstance(value, list):
        return ", ".join(str(v) for v in value)
    return "" if value is None else str(value)


def print_doc(doc: dict, prefix: str = "") -> None:
    print(f"{prefix}ID:     {first(doc.get(ID_FIELD))}")
    print(f"{prefix}Titel:  {first(doc.get(TITLE_FIELD))}")
    print(f"{prefix}Autor:  {first(doc.get(AUTHOR_FIELD))}")


def parse_interesting_terms(raw) -> list[str]:
    """interestingTerms kann Liste (list) oder Dict/Paarliste (details) sein."""
    if raw is None:
        return []
    if isinstance(raw, dict):
        return [f"{t} (Boost {b})" for t, b in raw.items()]
    if isinstance(raw, list):
        # "details" kommt in JSON als flache Liste [term, boost, term, boost, ...]
        if raw and len(raw) % 2 == 0 and all(
            isinstance(x, (int, float)) for x in raw[1::2]
        ):
            return [f"{t} (Boost {b})" for t, b in zip(raw[::2], raw[1::2])]
        return [str(t) for t in raw]
    return [str(raw)]


def parse_overrides(items: list[str]) -> dict:
    overrides = {}
    for item in items:
        if "=" not in item:
            raise SystemExit(f"Ungültiger --param '{item}', erwartet key=value")
        key, value = item.split("=", 1)
        overrides[key.strip()] = value.strip()
    return overrides


# ---------------------------------------------------------------------------
# Suche
# ---------------------------------------------------------------------------
def top1(solr: pysolr.Solr, query: str) -> dict | None:
    results = solr.search(
        query,
        **{
            "defType": "edismax",
            "qf": "fulltext",
            "rows": 1,
            "fl": f"{ID_FIELD},{TITLE_FIELD},{AUTHOR_FIELD},score",
        },
    )
    docs = list(results)
    return docs[0] if docs else None


def more_like_this(doc_id: str, overrides: dict) -> tuple[list[dict], list[str]]:
    escaped = doc_id.replace("\\", "\\\\").replace('"', '\\"')
    params = {
        "q": f'{ID_FIELD}:"{escaped}"',
        "rows": NUM_SIMILAR,
        "fl": f"{ID_FIELD},{TITLE_FIELD},{AUTHOR_FIELD},score",
        "wt": "json",
    }
    params.update(overrides)  # überschreibt die Handler-Defaults
    resp = requests.get(f"{CORE_URL}{HANDLER_NAME}", params=params, timeout=120)
    resp.raise_for_status()
    body = resp.json()
    docs = body.get("response", {}).get("docs", [])
    terms = parse_interesting_terms(body.get("interestingTerms"))
    return docs, terms


# ---------------------------------------------------------------------------
def run_search(solr: pysolr.Solr, query: str, overrides: dict) -> None:
    """Eine komplette Runde: Top-1-Suche, MLT-Abfrage, Ausgabe."""
    doc = top1(solr, query)
    if doc is None:
        print("Keine Treffer.")
        return

    print("\n=== Top-1-Dokument (Ausgangsdokument) ===")
    print_doc(doc)

    similar, terms = more_like_this(first(doc[ID_FIELD]), overrides)

    print(f"\n=== Bis zu {NUM_SIMILAR} ähnliche E-Books ===")
    if not similar:
        print("Keine ähnlichen Dokumente gefunden.")
    for rank, sim in enumerate(similar, start=1):
        print(f"{rank}.")
        print_doc(sim, prefix="   ")

    print("\n=== Interessanteste Terme des Ausgangsdokuments ===")
    if terms:
        for term in terms:
            print(f"  {term}")
    else:
        print("  (keine zurückgeliefert)")


def main() -> None:
    parser = argparse.ArgumentParser(description="Solr MoreLikeThis auf pg_fulltexts")
    parser.add_argument(
        "--param",
        action="append",
        default=[],
        metavar="KEY=VALUE",
        help="MLT-Parameter überschreiben, z.B. --param mlt.mintf=1 (mehrfach möglich)",
    )
    args = parser.parse_args()
    overrides = parse_overrides(args.param)

    ensure_handler()

    solr = pysolr.Solr(CORE_URL, timeout=60)

    if overrides:
        print(f"Überschriebene MLT-Parameter: {overrides}")

    # Schleife: nach jeder Suche kann direkt die nächste eingegeben werden.
    # Leere Eingabe oder Eingabe von 'q' beendet das Programm.
    while True:
        query = input("\nSuchanfrage (leer/'q' zum Beenden): ").strip()
        if not query or query.lower() in ("q"):
            print("Ende.")
            break

        try:
            run_search(solr, query, overrides)
        except (requests.RequestException, pysolr.SolrError) as exc:
            # Ein Fehler (z.B. Solr nicht erreichbar) soll die Schleife nicht beenden
            print(f"Fehler bei der Anfrage: {exc}")


if __name__ == "__main__":
    main()