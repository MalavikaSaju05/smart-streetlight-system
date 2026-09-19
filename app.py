from flask import Flask, render_template, request, jsonify
from datetime import datetime
import time

app = Flask(__name__)

# ============================================================
# LATEST ESP32 STATUS
# ============================================================

latest_status = {
    "environment": "unknown",
    "motion": "none",

    "light1": "off",
    "light2": "off",
    "light3": "off",

    "brightness": 0,
    "fault": "none",

    "last_updated": None,
    "last_seen": 0,
    "esp32_connected": False
}

# ESP32 considered connected if an update was received
# within the last 10 seconds.
ESP32_TIMEOUT = 10


# ============================================================
# DASHBOARD
# ============================================================

@app.route("/")
def index():
    return render_template("index.html")


# ============================================================
# ESP32 -> SERVER
# ============================================================

@app.route("/api/status", methods=["POST"])
def receive_status():

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "status": "error",
            "message": "Invalid JSON"
        }), 400

    # --------------------------------------------------------
    # Update only fields supplied by ESP32
    # --------------------------------------------------------

    if "environment" in data:
        latest_status["environment"] = str(data["environment"])

    if "motion" in data:
        latest_status["motion"] = str(data["motion"])

    if "light1" in data:
        latest_status["light1"] = str(data["light1"])

    if "light2" in data:
        latest_status["light2"] = str(data["light2"])

    if "light3" in data:
        latest_status["light3"] = str(data["light3"])

    if "brightness" in data:
        try:
            latest_status["brightness"] = int(data["brightness"])
        except (ValueError, TypeError):
            pass

    if "fault" in data:
        latest_status["fault"] = str(data["fault"])

    # --------------------------------------------------------
    # Connection information
    # --------------------------------------------------------

    now = time.time()

    latest_status["last_seen"] = now
    latest_status["last_updated"] = datetime.now().strftime(
        "%H:%M:%S"
    )

    latest_status["esp32_connected"] = True

    # --------------------------------------------------------
    # Server log
    # --------------------------------------------------------

    print(
        "[ESP32]",
        "Environment:", latest_status["environment"],
        "| Motion:", latest_status["motion"],
        "| Brightness:", latest_status["brightness"],
        "| L1:", latest_status["light1"],
        "| L2:", latest_status["light2"],
        "| L3:", latest_status["light3"],
        "| Fault:", latest_status["fault"]
    )

    return jsonify({
        "status": "success"
    }), 200


# ============================================================
# SERVER -> DASHBOARD
# ============================================================

@app.route("/api/status", methods=["GET"])
def get_status():

    now = time.time()

    # Check whether ESP32 has sent anything recently
    if latest_status["last_seen"] == 0:
        connected = False
    else:
        connected = (
            now - latest_status["last_seen"]
            <= ESP32_TIMEOUT
        )

    response = latest_status.copy()

    response["esp32_connected"] = connected

    # Don't expose internal timestamp to browser
    response.pop("last_seen", None)

    return jsonify(response)


# ============================================================
# HEALTH CHECK
# ============================================================

@app.route("/health")
def health():

    return jsonify({
        "status": "ok"
    })


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        threaded=True
    )
