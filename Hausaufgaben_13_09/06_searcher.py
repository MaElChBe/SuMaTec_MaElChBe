"""
Integrierte Metadaten- und Volltextsuche auf dem Solr-Core pg_fulltexts.

Fuer jede Suchanfrage wird mit dem Edismax-Query-Parser ein Top-10-Ranking ermittelt.
Ausgegeben werden Rang, ID, Titel, Aufnahmedatum, Autor(en), Sprache(n) und Subject(s).

authors: Beata Lakeberg, Christin Seegert, Martina Schildt, Elena Torlopova
license: MIT License
version: 1.0
date: 2026-11-08  
"""

import locale
from datetime import datetime

import pysolr

SOLR_CORE_URL = "http://localhost:8983/solr/pg_fulltexts"

locale.setlocale(locale.LC_ALL, "de_DE.UTF-8")


def search(solr, query):
    params = {
        "defType": "edismax",  # Erweiterter DisMax-Query-Parser
        # Durchsuchte Indexfelder mit Gewichtung
        "qf": "title^5 authors^2 subjects^1 fulltext^2 fulltext_alternative^3",
        "q.op": "OR",          # Suchterme standardmaessig per OR verknuepfen
        "mm": "10%",           # mindestens 10 % der Suchterme muessen im Dokument vorkommen
        # Boost Function: neuere E-Books erhalten eine hoehere Relevanzbewertung
        "bf": "recip(ms(NOW,issued),3.16e-11,1,1)",
        "rows": 10,            # Top-10-Ranking
        "fl": "id, title, issued, authors, language, subjects, score",
    }

    results = solr.search(query, **params)
    if not results or len(results) == 0:
        print("Ihre Suchanfrage liefert keine Treffer!")
        return

    print(f"\n* * * Insgesamt {results.hits} Suchergebnisse gefunden - "
          f"{len(results)} Treffer werden angezeigt. * * *\n")

    for rank, result in enumerate(results, start=1):
        issued = datetime.fromisoformat(result.get("issued").replace("Z", "+00:00"))
        #print(f"""Rang {rank}
        print(f"""Rang {rank}  (Score: {result.get('score', 0):.4f})
          ID: {result.get('id')}
          Titel: {result.get('title')}
          Aufnahmedatum: {issued:%d. %B %Y}
          Autor(en): {", ".join(result.get('authors'))}
          Sprache(n): {", ".join(result.get('language'))}
          Subject(s): {", ".join(result.get('subjects'))}
""")


if __name__ == "__main__":
    print("Gib eine Suchanfrage ein oder 'quit!' zum Verlassen.")
    solr = pysolr.Solr(SOLR_CORE_URL, timeout=60)

    while True:
        user_query = input("Suchanfrage: ").strip()
        if user_query.lower() == "quit!":
            break
        elif user_query:
            search(solr, user_query)