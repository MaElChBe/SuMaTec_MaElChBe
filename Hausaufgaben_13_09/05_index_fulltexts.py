'''
Das Programm liest die gefilterten Volltexte aus dem Verzeichnis fulltexts ein. Für jede eingelesene Volltextdatei wird auf Basis 
der E-Book-ID eine Solr-Query im Solr-Core my1stcore abgesetzt, um die folgenden Metadaten des E-Books zu ermitteln:
    - Titel
    - Liste der Autoren (1..n)
    - Liste der Sprachen (1..n)
    - Liste der Subjects (1..n)
    - Datum der Aufnahme des E-Books in Project Gutenberg
Die zurückgelieferten Metadaten des E-Books werden zusammen mit dem Volltext des E-Books im Solr-Core pg_fulltexts auf Basis des 
zuvor angelegten Solr-Schemas indexiert.

authors: Beata Lakeberg, Christin Seegert, Martina Schildt, Elena Torlopova
license: MIT License
version: 1.0
date: 2026-11-08  
'''
import locale
import re
from pathlib import Path
 
import pysolr
 
# --- Konfiguration -----------------------------------------------------------
SOLR_META_URL = "http://localhost:8983/solr/my1stcore"         # Metadaten (Quelle)
SOLR_FULLTEXT_URL = "http://localhost:8983/solr/pg_fulltexts"  # Volltexte (Ziel)
FULLTEXT_DIR = Path("fulltexts")
BATCH_SIZE = 20  # Volltexte sind gross, daher kleinere Pakete als bei den Metadaten
locale.setlocale(locale.LC_ALL, "de_DE.UTF-8")
 
# Feldnamen im Core my1stcore
META_ID_FIELD = "id"
META_FIELDS = ["id", "title", "authors", "language", "subjects", "issued"]
 
# Feldname fuer den Volltext im Core pg_fulltexts
FULLTEXT_FIELD = "fulltext"
 
 
def extract_book_id(path: Path) -> str | None:
    """Ermittelt die E-Book-ID aus dem Dateinamen, z. B. '1234_filtered.txt' -> '1234'."""
    match = re.fullmatch(r"(\d+)_filtered", path.stem)
    return match.group(1) if match else None
 
 
def fetch_metadata(solr_meta: pysolr.Solr, book_id: str) -> dict | None:
    """Fragt die Metadaten eines E-Books anhand der ID im Core my1stcore ab."""
    results = solr_meta.search(
        f'{META_ID_FIELD}:"{book_id}"',
        fl=",".join(META_FIELDS),
        rows=1,
    )
    for doc in results:
        return doc
    return None
 
 
def build_doc(meta: dict, text: str) -> dict:
    """Baut das Solr-Dokument fuer pg_fulltexts: Metadaten uebernehmen + Volltext."""
    doc = {field: meta[field] for field in META_FIELDS if field in meta}
    doc[FULLTEXT_FIELD] = text
    return doc
 
 
def index_fulltexts(
    fulltext_dir: Path = FULLTEXT_DIR,
    meta_url: str = SOLR_META_URL,
    fulltext_url: str = SOLR_FULLTEXT_URL,
    batch_size: int = BATCH_SIZE,
):
    solr_meta = pysolr.Solr(meta_url, timeout=60)
    solr_full = pysolr.Solr(fulltext_url, timeout=300, always_commit=False)
 
    total = 0
    skipped = 0
    batch = []
 
    for path in sorted(fulltext_dir.glob("*_filtered.txt")):
        book_id = extract_book_id(path)
        if book_id is None:
            print(f"Keine ID im Dateinamen: {path.name} - uebersprungen.")
            skipped += 1
            continue
 
        meta = fetch_metadata(solr_meta, book_id)
        if meta is None:
            print(f"Keine Metadaten fuer ID {book_id} gefunden - uebersprungen.")
            skipped += 1
            continue
 
        text = path.read_text(encoding="utf-8", errors="replace")
        batch.append(build_doc(meta, text))
 
        if len(batch) >= batch_size:
            solr_full.add(batch)
            total += len(batch)
            print(f"{total:n} Volltexte indexiert.")
            batch = []
 
    if batch:
        solr_full.add(batch)
        total += len(batch)
 
    solr_full.commit()
    print(f"{total:n} Volltexte indexiert, {skipped:n} uebersprungen.")
 
 
if __name__ == "__main__":
    index_fulltexts()