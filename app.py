"""
Smart Street Light - Flask backend (Render)

Endpoints
  GET  /              dashboard page
  POST /api/status    ESP32 pushes its latest state (JSON)
  GET  /api/status    dashboard reads the latest state
  GET  /health        tiny keep-alive / health-check endpoint

The state lives in memory, so run with ONE gunicorn worker:
  gunicorn app:app --workers 1 --threads 4 --keep-alive 5 --timeout 30
"""

import os
import threading
import time
from datetime import datetime, timedelta, timezone

from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

# ESP32 counts as connected if we heard from it within this many seconds.
# (The ESP32 sends a heartbeat every ~3 s, so 10 s tolerates 2 lost packets.)
ESP32_TIMEOUT = 10

# Render servers run in UTC. Show the "last updated" clock in IST.
DISPLAY_TZ = timezone(timedelta(hours=5, minutes=30))

# Allowed values for each text field (keeps the same JSON format as before).
VALID_VALUES = {
    "environment": {"day", "night"},
    "motion": {"none", "detected"},
    "light1": {"off", "dim", "bright", "fault"},
    "light2": {"off", "dim", "bright"},
    "light3": {"off", "dim", "bright"},
    "fault": {"none", "LIGHT1_FAILED"},
}

state_lock = threading.Lock()

# Latest data received from the ESP32
latest_status = {
    "environment": "unknown",
    "motion": "none",
    "light1": "off",
    "light2": "off",
    "light3": "off",
    "brightness": 0,
    "fault": "none",
    "last_updated": None,
    "esp32_connected": False,
    "last_seen": 0,
}

STATE_FIELDS = ("environment", "motion", "light1", "light2", "light3",
                "brightness", "fault")


def validate(data):
    """Return (clean_values, errors). Missing fields are simply not updated."""
    clean, errors = {}, []

    for field, allowed in VALID_VALUES.items():
        if field not in data:
            continue
        value = data[field]
        if not isinstance(value, str):
            errors.append(f"{field} must be a string")
            continue
        # environment/motion/lights are lowercase; the fault code is exact
        value = value if field == "fault" else value.strip().lower()
        if value not in allowed:
            errors.append(f"{field} has invalid value '{value}'")
            continue
        clean[field] = value

    if "brightness" in data:
        b = data["brightness"]
        if isinstance(b, bool) or not isinstance(b, int) or not 0 <= b <= 255:
            errors.append("brightness must be an integer from 0 to 255")
        else:
            clean["brightness"] = b

    return clean, errors


@app.after_request
def no_cache_for_api(response):
    # Never let a browser or proxy serve a stale status.
    if request.path.startswith("/api/"):
        response.headers["Cache-Control"] = "no-store, max-age=0"
    return response


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/health")
def health():
    return "ok", 200


@app.route("/api/status", methods=["POST"])
def receive_status():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Invalid or missing JSON body"}), 400

    clean, errors = validate(data)
    if errors:
        return jsonify({"error": "Validation failed", "details": errors}), 400

    with state_lock:
        changed = any(
            latest_status[key] != value for key, value in clean.items()
        )
        latest_status.update(clean)
        latest_status["last_seen"] = time.time()
        latest_status["last_updated"] = datetime.now(DISPLAY_TZ).strftime("%H:%M:%S")
        latest_status["esp32_connected"] = True
        snapshot = {key: latest_status[key] for key in STATE_FIELDS}

    # Log only real changes, not every heartbeat.
    if changed:
        print(
            "ESP32 UPDATE:", snapshot["environment"],
            "| Motion:", snapshot["motion"],
            "| Brightness:", snapshot["brightness"],
            "| L1:", snapshot["light1"],
            "| L2:", snapshot["light2"],
            "| L3:", snapshot["light3"],
            "| Fault:", snapshot["fault"],
            flush=True,
        )

    return jsonify({"status": "success"}), 200


@app.route("/api/status", methods=["GET"])
def get_status():
    with state_lock:
        response = latest_status.copy()

    if response["last_seen"] == 0:
        response["esp32_connected"] = False
        response["seconds_since_last_update"] = None
    else:
        age = time.time() - response["last_seen"]
        response["esp32_connected"] = age <= ESP32_TIMEOUT
        response["seconds_since_last_update"] = round(age, 1)

    return jsonify(response)


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        threaded=True,
    )
