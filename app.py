from flask import Flask, request, jsonify, render_template
import time
from datetime import datetime

app = Flask(__name__)

latest_state = {
    "environment": "waiting",
    "motion": "none",
    "light1": "off",
    "light2": "off",
    "light3": "off",
    "brightness": 0,
    "fault": "none",
    "esp32_connected": False,
    "last_updated": "Waiting for ESP32..."
}

last_seen = 0

ESP32_TIMEOUT = 8


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/status", methods=["POST"])
def receive_status():

    global latest_state
    global last_seen

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "status": "error",
            "message": "Invalid JSON"
        }), 400

    latest_state["environment"] = data.get(
        "environment",
        "unknown"
    )

    latest_state["motion"] = data.get(
        "motion",
        "none"
    )

    latest_state["light1"] = data.get(
        "light1",
        "off"
    )

    latest_state["light2"] = data.get(
        "light2",
        "off"
    )

    latest_state["light3"] = data.get(
        "light3",
        "off"
    )

    latest_state["brightness"] = int(
        data.get("brightness", 0)
    )

    latest_state["fault"] = data.get(
        "fault",
        "none"
    )

    latest_state["esp32_connected"] = True

    latest_state["last_updated"] = (
        datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    )

    last_seen = time.time()

    print("ESP32 DATA:", latest_state)

    return jsonify({
        "status": "success"
    })


@app.route("/api/status", methods=["GET"])
def send_status():

    if last_seen == 0:
        latest_state["esp32_connected"] = False

    elif time.time() - last_seen > ESP32_TIMEOUT:
        latest_state["esp32_connected"] = False

    return jsonify(latest_state)


@app.route("/health")
def health():

    return jsonify({
        "status": "ok"
    })


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )
