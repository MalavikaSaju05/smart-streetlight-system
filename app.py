from flask import Flask, render_template, request, jsonify
from datetime import datetime

app = Flask(__name__)

# This dictionary holds the LATEST status received from the ESP32.
# In a real product you'd use a database; for a student project, memory is fine.
latest_status = {
    "environment": "unknown",
    "motion": "none",
    "light1": "off",
    "light2": "off",
    "light3": "off",
    "brightness": 0,
    "fault": "none",
    "last_updated": None,
    "esp32_connected": False
}


@app.route("/")
def index():
    """Serves the dashboard web page."""
    return render_template("index.html")


@app.route("/api/status", methods=["POST"])
def receive_status():
    """
    This is the endpoint the ESP32 sends data to.
    It expects a JSON body like:
    {
      "environment": "night",
      "motion": "detected",
      "light1": "bright",
      "light2": "bright",
      "light3": "dim",
      "brightness": 255,
      "fault": "none"
    }
    """
    data = request.get_json(silent=True)

    if data is None:
        return jsonify({"error": "Invalid or missing JSON body"}), 400

    latest_status["environment"] = data.get("environment", latest_status["environment"])
    latest_status["motion"] = data.get("motion", latest_status["motion"])
    latest_status["light1"] = data.get("light1", latest_status["light1"])
    latest_status["light2"] = data.get("light2", latest_status["light2"])
    latest_status["light3"] = data.get("light3", latest_status["light3"])
    latest_status["brightness"] = data.get("brightness", latest_status["brightness"])
    latest_status["fault"] = data.get("fault", latest_status["fault"])
    latest_status["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    latest_status["esp32_connected"] = True

    print("Received update from ESP32:", latest_status)

    return jsonify({"message": "Status updated successfully"}), 200


@app.route("/api/status", methods=["GET"])
def get_status():
    """
    The dashboard webpage calls this repeatedly (every couple of seconds)
    to fetch the latest status and update itself, without reloading the page.
    """
    return jsonify(latest_status)


if __name__ == "__main__":
    # host="0.0.0.0" makes Flask reachable from other devices on the network
    # (needed so the ESP32 / Wokwi can reach it, not just your own browser).
    app.run(host="0.0.0.0", port=5000)