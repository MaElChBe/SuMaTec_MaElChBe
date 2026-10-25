"""Hier werden die IDs aller E-Books ermittelt, die in deutscher Sprache vorliegen und den Dokumenttyp Text besitzen.
 Statt rows werden cursorMark-Parameter verwendet.
 Die zurückgelieferten E-Book-IDs werden in der Textdatei ebook_ids.txt abgespeichert (eine ID pro Zeile).
 Die Anzahl der gespeicherten E-Book-IDs wird auf der Konsole ausgegeben."""

import locale
SOLR_CORE_URL = "http://localhost:8983/solr/my1stcore"
import pysolr
solr = pysolr.Solr(SOLR_CORE_URL, timeout=60)


AUSGABEDATEI = "ebook_ids.txt"
locale.setlocale(locale.LC_ALL, "de_DE.UTF-8")

#Suchanfrage mit cursorMark-Regeln (sort, startwert und rows)
def search(solr):
    params = {
        "q": "*:*",
        "fq": ["type:Text", "language:de"],
        "sort": "id asc",
        "rows": 500,
        "fl": "id",
        "cursorMark": "*",
    }

    #Suche wird durchgeführt
    results = solr.search(**params)
    if not results or len(results) == 0:
        print("Ihre Suchanfrage liefert keine Treffer!")
        return []
    #For-Schleife läuft alle Ergebnis-Seiten (cursorMark) durch und alle IDs werden in eine Liste gesammelt.
    ids = []
    for buch in results:
        ids.append(buch["id"])

    # TXT-Datei wird geöffnet und die E-Book-ID dort abgespeichert.
    with open("../ebook_ids.txt", "w", encoding="utf-8") as datei:
        for ebook_id in ids:
            datei.write(f"{ebook_id}\n")

    return ids


if __name__ == "__main__" :
    solr = pysolr.Solr(SOLR_CORE_URL, timeout=60)
    ids = search(solr)
    print(f"\n Es hat alles geklappt! \n Insgesamt wurden {len (ids)} Suchergebnisse gefunden und die TXT-Datei wurde erfolgreich gespeichert. \n Well done!\n")
