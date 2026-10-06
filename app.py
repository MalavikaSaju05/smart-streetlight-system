from flask import Flask, request, jsonify, render_template
from datetime import datetime
import time

app = Flask(__name__)

# ============================================================
# IN-MEMORY STATE STORE
# ============================================================
# Stores the latest status sent by the ESP32
latest_state = {
    "environment": "unknown",
    "motion": "none",
    "light1": "off",
    "light2": "off",
    "light3": "off",
    "brightness": 0,
    "fault": "none",
    "last_updated": "Never",
    "esp32_connected": False
}

# Timestamp of the last received HTTP POST from ESP32
last_seen_timestamp = 0
ESP32_TIMEOUT_SECONDS = 6  # If no update within 6s, mark ESP32 disconnected


# ============================================================
# HELPER FUNCTIONS
# ============================================================
def check_esp32_connection():
    """Calculates if the ESP32 is currently online based on heartbeat timing."""
    global last_seen_timestamp
    if last_seen_timestamp == 0:
        return False
    return (time.time() - last_seen_timestamp) < ESP32_TIMEOUT_SECONDS


# ============================================================
# ROUTES
# ============================================================

@app.route("/")
def index():
    """Serves the main dashboard user interface."""
    return render_template("index.html")


@app.route("/api/status", methods=["GET", "POST"])
def handle_status():
    global latest_state, last_seen_timestamp

    # --------------------------------------------------------
    # POST: Incoming data from ESP32
    # --------------------------------------------------------
    if request.method == "POST":
        data = request.get_json(silent=True)

        if not data:
            return jsonify({"status": "error", "message": "Invalid or missing JSON payload"}), 400

        # Update in-memory state with fields sent by ESP32
        latest_state["environment"] = str(data.get("environment", "unknown"))
        latest_state["motion"] = str(data.get("motion", "none"))
        latest_state["light1"] = str(data.get("light1", "off"))
        latest_state["light2"] = str(data.get("light2", "off"))
        latest_state["light3"] = str(data.get("light3", "off"))
        latest_state["brightness"] = data.get("brightness", 0)
        latest_state["fault"] = str(data.get("fault", "none"))

        # Update timestamp metadata
        last_seen_timestamp = time.time()
        latest_state["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        latest_state["esp32_connected"] = True

        print(f"[HTTP POST] Updated state from ESP32 at {latest_state['last_updated']}")

        return jsonify({"status": "success", "message": "State updated"}), 200

    # --------------------------------------------------------
    # GET: Polling request from JavaScript Dashboard
    # --------------------------------------------------------
    elif request.method == "GET":
        # Dynamic check to verify if ESP32 is actively communicating
        latest_state["esp32_connected"] = check_esp32_connection()

        return jsonify(latest_state), 200


# ============================================================
# APP ENTRY POINT
# ============================================================
if __name__ == "__main__":
    # Host 0.0.0.0 allows connections from external IPs (local network or Render)
    app.run(host="0.0.0.0", port=5000, debug=True)
