
#!/usr/bin/env python3
import json
import os
import time
import urllib.parse
import urllib.request
import urllib.error

from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from datetime import date

BASE = "https://api.schiphol.nl/public/public-flights/v4"
TOKEN_URL = "https://api.auth.schiphol.nl/oauth/token"

_token = None
_expires = 0


def config():
    client_id = os.environ.get("SCHIPHOL_CLIENT_ID")
    client_secret = os.environ.get("SCHIPHOL_CLIENT_SECRET")

    if not client_id or not client_secret:
        raise RuntimeError("Schiphol API-gegevens ontbreken.")

    return {
        "client_id": client_id,
        "client_secret": client_secret
    }


def get_token(cfg):
    global _token, _expires

    if _token and time.time() < _expires - 60:
        return _token

    body = urllib.parse.urlencode({
        "grant_type": "client_credentials",
        "client_id": cfg["client_id"],
        "client_secret": cfg["client_secret"],
        "audience": "https://api.schiphol.nl/public"
    }).encode()

    req = urllib.request.Request(
        TOKEN_URL,
        data=body,
        headers={
            "Content-Type": "application/x-www-form-urlencoded"
        }
    )

    with urllib.request.urlopen(req, timeout=20) as res:
        payload = json.loads(res.read().decode())

    _token = payload["access_token"]
    _expires = time.time() + int(payload.get("expires_in", 1800))

    return _token


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            directory=str(Path(__file__).parent),
            **kwargs
        )

    def do_GET(self):
        if self.path.startswith("/api/flights"):
            try:
                cfg = config()

                q = urllib.parse.parse_qs(
                    urllib.parse.urlparse(self.path).query
                )

                day = q.get("date", [date.today().isoformat()])[0]

                token = get_token(cfg)
                all_flights = []

                for page_no in range(5):
                    url = BASE + "/flights?" + urllib.parse.urlencode({
                        "scheduleDate": day,
                        "flightDirection": "D",
                        "page": page_no
                    })

                    req = urllib.request.Request(
                        url,
                        headers={
                            "Authorization": "Bearer " + token,
                            "Accept": "application/json"
                        }
                    )

                    with urllib.request.urlopen(req, timeout=25) as res:
                        payload = json.loads(
                            res.read().decode("utf-8")
                        )

                    batch = payload.get("flights", [])
                    print("VOORBEELD VLUCHT:", json.dumps(batch[0], ensure_ascii=False) if batch else "Geen vluchten")
                    all_flights.extend(batch)

                    if len(batch) < 20:
                        break

                data = json.dumps({
                    "flights": all_flights
                
                }, ensure_ascii=False).encode("utf-8")

                self.send_response(200)
                self.send_header(
                    "Content-Type",
                    "application/json; charset=utf-8"
                )
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                self.wfile.write(data)

            except urllib.error.HTTPError as e:
                self.send_error(
                    e.code,
                    "Schiphol API-fout: HTTP " + str(e.code)
                )

            except Exception:
                self.send_error(500, "Er ging iets mis bij het ophalen van vluchten.")

            return

        return super().do_GET()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8000"))

    server = ThreadingHTTPServer(
        ("0.0.0.0", port),
        Handler
    )

    print("Amsteldam Airport is gestart op poort", port)

    server.serve_forever()
