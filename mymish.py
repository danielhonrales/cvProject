
import cv2
import numpy as np
import time

class card_info:

    def __init__(self):
        self.outline = [] 
        self.center = [] 
        self.subimage = [] 
       
def locard(img):
    
    conts,tier = cv2.findContours(img,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    var =range(len(conts))
    sorter = sorted(var, key=lambda i : cv2.contourArea(conts[i]),reverse=True)

  
    if len(conts) != 0:
        
        iscard = np.zeros(len(conts),dtype=bool)
        newcont = []
        newtier = []

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
    else: 
        return [], []

    return newcont, iscard


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

stream = cv2.VideoCapture(0)
stream.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
stream.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
font = cv2.FONT_HERSHEY_SIMPLEX
time.sleep(1) 
cam_quit = 0 

while cam_quit == 0:
    ret, image = stream.read()
    pre = procimg(image)    
    contsort,  iscard = locard(pre)
    card = []
    for i in range(len(contsort)):
        if ( iscard[i] == True):
            card.append(cardpoc(contsort[i],image))
            
    temps = []
    for i in range(len(card)):
        temps.append(card[i].outline)

        cv2.drawContours(image,temps, -1, (255,0,0), 2)
            
    cv2.imshow("pokemon detection",image)
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        cam_quit = 1

stream.release()
cv2.destroyAllWindows()






