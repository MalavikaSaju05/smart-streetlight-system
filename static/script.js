async function updateDashboard()
{
    try
    {
        const response =
            await fetch("/api/status");

        const data =
            await response.json();

        document.getElementById(
            "environment"
        ).textContent =
            data.environment.toUpperCase();

        document.getElementById(
            "motion"
        ).textContent =
            data.motion.toUpperCase();

        document.getElementById(
            "brightness"
        ).textContent =
            Math.round(
                data.brightness / 255 * 100
            ) + "%";

        document.getElementById(
            "light1-status"
        ).textContent =
            data.light1.toUpperCase();

        document.getElementById(
            "light2-status"
        ).textContent =
            data.light2.toUpperCase();

        document.getElementById(
            "light3-status"
        ).textContent =
            data.light3.toUpperCase();

        document.getElementById(
            "fault"
        ).textContent =
            data.fault === "none"
                ? "✓ NO FAULT"
                : "⚠ " + data.fault;

        document.getElementById(
            "last-updated"
        ).textContent =
            data.last_updated;

    }
    catch(error)
    {
        console.error(error);
    }
}

updateDashboard();

setInterval(
    updateDashboard,
    1000
);
