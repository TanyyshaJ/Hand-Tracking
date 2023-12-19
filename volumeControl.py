import cv2 as cv
import mediapipe as mp
import time
import numpy as np
import handtracking as ht
import math
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

########################
wCam, hCam = 640, 480
########################

capture = cv.VideoCapture(0)

#setting dimensions
capture.set(3, wCam)
capture.set(4, hCam)



devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = interface.QueryInterface(IAudioEndpointVolume)
volRange = volume.GetVolumeRange()
minVol = volRange[0]
maxVol = volRange[1]
vol = 0
volBar = 400
volPer = 0

pTime = 0

detector = ht.HandDetector(detectionCon=0.7)    #since we want it to be more precise

while True:
    success, img = capture.read()

    img = detector.findHands(img=img)
    lmList = detector.findPosition(img=img, draw=False)
    if len(lmList)!=0:
        # print(lmList[4], lmList[8]) 4 and 8 are the codes for the tip of the index and thumb!

        x1, y1 = lmList[4][1], lmList[4][2]
        x2, y2 = lmList[8][1], lmList[8][2]
        cx, cy = (x1+x2)//2, (y1+y2)//2

        cv.circle(img, (x1, y1), 10, (255,0,255), cv.FILLED)    #plotting a circle on the thumb
        cv.circle(img, (x2, y2), 10, (255,0,255), cv.FILLED)    #plotting a circle on the tip of index
        cv.line(img, (x1,y1), (x2,y2), (255,0,0), 3)            #plotting a line between them
        cv.circle(img, (cx, cy), 10, (255,0,255), cv.FILLED)    #plotting a point between the line

        length = math.hypot(x2-x1, y2-y1)   #gives the length of line, helps calculate how low/high will the volume be 
        # print(length)

        #Hand Range: 20-300, given by length
        #Vol Range: -95 to 0, by running the pycaw function

        vol = np.interp(length, [20, 300], [minVol, maxVol])
        volBar = np.interp(length, [20, 300], [400, 150])
        volPer = np.interp(length, [20, 300], [0, 100])
        volume.SetMasterVolumeLevel(vol, None)
        

        if length<50:
            cv.circle(img, (cx, cy), 10, (0,255,0), cv.FILLED)

    #for the rectangle 
    cv.rectangle(img, (50, 150), (85, 400), (0,255,0), 3)
    cv.rectangle(img, (50, int(volBar)), (85, 400), (0,255,0), cv.FILLED)
    cv.putText(img, f"Vol: {int(volPer)}%", (40,450), cv.FONT_HERSHEY_COMPLEX, 1, (0,0,255), 2)

    cTime = time.time()
    fps = 1/(cTime-pTime)
    pTime = cTime

    cv.putText(img, f"FPS: {int(fps)}", (40,70), cv.FONT_HERSHEY_COMPLEX, 1, (255,0,0), 3)
    cv.imshow("Img", img)
    cv.waitKey(1)