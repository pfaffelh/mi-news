#!/usr/bin/env python3
"""Den initialen Instagram-Long-Lived-Token ablegen (einmalige Einrichtung).

Der Refresh-Job (bin/refresh_ig_token.py) ERNEUERT nur einen vorhandenen Token;
den ERSTEN Token muss man von Hand aus dem Meta-App-Dashboard holen und hiermit
ablegen. Danach uebernimmt der woechentliche Cron.

Token-Quelle (in dieser Reihenfolge):
  1. Datei als Argument:  set_ig_token.py <datei>
     Die Datei darf ENTWEDER der rohe Token sein ODER eine ig_token.json
     (dann wird das Feld access_token herausgezogen -- praktisch, um eine lokal
     erzeugte ig_token.json 1:1 nach www2 zu kopieren und hier einzuspielen).
  2. sonst stdin:         printf '%s' '<TOKEN>' | set_ig_token.py

Geschrieben wird nach misc.config.ig_token_file (auf www2:
/var/lib/mi-news/ig_token.json), mode 600, im selben Format wie der Refresh-Job.

Sicherung: Ein bereits vorhandener, noch gueltiger Token wird NICHT ohne --force
ueberschrieben -- sonst wuerde ein Deploy/Fehlgriff den vom Cron frisch rotierten
Token durch einen aelteren ersetzen.

Aufruf als der User, der die App ausfuehrt (auf www2: www-data), damit die Datei
diesem gehoert, z. B.:

    printf '%s' '<TOKEN>' | sudo -u www-data \\
        /usr/local/lib/mi-news/venv/bin/python \\
        /usr/local/lib/mi-news/bin/set_ig_token.py

Exit-Codes: 0 = abgelegt, 1 = Fehler / nichts geaendert.
"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from misc import instagram as ig
from misc.config import ig_token_file

# 60 Tage in Sekunden -- so lange ist ein frisch erzeugter Long-Lived Token gueltig.
LEBENSDAUER = 60 * 24 * 3600


def token_lesen(quelle):
    """Token aus Datei (Argument) oder stdin lesen. Akzeptiert rohen Token oder
    eine ig_token.json (dann access_token herausziehen)."""
    if quelle:
        with open(quelle, encoding="utf-8") as f:
            roh = f.read()
    else:
        roh = sys.stdin.read()
    roh = roh.strip()
    if not roh:
        return None
    if roh.startswith("{"):          # sieht nach ig_token.json aus
        try:
            return (json.loads(roh).get("access_token") or "").strip() or None
        except ValueError:
            return None
    return roh


def main():
    ap = argparse.ArgumentParser(description="Initialen Instagram-Token ablegen.")
    ap.add_argument("datei", nargs="?",
                    help="Datei mit rohem Token oder ig_token.json (sonst stdin)")
    ap.add_argument("--force", action="store_true",
                    help="vorhandenen, noch gueltigen Token ueberschreiben")
    args = ap.parse_args()

    rest = ig.token_restlaufzeit()
    if rest is not None and rest >= 0 and not args.force:
        print(f"Es liegt bereits ein gueltiger Token in {ig_token_file} "
              f"({rest} Tage Restlaufzeit). Zum Ueberschreiben --force nutzen.",
              file=sys.stderr)
        return 1

    token = token_lesen(args.datei)
    if not token:
        print("Kein Token gelesen (leere Eingabe oder kein access_token in der "
              "JSON).", file=sys.stderr)
        return 1

    ig.speichere_token(token, LEBENSDAUER)
    print(f"Token abgelegt in {ig_token_file} — Restlaufzeit "
          f"{ig.token_restlaufzeit()} Tage.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
