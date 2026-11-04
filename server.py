#!/usr/bin/env python3
"""Local-only proxy for Schiphol PublicFlight API. Keeps secrets off the browser."""
import json, os, time, urllib.parse, urllib.request, urllib.error
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from datetime import date

BASE = "https://api.schiphol.nl/public/public-flights/v4"
TOKEN_URL = "https://api.auth.schiphol.nl/oauth/token"
CONFIG_PATH = Path(__file__).with_name("config.json")
_token, _expires = None, 0

def config():
    if not CONFIG_PATH.exists():
        raise RuntimeError("config.json ontbreekt. Kopieer config.example.json naar config.json en vul je gegevens in.")
    data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    if not data.get("client_id") or not data.get("client_secret"):
        raise RuntimeError("Vul client_id en client_secret in config.json in.")
    return data

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
    req = urllib.request.Request(TOKEN_URL, data=body, headers={"Content-Type":"application/x-www-form-urlencoded"})
    with urllib.request.urlopen(req, timeout=20) as res:
        payload = json.loads(res.read().decode())
    _token = payload["access_token"]
    _expires = time.time() + int(payload.get("expires_in", 1800))
    return _token

class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(Path(__file__).parent), **kwargs)

    def do_GET(self):
        if self.path.startswith("/api/flights"):
            try:
                cfg = config()
                q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
                day = q.get("date", [date.today().isoformat()])[0]
                page = q.get("page", ["0"])[0]
                token = get_token(cfg)
                all_flights = []
                # Schiphol returns at most 20 flights per page; collect up to 100.
                for page_no in range(5):
                    url = BASE + "/flights?" + urllib.parse.urlencode({
                        "scheduleDate": day, "flightDirection": "D", "page": page_no
                    })
                    req = urllib.request.Request(url, headers={
                        "Authorization": "Bearer " + token,
                        "Accept": "application/json"
                    })
                    with urllib.request.urlopen(req, timeout=25) as res:
                        payload = json.loads(res.read().decode("utf-8"))
                    batch = payload.get("flights", [])
                    all_flights.extend(batch)
                    if len(batch) < 20:
                        break
                data = json.dumps({"flights": all_flights}, ensure_ascii=False).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                self.wfile.write(data)
            except urllib.error.HTTPError as e:
                detail = e.read().decode("utf-8", "replace")
                self.send_error(e.code, "Schiphol API gaf HTTP " + str(e.code) + ": " + detail[:500])
            except Exception as e:
                self.send_error(500, str(e))
            return
        return super().do_GET()

    def log_message(self, fmt, *args):
        print("%s - %s" % (self.address_string(), fmt % args))

if __name__ == "__main__":
    print("Amsteldam Airport draait op http://127.0.0.1:8000")
    print("Alleen lokaal toegankelijk. Stoppen: Ctrl+C")
    ThreadingHTTPServer(("127.0.0.1", 8000), Handler).serve_forever()
