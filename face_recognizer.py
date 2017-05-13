#!/usr/bin/python
import cv2
import numpy as np
import os
from PIL import Image

# sciezka do pliku wynikowego z treneningu  (xml)
cascadePath = "haarcascade_frontalface_alt.xml"
faceCascade = cv2.CascadeClassifier(cascadePath)

#recognizer = cv2.createFisherFaceRecognizer()
# recognizer = cv2.createEigenFaceRecognizer()
recognizer = cv2.createLBPHFaceRecognizer()

witdh_face = 250
hight_face = 250


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
        nbr = int(image_path[20:22])
        image = cv2.equalizeHist(image)
        # wykrycie twarzy na zdjeciu (skopiowane od Macieja
        faces = faceCascade.detectMultiScale(image)
        # faces = faceCascade.detectMultiScale(image)
        # na wykrytej twarzy
        for (x, y, w, h) in faces:
            images.append(image[y: y + hight_face, x: x + witdh_face])
            print(image_path)
            # dodanie etykiety
            labels.append(nbr)
            # wyswietlenie dodanej twarzy
            cv2.imshow("Adding faces to traning set...", image[y: y + hight_face, x: x + witdh_face])
            cv2.waitKey(50)
    return images, labels


if __name__ == '__main__':
    # sciezka dostepu do plikow z zdjeciami (do nauki)
    path = './testowe_zdjecia'
    # Call the get_images_and_labels function and get the face images and the
    # corresponding labels
    images, labels = get_images_and_labels(path)
    cv2.destroyAllWindows()
    recognizer.load("wytrenowany_plik_LBPH.mdl")
    # wykonanie treningu
    recognizer.update(images, np.array(labels))
    recognizer.save("wytrenowany_plik_LBPH.mdl")
    #recognizer.load("wytrenowany_plik.mdl")

    image_paths = [os.path.join(path, f) for f in os.listdir(path) if f.endswith('.test')]
    for image_path in image_paths:
        predict_image_pil = Image.open(image_path).convert('L')
        print(image_path)
        predict_image = np.array(predict_image_pil, 'uint8')

        faces = faceCascade.detectMultiScale(predict_image)

        for (x, y, w, h) in faces:
            cropped = predict_image[y: y + hight_face, x: x + witdh_face].copy()
            nbr_predicted, conf = recognizer.predict(cropped)
            nbr_actual = int(image_path[20:22])
            if nbr_actual == nbr_predicted:
                print "{} poprawnie rozpoznane z dokladnoscia ) {}".format(nbr_actual, conf)
            else:
                print "{} niepoprawne rozpoznanie {}".format(nbr_actual, nbr_predicted)
            cv2.imshow("twarz ktora probowano rozpoznac", predict_image)
            cv2.waitKey(0)
