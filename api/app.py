import json
from flask import Flask, render_template, Response
from flask_cors import CORS
import time
import pickle
import pandas as pd
import cv2
from ultralytics import YOLO

app = Flask(__name__, template_folder='../front-end/templates', static_folder='../front-end/static')
CORS(app, resources={r'/events': {'origins': 'http://127.0.0.1:5000'}})

# Initialize data
with open("pickle", "rb") as f:
    data = pickle.load(f)
    polylines, parking_number = data['polylines'], data['parking_number']

my_file = open("coco.txt", "r")
data = my_file.read()
class_list = data.split("\n")

# Initialize YOLO model
model = YOLO('yolov8s.pt')

# Initialize VideoCapture
cap = cv2.VideoCapture('video.mp4')

def get_parking_status(px, polylines, parking_number):
    list1 = []
    list2 = []
    for index, row in px.iterrows():
        x1 = int(row[0])
        y1 = int(row[1])
        x2 = int(row[2])
        y2 = int(row[3])
        d = int(row[5])

        c = class_list[d]
        cx = int(x1 + x2) // 2
        cy = int(y1 + y2) // 2
        if 'car' in c:
            list1.append([cx, cy])

    counter1 = []
    for i, polyline in enumerate(polylines):
        list2.append(i)
        for i1 in list1:
            cx1 = i1[0]
            cy1 = i1[1]
            result = cv2.pointPolygonTest(polyline, ((cx1, cy1)), False)
            if result >= 0:
                counter1.append(i)  # i is the index of the parking area

    area_status = {parking_number[i]: i not in counter1 for i in list2}
    total_free_spaces = sum(1 for full in area_status.values() if not full)

    return area_status, total_free_spaces

def event_stream():
    with app.app_context():
        while True:
            time.sleep(1)  # Adjust the sleep time as needed

            _, frame = cap.read()
            frame = cv2.resize(frame, (1020, 500))
            results = model.predict(frame)
            a = results[0].boxes.data
            px = pd.DataFrame(a).astype("float")

            area_status, total_free_spaces = get_parking_status(px, polylines, parking_number)

            # Convert area_status dictionary to a list of objects
            area_status_list = [{"AreaNumber": name, "Full": full} for name, full in area_status.items()]

            data = {"area_status": area_status_list, "total_free_spaces": total_free_spaces}
            yield f"data: {json.dumps(data)}\n\n"


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/events')
def sse():
    return Response(event_stream(), content_type='text/event-stream')

if __name__ == '__main__':
    app.run(debug=True, threaded=True)
