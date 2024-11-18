import re

# Datei einlesen
with open("WS2024-2025.dat", "r", encoding="utf-8") as file:
    data = file.read()

# Einträge blockweise aufteilen
blocks = re.split(r"\n\s*\{\s*", data)
blocks = [block.strip().rstrip("}") for block in blocks if block.strip()]

# Liste für die Dictionaries initialisieren
entries = []

# Jeden Block parsen und in ein Dictionary umwandeln
for block in blocks:
    entry = {}
    # Zeilenweise splitten und key-value Paare extrahieren
    for line in block.splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"')
            
            # Falls mehrere Werte in einer Zeile vorhanden sind, splitten
            if '"' in line and line.count('"') > 2:
                value = re.findall(r'"([^"]*)"', line)
            
            entry[key] = value

    entries.append(entry)

# Ausgabe zur Kontrolle
for entry in entries:
    print(entry)
