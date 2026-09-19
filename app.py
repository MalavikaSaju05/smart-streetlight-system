from flask import Flask, render_template, request, jsonify
from datetime import datetime, timezone
import time

app = Flask(__name__)

# Latest data received from ESP32
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
    "last_seen": 0
}

# ESP32 is considered connected if we heard from it
# within this many seconds.
ESP32_TIMEOUT = 10


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/status", methods=["POST"])
def receive_status():

    data = request.get_json(silent=True)

    if data is None:
        return jsonify({
            "error": "Invalid or missing JSON body"
        }), 400

    # Update values
    latest_status["environment"] = data.get(
        "environment",
        latest_status["environment"]
    )

    latest_status["motion"] = data.get(
        "motion",
        latest_status["motion"]
    )

    latest_status["light1"] = data.get(
        "light1",
        latest_status["light1"]
    )

    latest_status["light2"] = data.get(
        "light2",
        latest_status["light2"]
    )

    latest_status["light3"] = data.get(
        "light3",
        latest_status["light3"]
    )

    latest_status["brightness"] = data.get(
        "brightness",
        latest_status["brightness"]
    )

    latest_status["fault"] = data.get(
        "fault",
        latest_status["fault"]
    )

    # Current time
    now = time.time()

    latest_status["last_seen"] = now

    latest_status["last_updated"] = datetime.now().strftime(
        "%H:%M:%S"
    )

    latest_status["esp32_connected"] = True

    print(
        "ESP32 UPDATE:",
        latest_status["environment"],
        "| Motion:",
        latest_status["motion"],
        "| Brightness:",
        latest_status["brightness"],
        "| L1:",
        latest_status["light1"],
        "| L2:",
        latest_status["light2"],
        "| L3:",
        latest_status["light3"],
        "| Fault:",
        latest_status["fault"]
    )

    return jsonify({
        "status": "success"
    }), 200


@app.route("/api/status", methods=["GET"])
def get_status():

    # Check whether ESP32 is still sending data
    if latest_status["last_seen"] == 0:
        connected = False
    else:
        connected = (
            time.time() - latest_status["last_seen"]
            <= ESP32_TIMEOUT
        )

    response = latest_status.copy()

    response["esp32_connected"] = connected

    return jsonify(response)


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        threaded=True
    )
