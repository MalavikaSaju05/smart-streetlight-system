let lastServerUpdate = null;


function setBulb(elementId, statusText) {

    const bulb = document.getElementById(elementId);

    bulb.className = "light-symbol";

    if (statusText === "bright") {

        bulb.classList.add("bright");

    } else if (statusText === "dim") {

        bulb.classList.add("dim");

    } else if (statusText === "fault") {

        bulb.classList.add("fault");

    } else {

        bulb.classList.add("off");
    }
}


async function refreshStatus() {

    try {

        const response = await fetch(
            "/api/status",
            {
                cache: "no-store"
            }
        );

        if (!response.ok) {

            throw new Error(
                "Server returned " + response.status
            );
        }

        const data = await response.json();


        // =========================
        // ENVIRONMENT
        // =========================

        document.getElementById(
            "environment"
        ).textContent =
            String(data.environment).toUpperCase();


        // =========================
        // MOTION
        // =========================

        document.getElementById(
            "motion"
        ).textContent =
            String(data.motion).toUpperCase();


        // =========================
        // BRIGHTNESS
        // =========================

        let brightness = Number(data.brightness);

        // Convert PWM 0-255 to percentage
        let brightnessPercent =
            Math.round((brightness / 255) * 100);

        document.getElementById(
            "brightness"
        ).textContent =
            brightnessPercent + "%";


        // =========================
        // LIGHT STATUS
        // =========================

        document.getElementById(
            "light1-status"
        ).textContent =
            String(data.light1).toUpperCase();

        document.getElementById(
            "light2-status"
        ).textContent =
            String(data.light2).toUpperCase();

        document.getElementById(
            "light3-status"
        ).textContent =
            String(data.light3).toUpperCase();


        // =========================
        // BULBS
        // =========================

        setBulb(
            "light1-bulb",
            data.light1
        );

        setBulb(
            "light2-bulb",
            data.light2
        );

        setBulb(
            "light3-bulb",
            data.light3
        );


        // =========================
        // FAULT
        // =========================

        const faultEl =
            document.getElementById("fault");


        if (data.fault !== "none") {

            faultEl.textContent =
                "⚠ " + String(data.fault).toUpperCase();

            faultEl.classList.add("alert");

        } else {

            faultEl.textContent =
                "✓ NO FAULT";

            faultEl.classList.remove("alert");
        }


        // =========================
        // LAST UPDATED
        // =========================

        document.getElementById(
            "last-updated"
        ).textContent =
            data.last_updated || "Never";


        // =========================
        // CONNECTION
        // =========================

        const badge =
            document.getElementById(
                "connection-badge"
            );


        if (data.esp32_connected) {

            badge.textContent =
                "ESP32: Connected";

            badge.className =
                "badge connected";

        } else {

            badge.textContent =
                "ESP32: Not connected";

            badge.className =
                "badge disconnected";
        }


        lastServerUpdate =
            Date.now();


    } catch (error) {

        console.error(
            "Dashboard error:",
            error
        );


        const badge =
            document.getElementById(
                "connection-badge"
            );

        badge.textContent =
            "Server unreachable";

        badge.className =
            "badge disconnected";
    }
}


// First update immediately
refreshStatus();


// Refresh every 500 ms
setInterval(
    refreshStatus,
    500
);
