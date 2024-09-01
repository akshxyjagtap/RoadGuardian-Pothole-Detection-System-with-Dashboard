import cv2 as cv
import time
import subprocess as sp
import re
import os
import json
import datetime

# Define function to get geolocation using laptop's GPS
def get_geolocation():
    accuracy = 3  # Starting desired accuracy
    pshellcomm = ['powershell']
    pshellcomm.append('add-type -assemblyname system.device; '\
                      '$loc = new-object system.device.location.geocoordinatewatcher;'\
                      '$loc.start(); '\
                      'while(($loc.status -ne "Ready") -and ($loc.permission -ne "Denied")) '\
                      '{start-sleep -milliseconds 100}; '\
                      '$acc = %d; '\
                      'while($loc.position.location.horizontalaccuracy -gt $acc) '\
                      '{start-sleep -milliseconds 100; $acc = [math]::Round($acc*1.5)}; '\
                      '$loc.position.location.latitude; '\
                      '$loc.position.location.longitude; '\
                      '$loc.position.location.horizontalaccuracy; '\
                      '$loc.stop()' % (accuracy))

    try:
        p = sp.Popen(pshellcomm, stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.STDOUT, text=True)
        (out, err) = p.communicate()
        out = re.split('\n', out)
        lat = float(out[0])
        lon = float(out[1])
        radius = int(out[2])
        return lat, lon
    except Exception as e:
        print(f"Error getting geolocation: {e}")
        return None, None

# Function to convert local time to UTC
def local_to_utc(local_dt):
    local_tz = datetime.timezone(datetime.timedelta(hours=5, minutes=30))  # UTC offset for India Standard Time
    local_dt = local_dt.replace(tzinfo=local_tz)
    utc_dt = local_dt.astimezone(datetime.timezone.utc)
    return utc_dt

# Reading label names from obj.names file
class_name = []
try:
    with open(r'utils/obj.names', 'r') as f:
        class_name = [cname.strip() for cname in f.readlines()]
except Exception as e:
    print(f"Error reading label names: {e}")

# Importing model weights and config file
# Defining the model parameters
net1 = cv.dnn.readNet(r'utils/yolov4_tiny.weights', r'utils/yolov4_tiny.cfg')
net1.setPreferableBackend(cv.dnn.DNN_BACKEND_CUDA)
net1.setPreferableTarget(cv.dnn.DNN_TARGET_CUDA_FP16)
model1 = cv.dnn_DetectionModel(net1)
model1.setInputParams(size=(640, 480), scale=1/255, swapRB=True)

# Defining the video source (0 for camera or file name for video)
try:
    cap = cv.VideoCapture(0)  # Use 0 for webcam
    width = cap.get(3)
    height = cap.get(4)
except Exception as e:
    print(f"Error opening video source: {e}")
    exit(1)

# Defining parameters for result saving and get coordinates
# Defining initial values for some parameters in the script
result_path = "pothole_coordinates"
if not os.path.exists(result_path):
    os.makedirs(result_path)

starting_time = time.time()
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

                # Get current date-time in local format and convert to UTC
                current_datetime_local = datetime.datetime.now()
                current_datetime_utc = str(local_to_utc(current_datetime_local))

                # Get geolocation
                latitude, longitude = get_geolocation()

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

    # Writing FPS on frame
    endingTime = time.time() - starting_time
    fps = frame_counter / endingTime

    cv.putText(frame, f'FPS: {fps}', (20, 50), cv.FONT_HERSHEY_COMPLEX, 0.7, (0, 255, 0), 2)

    # Showing result
    cv.imshow('frame', frame)
    key = cv.waitKey(1)
    if key == ord('q'):
        break

    # Save aggregated pothole data to JSON file
    try:
        with open('pothole_data.json', 'w') as json_file:
            json.dump(pothole_data, json_file, indent=4)
            print(pothole_data, "saved")
    except Exception as e:
        print(f"Error saving pothole data to JSON file: {e}")

# End
cap.release()
cv.destroyAllWindows()
