/*
 * js/router.js - Agentic-PMPlus Frontend
 *
 * Minimaler Hash-Router (kein Framework noetig fuer eine handvoll Bildschirme).
 * Routen-Muster: "/", "/order/:orderId", "/verlauf", "/kalibrierung".
 */

const routes = [];

export function registerRoute(pattern, handler) {
  const paramNames = [];
  const regexSource = pattern
    .split("/")
    .map((segment) => {
      if (segment.startsWith(":")) {
        paramNames.push(segment.slice(1));
        return "([^/]+)";
      }
      return segment.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    })
    .join("/");
  routes.push({ regex: new RegExp(`^${regexSource}$`), paramNames, handler });
}

function currentPath() {
  const hash = window.location.hash || "#/";
  return hash.slice(1) || "/";
}

async function dispatch() {
  const path = currentPath();
  document.querySelectorAll("[data-route]").forEach((link) => {
    link.classList.toggle("active", link.dataset.route === path.split("/").slice(0, 2).join("/") || link.dataset.route === path);
  });

  for (const route of routes) {
    const match = path.match(route.regex);
    if (match) {
      const params = {};
      route.paramNames.forEach((name, i) => {
        params[name] = decodeURIComponent(match[i + 1]);
      });
      await route.handler(params);
      return;
    }
  }
  document.getElementById("app").innerHTML = `<p class="error-banner">Unbekannte Seite: ${path}</p>`;
}

export function startRouter() {
  window.addEventListener("hashchange", dispatch);
  window.addEventListener("DOMContentLoaded", dispatch);
  if (document.readyState !== "loading") dispatch();
}

export function navigate(path) {
  window.location.hash = `#${path}`;
}
