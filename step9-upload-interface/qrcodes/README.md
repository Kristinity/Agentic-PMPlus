# QR-Codes für die Live-Präsentation (2026-07-28)

- `github-repo-qrcode.png` – verlinkt auf `https://github.com/Kristinity/Agentic-PMPlus/tree/main`
  (Quellcode, dauerhaft gültig).
- `live-demo-tunnel-qrcode.png` – verlinkt auf einen **temporären** Cloudflare Quick Tunnel
  (`trycloudflare.com`), der auf den lokal laufenden `step9-upload-interface`-Container zeigte.
- `expert-review-qrcode.png` – verlinkt auf den **step7-active-learning-Review-Screen**
  (`step7-active-learning/frontend/index.html`, Warteschlange + PGP/LLM-Review +
  Entscheidungserfassung mit Provenienz). Zeigt die im step9-Screen bewusst fehlende
  Experten-Rückkopplung (PGP folgen / LLM folgen / eigene Reihenfolge) – aber auf der
  **geteilten** Pipeline-Auftragslage (`shared/data/tau_vergleich.csv`), NICHT auf den
  individuellen Uploads einzelner Studis aus step9 (die laufen isoliert in eigenen
  Temp-Verzeichnissen, s. `pipeline.py:build_run_dir`). Zwei separate Tunnel dahinter:
  Frontend (nginx, Port 8080) und Backend-API (FastAPI, Port 8007) – die URL kodiert
  beide über den `?api=`-Query-Parameter (`index.html?api=<Backend-Tunnel-URL>`,
  s. `frontend/README.md` für die Origin-Überschreibung).

**Wichtig:** Die Tunnel-URL im zweiten QR-Code ist nur gültig, solange der zugehörige
`cloudflared`-Prozess und der Docker-Container liefen (kein Account-Tunnel, keine
Uptime-Garantie). Nach dem Ende dieser Session/Präsentation führt der Link ins Leere.
Für einen erneuten Live-Test muss ein neuer Tunnel gestartet und ein neuer QR-Code erzeugt
werden (andere URL, siehe `docker-compose.yml`/`RUNBOOK.md` für den lokalen Start von
`step9-upload-interface`).

**Verlauf:** Der ursprüngliche Tunnel (`finally-garmin-rose-fix.trycloudflare.com`) verlor
am 2026-07-28 gegen 12:07 Uhr dauerhaft die Verbindung zu Cloudflares Edge-Netzwerk
(wiederholte QUIC-Timeouts) und wurde um 15:03 Uhr durch einen neuen Tunnel
(`screenshots-trio-costa-average.trycloudflare.com`) ersetzt – die Grafik in diesem Ordner
spiegelt die neue URL. Quick Tunnels ohne Account haben laut Cloudflare keine
Uptime-Garantie; bei einem erneuten Ausfall während einer Präsentation hilft nur ein
Neustart des Tunnels (neue URL, neuer QR-Code). Dasselbe gilt für die beiden Tunnel
hinter `expert-review-qrcode.png` (Frontend + Backend) – fällt einer der beiden aus,
ist die gesamte kombinierte URL ungültig und beide Tunnel müssen neu gestartet werden.
