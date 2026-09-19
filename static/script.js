// Smart Street Light dashboard
// Element IDs used (must exist in index.html):
//   environment, motion, brightness, fault, last-updated, connection-badge,
//   light1-status, light1-bulb, light2-status, light2-bulb, light3-status, light3-bulb

const POLL_INTERVAL_MS = 700;   // wait between polls (measured AFTER the previous one finishes)
const FETCH_TIMEOUT_MS = 4000;  // give up on one request after 4 s

let missingIds = new Set();

// Null-safe element lookup: a missing element is reported once, never throws.
function el(id) {
    const node = document.getElementById(id);
    if (!node && !missingIds.has(id)) {
        missingIds.add(id);
        console.warn("Dashboard: element with id '" + id + "' not found in index.html");
    }
    return node;
}

function setText(id, text) {
    const node = el(id);
    if (node) node.textContent = text;
}

function show(value) {
    if (value === undefined || value === null || value === "unknown") return "--";
    return String(value).toUpperCase();
}

function setBulb(id, statusText) {
    const bulb = el(id);
    if (!bulb) return;

    bulb.className = "light-symbol";

    if (statusText === "bright") {
        bulb.classList.add("bright");
    } else if (statusText === "dim") {
        bulb.classList.add("dim");
    } else if (statusText === "fault") {
        bulb.classList.add("fault");
    } else {
        bulb.classList.add("off");
    }
}

function setBadge(text, connected) {
    const badge = el("connection-badge");
    if (!badge) return;
    badge.textContent = text;
    badge.className = "badge " + (connected ? "connected" : "disconnected");
}

function render(data) {
    setText("environment", show(data.environment));
    setText("motion", show(data.motion));

    const brightness = Number(data.brightness) || 0;
    setText("brightness", Math.round((brightness / 255) * 100) + "%");

    setText("light1-status", show(data.light1));
    setText("light2-status", show(data.light2));
    setText("light3-status", show(data.light3));

    setBulb("light1-bulb", data.light1);
    setBulb("light2-bulb", data.light2);
    setBulb("light3-bulb", data.light3);

    const faultEl = el("fault");
    if (faultEl) {
        if (data.fault && data.fault !== "none") {
            faultEl.textContent = "⚠ " + String(data.fault).toUpperCase();
            faultEl.classList.add("alert");
        } else {
            faultEl.textContent = "✓ NO FAULT";
            faultEl.classList.remove("alert");
        }
    }

    setText("last-updated", data.last_updated || "Never");

    if (data.esp32_connected) {
        setBadge("ESP32: Connected", true);
    } else {
        setBadge("ESP32: Not connected", false);
    }
}

async function refreshStatus() {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), FETCH_TIMEOUT_MS);

    try {
        const response = await fetch("/api/status", {
            cache: "no-store",
            signal: controller.signal
        });

        if (!response.ok) {
            throw new Error("Server returned " + response.status);
        }

        const data = await response.json();
        render(data);

    } catch (error) {
        console.error("Dashboard error:", error);
        // This only means the BROWSER could not reach the server.
        setBadge("Server unreachable", false);

    } finally {
        clearTimeout(timer);
        // Always schedule the next poll, whatever happened above.
        // Chaining setTimeout (not setInterval) prevents overlapping requests.
        setTimeout(refreshStatus, POLL_INTERVAL_MS);
    }
}

refreshStatus();
