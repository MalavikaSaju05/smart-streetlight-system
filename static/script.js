// This script asks the Flask server "what's the latest status?" every 2 seconds
// and updates the page without reloading it.

function setBulb(elementId, statusText) {
  const bulb = document.getElementById(elementId);
  bulb.className = "light-symbol"; // reset

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

async function refreshStatus() {
  try {
    const response = await fetch("/api/status");
    const data = await response.json();

    document.getElementById("environment").textContent = data.environment.toUpperCase();
    document.getElementById("motion").textContent = data.motion.toUpperCase();
    document.getElementById("brightness").textContent = data.brightness;

    const faultEl = document.getElementById("fault");
    faultEl.textContent = data.fault.toUpperCase();
    faultEl.classList.toggle("alert", data.fault !== "none");

    document.getElementById("light1-status").textContent = data.light1.toUpperCase();
    document.getElementById("light2-status").textContent = data.light2.toUpperCase();
    document.getElementById("light3-status").textContent = data.light3.toUpperCase();

    setBulb("light1-bulb", data.light1);
    setBulb("light2-bulb", data.light2);
    setBulb("light3-bulb", data.light3);

    document.getElementById("last-updated").textContent = data.last_updated || "Never";

    const badge = document.getElementById("connection-badge");
    if (data.esp32_connected) {
      badge.textContent = "ESP32: Connected";
      badge.className = "badge connected";
    } else {
      badge.textContent = "ESP32: Not connected yet";
      badge.className = "badge disconnected";
    }
  } catch (error) {
    console.error("Failed to fetch status:", error);
    const badge = document.getElementById("connection-badge");
    badge.textContent = "ESP32: Server unreachable";
    badge.className = "badge disconnected";
  }
}

// Fetch immediately on load, then every 2 seconds
refreshStatus();
setInterval(refreshStatus, 500);
