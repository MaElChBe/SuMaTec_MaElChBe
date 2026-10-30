import os

def read_text(path):
    """Liest eine Textdatei als UTF-8, bei Fehlern als Latin-1 (Windows-1252) ein."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read().splitlines(keepends=True)
    except UnicodeDecodeError:
        with open(path, "r", encoding="cp1252", errors="replace") as f:
            return f.read().splitlines(keepends=True)

def extract_gutenberg_text(input_file, output_file):
    """
    Extrahiert den Text zwischen '*** START … ***' und '*** END … ***' aus einer
    E-Book-Textdatei vom Project Gutenberg (ohne Header und Footer) und speichert
    ihn in einer neuen Textdatei.

    Die Originaldatei wird als UTF-8 gelesen, bei Dekodierungsfehlern als
    Windows-1252. Die Ausgabedatei wird immer als UTF-8 geschrieben.

    Parameter:
    - input_file (str): Pfad zur Originaldatei (<ebook_id>.txt).
    - output_file (str): Pfad zur bereinigten Ausgabedatei (<ebook_id>_filtered.txt).

    Gibt eine Meldung aus, wenn Start- oder End-Marker fehlen.

    authors: Beata Lakeberg, Christin Seegert, Martina Schildt, Elena Torlopova
    license: MIT License
    version: 1.0
    date: 2026-10-29
    """
    start_marker = "*** START OF THE PROJECT GUTENBERG EBOOK "
    end_marker = "*** END OF THE PROJECT GUTENBERG EBOOK "
    inside_text = False   # Start-Marker gefunden, wir sind im Buchtext
    end_found = False     # End-Marker gefunden


    # Originaldatei einlesen (UTF-8, bei Fehlern Windows-1252) und in Zeilen aufteilen
    lines = read_text(input_file)

    # Zeilen durchlaufen, Text zwischen Start- und End-Marker in die Ausgabedatei schreiben
    with open(output_file, "w", encoding="utf-8") as outfile:
        for line in lines:
            if line.startswith(start_marker):
                inside_text = True  # Start-Marker gefunden → Ab jetzt den Inhalt aus dem E-Book aufsammeln
                continue
            if line.startswith(end_marker):
                end_found = True
                break # Ende-Marker gefunden → Den weiteren Inhalt der Textdatei ignorieren
            if inside_text:
                outfile.write(line)  # relevanter Text für die Ausgabedatei

    if inside_text and end_found:
        print(f"Extrahierter Text wurde gespeichert in: {output_file}")
    elif not inside_text:
        print(f"Kein Start-Marker gefunden in: {input_file}.")
    else:
        print(f"Kein End-Marker gefunden in: {input_file}. Der Text wurde bis zum Dateiende übernommen.")

if __name__ == "__main__":
    input_dir = "fulltexts"
    # Alle Originaldateien (<ebook_id>.txt) im Volltextverzeichnis verarbeiten,
    # bereits gefilterte Dateien (<ebook_id>_filtered.txt) überspringen
    num_of_files_processed = 0 # Zähler für die verarbeiteten Dateien
    
    for filename in os.listdir(input_dir):
        if filename.endswith(".txt") and not filename.endswith("_filtered.txt"):
            num_of_files_processed += 1
            input_file = os.path.join(input_dir, filename)
            output_file = os.path.join(input_dir, filename.replace(".txt", "_filtered.txt"))
            extract_gutenberg_text(input_file, output_file)

    print(f"{num_of_files_processed} Dateien verarbeitet.")