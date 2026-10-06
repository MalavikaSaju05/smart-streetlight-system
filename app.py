from flask import Flask, render_template, request, jsonify
from datetime import datetime

app = Flask(__name__)

# Shared state holding the latest status
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
    """Serves the main dashboard page."""
    return render_template("index.html")

@app.route("/api/status", methods=["GET"])
def get_status():
    """Called every 2 seconds by the web browser dashboard."""
    return jsonify(latest_status)

@app.route("/api/status", methods=["POST"])
def update_status():
    """Called periodically by the ESP32 to publish sensor updates."""
    global latest_status
    try:
        data = request.get_json(force=True)
        print(f"[HTTP POST Received]: {data}")

        latest_status["environment"] = data.get("environment", latest_status["environment"])
        latest_status["motion"] = data.get("motion", latest_status["motion"])
        latest_status["light1"] = data.get("light1", latest_status["light1"])
        latest_status["light2"] = data.get("light2", latest_status["light2"])
        latest_status["light3"] = data.get("light3", latest_status["light3"])
        latest_status["brightness"] = data.get("brightness", latest_status["brightness"])
        latest_status["fault"] = data.get("fault", latest_status["fault"])
        latest_status["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        latest_status["esp32_connected"] = True

        return jsonify({"status": "success", "message": "Data updated successfully"}), 200

    except Exception as e:
        print(f"[HTTP Error]: {e}")
        return jsonify({"status": "error", "message": str(e)}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
