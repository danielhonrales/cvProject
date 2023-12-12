import VideoStream
import cv2
from datetime import datetime
import os
  
camera = VideoStream.VideoStream((640,360),10,2,2)
camera.start()
 
counter = 0
print('Starting image capture')
while True:
     
    # get image from webcam
    success, image = camera.read()  # read the camera frame
    if not success:
        print("broke")
        break
 
    # display image
    cv2.imshow('grid', image)
    cv2.waitKey(3000)
 
    # save image to file, if pattern found
    ret, corners = cv2.findChessboardCorners(cv2.cvtColor(image,cv2.COLOR_BGR2GRAY), (7,6), None)
 
    if ret == True:
        counter += 1
        print(f'Got image with corners: {counter}')
        filename = datetime.now().strftime('%Y%m%d_%Hh%Mm%Ss%f') + '.jpg'
        cv2.imwrite(filename, image)