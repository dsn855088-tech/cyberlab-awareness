from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse
from http.cookies import SimpleCookie
from collections import deque
import json, secrets, datetime, os, re, hmac

ROOT=Path(__file__).resolve().parent
STATIC=ROOT/"static"
events=deque(maxlen=500)
sessions={}
TTL=8*60*60
ALLOWED={"demo_started","lesson_completed"}

def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")

def send(h,status,body,ctype="text/html; charset=utf-8",headers=None):
    h.send_response(status)
    h.send_header("Content-Type",ctype)
    h.send_header("Cache-Control","no-store")
    h.send_header("X-Content-Type-Options","nosniff")
    h.send_header("Referrer-Policy","no-referrer")
    h.send_header("Content-Security-Policy","default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; connect-src 'self'; base-uri 'none'; frame-ancestors 'none'")
    for k,v in (headers or []): h.send_header(k,v)
    h.end_headers(); h.wfile.write(body)

def jsend(h,status,obj,headers=None):
    return send(h,status,json.dumps(obj).encode(),"application/json; charset=utf-8",headers)

def readbody(h):
    n=int(h.headers.get("Content-Length","0"))
    if n<1 or n>4096: raise ValueError()
    return json.loads(h.rfile.read(n).decode())

def cookie(h):
    c=SimpleCookie()
    try:
        c.load(h.headers.get("Cookie",""))
        return c["cyberlab_admin"].value if "cyberlab_admin" in c else ""
    except Exception: return ""

def admin(h):
    t=cookie(h); exp=sessions.get(t)
    if not t or not exp: return False
    if exp < datetime.datetime.now(datetime.timezone.utc).timestamp():
        sessions.pop(t,None); return False
    return True

class H(BaseHTTPRequestHandler):
    def do_GET(self):
        p=urlparse(self.path).path
        static={" /":"participant.html","/":"participant.html","/lesson":"lesson.html","/styles.css":"styles.css","/app.js":"app.js"}
        if p in static:
            f=static[p]; typ="text/css; charset=utf-8" if f.endswith(".css") else "text/javascript; charset=utf-8" if f.endswith(".js") else "text/html; charset=utf-8"
            return send(self,200,(STATIC/f).read_bytes(),typ)
        if p=="/investigator":
            return send(self,200,(STATIC/("investigator.html" if admin(self) else "admin_login.html")).read_bytes())
        if p=="/investigator.js":
            if not admin(self): return send(self,401,b"Unauthorized","text/plain")
            return send(self,200,(STATIC/"investigator.js").read_bytes(),"text/javascript; charset=utf-8")
        if p=="/api/admin/events":
            if not admin(self): return jsend(self,401,{"error":"Sign in required"})
            rows=list(events)
            return jsend(self,200,{"events":rows,"counts":{"demo_started":sum(e["event_type"]=="demo_started" for e in rows),"lesson_completed":sum(e["event_type"]=="lesson_completed" for e in rows)}})
        return send(self,404,b"Not found","text/plain")
    def do_POST(self):
        p=urlparse(self.path).path
        try: data=readbody(self)
        except Exception: return jsend(self,400,{"error":"Invalid request"})
        if p=="/api/event":
            if data.get("consent") is not True: return jsend(self,400,{"error":"Consent required"})
            typ=data.get("event_type"); name=data.get("participant_name"); code=data.get("participant_code"); aid=data.get("anon_id")
            if typ not in ALLOWED or not isinstance(name,str) or not isinstance(code,str) or not re.fullmatch(r"[a-f0-9-]{16,40}",aid if isinstance(aid,str) else ""):
                return jsend(self,400,{"error":"Invalid event details"})
            name=" ".join(name.strip().split())[:80]; code=" ".join(code.strip().split())[:40]
            if not name or not code: return jsend(self,400,{"error":"Name and participant code required"})
            # Explicit allowlist: demo username/password fields are never accepted or stored.
            events.append({"time":now(),"event_type":typ,"participant_name":name,"participant_code":code,"anon_id":aid[:40]})
            return jsend(self,201,{"ok":True})
        if p=="/admin/login":
            configured=os.environ.get("ADMIN_PASSWORD",""); supplied=data.get("password","")
            if not configured: return jsend(self,503,{"error":"Admin password is not configured in Render Environment."})
            if not isinstance(supplied,str) or not hmac.compare_digest(supplied,configured): return jsend(self,401,{"error":"Incorrect administrator password"})
            token=secrets.token_urlsafe(32); sessions[token]=datetime.datetime.now(datetime.timezone.utc).timestamp()+TTL
            secure="; Secure" if os.environ.get("RENDER")=="true" else ""
            return jsend(self,200,{"ok":True},[("Set-Cookie",f"cyberlab_admin={token}; HttpOnly; SameSite=Strict; Path=/; Max-Age={TTL}{secure}")])
        if p=="/admin/logout":
            sessions.pop(cookie(self),None); secure="; Secure" if os.environ.get("RENDER")=="true" else ""
            return jsend(self,200,{"ok":True},[("Set-Cookie","cyberlab_admin=; HttpOnly; SameSite=Strict; Path=/; Max-Age=0"+secure)])
        return jsend(self,404,{"error":"Not found"})
    def log_message(self,fmt,*args): pass

if __name__=="__main__":
    port=int(os.environ.get("PORT","8000")); host="0.0.0.0" if os.environ.get("RENDER")=="true" else "127.0.0.1"
    print(f"CyberLab listening on {host}:{port}")
    ThreadingHTTPServer((host,port),H).serve_forever()
