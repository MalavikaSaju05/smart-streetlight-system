from flask import Flask, request, jsonify, render_template
from datetime import datetime
import time


# ============================================================
# FLASK APPLICATION
# ============================================================

app = Flask(__name__)


# ============================================================
# ESP32 TIMEOUT
# ============================================================

ESP32_TIMEOUT_SECONDS = 10


# ============================================================
# DEFAULT STATE
# ============================================================

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


# Last time ESP32 sent data
last_seen_timestamp = 0


# ============================================================
# CHECK ESP32 CONNECTION
# ============================================================

def is_esp32_connected():

    if last_seen_timestamp == 0:
        return False

    elapsed_time = (
        time.time() -
        last_seen_timestamp
    )

    return (
        elapsed_time <=
        ESP32_TIMEOUT_SECONDS
    )


# ============================================================
# DASHBOARD
# ============================================================

@app.route("/")
def dashboard():

    return render_template(
        "index.html"
    )


# ============================================================
# ESP32 API
# ============================================================

@app.route(
    "/api/status",
    methods=["POST"]
)
def receive_status():

    global latest_state
    global last_seen_timestamp


    # --------------------------------------------------------
    # Read JSON
    # --------------------------------------------------------

    data = request.get_json(
        silent=True
    )


    # --------------------------------------------------------
    # Validate JSON
    # --------------------------------------------------------

    if not isinstance(
        data,
        dict
    ):
        return jsonify({
            "status": "error",
            "message": "Invalid JSON"
        }), 400


    # --------------------------------------------------------
    # Environment
    # --------------------------------------------------------

    latest_state["environment"] = str(
        data.get(
            "environment",
            "unknown"
        )
    )


    # --------------------------------------------------------
    # Motion
    # --------------------------------------------------------

    latest_state["motion"] = str(
        data.get(
            "motion",
            "none"
        )
    )


    # --------------------------------------------------------
    # Light 1
    # --------------------------------------------------------

    latest_state["light1"] = str(
        data.get(
            "light1",
            "off"
        )
    )


    # --------------------------------------------------------
    # Light 2
    # --------------------------------------------------------

    latest_state["light2"] = str(
        data.get(
            "light2",
            "off"
        )
    )


    # --------------------------------------------------------
    # Light 3
    # --------------------------------------------------------

    latest_state["light3"] = str(
        data.get(
            "light3",
            "off"
        )
    )


    # --------------------------------------------------------
    # Brightness
    # --------------------------------------------------------

    try:

        brightness = int(
            data.get(
                "brightness",
                0
            )
        )

        brightness = max(
            0,
            min(
                255,
                brightness
            )
        )

        latest_state["brightness"] = (
            brightness
        )

    except (
        ValueError,
        TypeError
    ):

        latest_state["brightness"] = 0


    # --------------------------------------------------------
    # Fault
    # --------------------------------------------------------

    latest_state["fault"] = str(
        data.get(
            "fault",
            "none"
        )
    )


    # --------------------------------------------------------
    # ESP32 connection
    # --------------------------------------------------------

    latest_state[
        "esp32_connected"
    ] = True


    # --------------------------------------------------------
    # Timestamp
    # --------------------------------------------------------

    latest_state[
        "last_updated"
    ] = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )


    # --------------------------------------------------------
    # Update last seen
    # --------------------------------------------------------

    last_seen_timestamp = (
        time.time()
    )


    # --------------------------------------------------------
    # Server console
    # --------------------------------------------------------

    print(
        "[ESP32 DATA]",
        latest_state
    )


    # --------------------------------------------------------
    # Response
    # --------------------------------------------------------

    return jsonify({
        "status": "success",
        "message": "State updated"
    }), 200


# ============================================================
# DASHBOARD API
# ============================================================

@app.route(
    "/api/status",
    methods=["GET"]
)
def get_status():

    connected = (
        is_esp32_connected()
    )


    # --------------------------------------------------------
    # ESP32 disconnected
    #
    # Do NOT show old sensor values.
    # --------------------------------------------------------

    if not connected:

        return jsonify({

            "environment": "waiting",

            "motion": "none",

            "light1": "off",

            "light2": "off",

            "light3": "off",

            "brightness": 0,

            "fault": "none",

            "esp32_connected": False,

            "last_updated":
                latest_state[
                    "last_updated"
                ]

        })


    # --------------------------------------------------------
    # ESP32 connected
    # --------------------------------------------------------

    latest_state[
        "esp32_connected"
    ] = True

    return jsonify(
        latest_state
    )


# ============================================================
# HEALTH CHECK
# ============================================================

@app.route("/health")
def health():

    return jsonify({
        "status": "ok",
        "service": "smart-streetlight",
        "esp32_connected":
            is_esp32_connected()
    })


# ============================================================
# LOCAL DEVELOPMENT
# ============================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )
