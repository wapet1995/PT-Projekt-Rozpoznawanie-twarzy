# -*- coding: utf-8 -*-
# !/usr/bin/python
import cv2
import numpy as np
import os
from PIL import Image
import MySQLdb
import time
from datetime import datetime
import sys

# sciezka do pliku wynikowego z treneningu  (xml)
face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_alt.xml")

recognizer = cv2.createFisherFaceRecognizer()
# recognizer = cv2.createEigenFaceRecognizer()
# recognizer = cv2.createLBPHFaceRecognizer()

ip_server = None

witdh_face = 250
hight_face = 250
w_frame = 640
h_frame = 480
photos = 10
path_photos = 'baza_zdjec'


def add_image(choise = "camera"):
    images = []
    labels = []
    name = raw_input("Podaj imię: ")
    surname = raw_input("Podaj nazwisko: ")
    try:
        # polaczenie z BD
        conn = MySQLdb.connect(host=ip_server, port=3306, user="maciej", passwd="WApet1995",
                               db="Rozpoznawanie_twarzy_db")
        c = conn.cursor()
        c.execute("SELECT LABEL FROM Osoby WHERE NAME = %s and SURNAME = %s", (name, surname))
        label = c.fetchall()
        if len(label) > 0:
            c.execute("INSERT INTO Osoby(NAME, SURNAME) VALUES (%s,%s)", (name, surname))
            c.execute("SELECT LABEL FROM Osoby WHERE NAME = %s and SURNAME = %s", (name, surname))
            label = c.fetchall()
    except:
        raw_input("Problem z połączeniem z bazą danych. Proszę naprawić połączenie i spróbować ponownie")
        sys.exit(0)

    if choise == "camera":
        camera = cv2.VideoCapture(0)
        time.sleep(0.25)
        frame = camera.read()[1]
        cv_size = lambda img: tuple(frame.shape[1::-1])
        x_frame = int(cv_size(frame)[0] / 2) - int(w_frame / 2)
        y_frame = int(cv_size(frame)[1] / 2) - int(h_frame / 2)

        photo_counter = 0
        photo_take = False
        while photo_counter < photos:
            while not (photo_take):
                frame = camera.read()[1]
                gray = frame[y_frame: y_frame + h_frame, x_frame: x_frame + w_frame].copy()
                gray = cv2.cvtColor(gray, cv2.COLOR_BGR2GRAY)
                cv2.rectangle(frame, (x_frame, y_frame), (x_frame + w_frame, y_frame + h_frame), (255, 255, 255), 2)
                # wykryj twarze
                faces = face_cascade.detectMultiScale(gray, 1.3, 8)
                cv2.putText(frame, "Umiesc twarz w ramce, zdjecie " + str(photo_counter) + " z  " + str(photos),
                            (10, 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                if len(faces) == 1:
                    for (x, y, w, h) in faces:
                        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                        if (w <= witdh_face + 50) and (w >= witdh_face - 50) and (h <= hight_face + 50) and (
                            h >= hight_face - 50):
                            cv2.putText(frame, "Wcisnik spacje, aby wykonac zdjecie", (x + 5, y + 10),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                            key = cv2.waitKey(100)
                            if key == 32:
                                images.append(gray[y: y + hight_face, x: x + witdh_face])
                                labels.append(label)
                                photo_counter += 1
                                cv2.imwrite("./" + path_photos + "/" + str(label) + "_" + datetime.now().strftime('%Y-%m-%d %H_%M_%S_') + str(photo_counter) + ".JPG", gray)
                                photo_take = True
                                time.sleep(0.1)
                        else:
                            cv2.putText(frame, "Oddal lub przybliz sie", (x + 5, y + 10),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                else:
                    if len(faces) > 1:
                        for (x, y, w, h) in faces:
                            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                        cv2.putText(frame, "W ramce powinna znajdowac sie tylko jedna twarz", (20, 40),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                    else:
                        cv2.putText(frame, "W ramce nie znajduje sie twarz", (20, 40),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                cv2.imshow("Dodawanie zdjecia z kamery", frame)
                key = cv2.waitKey(100)
                if key == 27:
                    photo_counter = 10
                    break

            if photo_counter >= 10:
                cv2.destroyAllWindows()
                camera.release()
                key = raw_input("Czy chcesz ponownie dodać zdjęcia?: T/N")
                while True:
                    if key == "t" or key == "T":
                        camera = cv2.VideoCapture(0)
                        photo_counter = 0
                        break
                    else:
                        if key == "n" or key == "N":
                            break
                    key = raw_input()
            else:
                photo_take = False
    else:
        images, labels = get_new_images_and_labels(images, labels, choise)
    images, labels = get_images_and_labels(images, labels, "./" + path_photos)
    return images, labels
    # dodalismy zdjecia mozna przejsc do innej funkcji z treningiem


def get_new_images_and_labels(images, labels, path):
    # format pliku (nazwa twarzy [subjectNUMER] po kropce wyraz twarzy
    # nie wrzucamy do treningu pkikow z rozszrezeniem test - sa do testow
    image_paths = [os.path.join(path, f) for f in os.listdir(path) if (f.endswith('.JPG') or f.endswith('.jpg') or f.endswith('.Jpg') or f.endswith('.PNG') or f.endswith('.png') or f.endswith('.Png'))]
    index = 0
    for image_path in image_paths:
        # wczytanie obrazu i przerobienie na skale szarosci
        image_pil = Image.open(image_path).convert('L')

        # konwersja na numpy array
        image = np.array(image_pil, 'uint8')
        # uzyskanie numeru twarzy z nazwy pliku
        print image_path
        cv2.imwrite(
            "./" + path_photos + "/" + str(label) + "_" + datetime.now().strftime('%Y-%m-%d %H_%M_%S_') + str(
                index) + ".JPG", image)
        index += 1
        faces = face_cascade.detectMultiScale(image, 1.3, 8)
        for (x, y, w, h) in faces:
            images.append(image[y: y + hight_face, x: x + witdh_face])
            # dodanie etykiety
            labels.append(label)
    return images, labels

def get_images_and_labels(images, labels, path):
    # format pliku (nazwa twarzy [subjectNUMER] po kropce wyraz twarzy
    # nie wrzucamy do treningu pkikow z rozszrezeniem test - sa do testow
    image_paths = [os.path.join(path, f) for f in os.listdir(path) if (f.endswith('.JPG') or f.endswith('.jpg') or f.endswith('.Jpg') or f.endswith('.PNG') or f.endswith('.png') or f.endswith('.Png'))]

    for image_path in image_paths:
        # wczytanie obrazu i przerobienie na skale szarosci
        image_pil = Image.open(image_path).convert('L')

        # konwersja na numpy array
        image = np.array(image_pil, 'uint8')
        # uzyskanie numeru twarzy z nazwy pliku
        print image_path
        base = os.path.basename(image_path)
        nbr = base.split("_")[0]
        if is_number(nbr):
            nbr = int(nbr)
            faces = face_cascade.detectMultiScale(image, 1.3, 8)
            for (x, y, w, h) in faces:
                images.append(image[y: y + hight_face, x: x + witdh_face])
                # dodanie etykiety
                labels.append(nbr)
        else:
            print "Nie dodano: " + image_path + " z powodu błednej nazwy"
    return images, labels

def is_number(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

if __name__ == '__main__':
    ip_server = raw_input("Podaj ip serwera: ")
    while True:
        # choise = raw_input("jesli chcesz dodac zdjecie do danej osoby wpisz 1 jesli nowa osobe chcesz dodac wpisz 2: ")
        choise = raw_input("Wybierz sposób dodawania: \n\t camera - danie zdjęć bezpośrednio z kamery, \n\t <pełna ścieżka folderu> - pełna ścieżka do folderu z nowymi zdjeciami \n\t q - wyjście z prgramu wybór:")
        if choise == "q":
            sys.exit(0)
        images, labels = add_image(choise)
        if len(images) == len(labels) and len(images) > 1:
            # wykonanie treningu i zapisanie
            recognizer.train(images, np.array(labels))
            recognizer.save("wytrenowany_plik.mdl")
            print "koniec treningu"

