// ============================================================
// SMART STREET LIGHT DASHBOARD
// ============================================================
//
// The browser periodically asks Flask for the latest ESP32
// state.
//
// IMPORTANT:
// The dashboard does NOT control the physical lights.
// ESP32 controls the lights locally.
// The dashboard only displays the latest state received
// from ESP32.
// ============================================================


const POLL_INTERVAL_MS = 700;
const FETCH_TIMEOUT_MS = 3000;


// ============================================================
// SAFE DOM LOOKUP
// ============================================================

function el(id) {

    return document.getElementById(id);

}


// ============================================================
// DISPLAY VALUE
// ============================================================

function displayValue(value) {

    if (
        value === undefined ||
        value === null ||
        value === "unknown"
    ) {

        return "--";

    }

    return String(value).toUpperCase();

}


// ============================================================
// UPDATE TEXT
// ============================================================

function setText(id, value) {

    const element = el(id);

    if (!element) {
        return;
    }

    element.textContent = value;

}


// ============================================================
// UPDATE BULB
// ============================================================

function setBulb(id, status) {

    const bulb = el(id);

    if (!bulb) {
        return;
    }


    // Remove previous status classes

    bulb.className = "light-symbol";


    // Apply current status

    if (status === "bright") {

        bulb.classList.add("bright");

    }

    else if (status === "dim") {

        bulb.classList.add("dim");

    }

    else if (status === "fault") {

        bulb.classList.add("fault");

    }

    else {

        bulb.classList.add("off");

    }

}


// ============================================================
// CONNECTION BADGE
// ============================================================

function updateConnectionBadge(connected) {

    const badge = el("connection-badge");

    if (!badge) {
        return;
    }


    if (connected) {

        badge.textContent = "ESP32: Connected";

        badge.className =
            "badge connected";

    }

    else {

        badge.textContent = "ESP32: Not connected";

        badge.className =
            "badge disconnected";

    }

}


// ============================================================
// RENDER SERVER DATA
// ============================================================

function render(data) {


    // --------------------------------------------------------
    // Environment
    // --------------------------------------------------------

    setText(
        "environment",
        displayValue(data.environment)
    );


    // --------------------------------------------------------
    // Motion
    // --------------------------------------------------------

    setText(
        "motion",
        displayValue(data.motion)
    );


    // --------------------------------------------------------
    // Brightness
    // --------------------------------------------------------

    let brightness =
        Number(data.brightness);

    if (
        Number.isNaN(brightness)
    ) {

        brightness = 0;

    }


    brightness =
        Math.max(
            0,
            Math.min(
                255,
                brightness
            )
        );


    const percentage =
        Math.round(
            (brightness / 255) * 100
        );


    setText(
        "brightness",
        percentage + "%"
    );


    // --------------------------------------------------------
    // Light 1
    // --------------------------------------------------------

    setText(
        "light1-status",
        displayValue(data.light1)
    );

    setBulb(
        "light1-bulb",
        data.light1
    );


    // --------------------------------------------------------
    // Light 2
    // --------------------------------------------------------

    setText(
        "light2-status",
        displayValue(data.light2)
    );

    setBulb(
        "light2-bulb",
        data.light2
    );


    // --------------------------------------------------------
    // Light 3
    // --------------------------------------------------------

    setText(
        "light3-status",
        displayValue(data.light3)
    );

    setBulb(
        "light3-bulb",
        data.light3
    );


    // --------------------------------------------------------
    // Fault
    // --------------------------------------------------------

    const faultElement =
        el("fault");


    if (faultElement) {

        if (
            data.fault &&
            data.fault !== "none"
        ) {

            faultElement.textContent =
                "⚠ " +
                String(data.fault).toUpperCase();

            faultElement.classList.add(
                "alert"
            );

        }

        else {

            faultElement.textContent =
                "✓ NO FAULT";

            faultElement.classList.remove(
                "alert"
            );

        }

    }


    // --------------------------------------------------------
    // Last Updated
    // --------------------------------------------------------

    setText(
        "last-updated",
        data.last_updated || "Never"
    );


    // --------------------------------------------------------
    // ESP32 Connection
    // --------------------------------------------------------

    updateConnectionBadge(
        Boolean(data.esp32_connected)
    );

}


// ============================================================
// FETCH STATUS
// ============================================================

async function refreshStatus() {


    const controller =
        new AbortController();


    const timeout =
        setTimeout(
            () => controller.abort(),
            FETCH_TIMEOUT_MS
        );


    try {


        const response =
            await fetch(
                "/api/status?_=" +
                Date.now(),
                {
                    method: "GET",

                    cache: "no-store",

                    signal:
                        controller.signal,

                    headers: {
                        "Cache-Control":
                            "no-cache"
                    }
                }
            );


        if (!response.ok) {

            throw new Error(
                "HTTP " +
                response.status
            );

        }


        const data =
            await response.json();


        render(data);


    }

    catch (error) {


        console.error(
            "Dashboard error:",
            error
        );


        // Do not overwrite all the
        // existing data.
        //
        // Only indicate that the browser
        // could not reach Flask.

        const badge =
            el("connection-badge");


        if (badge) {

            badge.textContent =
                "Server unreachable";

            badge.className =
                "badge disconnected";

        }


    }

    finally {


        clearTimeout(timeout);


        // Schedule the next request.

        setTimeout(
            refreshStatus,
            POLL_INTERVAL_MS
        );

    }

}


// ============================================================
// START DASHBOARD
// ============================================================

refreshStatus();
