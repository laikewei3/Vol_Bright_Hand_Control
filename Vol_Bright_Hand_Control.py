import cv2
import time
import numpy as np
import hand_tracking_module as htm
import math
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import screen_brightness_control as sbc

wCam, hCam = 640, 480

cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)

pTime = 0
detector = htm.handDetector()


devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
# volume.GetMute()
# volume.GetMasterVolumeLevel()
vol_range = volume.GetVolumeRange()
minVol = vol_range[0]
maxVol = vol_range[1]

vol = 0
vol_percent = np.interp(int(volume.GetMasterVolumeLevel()), [-96, 0], [0, 100])
vol_bar = np.interp(vol_percent, [0, 100], [400, 150])
bright_percent = sbc.get_brightness()[0]
bright_bar = np.interp(bright_percent, [0, 100], [400, 150])
while True:
    success, img = cap.read()
    img = detector.find_hands(img)
    lmList, handsType = detector.find_position(img, draw=False)
    if len(lmList) != 0:
        if 'Left' in handsType:
            x1, y1 = lmList[4][1], lmList[4][2]
            x2, y2 = lmList[8][1], lmList[8][2]
            cx, cy = (x1+x2)//2, (y1+y2)//2

            cv2.circle(img, (x1,y1), 15, (255, 0, 255), cv2.FILLED)
            cv2.circle(img, (x2, y2), 15, (255, 0, 255), cv2.FILLED)
            cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3)
            cv2.circle(img, (cx, cy), 15, (255, 0, 255), cv2.FILLED)

            length = math.hypot(x2-x1, y2-y1)

            # Hand Range = 40-280
            # Volume Range = -96 - 0
            vol = np.interp(length, [40, 280], [minVol, maxVol])
            vol_bar = np.interp(length, [40, 280], [400, 150])
            vol_percent = np.interp(length, [40, 280], [0, 100])
            volume.SetMasterVolumeLevel(vol, None)

            if length < 40:
                cv2.circle(img, (cx, cy), 15, (0, 0, 0), cv2.FILLED)
        elif 'Right' in handsType:
            x1, y1 = lmList[4][1], lmList[4][2]
            x2, y2 = lmList[8][1], lmList[8][2]
            cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

            cv2.circle(img, (x1, y1), 15, (150, 0, 150), cv2.FILLED)
            cv2.circle(img, (x2, y2), 15, (150, 0, 150), cv2.FILLED)
            cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3)
            cv2.circle(img, (cx, cy), 15, (150, 0, 150), cv2.FILLED)

            length = math.hypot(x2 - x1, y2 - y1)

            bright_percent = np.interp(length, [40, 280], [0, 100])
            bright_bar = np.interp(length, [40, 280], [400, 150])
            sbc.set_brightness(bright_percent)

            if length < 40:
                cv2.circle(img, (cx, cy), 15, (0, 0, 0), cv2.FILLED)

    cv2.rectangle(img, (50, 150), (85, 400), (255, 0, 0), 3)
    cv2.rectangle(img, (50, int(vol_bar)), (85, 400), (255, 0, 0), cv2.FILLED)
    cv2.putText(img, f'V:{int(vol_percent)}%', (50, 450), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 0, 0), 1)

    cv2.rectangle(img, (550, 150), (585, 400), (0, 255, 0), 3)
    cv2.rectangle(img, (550, int(bright_bar)), (585, 400), (0, 255, 0), cv2.FILLED)
    cv2.putText(img, f'B:{int(bright_percent)}%', (550, 450), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 255, 0), 1)

    cTime = time.time()
    fps = 1 / (cTime-pTime)
    pTime = cTime

    cv2.putText(img, f'FPS:{int(fps)}', (40, 70), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 150), 1)
    cv2.imshow("Video", img)

    key = cv2.waitKey(1)
    if key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()