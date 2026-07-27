/*
 * js/api.js - Agentic-PMPlus Frontend
 *
 * Duenner fetch()-Wrapper gegen den /api-Proxy (server.py -> step7-active-learning).
 *
 * Fail-safe statt fail-open (nicht verhandelbare Leitplanke 5,
 * .claude/agents/role/frontend-dev.md): jeder Fehler (Netzwerk, Backend down, 4xx/5xx)
 * wirft eine ApiError. Aufrufer duerfen daraus NIE einen leeren/alten Zustand als
 * "aktuell" render - jede View muss den Fehler sichtbar anzeigen und darf keine
 * vorherigen Daten stillschweigend stehen lassen.
 */

export class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.status = status;
  }
}

async function request(path, options = {}) {
  let response;
  try {
    response = await fetch(`/api${path}`, {
      headers: { "Content-Type": "application/json" },
      ...options,
    });
  } catch (networkError) {
    // Server nicht erreichbar (z.B. Proxy/Backend down) - kein stiller Fallback.
    throw new ApiError(
      `Verbindung zum Server fehlgeschlagen: ${networkError.message}`,
      0,
    );
  }

  let payload = null;
  const text = await response.text();
  if (text) {
    try {
      payload = JSON.parse(text);
    } catch (_parseError) {
      throw new ApiError(`Unerwartete Server-Antwort (kein JSON): ${text.slice(0, 200)}`, response.status);
    }
  }

  if (!response.ok) {
    const detail = payload && (payload.detail || payload.error) ? (payload.detail || payload.error) : response.statusText;
    throw new ApiError(detail || `Serverfehler (${response.status})`, response.status);
  }

  return payload;
}

export function getEskalationen() {
  return request("/eskalationen");
}

export function getVerlauf({ order_id, ab, bis } = {}) {
  const params = new URLSearchParams();
  if (order_id) params.set("order_id", order_id);
  if (ab) params.set("ab", ab);
  if (bis) params.set("bis", bis);
  const qs = params.toString();
  return request(`/verlauf${qs ? `?${qs}` : ""}`);
}

export function postEntscheidung(body) {
  return request("/entscheidung", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export function getKalibrierung() {
  return request("/kalibrierung");
}
