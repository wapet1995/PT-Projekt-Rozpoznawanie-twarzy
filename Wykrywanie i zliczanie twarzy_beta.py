#!/usr/bin/python
import time
import cv2
import imutils
from picamera.array import PiRGBArray
from picamera import PiCamera
import thread
import sys

# Zaladuj plik z klasyfikatorami do wykrycia twarzy
face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_alt.xml")

''' inicjalizacja parametrow kamery
----------------------------------------------------------------------------------------'''
camera = PiCamera(resolution=(640, 480))  # ustawienie wymiarow obrazu
camera.iso = 800
camera.led = False
rawCapture = PiRGBArray(camera, size=(640, 480))
camera.rotation = 180
camera.brightness = 55
camera.framerate = 24  # w ciemnosci 0.5,          w dzien 24
camera.color_effects = None  # w ciemnosci (128,128),    w dzien None
camera.exposure_mode = 'auto'  # w ciemnosci night,        w dzien auto
camera.shutter_speed = 6000000
time.sleep(0.25)

camera.start_preview()  # rezerwacja zosobow kamery
time.sleep(2)

''' inicjacja zmiennych globalnych
----------------------------------------------------------------------------------------'''
faces = []  # tablica przechowujaca wykryte twarze
gray = None
is_dark = 0  # zmienna oznaczajaca czy jest ciemno

# ustalenie pierwszej klatki z kamery
camera.capture(rawCapture, format='bgr', use_video_port=True)
frame = rawCapture.array
rawCapture.truncate(0)

# wybor algorytmu rozpoznajacego twarze
recognizer = cv2.createFisherFaceRecognizer()

# Ustalenie wymierow twarzy przy rozpoznawaniu twarzy
witdh_face = 250
hight_face = 250


'''  pobieranie biezacej klatki
----------------------------------------------------------------------------------------'''
def make_frame():
    global frame
    while True:
        camera.capture(rawCapture, format='bgr', use_video_port=True)
        frame = rawCapture.array
        rawCapture.truncate(0)


'''  wykrywanie twarzy
----------------------------------------------------------------------------------------'''
def detect_faces():
    global frame
    global faces
    global gray
    while True:
        # przekonwertuj na odcienie szarosci
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)
        # wykryj twarze
        faces = face_cascade.detectMultiScale(gray, 1.3, 4)


'''  MAIN
----------------------------------------------------------------------------------------'''
if __name__ == '__main__':
    thread.start_new_thread(make_frame, ())
    thread.start_new_thread(detect_faces, ())
    while True:
        if len(faces) == 0:
            cv2.putText(frame, "Nie wykryto twarzy", (10, 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        else:
            # wyroznij twarze umieszczajac je w ramkach
            for (x, y, w, h) in faces:
                cropped = gray[y: y + hight_face, x: x + witdh_face].copy()
                nbr_predicted, conf = recognizer.predict(cropped)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(frame, nbr_predicted + " " + conf, (10, 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            # dodaj do klatki tekst mowiacy o ilosci wykrytych twarzy
            cv2.putText(frame, "Wykryte: {} twarze".format(len(faces)), (10, 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        cv2.imshow("Wykrywanie twarzy", frame)
        # zamykanie programu po wcisnieciu ESC
        key = cv2.waitKey(10)
        if key == 27:
            cv2.destroyWindow("Wykrywanie twarzy")
            break
    camera.stop_preview()
    cv2.destroyAllWindows()
    sys.exit()
