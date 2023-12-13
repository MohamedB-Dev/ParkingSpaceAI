import cv2
import numpy as np
import pickle
import pandas as pd
from ultralytics import YOLO
import cvzone


with open("pickle","rb") as f :
            data=pickle.load(f)
            polylines,parking_number=data['polylines'],data['parking_number']


my_file = open("coco.txt", "r")
data = my_file.read()
class_list = data.split("\n")

model=YOLO('yolov8s.pt')


cap=cv2.VideoCapture('video.mp4')

count=0

while True:
    ret, frame = cap.read()
    if not ret:
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        continue
   
    count += 1
    if count % 3 != 0:
       continue

    frame=cv2.resize(frame,(1020,500))
    frame_copy = frame.copy()
    results=model.predict(frame)
    a=results[0].boxes.data
    px=pd.DataFrame(a).astype("float")
    list1=[]    
    list3=[]
    for index,row in px.iterrows():
 
        x1=int(row[0])
        y1=int(row[1])
        x2=int(row[2])
        y2=int(row[3])
        d=int(row[5])
        
        c=class_list[d]
        cx=int(x1+x2)//2
        cy=int(y1+y2)//2
        if 'car' in c:
            list1.append([cx,cy])
            cv2.rectangle(frame,(x1,y1),(x2,y2),(255,255,255),2) 
        if 'person' in c:
            list3.append([cx,cy])
            cv2.rectangle(frame,(x1,y1),(x2,y2),(139,139,0),2) 


    counter1=[]
    list2=[]
    for i,polyline in enumerate (polylines):
        list2.append(i)
        cv2.polylines(frame,[polyline],True,(0,255,0),2)
        cvzone.putTextRect(frame,f'{parking_number[i]}', tuple(polyline[0]),1,1)  
        for i1 in list1 :
            cx1=i1[0]
            cy1=i1[1]
            result=cv2.pointPolygonTest(polyline,((cx1,cy1)),False)
            if result>=0:
                cv2.circle(frame,(cx1,cy1),5,(255,0,0),-1) 
                cv2.polylines(frame,[polyline],True,(0,0,255),2)
                counter1.append(cx1) 


    cv2.imshow('FRAME', frame)  
    key = cv2.waitKey(1) & 0xFF
