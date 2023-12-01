from extractModelData import *
from OpenGL.GL import *
from OpenGL.GLU import *
from pygame.locals import *
import pygame
import sys

colors = [     #colors for our faces
    (0,255,0), #green
    (255,0,0), #red
    (255,255,0), #yellow
    (0,255,255), #cyan
    (0,0,255), #blue
    (255,255,255) #white
]

moving = False

def drawModel(vertices, faces):
    glClear(GL_COLOR_BUFFER_BIT or GL_DEPTH_BUFFER_BIT) #clears each frame
    glBegin(GL_TRIANGLES)  #drawing method
    for face in faces:
        color = 0
        for vertexIndex in face:
            color = (color + 1) % 5
            glColor3fv(colors[color])
            glVertex3fv(vertices[vertexIndex - 1])
    glEnd()

def moveModel():
    if moving:
        glRotate(0, 1, 0, 0)

###############################################################################################
# Main
###############################################################################################

modelFile = ".\Models\Cubone\cubone.obj"
vertices, faces = extractModelData(modelFile)

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
    drawModel(vertices, faces)
    moveModel()
    FPS.tick(60)
    
    
