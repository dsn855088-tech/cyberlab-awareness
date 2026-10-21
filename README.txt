CYBERLAB AWARENESS DEMO + INVESTIGATOR DASHBOARD

Features:
- Fictional social-engineering awareness flow.
- Participant username/password fields are never read by JavaScript or sent to the server.
- Consent is required before generic event logging.
- Investigator dashboard at /investigator, protected by an ADMIN_PASSWORD environment variable.
- Dashboard auto-refreshes every 3 seconds and displays event type, timestamp, and a random anonymous session ID.
- No participant names, emails, IP addresses, or credentials are intentionally recorded by this app.
- Recent events are held in memory (maximum 500) and disappear when the service restarts/redeploys. Admin login sessions are also in memory.

SETUP ON RENDER:
1. In Render, open the cyberlab-awareness Web Service.
2. Open Environment (or Settings > Environment Variables).
3. Add environment variable:
   Key: ADMIN_PASSWORD
   Value: choose a long, unique password and keep it private.
4. Save changes and redeploy if prompted.
5. Open https://YOUR-SERVICE.onrender.com/investigator and sign in with that password.

PARTICIPANT URL:
https://YOUR-SERVICE.onrender.com/

INVESTIGATOR URL:
https://YOUR-SERVICE.onrender.com/investigator

LOCAL RUN:
python app.py
open http://127.0.0.1:8000
For local dashboard access, set ADMIN_PASSWORD in your terminal environment before running app.py.

PRIVACY / LIMITATIONS:
- Use only with informed, consenting participants.
- The demo fields are not real authentication; never enter real credentials.
- The app accepts only generic event type, consent flag, and random anonymous session ID. It ignores username/password fields and does not log request bodies.
- The dashboard is password-protected. Use a strong unique ADMIN_PASSWORD and do not share it.
- This is a learning demo, not a production-grade security or evidence-management system. The built-in Python HTTP server and in-memory event store are intentionally simple. Events may be lost on restart and are not a durable forensic record.
- Hosting platform infrastructure may maintain its own operational/security logs outside this app's event data.
