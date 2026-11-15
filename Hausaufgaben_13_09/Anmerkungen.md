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

# Anmerkungen zur Bonusaufgabe

Beim Testen des Codes ist uns Folgendes aufgefallen:
In der Liste der „interessantesten Terme des Ausgangsdokuments“ erscheinen Terme, die im Originaltext nicht in dieser Form vorkommen.
+  Bsp. 1: Term `schlosskirch`. Im Text kommt nur das Wort "Schloßkirche" vor
+  Bsp. 2: Term `kurfurst`. Im Text - das Wort "Kurfürst"
Eine Textsuche nach diesen Termen im Ausgangsdokument bleibt deshalb erfolglos.

**Ursache für solche Ergebnisse**:
Die Ähnlichkeitssuche (MoreLikeThis) arbeitet nicht auf dem Originaltext, sondern auf den Index-Termen des verwendeten Feldes. Diese entstehen durch die Analysekette des Feldtyps. Das Feld `fulltext` verwendet eine Kette mit `GermanNormalizationFilter` (ß→ss, Umlautnormalisierung) und `GermanLightStemFilter`. 
+ Aus "Schloßkirche" wird zunächst `schlosskirche` und dann der Stamm `schlosskirch`.
+ Auch andere Wörter werden auf ihre Stammform reduziert (z. B. "Kirchen" und "Kirche zu kirch).
+ Aus "Kurfürst" -> `kurfurst`

**Vorteil**
Unterschiedliche Schreibweisen (z. B. „Schloßkirche“ und „Schlosskirche“) werden auf denselben Term abgebildet und zählen somit für die Ähnlichkeit gleich.

**Hinweis zum Feldtyp**
Wenn anstatt des Feldes `fulltext`, `fulltext_alternative` (Feldtyp `test_de_custom`: `LowerCase, Stop, GermanMinimalStem`) verwendet wird, wird aus "Schloßkirche" den Term `schloßkirch` erzeugt, da er das ß nicht normalisiert. Die Umlaute (ä, ö, ü) werden aber hier auch vereinfacht und aus "Kurfürst" wird den Term `kurfurst` ausgegeben.

Die Ergebnisse der Ähnlichkeitssuche hängen daher vom gewählten Feld ab. Für die Aufgabe ist deshalb festzulegen, welches Feld verwendet werden soll, und die ausgegebenen Terme sind entsprechend als Index-Terme dieses Feldes zu interpretieren.