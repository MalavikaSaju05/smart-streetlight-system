from flask import Flask, render_template, jsonify
from datetime import datetime
import json
import threading
import time
import paho.mqtt.client as mqtt

app = Flask(__name__)

# MQTT Settings — synchronized with Wokwi sketch
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
MQTT_TOPIC = "malavika_streetlight_demo/status"

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

status_lock = threading.Lock()

def on_connect(client, userdata, flags, reason_code, properties=None):
    print(f"[MQTT] Connected to broker (code: {reason_code})")
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        with status_lock:
            latest_status.update({
                "environment": payload.get("environment", latest_status["environment"]),
                "motion": payload.get("motion", latest_status["motion"]),
                "light1": payload.get("light1", latest_status["light1"]),
                "light2": payload.get("light2", latest_status["light2"]),
                "light3": payload.get("light3", latest_status["light3"]),
                "brightness": payload.get("brightness", latest_status["brightness"]),
                "fault": payload.get("fault", latest_status["fault"]),
                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "esp32_connected": True
            })
    except Exception as e:
        print(f"[MQTT] Payload error: {e}")

def on_disconnect(client, userdata, disconnect_flags, reason_code, properties=None):
    with status_lock:
        latest_status["esp32_connected"] = False

def start_mqtt():
    while True:
        try:
            client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
            client.on_connect = on_connect
            client.on_message = on_message
            client.on_disconnect = on_disconnect
            client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
            client.loop_forever()
        except Exception as e:
            print(f"[MQTT] Thread reconnecting in 5s: {e}")
            time.sleep(5)

# Start background MQTT listener thread
mqtt_thread = threading.Thread(target=start_mqtt, daemon=True)
mqtt_thread.start()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/status", methods=["GET"])
def get_status():
    with status_lock:
        return jsonify(latest_status)

@app.route("/ping", methods=["GET"])
def ping():
    return jsonify({"status": "alive"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
