#!/usr/bin/env python3
"""Den Instagram-Token erneuern. Gehoert in einen woechentlichen Cron-Job.

Warum woechentlich und nicht alle 59 Tage: Der Token ist 60 Tage gueltig und
laesst sich nur erneuern, solange er noch lebt. Meta ist da eindeutig --
"Tokens that have not been refreshed in 60 days will expire and can no longer
be refreshed." Ein abgelaufener Token ist endgueltig verloren; dann muss im
Meta-App-Dashboard von Hand ein neuer erzeugt werden.

Bei woechentlichem Lauf darf der Job also siebenmal hintereinander scheitern,
bevor ueberhaupt etwas kaputtgeht. Bei monatlichem Lauf reichen zwei Ausfaelle.

Einrichtung auf www2 (App laeuft als www-data):

    sudo mkdir -p /var/lib/mi-news
    sudo chown www-data: /var/lib/mi-news
    sudo chmod 700 /var/lib/mi-news
    # .netrc und ig_token.json dort ablegen, mode 600, owner www-data

    # /etc/cron.d/mi-news-token
    17 3 * * 1 www-data /usr/local/lib/mi-news/venv/bin/python \
        /usr/local/lib/mi-news/bin/refresh_ig_token.py >> /var/log/mi-news-token.log 2>&1

Exit-Codes: 0 = erneuert, 1 = Fehler (Cron schickt dann eine Mail).
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timezone

from misc import instagram as ig
from misc.config import ig_token_file


def main():
    vorher = ig.token_restlaufzeit()
    if vorher is None:
        print(f"FEHLER: Kein Token in {ig_token_file}.", file=sys.stderr)
        print("Einmalig im Meta-App-Dashboard erzeugen und dort ablegen.",
              file=sys.stderr)
        return 1

    if vorher < 0:
        print(f"FEHLER: Token seit {-vorher} Tagen abgelaufen und nicht mehr "
              f"erneuerbar. Im Meta-App-Dashboard einen neuen erzeugen.",
              file=sys.stderr)
        return 1

    try:
        daten = ig.refresh_token()
    except Exception as e:
        print(f"FEHLER beim Erneuern: {e}", file=sys.stderr)
        print(f"Token laeuft noch {vorher} Tage. Bis dahin kann der Job erneut "
              f"laufen; danach ist der Token verloren.", file=sys.stderr)
        return 1

    nachher = ig.token_restlaufzeit()
    jetzt = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")
    print(f"{jetzt}  Token erneuert: {vorher} -> {nachher} Tage Restlaufzeit.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
