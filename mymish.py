
import cv2
import numpy as np
import time
import os
import VideoStream


BKG_THRESH = 60
CARD_MAX_AREA = 120000
CARD_MIN_AREA = 25000


def flattener(image, pts, w, h):
 
    temp_rect = np.zeros((4,2), dtype = "float32")
    s = np.sum(pts, axis = 2)
    tl = pts[np.argmin(s)]
    br = pts[np.argmax(s)]
    diff = np.diff(pts, axis = -1)
    tr = pts[np.argmin(diff)]
    bl = pts[np.argmax(diff)]

    if w <= 0.8*h:
        temp_rect[0] = tl
        temp_rect[1] = tr
        temp_rect[2] = br
        temp_rect[3] = bl

    if w >= 1.2*h: 
        temp_rect[0] = bl
        temp_rect[1] = tl
        temp_rect[2] = tr
        temp_rect[3] = br
    
    if w > 0.8*h and w < 1.2*h: 
        if pts[1][0][1] <= pts[3][0][1]:
            temp_rect[0] = pts[1][0] 
            temp_rect[1] = pts[0][0] 
            temp_rect[2] = pts[3][0] 
            temp_rect[3] = pts[2][0] 

   
        if pts[1][0][1] > pts[3][0][1]:
            temp_rect[0] = pts[0][0] 
            temp_rect[1] = pts[3][0] 
            temp_rect[2] = pts[2][0] 
            temp_rect[3] = pts[1][0] 
            
        
    maxWidth = 200
    maxHeight = 300

   
    dst = np.array([[0,0],[maxWidth-1,0],[maxWidth-1,maxHeight-1],[0, maxHeight-1]], np.float32)
    M = cv2.getPerspectiveTransform(temp_rect,dst)
    warp = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
    
    return warp





class card_info:

    def __init__(self):
        self.outline = [] 
        self.width =0
        self.height = 0 
        self.corner_cords = [] 
        self.center = [] 
        self.subimage = [] 
       
def find_cards(img):
    
    conts,tier = cv2.findContours(img,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    index_sort = sorted(range(len(conts)), key=lambda i : cv2.contourArea(conts[i]),reverse=True)

  
    if len(conts) != 0:
        

        newcont = []
        newtier = []
        iscard = np.zeros(len(conts),dtype=bool)


        for i in index_sort:
            newcont.append(conts[i])
            newtier.append(tier[0][i])

    

        for i in range(len(newcont)):
            size = cv2.contourArea(newcont[i])
            peri = cv2.arcLength(newcont[i],True)
            approx = cv2.approxPolyDP(newcont[i],0.01*peri,True)
            
            #if ((size < CARD_MAX_AREA) and (size > CARD_MIN_AREA) and (newtier[i][3] == -1) and (len(approx) == 4)):
            #    iscard[i] = True

            if CARD_MIN_AREA < size < CARD_MAX_AREA and newtier[i][3] == -1 and len(approx) == 4:
                iscard[i] = True
    else: 
        return [], []

    return newcont, iscard

def cardpoc(cont, image):
    currentcard = card_info()
    currentcard.outline = cont

    perm = cv2.arcLength(cont,True)
    appr = cv2.approxPolyDP(cont,0.01*perm,True)
    pnts = np.float32(appr)
    currentcard.corner_cords = pnts

    x,y,w,h = cv2.boundingRect(cont)
    currentcard.width, currentcard.height = w, h

    #change
    average = np.sum(pnts, axis=0)/len(pnts)
    cent_x = int(average[0][0])
    cent_y = int(average[0][1])
    currentcard.center = [cent_x, cent_y]

    
    currentcard.subimage = flattener(image, pnts, w, h)

   
    return currentcard



def preprocess_image(image):
  

    grayimg = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(grayimg,(5,5),0)

    
    img_w, img_h = np.shape(image)[:2]
    bkg_level = grayimg[int(img_h/100)][int(img_w/2)]
    thresh_level = bkg_level + BKG_THRESH

    retval, thresh = cv2.threshold(blur,thresh_level,255,cv2.THRESH_BINARY)
    
    return thresh





IM_WIDTH = 1280
IM_HEIGHT = 720 
FRAME_RATE = 10


font = cv2.FONT_HERSHEY_SIMPLEX
videostream = VideoStream.VideoStream((1280,720),10,1,0).start()
cam = cv2.VideoCapture(0)
time.sleep(1) 
cam_quit = 0 

while cam_quit == 0:
    image = videostream.read()
    
    pre_proc = preprocess_image(image)    
    cnts_sort, cnt_is_card = find_cards(pre_proc)

    if len(cnts_sort) != 0:       
        cards = []
        k = 0

        for i in range(len(cnts_sort)):
            if (cnt_is_card[i] == True):
                cards.append(cardpoc(cnts_sort[i],image))
                k = k + 1
	    
        if (len(cards) != 0):
            temp_cnts = []
            for i in range(len(cards)):
                temp_cnts.append(cards[i].outline)
            cv2.drawContours(image,temp_cnts, -1, (255,0,0), 2)
            cv2.imshow("warp display",cards[i].subimage)
            print("warp display")
        
    
    cv2.imshow("Card Detector",image)
    
    
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        cam_quit = 1
        
cv2.destroyAllWindows()
videostream.stop()





