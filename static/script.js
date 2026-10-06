// ============================================================
// SMART STREET LIGHT DASHBOARD
// ============================================================

const POLL_INTERVAL_MS = 2000;
const FETCH_TIMEOUT_MS = 5000;

let consecutiveFailures = 0;


// ============================================================
// DOM HELPER
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
// SET TEXT
// ============================================================

function setText(id, value) {

    const element = el(id);

    if (!element) {
        return;
    }

    element.textContent = value;
}


// ============================================================
// SET LIGHT BULB
// ============================================================

function setBulb(id, status) {

    const bulb = el(id);

    if (!bulb) {
        return;
    }

    // Remove old classes
    bulb.className = "light-symbol";


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

function updateConnectionBadge(
    connected
) {

    const badge =
        el("connection-badge");

    if (!badge) {
        return;
    }


    if (connected) {

        badge.textContent =
            "ESP32: Connected";

        badge.className =
            "badge connected";

    }

    else {

        badge.textContent =
            "ESP32: Not connected";

        badge.className =
            "badge disconnected";
    }
}


// ============================================================
// RENDER SERVER DATA
// ============================================================

function render(data) {

    // --------------------------------------------------------
    // ENVIRONMENT
    // --------------------------------------------------------

    setText(
        "environment",
        displayValue(
            data.environment
        )
    );


    // --------------------------------------------------------
    // MOTION
    // --------------------------------------------------------

    setText(
        "motion",
        displayValue(
            data.motion
        )
    );


    // --------------------------------------------------------
    // BRIGHTNESS
    // --------------------------------------------------------

    let brightness =
        Number(data.brightness);


    if (Number.isNaN(brightness)) {

        brightness = 0;
    }


    brightness = Math.max(
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
    // LIGHT 1
    // --------------------------------------------------------

    setText(
        "light1-status",
        displayValue(
            data.light1
        )
    );


    setBulb(
        "light1-bulb",
        data.light1
    );


    // --------------------------------------------------------
    // LIGHT 2
    // --------------------------------------------------------

    setText(
        "light2-status",
        displayValue(
            data.light2
        )
    );


    setBulb(
        "light2-bulb",
        data.light2
    );


    // --------------------------------------------------------
    // LIGHT 3
    // --------------------------------------------------------

    setText(
        "light3-status",
        displayValue(
            data.light3
        )
    );


    setBulb(
        "light3-bulb",
        data.light3
    );


    // --------------------------------------------------------
    // FAULT
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
                String(
                    data.fault
                ).toUpperCase();


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
    // LAST UPDATED
    // --------------------------------------------------------

    setText(
        "last-updated",
        data.last_updated ||
        "Never"
    );


    // --------------------------------------------------------
    // ESP32 CONNECTION
    // --------------------------------------------------------

    updateConnectionBadge(
        Boolean(
            data.esp32_connected
        )
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
                "/api/status?t=" +
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


        // Request succeeded
        consecutiveFailures = 0;


        // Update dashboard
        render(data);

    }


    catch (error) {

        consecutiveFailures++;


        console.error(
            "Dashboard error:",
            error
        );


        const badge =
            el(
                "connection-badge"
            );


        if (badge) {

            if (
                consecutiveFailures <= 2
            ) {

                badge.textContent =
                    "Connecting...";

            }

            else {

                badge.textContent =
                    "Server unreachable";
            }


            badge.className =
                "badge disconnected";
        }

    }


    finally {

        clearTimeout(timeout);
    }
}


// ============================================================
// START DASHBOARD
// ============================================================

setInterval(
    refreshStatus,
    POLL_INTERVAL_MS
);


refreshStatus();
