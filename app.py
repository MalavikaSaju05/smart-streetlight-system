"""
SMART STREET LIGHT DASHBOARD — MQTT VERSION

Change from the HTTP version:
- REMOVED: the POST /api/status route (ESP32 no longer calls Flask directly)
- ADDED: a background MQTT subscriber thread that listens to the same topic
  the ESP32 publishes to, and updates the same latest_status dictionary.
- UNCHANGED: GET /api/status, the dashboard route "/", and all of
  templates/index.html, static/style.css, static/script.js.
  The browser-facing side doesn't know or care that MQTT is involved.
"""

from flask import Flask, render_template, jsonify
from datetime import datetime
import json
import threading
import paho.mqtt.client as mqtt

app = Flask(__name__)

# ============================================================
# MQTT SETTINGS — must match the ESP32 sketch exactly
# ============================================================
MQTT_BROKER = "test.mosquitto.org"
MQTT_PORT = 1883
MQTT_TOPIC = "malavika_streetlight_demo/status"  # <-- must match the ESP32 code exactly

# ============================================================
# SHARED STATE
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
    "esp32_connected": False
}

status_lock = threading.Lock()  # protects latest_status from being read/written at the same time


# ============================================================
# MQTT CALLBACKS
# ============================================================
def on_connect(client, userdata, flags, reason_code, properties=None):
    print(f"[MQTT] Connected to broker (reason code: {reason_code})")
    client.subscribe(MQTT_TOPIC)
    print(f"[MQTT] Subscribed to topic: {MQTT_TOPIC}")


def on_message(client, userdata, msg):
    """
    Called automatically whenever a new message arrives on our topic.
    This is the MQTT equivalent of the old POST /api/status route.
    """
    try:
        payload = json.loads(msg.payload.decode())
        print(f"[MQTT] Received: {payload}")

        with status_lock:
            latest_status["environment"] = payload.get("environment", latest_status["environment"])
            latest_status["motion"] = payload.get("motion", latest_status["motion"])
            latest_status["light1"] = payload.get("light1", latest_status["light1"])
            latest_status["light2"] = payload.get("light2", latest_status["light2"])
            latest_status["light3"] = payload.get("light3", latest_status["light3"])
            latest_status["brightness"] = payload.get("brightness", latest_status["brightness"])
            latest_status["fault"] = payload.get("fault", latest_status["fault"])
            latest_status["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            latest_status["esp32_connected"] = True

    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        print(f"[MQTT] Failed to parse message: {e}")


def on_disconnect(client, userdata, reason_code, properties=None):
    print(f"[MQTT] Disconnected (reason code: {reason_code})")


# ============================================================
# START MQTT CLIENT IN A BACKGROUND THREAD
# ============================================================
def start_mqtt_client():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect

    client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)

    # loop_forever() blocks, so it must run in its own thread,
    # otherwise Flask would never get to serve web pages.
    client.loop_forever()


# Start the MQTT listener thread once, when the app starts.
# daemon=True means this thread shuts down automatically when Flask stops.
mqtt_thread = threading.Thread(target=start_mqtt_client, daemon=True)
mqtt_thread.start()


# ============================================================
# WEB ROUTES (unchanged behavior from the HTTP version)
# ============================================================
@app.route("/")
def index():
    """Serves the dashboard web page."""
    return render_template("index.html")


@app.route("/api/status", methods=["GET"])
def get_status():
    """
    The dashboard webpage still calls this every 2 seconds, exactly as before.
    It has no idea the data arrived via MQTT instead of a direct POST.
    """
    with status_lock:
        return jsonify(latest_status)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)
    # use_reloader=False is important here: Flask's debug auto-reloader
    # starts your script twice, which would start two MQTT subscriber
    # threads and cause duplicate/confusing messages.
