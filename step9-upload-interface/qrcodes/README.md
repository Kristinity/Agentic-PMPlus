# QR-Codes für die Live-Präsentation (2026-07-28)

- `github-repo-qrcode.png` – verlinkt auf `https://github.com/Kristinity/Agentic-PMPlus/tree/main`
  (Quellcode, dauerhaft gültig).
- `live-demo-tunnel-qrcode.png` – verlinkt auf einen **temporären** Cloudflare Quick Tunnel
  (`trycloudflare.com`), der auf den lokal laufenden `step9-upload-interface`-Container zeigte.

**Wichtig:** Die Tunnel-URL im zweiten QR-Code ist nur gültig, solange der zugehörige
`cloudflared`-Prozess und der Docker-Container liefen (kein Account-Tunnel, keine
Uptime-Garantie). Nach dem Ende dieser Session/Präsentation führt der Link ins Leere.
Für einen erneuten Live-Test muss ein neuer Tunnel gestartet und ein neuer QR-Code erzeugt
werden (andere URL, siehe `docker-compose.yml`/`RUNBOOK.md` für den lokalen Start von
`step9-upload-interface`).
