from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse
import json, secrets, datetime, os

ROOT = Path(__file__).resolve().parent
STATIC = ROOT / "static"
LOG = ROOT / "events.json"
MAX_BODY = 4096

def respond(h, status, data, content_type="text/html; charset=utf-8"):
    h.send_response(status)
    h.send_header("Content-Type", content_type)
    h.send_header("Cache-Control", "no-store")
    h.send_header("X-Content-Type-Options", "nosniff")
    h.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; connect-src 'self'; base-uri 'none'; frame-ancestors 'none'")
    h.end_headers()
    h.wfile.write(data)

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = urlparse(self.path).path
        routes = {"/": "participant.html", "/lesson": "lesson.html",
                  "/styles.css": "styles.css", "/app.js": "app.js"}
        if path not in routes:
            return respond(self, 404, b"Not found", "text/plain; charset=utf-8")
        name = routes[path]
        ctype = "text/css; charset=utf-8" if name.endswith(".css") else ("text/javascript; charset=utf-8" if name.endswith(".js") else "text/html; charset=utf-8")
        try:
            data = (STATIC / name).read_bytes()
        except OSError:
            return respond(self, 500, b"Project file missing", "text/plain; charset=utf-8")
        return respond(self, 200, data, ctype)

    def do_POST(self):
        if urlparse(self.path).path != "/api/event":
            return respond(self, 404, b'{"error":"Not found"}', "application/json; charset=utf-8")
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length < 1 or length > MAX_BODY:
                raise ValueError()
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
        except Exception:
            return respond(self, 400, b'{"error":"Invalid request"}', "application/json; charset=utf-8")
        if payload.get("consent") is not True or payload.get("event_type") not in ("demo_started", "training_reveal"):
            return respond(self, 400, b'{"error":"Training acknowledgement required"}', "application/json; charset=utf-8")
        # Deliberately accept no username/password fields and never log request bodies.
        # For this public demo, store only aggregate generic event counts in memory.
        if not hasattr(self.server, "event_counts"):
            self.server.event_counts = {"demo_started": 0, "training_reveal": 0}
        self.server.event_counts[payload["event_type"]] += 1
        event_id = secrets.token_hex(4)
        return respond(self, 201, json.dumps({"ok": True, "event_id": event_id}).encode(), "application/json; charset=utf-8")

    def log_message(self, fmt, *args):
        # Avoid routine request logging in console.
        pass

if __name__ == "__main__":
    # Render supplies PORT and requires a public-facing bind. Locally default to localhost.
    port = int(os.environ.get("PORT", "8000"))
    host = "0.0.0.0" if os.environ.get("RENDER") == "true" else "127.0.0.1"
    print(f"CyberLab awareness simulation listening on {host}:{port}")
    print("No username/password values are transmitted, accepted by the server, or stored.")
    ThreadingHTTPServer((host, port), Handler).serve_forever()
