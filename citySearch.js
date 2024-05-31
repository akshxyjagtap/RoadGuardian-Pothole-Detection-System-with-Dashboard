let cityMap;
let pinMarker; // To keep track of the placed pin

// Function to initialize the city map
function initCityMap() {
    cityMap = L.map('map').setView([20, 77], 5); // Default center (India)

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(cityMap);

    cityMap.on('click', onMapClick); // Add event listener for map clicks
}

// Function to search for a city and update the map
function searchCity() {
    const searchInput = document.getElementById('citySearchInput').value.toLowerCase().trim();

    if (!searchInput) {
        alert('Please enter a city name.');
        return;
    }

    fetch('cities.json')
        .then(response => response.json())
        .then(data => {
            const city = data.cities.find(c => c.name.toLowerCase() === searchInput);

            if (city) {
                cityMap.panTo([city.latitude, city.longitude]);
                cityMap.setZoom(10); // Adjust zoom level
                analyzeArea(city.latitude, city.longitude, 100); // Analyze area with default radius of 100 km
            } else {
                alert('City not found!');
            }
        })
        .catch(error => {
            console.error('Error fetching city data:', error);
            alert('Error fetching city data. Please try again later.');
        });
}

// Function to handle map clicks
function onMapClick(event) {
    if (pinMarker) {
        cityMap.removeLayer(pinMarker);
    }

    pinMarker = L.marker(event.latlng).addTo(cityMap);

    const radius = prompt('Enter the radius around the pin (in kilometers):');
    if (radius) {
        const latitude = event.latlng.lat;
        const longitude = event.latlng.lng;
        analyzeArea(latitude, longitude, parseFloat(radius));
    }
}

// Function to analyze potholes in a specified area with a given radius
function analyzeArea(latitude, longitude, radius) {
    fetch('pothole_data.json')
        .then(response => response.json())
        .then(data => {
            // Filter pothole data for the specified area using latitude and longitude
            const areaPotholes = data.filter(pothole => {
                const distance = calculateDistance(latitude, longitude, pothole.latitude, pothole.longitude);
                return distance < radius; // Use the specified radius
            });

            // Perform analysis on the filtered data
            const numPotholes = areaPotholes.length;
            const averageSeverity = calculateAverageSeverity(areaPotholes);

            // Generate a report based on the analysis
            const report = `
                <h2>Area Analysis Report</h2>
                <p>Latitude: ${latitude}</p>
                <p>Longitude: ${longitude}</p>
                <p>Radius: ${radius} km</p>
                <p>Number of Potholes Detected: ${numPotholes}</p>
                <p>Average Severity: ${averageSeverity}</p>
                <!-- Add more analysis results here -->
            `;
            document.getElementById('analysisReport').innerHTML = report;
        })
        .catch(error => {
            console.error('Error fetching pothole data:', error);
            alert('Error fetching pothole data. Please try again later.');
        });
}

// Helper function to calculate distance between two points (in kilometers)
function calculateDistance(lat1, lon1, lat2, lon2) {
    const R = 6371; // Radius of the Earth in kilometers
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLon = (lon2 - lon1) * Math.PI / 180;
    const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
              Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
              Math.sin(dLon / 2) * Math.sin(dLon / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    return R * c;
}

// Helper function to calculate average severity of potholes
function calculateAverageSeverity(potholes) {
    if (potholes.length === 0) return 'N/A';

    const totalSeverity = potholes.reduce((acc, pothole) => acc + severityValue(pothole.severity), 0);
    return (totalSeverity / potholes.length).toFixed(2);
}

// Helper function to assign numeric values to severity levels
function severityValue(severity) {
    switch (severity.toLowerCase()) {
        case 'low':
            return 1;
        case 'medium':
            return 2;
        case 'high':
            return 3;
        default:
            return 0;
    }
}

// Initialize the city map when the script is loaded
document.addEventListener('DOMContentLoaded', initCityMap);
