/*
 * js/app.js - Agentic-PMPlus Frontend
 * Verdrahtet die Routen mit den jeweiligen Views (siehe frontend/README.md fuer die
 * Bildschirm-Struktur-Begruendung, abgeleitet aus
 * Active-Learning-Loop-und-Frontend-Konzept.md Abschnitt 2).
 */
import { registerRoute, startRouter } from "./router.js";
import { renderQueue } from "./views/queue.js";
import { renderOrderDetail } from "./views/orderDetail.js";
import { renderHistory } from "./views/history.js";
import { renderCalibration } from "./views/calibration.js";

registerRoute("/", renderQueue);
registerRoute("/order/:orderId", renderOrderDetail);
registerRoute("/verlauf", renderHistory);
registerRoute("/kalibrierung", renderCalibration);

startRouter();
