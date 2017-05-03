#!/usr/bin/python
import time
import cv2
import imutils
from picamera.array import PiRGBArray
from picamera import PiCamera
import thread

# inicjalizacja parametrow kamery
camera = PiCamera(
    resolution=(640, 480))
camera.iso = 800
camera.led = False
rawCapture = PiRGBArray(camera, size=(640, 480))
camera.rotation = 180
camera.brightness = 55
camera.framerate =  24          # w ciemnosci 0.5,          w dzien 24
camera.color_effects = None     # w ciemnosci (128,128),    w dzien None
camera.exposure_mode = 'auto'   # w ciemnosci night,        w dzien auto
camera.shutter_speed = 6000000
time.sleep(0.25)

camera.start_preview()
time.sleep(2)

# pobierz bierzaca klatke
camera.capture(rawCapture, format='bgr', use_video_port=True)
frame = rawCapture.array
rawCapture.truncate(0)

faces = []

def make_frame():
    global frame
    while True:
        # pobierz bierzaca klatke
        camera.capture(rawCapture, format='bgr', use_video_port=True)
        frame = rawCapture.array
        rawCapture.truncate(0)

def detect_faces():
    global frame
    global faces
    while True:
        # przekonwertuj na odcienie szarosci
        #gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # wykryj twarze
        faces = face_cascade.detectMultiScale(frame, 1.2, 6)
        # wyroznij twarze umieszczajac je w ramkach
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        # dodaj do klatki tekst mowiacy o ilosci wykrytych twarzy
        cv2.putText(frame, "Wykryto: {} twarzy".format(len(faces)), (10, 20),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)


# Zaladuj plik z klasyfikatorami do wykrycia twarzy
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_alt.xml')

thread.start_new_thread(make_frame,())
thread.start_new_thread(detect_faces,())
while True:
    # wyroznij twarze umieszczajac je w ramkach
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
    # dodaj do klatki tekst mowiacy o ilosci wykrytych twarzy
    cv2.putText(frame, "Wykryto: {} twarzy".format(len(faces)), (10, 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    cv2.imshow("Wykrywanie twarzy", frame)
    # zamykanie programu po wcisnieciu ESC
    key = cv2.waitKey(10)
    if key == 27:
        cv2.destroyWindow("Wykrywanie twarzy")
        break
camera.stop_preview()
cv2.destroyAllWindows()
