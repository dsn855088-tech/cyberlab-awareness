CYBERLAB CONSENT-BASED PARTICIPANT ACTIVITY DASHBOARD

Collects only after explicit consent:
- participant name
- participant code
- generic event type (demo_started or lesson_completed)
- UTC timestamp
- random anonymous session ID

Does NOT collect:
- text in demo username/password fields; client JavaScript never reads those fields and server accepts only allowlisted event fields.

Dashboard URL: /investigator
Set ADMIN_PASSWORD as an environment variable in Render. Keep it secret; do not commit it to GitHub.
Participant URL: /

The latest 500 events and administrator sessions are held in memory and may be lost on restart/redeploy. This is a teaching demo, not a durable evidence-management system. Use only with informed participants and collect names only where necessary.
