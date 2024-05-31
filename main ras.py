# pip install -r requirements.txt
import cv2 as cv
import time
import os
from datetime import datetime
import json
import serial
import pynmea2
import requests

# Define function to read GPS data from NEO-6M module
def read_gps_data(ser):
    try:
        while True:
            data = ser.readline().decode('ascii')
            if data.startswith('$GPGGA'):
                msg = pynmea2.parse(data)
                latitude = msg.latitude
                longitude = msg.longitude
                return latitude, longitude
    except Exception as e:
        print(f"Error reading GPS data: {e}")
        return None, None

# Define function to get geolocation using IP-based service
def get_geolocation():
    try:
        response = requests.get('https://ipinfo.io/json')
        data = response.json()
        lat, lon = data['loc'].split(',')
        return float(lat), float(lon)
    except Exception as e:
        print(f"Error getting geolocation: {e}")
        return None, None

# Reading label names from obj.names file
class_name = []
try:
    with open('utils/obj.names', 'r') as f:
        class_name = [cname.strip() for cname in f.readlines()]
except Exception as e:
    print(f"Error reading label names: {e}")

# Importing model weights and config file
# Defining the model parameters
net1 = cv.dnn.readNet('utils/yolov4_tiny.weights', 'utils/yolov4_tiny.cfg')
net1.setPreferableBackend(cv.dnn.DNN_BACKEND_OPENCV)
net1.setPreferableTarget(cv.dnn.DNN_TARGET_CPU)
model1 = cv.dnn_DetectionModel(net1)
model1.setInputParams(size=(640, 480), scale=1/255, swapRB=True)

# Defining the video source (0 for camera or file name for video)
try:
    cap = cv.VideoCapture(0)  # Use 0 for webcam
    width  = cap.get(3)
    height = cap.get(4)
except Exception as e:
    print(f"Error opening video source: {e}")
    exit(1)

# Connect to GPS module via serial port
try:
    ser = serial.Serial('/dev/ttyAMA0', baudrate=9600, timeout=1)
except Exception as e:
    print(f"Error connecting to GPS module: {e}")
    ser = None

# Defining parameters for result saving
result_path = "pothole_coordinates"
Conf_threshold = 0.5
NMS_threshold = 0.4
frame_counter = 0
i = 0

# Initialize data list to store pothole information
pothole_data = []

# Detection loop
while True:
    ret, frame = cap.read()
    frame_counter += 1
    if not ret:
        print("Error reading frame")
        break

    # Analysis the stream with detection model
    try:
        classes, scores, boxes = model1.detect(frame, Conf_threshold, NMS_threshold)
    except Exception as e:
        print(f"Error detecting objects: {e}")
        continue

    for (classid, score, box) in zip(classes, scores, boxes):
        label = "pothole"
        x, y, w, h = box
        rec_area = w * h
        frame_area = width * height

        # Adjusted severity calculation
        severity = "Low"
        if rec_area / frame_area > 0.1:
            severity = "High"
        elif rec_area / frame_area > 0.02:
            severity = "Medium"

        # Drawing detection boxes on frame for detected potholes and saving coordinates txt and photo
        if len(scores) != 0 and scores[0] >= 0.7:
            if (rec_area / frame_area) <= 0.1 and box[1] < 600:
                cv.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 1)
                cv.putText(frame, f"Severity: {severity}", (box[0], box[1] - 10), cv.FONT_HERSHEY_COMPLEX, 0.5, (255, 0, 0), 1)

                # Read GPS data
                if ser:
                    latitude, longitude = read_gps_data(ser)
                else:
                    latitude, longitude = get_geolocation()

                # Get current date-time in UTC format
                current_datetime_utc = str(datetime.now())

                # Create dictionary with information
                pothole_info = {
                    "image_path": os.path.join(result_path, f'pot{i}.jpg'),
                    "latitude": latitude,
                    "longitude": longitude,
                    "severity": severity,
                    "datetime_utc": current_datetime_utc
                }

                # Append pothole information to data list
                pothole_data.append(pothole_info)

                # Save frame
                try:
                    cv.imwrite(os.path.join(result_path, f'pot{i}.jpg'), frame)
                    i += 1
                except Exception as e:
                    print(f"Error saving image: {e}")

    # Showing result
    cv.imshow('frame', frame)
    key = cv.waitKey(1)
    if key == ord('q'):
        break

# Save aggregated pothole data to JSON file
try:
    with open('pothole_data.json', 'w') as json_file:
        json.dump(pothole_data, json_file, indent=4)
        print("Pothole data saved")
except Exception as e:
    print(f"Error saving pothole data to JSON file: {e}")

# End
cap.release()
cv.destroyAllWindows()
