const expirationTimestamp = Number(
    document.body.dataset.expiration
);

const countdownElement = document.getElementById("countdown");
const timerElement = document.getElementById("session-timer");

function updateTimer() {
    const currentTime = Date.now() / 1000;
    const remainingTime = Math.max(
        0,
        Math.ceil(expirationTimestamp - currentTime)
    );

    const minutes = Math.floor(remainingTime / 60);
    const seconds = remainingTime % 60;

    countdownElement.textContent =
        `${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}`;

    if (remainingTime <= 0) {
        timerElement.textContent = "Sesja wygasła";

        // Na telefonie odświeżamy stronę, aby wyświetlić komunikat o wygaśnięciu.
        if (window.location.pathname.startsWith("/upload/")) {
            window.location.reload();
        } else {
            // Na komputerze ukrywamy nieaktualny kod QR.
            const qrImage = document.querySelector('img[src="/qr"]');

            if (qrImage) {
                qrImage.hidden = true;
            }

            // Pokazujemy przycisk rozpoczęcia nowej sesji.
            const newSessionForm = document.getElementById("new-session-form");

            if (newSessionForm) {
                newSessionForm.hidden = false;
            }
        }
    }
}

if (Number.isFinite(expirationTimestamp) && countdownElement && timerElement) {
    updateTimer();
    const timerInterval = setInterval(updateTimer, 1000);
}
