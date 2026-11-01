"""
Legt im Solr-Core pg_fulltexts ein Schema an, das zu den Spalten der pg_fulltexts_catalog.csv passt.

Nutzt die Solr Schema-API, zum Anlegen von Indexfeldtypen, Indexfeldern und Copy-Fields.
Das Skript erzeugt nur die Schema-Struktur. Das Einlesen und Indexieren der CSV-Daten
erfolgt in einem separaten Schritt.

Es wird einen Feldtyp 'text_de_custom' definiert, der folgende Eigenschaften besitzt:

  - verwendeter Tokenizer: StandardTokenizerFactory
  - Filterkette, welche die Tokens durchlaufen sollen: LowerCaseFilterFactory, 
  - StopFilterFactory (auf Basis der Datei stopwords_de.txt), GermanMinimalStemFilterFactory

authors: Beata Lakeberg, Christin Seegert, Martina Schildt, Elena Torlopova
license: MIT License
version: 1.0
date: 2026-11-01  
"""

import requests

# Basis-URL des Cores
SOLR_CORE_URL = "http://localhost:8983/solr/pg_fulltexts"

FIELD_TYPES = [
    {   
        "name": "text_de_custom",
        "class": "solr.TextField",
        "positionIncrementGap": "100",
        "analyzer": {
            "tokenizer": {"class": "solr.StandardTokenizerFactory"},
            "filters": [
                {"class": "solr.LowerCaseFilterFactory"},
                {
                    "class": "solr.StopFilterFactory",
                    "ignoreCase": "true",
                    "words": "lang/stopwords_de.txt",
                    "format": "snowball",
                },
                {"class": "solr.GermanMinimalStemFilterFactory"},
            ],
        },
    }
]

FIELDS = [
    #{"name": "id", "type": "string", "stored": True, "indexed": True, "multiValued": True},
    {"name": "id", "type": "string", "stored": True, "indexed": True, "multiValued": False},
    {"name": "title", "type": "text_de", "stored": True, "indexed": True, "multiValued": False},
    {"name": "authors", "type": "text_general", "stored": True, "indexed": True, "multiValued": True},
    {"name": "language", "type": "string", "stored": True, "indexed": True, "multiValued": True},
    {"name": "subjects", "type": "text_general", "stored": True, "indexed": True, "multiValued": True},
    {"name": "issued", "type": "pdate", "stored": True, "indexed": True, "multiValued": False},
    {"name": "fulltext", "type": "text_de", "stored": False, "indexed": True, "multiValued": False, "termVectors": True},
    {"name": "fulltext_alternative", "type": "text_de_custom", "stored": False, "indexed": True, "multiValued": False},
]

COPY_FIELDS = [{"source": "fulltext", "dest": "fulltext_alternative"}]

def get_existing_field_type_names(solr_core_url: str) -> set:
    """Gibt die Namen aller bereits vorhandenen Feldtypen zurück."""
     # timeout=30: Nach 30 Sekunden ohne Antwort bricht requests ab (z. B. wenn Solr nicht läuft).
    resp = requests.get(f"{solr_core_url}/schema/fieldtypes", timeout=30)
     # Bei HTTP-Fehlern (z. B. 404, wenn der Core nicht existiert) wird eine Exception ausgelöst.
    resp.raise_for_status()
    # Antwortaufbau: {"fieldTypes": [{"name": "string", ...}, ...]}
    # Die Set-Comprehension sammelt nur die Namen.
    return {t["name"] for t in resp.json().get("fieldTypes", [])}

def get_existing_field_names(solr_core_url: str) -> set:
    """Gibt die Namen aller bereits vorhandenen Felder zurück."""
    resp = requests.get(f"{solr_core_url}/schema/fields", timeout=30)
    resp.raise_for_status()
    fields = resp.json().get("fields", [])
    return {f["name"] for f in fields}

def get_existing_copy_fields(solr_core_url: str) -> set:
    """Gibt alle vorhandenen Copy-Fields als Menge von (Quelle, Ziel)-Paaren zurück."""
    resp = requests.get(f"{solr_core_url}/schema/copyfields", timeout=30)
    resp.raise_for_status()
    return {(c["source"], c["dest"]) for c in resp.json().get("copyFields", [])}

def create_schema(solr_core_url: str = SOLR_CORE_URL) -> None:
    """Legt fehlende Feldtypen, Felder und Copy-Fields an.
 
    Die Reihenfolge ist wichtig: Felder brauchen ihre Feldtypen, Copy-Fields
    brauchen Quell- und Zielfeld. Bereits vorhandene Elemente werden übersprungen,
    mehrfaches Ausführen ist unproblematisch.
    Es wird allerdings nur der Name geprüft, nicht die Definition.
    """
    # 1. Feldtypen: nur die anlegen, die noch fehlen.
    existing_types = get_existing_field_type_names(solr_core_url)
    new_types = [t for t in FIELD_TYPES if t["name"] not in existing_types]
    if new_types:
        resp = requests.post(f"{solr_core_url}/schema", json={"add-field-type": new_types}, timeout=30)
        resp.raise_for_status()
        print(f"{len(new_types)} Feldtyp(en) angelegt: {[t['name'] for t in new_types]}")
    else:
        print("Alle Feldtypen sind bereits vorhanden.")

    # 2. Felder: nur fehlende anlegen (benötigt die Feldtypen aus Schritt 1).
    existing_fields = get_existing_field_names(solr_core_url)
    new_fields = [f for f in FIELDS if f["name"] not in existing_fields]
    if new_fields:
        resp = requests.post(f"{solr_core_url}/schema", json={"add-field": new_fields}, timeout=30)
        resp.raise_for_status()
        print(f"{len(new_fields)} Feld(er) angelegt: {[f['name'] for f in new_fields]}")
    else:
        print("Alle Felder sind bereits im Schema vorhanden.")

    # 3. Copy-Fields: nur fehlende (Quelle, Ziel)-Paare anlegen (benötigt die Felder aus Schritt 2).
    existing_copy_fields = get_existing_copy_fields(solr_core_url)
    new_copy_fields = [
        c for c in COPY_FIELDS if (c["source"], c["dest"]) not in existing_copy_fields
    ]
    if new_copy_fields:
        resp = requests.post(f"{solr_core_url}/schema", json={"add-copy-field": new_copy_fields}, timeout=30)
        resp.raise_for_status()
        print(f"{len(new_copy_fields)} Copy-Field(s) angelegt: {new_copy_fields}")
    else:
        print("Alle Copy-Fields sind bereits vorhanden.")

# Skript nur ausführen, wenn es direkt gestartet wird
if __name__ == "__main__":
    create_schema()
