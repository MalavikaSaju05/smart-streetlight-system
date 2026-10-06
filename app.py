from flask import Flask, request, jsonify, render_template
from datetime import datetime
import time


app = Flask(__name__)


# ============================================================
# ESP32 TIMEOUT
# ============================================================

ESP32_TIMEOUT_SECONDS = 10


# ============================================================
# CURRENT SYSTEM STATE
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


last_seen_timestamp = 0


# ============================================================
# CHECK ESP32 CONNECTION
# ============================================================

def is_esp32_connected():

    if last_seen_timestamp == 0:
        return False

    return (
        time.time() - last_seen_timestamp
        <= ESP32_TIMEOUT_SECONDS
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
# ESP32 UPDATE ENDPOINT
#
# ESP32 sends data using GET parameters.
#
# Example:
#
# /api/update?environment=night&motion=none&
# light1=dim&light2=dim&light3=dim&
# brightness=40&fault=none
# ============================================================

@app.route("/api/update", methods=["GET"])
def update_from_esp32():

    global last_seen_timestamp


    # --------------------------------------------------------
    # Get data from ESP32
    # --------------------------------------------------------

    environment = request.args.get(
        "environment",
        "unknown"
    )

    motion = request.args.get(
        "motion",
        "none"
    )

    light1 = request.args.get(
        "light1",
        "off"
    )

    light2 = request.args.get(
        "light2",
        "off"
    )

    light3 = request.args.get(
        "light3",
        "off"
    )

    fault = request.args.get(
        "fault",
        "none"
    )


    # --------------------------------------------------------
    # Brightness
    # --------------------------------------------------------

    try:

        brightness = int(
            request.args.get(
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

    except (
        ValueError,
        TypeError
    ):

        brightness = 0


    # --------------------------------------------------------
    # Update state
    # --------------------------------------------------------

    latest_state["environment"] = environment

    latest_state["motion"] = motion

    latest_state["light1"] = light1

    latest_state["light2"] = light2

    latest_state["light3"] = light3

    latest_state["brightness"] = brightness

    latest_state["fault"] = fault

    latest_state["esp32_connected"] = True


    # --------------------------------------------------------
    # Timestamp
    # --------------------------------------------------------

    latest_state["last_updated"] = (
        datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    )


    last_seen_timestamp = time.time()


    # --------------------------------------------------------
    # Render log
    # --------------------------------------------------------

    print(
        "[ESP32 UPDATE]",
        latest_state
    )


    # --------------------------------------------------------
    # Response
    # --------------------------------------------------------

    return jsonify({

        "status": "success",

        "message": "ESP32 data updated",

        "state": latest_state

    }), 200


# ============================================================
# DASHBOARD STATUS
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
    # IMPORTANT:
    # Do not show old values.
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
    ), 200


# ============================================================
# HEALTH CHECK
# ============================================================

@app.route("/health")
def health():

    return jsonify({

        "status": "ok",

        "service":
            "smart-streetlight",

        "esp32_connected":
            is_esp32_connected()

    }), 200


# ============================================================
# RUN LOCALLY
# ============================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )
