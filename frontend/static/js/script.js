// script.js
function fetchStatus() {
    fetch('/status')
        .then(response => response.json())
        .then(data => {
            // Update status and location on the page
            document.getElementById('status').innerText = `Status: ${data.status}`;
            document.getElementById('location').innerText =
                `Location: ${data.latitude || 'N/A'}, ${data.longitude || 'N/A'}`;
        })
        .catch(err => {
            console.error("Error fetching status:", err);
        });
}

// Fetch the status every second
setInterval(fetchStatus, 1000);
