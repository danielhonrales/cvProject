import cv2 as cv
import VideoStream
from termcolor import colored
import os

PORT = 0
camera = VideoStream.VideoStream((1280,720),10,2,PORT).start()
if not camera.isOpened():
	print(colored("Camera not found", "green"), colored("Exiting...", "red"), sep="\n") 
	os._exit(1) # Exits all threads (important if using VideoStream.py)

cv.namedWindow("bruh", cv.WINDOW_AUTOSIZE, cv.WINDOW_OPENGL)

cv.waitKey(0)

cv.destroyAllWindows()