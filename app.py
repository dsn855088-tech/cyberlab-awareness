from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse
from http.cookies import SimpleCookie
from collections import deque
import json, secrets, datetime, os, re, hmac

ROOT = Path(__file__).resolve().parent
STATIC = ROOT / "static"
MAX_BODY = 4096
EVENT_TYPES = {"demo_started", "training_reveal"}
SESSION_TTL_SECONDS = 8 * 60 * 60
events = deque(maxlen=500)
admin_sessions = {}  # in-memory only; lost when the service restarts

def utc_now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")

def respond(h, status, data, content_type="text/html; charset=utf-8", extra_headers=None):
    h.send_response(status)
    h.send_header("Content-Type", content_type)
    h.send_header("Cache-Control", "no-store")
    h.send_header("X-Content-Type-Options", "nosniff")
    h.send_header("Referrer-Policy", "no-referrer")
    h.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; connect-src 'self'; base-uri 'none'; frame-ancestors 'none'; form-action 'self'")
    if extra_headers:
        for key, value in extra_headers:
            h.send_header(key, value)
    h.end_headers()
    h.wfile.write(data)

def json_response(h, status, obj):
    return respond(h, status, json.dumps(obj).encode("utf-8"), "application/json; charset=utf-8")

def read_json(h):
    length = int(h.headers.get("Content-Length", "0"))
    if length < 1 or length > MAX_BODY:
        raise ValueError("bad length")
    return json.loads(h.rfile.read(length).decode("utf-8"))

def admin_cookie(h):
    cookie = SimpleCookie()
    try:
        cookie.load(h.headers.get("Cookie", ""))
        return cookie["cyberlab_admin"].value if "cyberlab_admin" in cookie else ""
    except Exception:
        return ""

def is_admin(h):
    token = admin_cookie(h)
    expiry = admin_sessions.get(token)
    if not token or not expiry:
        return False
    if expiry < datetime.datetime.now(datetime.timezone.utc).timestamp():
        admin_sessions.pop(token, None)
        return False
    return True

def html_file(name):
    return (STATIC / name).read_bytes()

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/":
            return respond(self, 200, html_file("participant.html"))
        if path == "/lesson":
            return respond(self, 200, html_file("lesson.html"))
        if path == "/styles.css":
            return respond(self, 200, html_file("styles.css"), "text/css; charset=utf-8")
        if path == "/app.js":
            return respond(self, 200, html_file("app.js"), "text/javascript; charset=utf-8")
        if path == "/investigator":
            if not is_admin(self):
                return respond(self, 200, html_file("admin_login.html"))
            return respond(self, 200, html_file("investigator.html"))
        if path == "/investigator.js":
            if not is_admin(self):
                return respond(self, 401, b"Unauthorized", "text/plain; charset=utf-8")
            return respond(self, 200, html_file("investigator.js"), "text/javascript; charset=utf-8")
        if path == "/api/admin/events":
            if not is_admin(self):
                return json_response(self, 401, {"error": "Sign in required"})
            rows = list(events)
            counts = {
                "demo_started": sum(1 for e in rows if e["event_type"] == "demo_started"),
                "training_reveal": sum(1 for e in rows if e["event_type"] == "training_reveal"),
            }
            return json_response(self, 200, {"events": rows, "counts": counts, "limit": 500})
        return respond(self, 404, b"Not found", "text/plain; charset=utf-8")

    def do_POST(self):
        path = urlparse(self.path).path
        if path == "/api/event":
            try:
                payload = read_json(self)
            except Exception:
                return json_response(self, 400, {"error": "Invalid request"})
            # Accept only consent, event_type, and a random anonymous session identifier.
            # Username/password fields are never read, stored, or written to logs.
            if payload.get("consent") is not True or payload.get("event_type") not in EVENT_TYPES:
                return json_response(self, 400, {"error": "Training acknowledgement required"})
            anon_id = payload.get("anon_id", "")
            if not isinstance(anon_id, str) or not re.fullmatch(r"[a-f0-9-]{16,40}", anon_id):
                return json_response(self, 400, {"error": "Invalid anonymous session ID"})
            events.append({
                "time": utc_now(),
                "event_type": payload["event_type"],
                "anon_id": anon_id[:40],
            })
            return json_response(self, 201, {"ok": True})
        if path == "/admin/login":
            try:
                payload = read_json(self)
            except Exception:
                return json_response(self, 400, {"error": "Invalid request"})
            configured = os.environ.get("ADMIN_PASSWORD", "")
            supplied = payload.get("password", "")
            if not configured:
                return json_response(self, 503, {"error": "Administrator access is not configured. Set ADMIN_PASSWORD in Render Environment."})
            if not isinstance(supplied, str) or not hmac.compare_digest(supplied, configured):
                return json_response(self, 401, {"error": "Incorrect administrator password"})
            token = secrets.token_urlsafe(32)
            admin_sessions[token] = datetime.datetime.now(datetime.timezone.utc).timestamp() + SESSION_TTL_SECONDS
            secure = "; Secure" if os.environ.get("RENDER") == "true" else ""
            return json_response(self, 200, {"ok": True}, extra_headers=[
                ("Set-Cookie", f"cyberlab_admin={token}; HttpOnly; SameSite=Strict; Path=/; Max-Age={SESSION_TTL_SECONDS}{secure}")
            ])
        if path == "/admin/logout":
            token = admin_cookie(self)
            admin_sessions.pop(token, None)
            secure = "; Secure" if os.environ.get("RENDER") == "true" else ""
            return json_response(self, 200, {"ok": True}, extra_headers=[
                ("Set-Cookie", f"cyberlab_admin=; HttpOnly; SameSite=Strict; Path=/; Max-Age=0{secure}")
            ])
        return json_response(self, 404, {"error": "Not found"})

    def log_message(self, fmt, *args):
        # Do not write request bodies or routine URLs to logs.
        pass

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8000"))
    host = "0.0.0.0" if os.environ.get("RENDER") == "true" else "127.0.0.1"
    print(f"CyberLab listening on {host}:{port}")
    print("Only generic consented events are stored in memory. No credentials are accepted or logged.")
    ThreadingHTTPServer((host, port), Handler).serve_forever()
