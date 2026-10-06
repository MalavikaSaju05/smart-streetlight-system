from flask import Flask, request, jsonify, render_template
from datetime import datetime
import time

app = Flask(__name__)

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

last_seen_timestamp = 0
ESP32_TIMEOUT_SECONDS = 8


def check_esp32_connection():
    if last_seen_timestamp == 0:
        return False

    return time.time() - last_seen_timestamp <= ESP32_TIMEOUT_SECONDS


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/status", methods=["GET", "POST"])
def handle_status():

    global last_seen_timestamp

    # ---------------------------------------
    # ESP32 -> Flask
    # ---------------------------------------
    if request.method == "POST":

        data = request.get_json(silent=True)

        if not isinstance(data, dict):
            return jsonify({
                "status": "error",
                "message": "Invalid JSON"
            }), 400

        latest_state["environment"] = str(
            data.get("environment", "unknown")
        )

        latest_state["motion"] = str(
            data.get("motion", "none")
        )

        latest_state["light1"] = str(
            data.get("light1", "off")
        )

        latest_state["light2"] = str(
            data.get("light2", "off")
        )

        latest_state["light3"] = str(
            data.get("light3", "off")
        )

        try:
            brightness = int(
                data.get("brightness", 0)
            )

            latest_state["brightness"] = max(
                0,
                min(255, brightness)
            )

        except (ValueError, TypeError):

            latest_state["brightness"] = 0

        latest_state["fault"] = str(
            data.get("fault", "none")
        )

        # Record ESP32 activity
        last_seen_timestamp = time.time()

        latest_state["last_updated"] = (
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )

        latest_state["esp32_connected"] = True

        print(
            "[ESP32]",
            "Environment:", latest_state["environment"],
            "| Motion:", latest_state["motion"],
            "| Brightness:", latest_state["brightness"],
            "| L1:", latest_state["light1"],
            "| L2:", latest_state["light2"],
            "| L3:", latest_state["light3"],
            "| Fault:", latest_state["fault"]
        )

        return jsonify({
            "status": "success",
            "message": "State updated"
        }), 200

    # ---------------------------------------
    # Dashboard -> Flask
    # ---------------------------------------
    if request.method == "GET":

        latest_state["esp32_connected"] = (
            check_esp32_connection()
        )

        return jsonify(latest_state), 200


@app.route("/health")
def health():

    return jsonify({
        "status": "ok",
        "service": "smart-streetlight"
    }), 200


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )
