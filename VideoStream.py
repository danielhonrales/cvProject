
from threading import Thread
import cv2
class VideoStream:
    def __init__(self,src=0):
        
        
        self.vid = cv2.VideoCapture(src)
        self.vid.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.vid.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        (self.grabbed, self.frame) = self.vid.read()
        self.stopped = False
    def start(self):

        Thread(target=self.update,args=()).start()
        return self
    def update(self):

        while True:
            if self.stopped:
                self.vid.release()
                return
            (self.grabbed, self.frame) = self.vid.read()

    def read(self):
        return self.frame

    def stop(self):
        self.stopped = True
