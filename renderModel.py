from extractModelData import *
from OpenGL.GL import *
from OpenGL.GLU import *
from pygame.locals import *
import pygame
import sys
from PIL import Image
import numpy as np
import base64

colors = [     #colors for our faces
    (180, 180, 180), #green
]

moving = True

def drawModel(vertices, faces):
    glClear(GL_COLOR_BUFFER_BIT or GL_DEPTH_BUFFER_BIT) #clears each frame
    glBegin(GL_TRIANGLES)  #drawing method
    for face in faces:
        color = 0
        for vertexIndex in face:
            color = (color + 1) % len(colors)
            glColor3fv(colors[color])
            glVertex3fv(vertices[vertexIndex - 1])
    glEnd()

def moveModel():
    if moving:
        glRotate(0, 1, 0, 0)

def getClassification():
    classificationPath = '.\classification.txt'
    classification = None
    # Check if classification file exists
    if not os.path.isfile(classificationPath):
        print('No classification found')
    else:
        with open(classificationPath) as file:
            # Read through file
            for line in file:
                line = line.rstrip("\r\n")
                if line != 'Unconfident':
                    classification = line
    #return classification.lower()
    return classification

def drawImg(imagePath):
    startlen = 0
    startwid = 0
    width = 10
    height = 10
    length = 10
    glBegin(GL_QUADS)
    glColor4f(0.8, 0.8, 0.5, 1.0)
    glVertex2f(-1.0, 1.0)
    glVertex2f(1.0, 1.0)
    glVertex2f(1.0, -1.0)
    glVertex2f(-1.0, -1.0)
    glEnd()
    
    img = Image.open(imagePath).transpose(Image.FLIP_TOP_BOTTOM)
    imgData = np.array(img)
    
    glEnable(GL_TEXTURE_2D)
    texname = glGenTextures(1)
    
    glPixelStorei(GL_UNPACK_ALIGNMENT,1)
    glBindTexture(GL_TEXTURE_2D, texname)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
    
    gluBuild2DMipmaps(GL_TEXTURE_2D, GL_RGB, img.size[0], img.size[1], GL_RGB, GL_UNSIGNED_BYTE, imgData)
                

###############################################################################################
# Main
###############################################################################################

pygame.init()
display = (800, 800)
pygame.display.set_caption("Cubone Render")
FPS = pygame.time.Clock()
pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
gluPerspective(45, 1, .1, 50)
glTranslate(0, 0, -5)
#glRotate(-90, 1, 0, 0)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == KEYDOWN:
            if event.type == K_SPACE:
                moving = True
        if event.type == KEYUP:
            if event.key == K_SPACE:
                moving = False
    
    pygame.display.flip()
    
    classification = getClassification()
    if classification != None:
        modelFile = f".\Models\{classification}\{classification}.obj"
        vertices, faces = extractModelData(modelFile)
        drawModel(vertices, faces)
    else:
        glClear(GL_COLOR_BUFFER_BIT or GL_DEPTH_BUFFER_BIT)
    
    #drawImg('frame.jpg')
    moveModel()
    FPS.tick(60)
    
    
