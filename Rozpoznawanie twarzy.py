# -*- coding: utf-8 -*-
import picamera  # zaimportowanie biblioteki obsługującej kamerę
from time import sleep  # zaimportowanie biblioteki czasu

camera = picamera.PiCamera()  # utworzenie obiektu kamery

# ustawienie parametrów kamery
camera.sharpness = 0                # ostrość
camera.contrast = 0                 # kontrast
camera.brightness = 50              # jasność
camera.ISO = 0                      # ISO
camera.video_stabilization = False  # stabilizcja obrazu wideo
camera.image_effect = 'none'        # efekty obrazu
camera.color_effects = None         # kolor obrazu
camera.rotation = 180               # kąt obrotu obrazu

while True:
    camera.capture('image.jpg')
    sleep(5)
