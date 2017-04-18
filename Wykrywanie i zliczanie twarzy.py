#!/usr/bin/python
import time
import cv2
from picamera.array import PiRGBArray
from picamera import PiCamera

# inicjalizacja parametrow kamery
camera = PiCamera()
camera.resolution = (320, 240)
camera.framerate = 30
rawCapture = PiRGBArray(camera, size=(320, 240))
camera.rotation = 180
camera.video_stabilization = True
time.sleep(0.25)

# Zaladuj plik z klasyfikatorami do wykrycia twarzy
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_alt.xml')

while True:
    # pobierz bierzaca klatke
    camera.capture(rawCapture, format='bgr', use_video_port=True)
    frame = rawCapture.array
    rawCapture.truncate(0)

    # wykryj twarze
    faces = face_cascade.detectMultiScale(frame, 1.2, 6)

    # dodaj do klatki tekst mowiacy o ilosci wykrytych twarzy
    cv2.putText(frame, "Wykryto: {} twarzy".format(str(len(faces))), (10, 20),
        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

    # wyroznij twarze umieszczajac je w ramkach
    for (x,y,w,h) in faces:
        cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2)

    cv2.imshow("Wykrywanie twarzy", frame)

    # zamykanie programu po wcisnieciu ESC
    key = cv2.waitKey(10)
    if key == 27:
        cv2.destroyWindow("Wykrywanie twarzy")
        break

cv2.destroyAllWindows()