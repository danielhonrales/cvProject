
from threading import Thread
import cv2


class VideoStream:

    def __init__(self, resolution=(640,480),framerate=30,PiOrUSB=1,src=0):
        self.PiOrUSB = 2
        if self.PiOrUSB == 2: 
            self.stream = cv2.VideoCapture(src)
            ret = self.stream.set(3,resolution[0])
            ret = self.stream.set(4,resolution[1])
            (self.grabbed, self.frame) = self.stream.read()
        self.stopped = False

    def start(self):
        Thread(target=self.update,args=()).start()
        return self

    def update(self):
        if self.PiOrUSB == 2: 
            while True:
                if self.stopped:
                    
                    self.stream.release()
                    return

                
                (self.grabbed, self.frame) = self.stream.read()

    def read(self):
        return (self.grabbed, self.frame)

    def isOpened(self):
        # Return true if camera has been initialized
        return self.stream.isOpened()

    def stop(self):
        self.stopped = True
