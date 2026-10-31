"""
Lädt auf Basis der E-Book-IDs (aus der Textdatei ebook_ids.txt) die UTF-8-codierten
Volltexte der E-Books herunter und speichert sie im Verzeichnis fulltexts.
Die heruntergeladenen Volltextdateien erhalten den Namen <ebook_id>.txt.

Am Ende des Programms werden die Anzahl der erfolgreich heruntergeladenen
Volltextdateien sowie die Fehler (TXT-Datei konnte nicht gefunden / heruntergeladen
werden) auf der Konsole ausgegeben. Zusätzlich wird die Anzahl der übersprungenen
(bereits vorhandenen) Dateien ausgegeben.

Nach einer Unterbrechung hilft das bei der Überprüfung, ob alle Dateien
heruntergeladen wurden:
Anzahl heruntergeladener Dateien + übersprungene Dateien + Fehler = Die Anzahl vo E-Books IDs (beim Testen 2453)

authors: Beata Lakeberg, Christin Seegert, Elena Torlopova, Martina Schildt
license: MIT License
version: 1.0
date: 2026-10-27
"""

import requests
import os
import time

def download_file(url, filename):

    # zwischen 0.5 und 2 Sekunden zufällig warten
    time.sleep(0.5 + 1.5 * (os.urandom(1)[0] / 255))

    try:
        response = requests.get(url, timeout=60)
    except requests.RequestException as e:
        print(f"Fehler bei {url}: {e}")
        return False


    if response.status_code == requests.codes.ok:
        #with open(filename, "w", encoding="utf-8") as file:
        with open(filename, "wb") as file:
            file.write(response.content)
        print(f"Datei erfolgreich heruntergeladen und gespeichert unter {filename}")
        return True

    print(f"Fehler beim Herunterladen der Datei von URL {url}: {response.status_code}")
    return False


if __name__ == "__main__":
    base_dir = "fulltexts"
    os.makedirs(base_dir, exist_ok=True)

    num_of_downloads = 0
    num_of_skipped = 0
    failed_ids= []

    #ebook_ids.txt Datei  wird gelesen und aus jeder Zeile wird eine saubere E-Book-ID gemacht. Leere Zeilen werden übersprungen.
    with open("ebook_ids.txt", "r", encoding="utf-8") as file:
        for line in file:
            ebook_id = line.strip()
            if not ebook_id:
                continue

            # Es wird der Pfad aufgebaut, unter dem die heruntergeladene Datei gespeichert werden
            output_file = os.path.join(base_dir, f"{ebook_id}.txt")
            # Dateien, die bereits vorhanden und nicht leer sind, überspringen.
            if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
                num_of_skipped += 1 #zusätzlicher Zähler, wenn man Programm neu startet nach Unterbrechung.
                continue

            #Herunterladen und Mitzählen
            url = f"https://www.gutenberg.org/ebooks/{ebook_id}.txt.utf-8"
            print(f"Herunterladen der Textdatei von {url}")
            if download_file(url, output_file):
                num_of_downloads += 1
            else:
                failed_ids.append(ebook_id)


    print(f"Insgesamt {num_of_downloads} Volltextdateien erfolgreich heruntergeladen.")
    print(f"{num_of_skipped} Dateien waren bereits vorhanden und wurden übersprungen.")
    print(f"{len(failed_ids)} Fehler (keine TXT-Datei gefunden / Download fehlgeschlagen):")
    for ebook_id in failed_ids:
        print(f"  - {ebook_id}") #die E-Books IDs von Fehlern.