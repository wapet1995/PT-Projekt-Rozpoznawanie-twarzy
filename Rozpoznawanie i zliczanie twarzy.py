#!/usr/bin/python
import time
import cv2
import imutils
from picamera.array import PiRGBArray
from picamera import PiCamera
import thread
import sys
import MySQLdb

# ustawienie wymiarow obrazu z kamery
camera_width = 640
camera_hight = 480

# wybor algorytmu rozpoznajacego twarze
recognizer = cv2.createFisherFaceRecognizer()

# Zaladuj plik z klasyfikatorami do wykrycia twarzy
face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_alt.xml")

''' inicjalizacja parametrow kamery
----------------------------------------------------------------------------------------'''
camera = PiCamera(resolution=(camera_width, camera_hight))  # ustawienie wymiarow obrazu zkamery
camera.iso = 800
camera.led = False
rawCapture = PiRGBArray(camera, size=(camera_width, camera_hight))
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
faces = []      # tablica przechowujaca wykryte twarze
gray = None     #
is_dark = 0     # zmienna oznaczajaca czy jest ciemno

# ustalenie pierwszej klatki z kamery
camera.capture(rawCapture, format='bgr', use_video_port=True)
frame = rawCapture.array
rawCapture.truncate(0)

# Ustalenie wymierow twarzy przy rozpoznawaniu twarzy
witdh_face = 250
hight_face = 250


'''  pobieranie biezacej klatki z kamery
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
        faces = face_cascade.detectMultiScale(gray, 1.3, 6)


'''  MAIN
----------------------------------------------------------------------------------------'''
if __name__ == '__main__':
    try:
        # uruchomienie watkow odpowiedzialnych za wykonywanie klatek i wykrywanie twarzy
        thread.start_new_thread(make_frame, ())
        thread.start_new_thread(detect_faces, ())

        # wybor pliku z wytrenowanymi twarzami z poziomu komendy konsolowej
        if len(sys.arg) > 0:
            recognizer.load(sys.argv[1])
        else:
            recognizer.load("wytrenowany_plik.mdl")

        while True:
            # czy liczba wykrytych twarzy jest zerem?
            if len(faces) == 0:
                # jesli tak, dodaj do klatki napis "Nie wykryto twarzy"
                cv2.putText(frame, "Nie wykryto twarzy", (10, 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            else:
                # jesli nie, przeszukaj wszystkie twarze
                # wyroznij twarze umieszczajac je w ramkach
                for (x, y, w, h) in faces: # x, y - wspolrzedne wykrytej twarzy, w, h - wymiary wykrytej twarzy
                    cropped = gray[y: y + hight_face, x: x + witdh_face].copy()
                    cv_size = lambda img: tuple(img.shape[1::-1])
                    # sprawdzenie czy obraz nadaje sie do rozponawania twarzy
                    if not(cv_size(cropped)[0] == witdh_face and cv_size(cropped)[1] == hight_face):
                        pass
                    else:
                        # rozpoznaj twarze, przypisz wyszukana etykie oraz wspolczynnik odleglosci od originalnego obrazu
                        nbr_predicted, conf = recognizer.predict(cropped)
                        # polaczenie z baza danych
                        conn = MySQLdb.connect(host="localhost", user="root", passwd="inteligentnyzamek", db="Rozpoznawanie_twarzy_db")
                        c = conn.cursor()
                        # wykonanie zapytania wyszukujacego osobe na podstawie etykiety
                        c.execute("SELECT * FROM Osoby where LABEL = '%d'" % nbr_predicted)
                        person = c.fetchall()
                        # dodanie do klatki napisow o znalezionej osobie i wspolczynniku dopasowania obrazow
                        cv2.putText(frame, str(person[0][1]) + " " + str(person[0][2]), (x + 5, y + 15),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                        cv2.putText(frame, str(conf), (x + 5, y + h - 5),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                    # dodanie ramki do klatki w okolo wykrytej twarzy
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                # dodaj do klatki tekst mowiacgo o liczbie wykrytych twarzy
                cv2.putText(frame, "Wykryte twarze: {}".format(len(faces)), (10, 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            # wydrukowanie na ekranie klatki
            cv2.imshow("Wykrywanie twarzy", frame)
            key = cv2.waitKey(10)
            if key == 27:
                cv2.destroyWindow("Wykrywanie twarzy")
                break
    except Exception:
        camera.stop_preview()
        cv2.destroyAllWindows()
        sys.exit()
