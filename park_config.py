import cv2
import numpy as np
import cvzone
import pickle

cap = cv2.VideoCapture('video.mp4')

drawing=False
parking_number=[]
try:
    with open("pickle","rb") as f :
            data=pickle.load(f)
            polylines,parking_number=data['polylines'],data['parking_number']
except:
    polylines=[]


points=[]
current_number=" "


def draw(event,x,y,flag,param):
    global points,drawing
    drawing=True
    if event ==cv2.EVENT_LBUTTONDOWN:
        points=[(x,y)]
    elif event==cv2.EVENT_MOUSEMOVE:
        if drawing:
         points.append((x,y))
    elif event==cv2.EVENT_LBUTTONUP:
        drawing=False
        current_number=input('AreaNumber:-')
        if current_number:
            parking_number.append(current_number)
            polylines.append(np.array(points,np.int32))

    

while True:
    ret, frame = cap.read()
    if not ret:
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        continue
    frame=cv2.resize(frame,(1020,500))
    for i,polyline in enumerate (polylines):
        cv2.polylines(frame,[polyline],True,(0,0,255),2)
        cvzone.putTextRect(frame,f'{parking_number[i]}', tuple(polyline[0]),1,1)

    
    cv2.imshow('FRAME', frame)
    cv2.setMouseCallback('FRAME',draw)
    Key = cv2.waitKey(100) & 0xFF
    if Key==ord('s'):
        with open("pickle","wb") as f :
            data={'polylines':polylines,'parking_number':parking_number}
            pickle.dump(data,f)


cap.release()
cv2.destroyAllWindows()

