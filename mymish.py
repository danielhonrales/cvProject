
import cv2
import numpy as np
import time

class card_info:

    def __init__(self):
        self.outline = [] 
        self.center = [] 
        self.subimage = [] 
       
def locard(img, originalImg):
    
    conts,tier = cv2.findContours(img,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    var = range(len(conts))
    sorter = sorted(var, key=lambda i : cv2.contourArea(conts[i]),reverse=True)

  
    if len(conts) != 0:
        
        iscard = np.zeros(len(conts),dtype=bool)
        newcont = []
        newtier = []
        extrinsics = []

        for i in sorter:
            newtier.append(tier[0][i])
            newcont.append(conts[i])

        var2 =range(len(newcont))
        for i in var2:
            
            peri = cv2.arcLength(newcont[i],True)
            size = cv2.contourArea(newcont[i])
            approx = cv2.approxPolyDP(newcont[i],0.01*peri,True)

            if 25000 < size < 120000 and newtier[i][3] == -1 and len(approx) == 4:
                iscard[i] = True
                rvecs, tvecs = getVectors(originalImg, approx.reshape(4, 2))
                extrinsics.append((rvecs, tvecs))
    else: 
        return [], [], []

    return newcont, iscard, extrinsics

def getVectors(image, points):
    # order points
    points = order_points(points)
 
    # load calibration data
    with np.load('cameraCalibration.npz') as X:
        mtx, dist, _, _ = [X[i] for i in ('mtx','dist','rvecs','tvecs')]
   
    # set up criteria, image, points and axis
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
 
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
 
    imgp = np.array(points, dtype="float32")
 
    objp = np.array([[0.,0.,0.],[1.,0.,0.],
                        [1.,1.,0.],[0.,1.,0.]], dtype="float32")  
 
    # calculate rotation and translation vectors
    cv2.cornerSubPix(gray,imgp,(11,11),(-1,-1),criteria)
    _, rvecs, tvecs, _ = cv2.solvePnPRansac(objp, imgp, mtx, dist)
 
    return rvecs, tvecs

def order_points(points):
 
    s = points.sum(axis=1)
    diff = np.diff(points, axis=1)
     
    ordered_points = np.zeros((4,2), dtype="float32")
 
    ordered_points[0] = points[np.argmin(s)]
    ordered_points[2] = points[np.argmax(s)]
    ordered_points[1] = points[np.argmin(diff)]
    ordered_points[3] = points[np.argmax(diff)]
 
    return ordered_points

def cardpoc(cont, image):
    
    currentcard = card_info()
    currentcard.outline = cont

    x,y,w,h = cv2.boundingRect(cont)
  
    M = cv2.moments(cont)
    cent_x = int(M['m10'] / M['m00'])
    cent_y = int(M['m01'] / M['m00'])

    currentcard.center = [cent_x, cent_y]
    currentcard.subimage = image[y:y + h, x:x + w]
    return currentcard

def procimg(image):
  
    grayimg = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    blurimg = cv2.GaussianBlur(grayimg,(5,5),0)
    height = image.shape[0]
    width = image.shape[1]
    backgrounglvl = grayimg[int(height/90)][int(width/2.5)]
    lvl = backgrounglvl + 60
    val, thresh = cv2.threshold(blurimg,lvl,255,cv2.THRESH_BINARY)
    return thresh






