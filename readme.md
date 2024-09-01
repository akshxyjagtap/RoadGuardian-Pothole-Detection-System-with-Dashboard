# RoadGuardian: Pothole Detection System using YOLOv4 Tiny

[![MIT license](https://img.shields.io/badge/License-MIT-blue.svg)](https://lbesson.mit-license.org/)

**Dashboard**: [Pothole Detection Dashboard](https://akshxyjagtap.github.io/RoadGuardian-Pothole-Detection-System-with-Dashboard/)

An intelligent Pothole Detection system using YOLOv4 Tiny, capable of identifying and categorizing potholes in real-time video streams. The severity level of each pothole (Low, Medium, High) is assessed based on its area in the frame. This system provides a valuable tool for monitoring road conditions and prioritizing maintenance efforts. The repository includes Python code, YOLO model files, and sample data for easy implementation and testing.

## Overview

The pothole detection system is designed to:

- Process a video stream or file input.
- Detect potholes in the video frames using YOLOv4 Tiny.
- Draw bounding boxes around detected potholes.
- Save images of detected potholes along with their coordinates.
- Display the frames per second (FPS) processed.

## Requirements

- Python
- OpenCV (cv2)
- Geocoder
- Ensure the necessary YOLOv4 Tiny model weights (`yolov4_tiny.weights`) and label names (`obj.names`) are available.

## Usage

1. Ensure that the necessary libraries are installed.
2. Configure the paths to the YOLOv4 Tiny weights, configurations, and label names (`obj.names`) in the Python script.
3. Set the input video source (file path or camera) in the script.
4. Run the appropriate Python script:
   - `main_ras.py` for running on Raspberry Pi.
   - `Main_using_laptop_gps.py` for running on Windows desktop.
5. Press 'q' to stop the video stream and terminate the detection process.


## Web Interface

### Features

- **Pothole Mapping**: Displays pothole locations on a map using Leaflet.js.
- **City Search**: Allows users to search for a city and pan the map to that location.
- **Pothole Analysis**: Generates an analysis report including the average distance between potholes.

### Dashboard Features

- **Interactive Map**: Visualize the locations of detected potholes on an interactive map.
- **Search Functionality**: Users can search for a specific city to zoom in on the map.
- **Pothole Analysis Report**: Provides an analysis report on the dashboard, including the number of potholes detected and the average distance between them.
- **Severity Levels**: Displays the severity levels (Low, Medium, High) of detected potholes.
- **Real-time Updates**: Automatically updates the map and report as new pothole data is processed.

### Usage

1. **Home Page**: The home page provides information about the project and a link to the dashboard.
2. **Dashboard**: The dashboard displays the map with pothole locations and includes a search bar for city search and an analysis report section.

### File Structure

- `index.html`: The home page of the application.
- `dashboard.html`: The main dashboard displaying the map and analysis report.
- `citySearch.js`: JavaScript file for handling city search functionality.
- `potholeData.js`: JavaScript file for fetching and displaying pothole data on the map.
- `pothole_data.json`: JSON file containing pothole data.
- `cities.json`: JSON file containing city data for the search functionality.
- `styles.css`: CSS file for styling the pages (if applicable).

### JSON Data Format

#### `pothole_data.json`

```json
[
    {
        "image_path": "pothole_coordinates/pot94.jpg",
        "latitude": 19.076,
        "longitude": 72.8777,
        "severity": "Low",
        "datetime_utc": "2024-05-29 11:18:38.968232"
    },
    {
        "image_path": "pothole_coordinates/pot95.jpg",
        "latitude": 19.076,
        "longitude": 72.8777,
        "severity": "Low",
        "datetime_utc": "2024-05-29 11:18:38.987330"
    }
]
```
## Parameters and Customization

- Adjust confidence and NMS thresholds for detection accuracy (`Conf_threshold`, `NMS_threshold`).
- Modify the output directory (`result_path`) for saving detected pothole images and coordinates.

## Notes

- Ensure CUDA and GPU support for faster processing if using GPU-enabled OpenCV.
- Fine-tune detection parameters for better accuracy based on specific scenarios and video quality.

