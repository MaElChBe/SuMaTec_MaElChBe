# Anmerkungen zum Aufgabe 2 und 3

Nachdem Aufgabe 2 erledigt war und die txt-Dateien heruntergeladen worden waren, wurde kontrolliert, ob es leere Dateien gibt. Es gab keine leeren Dateien.

Nachdem jedoch Programm 03 (03_filter-works.py) durchgelaufen war, erschien in fünf Fällen die Meldung, dass kein Startmarker gefunden wurde.

Es handelte sich um die Dateien mit den IDs 31660, 36779, 43987, 43932 und 43931.

Bei der Durchsicht dieser Dateien zeigte sich, dass die _filtered.txt-Dateien leer waren und die .txt-Dateien lediglich folgenden Text enthielten:

“We apologize for this inconvenience. Your IP address has been automatically blocked from accessing specific eBook files at www.gutenberg.org. This is because the geoIP database shows your address is in the country of Germany.
The block applies to books by author Alfred D�blin (until January 1, 2028). No other Project Gutenberg eBooks, by any author, are blocked in Germany.
For more information, visit <a href="https://cand.pglaf.org/germany">cand.pglaf.org/germany</a>.”

Diese Sperrung erfolgte aufgrund des Rechtsstreits zwischen Project Gutenberg und dem S. Fischer Verlag.

Die Dateien wurden zunächst nicht als leer oder fehlerhaft erkannt, weil es sich um gültige txt-Dateien handelte. Sie enthielten jedoch keinen Buchtext, sondern nur einen Hinweis auf die Sperrung.

Um diesen Fehler zu beheben, wurde das Skript 02_fetch-works.py um eine Funktion ergänzt, die prüft, ob die heruntergeladene Datei tatsächlich Buchtext enthält und nicht nur den Sperrhinweis. Außerdem mussten die fünf .txt-Dateien manuell gelöscht werden. Nach einem erneuten Start von Programm 02 wurden diese fünf Dateien als fehlerhaft gekennzeichnet. Der erneute Start von Programm 03 führte diesmal zu keinen Fehlermeldungen.
