"""
frontend/server.py - Agentic-PMPlus

Sehr kleiner, bewusst abhaengigkeitsfreier Entwicklungs-/Container-Server fuer das
Planer-Frontend (Python-Standardbibliothek, kein Node/npm-Build noetig - siehe
frontend/README.md fuer die Stack-Begruendung).

Aufgaben:
1. Statische Dateien aus public/ ausliefern (index.html, css/, js/).
2. Alles unter /api/* an das step7-active-learning-Backend weiterreichen (Proxy).

Warum ein Proxy statt CORS im Backend: Frontend und Backend laufen als getrennte
Docker-Services auf getrennten Ports (Architektur-Backend-Frontend-Schnittstelle.md
Abschnitt 1: "ein kuenftiger Frontend-Service braucht eine Port-Freigabe"). Der Browser
wuerde plain fetch()-Aufrufe an eine andere Origin per Same-Origin-Policy blockieren.
Statt dafuer step7-active-learning/api.py anzufassen (nicht die Aufgabe von
frontend-dev, siehe .claude/agents/role/frontend-dev.md, "Scope-Disziplin" -
Datenaggregation/Backend ist backend-dev-Verantwortung), macht dieser Server alle
Aufrufe fuer den Browser zu Same-Origin-Aufrufen: /api/eskalationen -> intern an
BACKEND_URL + /eskalationen weitergereicht. Kein einziges Byte Backend-Code angefasst.
"""

import json
import os
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

PUBLIC_DIR = Path(__file__).parent / "public"
BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8000").rstrip("/")
PORT = int(os.environ.get("PORT", "8080"))

# Sehr kleine, feste Mime-Type-Tabelle (kein Bedarf an einer Zusatz-Bibliothek).
MIME_TYPES = {
    ".html": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".js": "application/javascript; charset=utf-8",
    ".json": "application/json; charset=utf-8",
    ".svg": "image/svg+xml",
    ".ico": "image/x-icon",
}


class Handler(BaseHTTPRequestHandler):
    server_version = "PMPlusFrontend/1.0"

    def log_message(self, fmt, *args):
        print(f"[frontend] {self.address_string()} - {fmt % args}")

    def do_GET(self):
        if self.path.startswith("/api/"):
            self._proxy("GET")
        else:
            self._serve_static()

    def do_POST(self):
        if self.path.startswith("/api/"):
            self._proxy("POST")
        else:
            self.send_error(404, "Nicht gefunden")

    # -- Statische Dateien -------------------------------------------------
    def _serve_static(self):
        rel_path = self.path.split("?", 1)[0].lstrip("/")
        if rel_path == "":
            rel_path = "index.html"
        candidate = (PUBLIC_DIR / rel_path).resolve()

        # Verhindert Zugriff ausserhalb von public/ (z.B. ../server.py).
        if PUBLIC_DIR not in candidate.parents and candidate != PUBLIC_DIR:
            self.send_error(403, "Verboten")
            return
        if not candidate.exists() or not candidate.is_file():
            # SPA-Fallback: unbekannte Pfade (z.B. /order/ORD-1001 durch den
            # client-seitigen Hash-Router) liefern index.html aus.
            candidate = PUBLIC_DIR / "index.html"

        content_type = MIME_TYPES.get(candidate.suffix, "application/octet-stream")
        body = candidate.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    # -- API-Proxy -----------------------------------------------------
    def _proxy(self, method):
        backend_path = self.path[len("/api"):] or "/"
        target_url = BACKEND_URL + backend_path

        content_length = int(self.headers.get("Content-Length", 0) or 0)
        body = self.rfile.read(content_length) if content_length else None

        req = urllib.request.Request(target_url, data=body, method=method)
        if body is not None:
            req.add_header("Content-Type", self.headers.get("Content-Type", "application/json"))

        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                self._send_proxied_response(resp.status, resp.read(), resp.headers.get("Content-Type"))
        except urllib.error.HTTPError as exc:
            # Backend hat einen Fehlerstatus geliefert (z.B. 400 bei fehlender
            # Begruendung, TICKET-B05) - 1:1 an den Client durchreichen, damit
            # das Frontend echte Fehler sieht statt eines generischen 500ers.
            self._send_proxied_response(exc.code, exc.read(), exc.headers.get("Content-Type"))
        except (urllib.error.URLError, TimeoutError, ConnectionError) as exc:
            # Fail-safe statt fail-open (frontend-dev.md, Leitplanke 5): Backend
            # nicht erreichbar -> klarer 503 an den Client, NIE stillschweigend
            # leere/alte Daten vortaeuschen.
            payload = json.dumps({
                "error": "backend_unreachable",
                "detail": f"Backend unter {BACKEND_URL} nicht erreichbar: {exc}",
            }).encode("utf-8")
            self._send_proxied_response(503, payload, "application/json")

    def _send_proxied_response(self, status, body, content_type):
        self.send_response(status)
        self.send_header("Content-Type", content_type or "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def main():
    print("=== Agentic-PMPlus Frontend ===")
    print(f"Statische Dateien: {PUBLIC_DIR}")
    print(f"API-Proxy: /api/* -> {BACKEND_URL}")
    print(f"Server laeuft auf 0.0.0.0:{PORT}")
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()


if __name__ == "__main__":
    main()
