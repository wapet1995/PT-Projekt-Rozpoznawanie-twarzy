#!/usr/bin/python

# Import the required modules
import cv2, os
import numpy as np
from PIL import Image

# sciezka do pliku wynikowego z treneningu  (xml)
cascadePath = "haarcascade_frontalface_alt_tree.xml"
faceCascade = cv2.CascadeClassifier(cascadePath)

recognizer = cv2.createFisherFaceRecognizer()
#recognizer = cv2.createEigenFaceRecognizer()
#recognizer = cv2.createLBPHFaceRecognizer()
x1 =250
y1 =250
def get_images_and_labels(path):
    # format pliku (nazwa twarzy [subjectNUMER] po kropce wyraz twarzy
    # nie wrzucamy do treningu pkikow z rozszrezeniem sad
    image_paths = [os.path.join(path, f) for f in os.listdir(path) if not f.endswith('.test')]
    images = []
    labels = []

    for image_path in image_paths:
        #wczytanie obrazu i przerobienie na skale szarosci
        image_pil = Image.open(image_path).convert('L')

        # konwersja na numpy array
        image = np.array(image_pil, 'uint8')
        # uzyskanie numeru twarzy z nazwy pliku
        nbr = int( image_path[20:22])
        # wykrycie twarzy na zdjeciu (skopiowane od Macieja
        faces = faceCascade.detectMultiScale(image)
        #faces = faceCascade.detectMultiScale(image)
        # na wykrytej twarzy
        for (x, y, w, h) in faces:
            images.append(image[y: y + y1, x: x + x1])
            print(image_path)
            #dodanie etykiety
            labels.append(nbr)
            #wyswietlenie dodanej twarzy
            #cv2.imshow("Adding faces to traning set...", image[y: y + y1, x: x + x1])
            cv2.waitKey(50)
    return images, labels

# sciezka dostepu do plikow z zdjeciami (do nauki)
path = './testowe_zdjecia'
# Call the get_images_and_labels function and get the face images and the
# corresponding labels
images, labels = get_images_and_labels(path)
cv2.destroyAllWindows()

# wykonanie treningu
recognizer.train(images, np.array(labels))


image_paths = [os.path.join(path, f) for f in os.listdir(path) if f.endswith('.test')]
for image_path in image_paths:
    predict_image_pil = Image.open(image_path).convert('L')
    print(image_path)
    predict_image = np.array(predict_image_pil, 'uint8')

    faces = faceCascade.detectMultiScale(predict_image)

    for (x, y, w, h) in faces:
        cropped = predict_image[y: y + y1, x: x + x1].copy()
        nbr_predicted, conf = recognizer.predict(cropped)
        nbr_actual = int( image_path[20:22])
        if nbr_actual == nbr_predicted:
            print "{} poprawnie rozpoznane z dokladnoscia ) {}".format(nbr_actual, conf)
        else:
            print "{} niepoprawne rozpoznanie {}".format(nbr_actual, nbr_predicted)
        cv2.imshow("twarz ktora probowano rozpoznac", predict_image[y: y + y1, x: x + x1])
        cv2.waitKey(1000)


#def face_recognition(Image):
# x1 = 250
# y1 =250
# predict_image_pil = Image.convert('L')
# predict_image = np.array(predict_image_pil, 'uint8')
# faces = faceCascade.detectMultiScale(predict_image)
# for (x, y, w, h) in faces:
#     cropped = predict_image[y: y + y1, x: x + x1].copy()
#     nbr_predicted, conf = recognizer.predict(cropped)