# !/usr/bin/python
import cv2
import numpy as np
import os
from PIL import Image
import MySQLdb
import time
from datetime import datetime
import sys
from progress.bar import Bar

# sciezka do pliku wynikowego z treneningu  (xml)
face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_alt.xml")

# wybor algorytmu rozpoznajacego twarz
recognizer = cv2.createLBPHFaceRecognizer(1, neighbors=10)

# zmienna przechowujaca adres IP bazy danych
ip_server = None

# parametry ramki i wielkosci twarzy
witdh_face = 250
hight_face = 250
w_frame = 640
h_frame = 480
photos = 5  # liczba zdjec przy dodawaniu kamera
path_photos = 'baza_zdjec'  # nazwa folderu przechowujacego baze zdjec


def take_label_from_database():
    name = raw_input("Podaj imie: ")
    if name == "":
        name = raw_input("Podaj imie: ")
    surname = raw_input("Podaj nazwisko: ")
    if surname == "":
        surname = raw_input("Podaj nazwisko: ")
    # polaczenie z baza danych
    try:
        conn = MySQLdb.connect(host=ip_server, port=3306, user="maciej", passwd="WApet1995",
                               db="Rozpoznawanie_twarzy_db")
        c = conn.cursor()
        c.execute("SELECT LABEL FROM Osoby WHERE NAME = %s and SURNAME = %s", (name, surname))
        if c.rowcount == 0:
            print "Dodaje uzytkownika do bazy danych: " + name + " " + surname
            c.execute("INSERT INTO Osoby(NAME, SURNAME) VALUES (%s,%s)", (name, surname))
            c.execute("SELECT LABEL FROM Osoby WHERE NAME = %s and SURNAME = %s", (name, surname))
        label = c.fetchone()[0]
		conn.commit()
        conn.close()
        return label
    except:
        raw_input("Problem z polaczeniem z bazz danych. Prosze naprawic polaczenie i sprobowac ponownie")
        sys.exit(0)


def save_named_file(label, index, image):
    cv2.imwrite(
        "./" + path_photos + "/" + str(label) + "_" + datetime.now().strftime('%Y-%m-%d %H_%M_%S_') + str(
            index) + ".JPG", image)


# funkcja odpowiedzialna za dodawanie zdjec danej osoby do treningu
def add_image(images, labels, choise="camera"):
    if choise == "camera":
        # pobranie etykiety z bazy danych
        label = take_label_from_database()
        camera = cv2.VideoCapture(0)  # ustawienie domyslnej kamery
        time.sleep(0.25)
        frame = camera.read()[1]  # pobranie klatki z kamery
        cv_size = lambda img: tuple(frame.shape[1::-1])
        x_frame = int(cv_size(frame)[0] / 2) - int(w_frame / 2)
        y_frame = int(cv_size(frame)[1] / 2) - int(h_frame / 2)
        photo_counter = 0
        photo_take = False
        while photo_counter < photos:
            while not photo_take:
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
                                save_named_file(label, photo_counter, gray)
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
                    photo_counter = photos
                    labels = []
                    images = []
                    break
            if photo_counter >= photos:
                cv2.destroyAllWindows()
                camera.release()
                key = raw_input("Czy chcesz ponownie dodac swoje zdjecia?: T/N \nwybor: ")
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
    return images, labels


def load_files_from_dir(path):
    return [os.path.join(path, f) for f in os.listdir(path) if (
        f.endswith('.JPG') or f.endswith('.jpg') or f.endswith('.Jpg') or f.endswith('.PNG') or f.endswith(
            '.png') or f.endswith('.Png'))]


def get_new_images_and_labels(images, labels, path):
    # pobranie etykiety z bazy danych
    label = take_label_from_database()
    # pobranie zdjec z folderu wskazanaego w zmiennej path
    image_paths = load_files_from_dir(path)
    index = 0
    bar = Bar('\nWgrywanie folderu ' + path + ' : ', max=len(image_paths))
    for image_path in image_paths:
        # wczytanie obrazu i przerobienie na skale szarosci
        image_pil = Image.open(image_path).convert('L')
        # konwersja na numpy array
        image = np.array(image_pil, 'uint8')
        # uzyskanie numeru twarzy z nazwy pliku
        save_named_file(label, index, image)
        index += 1
        faces = face_cascade.detectMultiScale(image, 1.3, 8)
        for (x, y, w, h) in faces:
            images.append(image[y: y + hight_face, x: x + witdh_face])
            # dodanie etykiety
            labels.append(label)
        bar.next()
    bar.finish()
    return images, labels


def get_images_and_labels(images, labels, path):
    # pobranie zdjec z folderu wskazanaego w zmiennej path
    image_paths = load_files_from_dir(path)
    bar = Bar(' Wgrywanie bazy danych: ', max=len(image_paths))
    for image_path in image_paths:
        # wczytanie obrazu i przerobienie na skale szarosci
        image_pil = Image.open(image_path).convert('L')
        # konwersja na numpy array
        image = np.array(image_pil, 'uint8')
        # uzyskanie numeru twarzy z nazwy pliku
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
            print "Nie dodano: " + image_path + " z powodu blednej nazwy"
        bar.next()
    bar.finish()
    return images, labels


def is_number(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


if __name__ == '__main__':
    train_or_update = True
    if len(sys.argv) > 1:
        train_or_update = False
        recognizer.load(sys.argv[1])
    ip_server = raw_input("Podaj adres IP serwera: ")
    while True:
        images, labels = [], []
        is_all_persons = False
        while not is_all_persons:
            choise = raw_input("Wybierz sposob dodawania: \n\t camera - dodanie zdjec bezposrednio z kamery, "
                               "\n\t <pelna sciezka folderu> - pelna sciezka do folderu z nowymi zdjeciami \n\t q - "
                               "wyjscie z programu \n wybor: ")
            if choise == "q":
                sys.exit(0)
            images, labels = add_image(images, labels, choise)
            while True:
                choise = raw_input("Chcesz dodac kolejna osobe?: T/N \n wybor: ")
                if choise == "t" or choise == "T":
                    is_all_persons = False
                    break
                else:
                    if choise == "n" or choise == "N":
                        is_all_persons = True
                        break
                    else:
                        print "Bledna odpowiedz"

        # wykonanie treningu i zapisanie
        if train_or_update:
            images, labels = get_images_and_labels(images, labels, "./" + path_photos)
            print "\nTrwa trenowanie klasyfikatora"
            recognizer.train(images, np.array(labels))
        else:
            if len(images) == len(labels) and len(images) > 0:
                print "\nTrwa aktualizacja klasyfikatora"
                recognizer.update(images, np.array(labels))
            else:
                print "Brak plikow do dodania"
        print "Trwa zapisywanie klasyfikatora do pliku"
        recognizer.save("wytrenowany_plik.mdl")
        print "Koniec treningu"
