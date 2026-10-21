CYBERLAB HOSTED AWARENESS DEMO

This is a fictional, consent-based social-engineering awareness lesson.
The username/password inputs are never read by JavaScript and are never sent
to the server. The server accepts only generic training event types and keeps
only aggregate counters in memory. It does not expose an event-log endpoint.

LOCAL RUN:
  python app.py
  open http://127.0.0.1:8000

HOSTING:
This package is prepared for Render. The app reads Render's PORT variable and
binds to 0.0.0.0 only when running on Render. Upload the contents to a GitHub
repository, then create a Render Web Service connected to that repository.
Use Build Command: echo No external dependencies
Use Start Command: python app.py
Render provides HTTPS on its onrender.com URL.

Privacy notes:
- Use only with informed, consenting participants.
- Never ask for or enter real credentials or personal information.
- Generic event counts are in memory only and are not persisted.
- Public hosting means anyone with the URL can open the lesson. Share only
  in an appropriate training context. For restricted audiences, add an
  access-code gate before distributing the URL.
- This is an educational demo, not a real authentication system.
