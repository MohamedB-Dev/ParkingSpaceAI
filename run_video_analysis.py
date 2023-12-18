import cv2
import numpy as np
import pickle
import pandas as pd
from ultralytics import YOLO
import cvzone
import json

# Define file paths and frame dimensions
pickle_file = 'parking_data.pkl'
class_file = 'coco.txt'
yolo_weights = 'yolov8s.pt'
video_file = 'video.mp4'
frame_width = 1020
frame_height = 500
frame_process_interval = 12  # Process every third frame

# Load parking space data
with open(pickle_file, "rb") as f:
    data = pickle.load(f)
    polylines, parking_numbers = data['polylines'], data['parking_numbers']

# Load class labels
with open(class_file, "r") as file:
    class_list = file.read().strip().split("\n")

# Initialize YOLO model
model = YOLO(yolo_weights)

# Start video capture
cap = cv2.VideoCapture(video_file)

def process_frame(frame, polylines, parking_numbers):
    """Process a single frame for parking spot detection."""
    frame = cv2.resize(frame, (frame_width, frame_height))
    results = model.predict(frame)
    detections = pd.DataFrame(results[0].boxes.data).astype("float")

    detected_cars = []
    for index, row in detections.iterrows():
        x1, y1, x2, y2, _, class_id = row.astype(int)
        if class_list[class_id] == 'car':
            cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
            detected_cars.append((cx, cy))
            cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 255, 255), 2)

    for i, polyline in enumerate(polylines):
        cv2.polylines(frame, [polyline], True, (0, 255, 0), 2)
        cvzone.putTextRect(frame, str(parking_numbers[i]), tuple(polyline[0]), 1, 1)
        # Check if cars are in the parking spots
        for car in detected_cars:
            if cv2.pointPolygonTest(polyline, car, False) >= 0:
                cv2.circle(frame, car, 5, (255, 0, 0), -1)
                cv2.polylines(frame, [polyline], True, (0, 0, 255), 2)

    detections_person = []
    for index, row in detections.iterrows():
        x1, y1, x2, y2, _, class_id = row.astype(int)
        if class_list[class_id] == 'person':
            cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
            detections_person.append((cx, cy))
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 123, 321), 2)
                  
    # Display the frame
    cv2.imshow('Frame', frame)

def main():
    """Main function to run the video analysis."""
    frame_counter = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue

        frame_counter += 1
        if frame_counter % frame_process_interval == 0:
            process_frame(frame, polylines, parking_numbers)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
