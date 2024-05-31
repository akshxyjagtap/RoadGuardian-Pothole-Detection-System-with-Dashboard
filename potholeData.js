function addPotholeMarkers() {
    fetch('pothole_data.json')
        .then(response => response.json())
        .then(data => {
            if (data && Array.isArray(data)) {
                data.forEach(pothole => {
                    // Extract data from pothole object
                    const lat = pothole.latitude;
                    const lng = pothole.longitude;
                    const imageURL = pothole.image_path;
                    const timestamp = pothole.datetime_utc;
                    const severity = pothole.severity; // Extract severity

                    // Call addPotholeMarker with extracted data
                    addPotholeMarker(lat, lng, imageURL, timestamp, severity);
                });
            } else {
                console.error('Invalid pothole data format');
            }
        })
        .catch(error => {
            console.error('Error fetching pothole data:', error);
        });
}

// Function to add a pothole marker with popup
function addPotholeMarker(lat, lng, imageURL, timestamp, severity) {
    var marker = L.marker([lat, lng]).addTo(cityMap);

    var formattedTimestamp = new Date(timestamp).toLocaleString('en-US', { 
        year: 'numeric', 
        month: '2-digit', 
        day: '2-digit', 
        hour: '2-digit', 
        minute: '2-digit', 
        second: '2-digit', 
        timeZone: 'UTC' 
    });

    var popupContent = `<div class="popup-content">`;
    popupContent += `<img class="popup-image" src="${imageURL}" alt="Pothole Image"><br>`;
    popupContent += `Severity: ${severity}<br>`; // Include severity in popup content
    popupContent += `Reported Date: ${formattedTimestamp}</div>`;

    marker.bindPopup(popupContent);
}

// Call the function to add pothole markers when the page loads
document.addEventListener('DOMContentLoaded', addPotholeMarkers);
