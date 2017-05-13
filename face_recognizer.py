#!/usr/bin/python
import cv2
import numpy as np
import os
from PIL import Image

# sciezka do pliku wynikowego z treneningu  (xml)
cascadePath = "haarcascade_frontalface_alt.xml"
faceCascade = cv2.CascadeClassifier(cascadePath)

recognizer = cv2.createFisherFaceRecognizer()
# recognizer = cv2.createEigenFaceRecognizer()
# recognizer = cv2.createLBPHFaceRecognizer()

witdh_face = 250
hight_face = 250

def add_image_to_train_set(choise):
    x=200
    y=200
    w=640
    h=640
    name = raw_input("Podaj imie: ")
    vorname=raw_input("Podaj nazwisko: ")
    index=100
    quantity=0

    #polaczenie z BD
    #conn = MySQLdb.connect(host="localhost", user="root", passwd="inteligentnyzamek", db="Rozpoznawanie_twarzy_db")
    #c = conn.cursor()
    #if choise == "1":
       #wyszukanie id osoby
    #else:
        #zapisujemy w bd
        # odczytujemy nowy numer i wpisujemy do zmiennej index

    count =0
    print "ustaw sie w bialej ramce jak juz bedziesz nacisnij przycisk"
    while(count<10):
        #cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 0), 2)
        print "jesli jestes tylko ty w ramce nacisnij jakis przycisk"
        cv2.waitkey()

        #sprawdzic ile jest twarzy i odczytac

        #jesli jest ilosc twarzy rowna 1
        if(quantity==1):
            count=count+1

            # zapisanie do zmiennej image image
            #zapisanie zdjecia w folderze

    #dodalismy zdjecia mozna przejsc do innej funkcji z treningiem

def get_images_and_labels(path):
    # format pliku (nazwa twarzy [subjectNUMER] po kropce wyraz twarzy
    # nie wrzucamy do treningu pkikow z rozszrezeniem test - sa do testow
    image_paths = [os.path.join(path, f) for f in os.listdir(path) if not f.endswith('.test')]
    images = []
    labels = []

    for image_path in image_paths:
        # wczytanie obrazu i przerobienie na skale szarosci
        image_pil = Image.open(image_path).convert('L')

        # konwersja na numpy array
        image = np.array(image_pil, 'uint8')
        # uzyskanie numeru twarzy z nazwy pliku
        base = os.path.basename(image_path)
        nbr = int(base[6:8])
        print nbr
        print "przewa"
        faces = faceCascade.detectMultiScale(image)
        for (x, y, w, h) in faces:
            images.append(image[y: y + hight_face, x: x + witdh_face])
            #print(image_path)
            # dodanie etykiety
            labels.append(nbr)
    return images, labels


if __name__ == '__main__':
    # sciezka dostepu do plikow z zdjeciami (do nauki)
    #choise = raw_input("jesli chcesz dodac zdjecie do danej osoby wpisz 1 jesli nowa osobe chcesz dodac wpisz 2: ")
    #add_image_to_train_set(choise)

    path = './testowe_zdjecia'
    images, labels = get_images_and_labels(path)
    get_images_and_labels(path)

    # wykonanie treningu i zapisanie
    recognizer.train(images, np.array(labels))
    recognizer.save("wytrenowany_plik.mdl")
    print "koniec treningu"

