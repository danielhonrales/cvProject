from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import cv2
from PIL import Image, ImageOps
import numpy as np
import VideoStream

class OpenGLGlyphs:

	# constants
	INVERSE_MATRIX = np.array([[ 1.0, 1.0, 1.0, 1.0],
								[-1.0,-1.0,-1.0,-1.0],
								[-1.0,-1.0,-1.0,-1.0],
								[ 1.0, 1.0, 1.0, 1.0]])

	width, height = 1280, 720

	def __init__(self):
		# initialise webcam and start thread
		self.webcam = VideoStream.VideoStream((self.width,self.height),10,2,1).start()

		# initialise texture
		self.texture_background = None

		self.main()


	def _init_gl(self, Width, Height):
		glClearColor(0.0, 0.0, 0.0, 0.0)
		glClearDepth(1.0)
		glDepthFunc(GL_LESS)
		glEnable(GL_DEPTH_TEST)
		glShadeModel(GL_SMOOTH)
		glMatrixMode(GL_PROJECTION)
		glColor(1.0, 1.0, 1.0)
		gluOrtho2D(-1.0, 1.0, -1.0, 1.0)

		# # Setup framebuffer
		# framebuffer = glGenFramebuffers (1)
		# glBindFramebuffer(GL_FRAMEBUFFER, framebuffer)

		# # Setup colorbuffer
		# colorbuffer = glGenRenderbuffers (1)
		# glBindRenderbuffer(GL_RENDERBUFFER, colorbuffer)
		# glRenderbufferStorage(GL_RENDERBUFFER, GL_RGBA, Width, Height)
		# glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_RENDERBUFFER, colorbuffer) 

		# # Setup depthbuffer
		# depthbuffer = glGenRenderbuffers (1)
		# glBindRenderbuffer(GL_RENDERBUFFER,depthbuffer)
		# glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH_COMPONENT, Width, Height)
		# glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_RENDERBUFFER, depthbuffer)
		
		# glViewport(0, 0, Width, Height)

		glLoadIdentity()
		gluPerspective(33.7, 1.3, 0.1, 100.0)
		glMatrixMode(GL_MODELVIEW)

		# assign texture
		glEnable(GL_TEXTURE_2D)
		self.texture_background = glGenTextures(1)

	def _draw_scene(self, image):
		print("DRAWING")
		glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
		# print("CHECK 1")
		glLoadIdentity()
		# print("CHECK 2")

		# # get image from webcam
		# success, image = self.webcam.read()
		# if not success:
		# 	print("broke")
		# 	return image

		# DEBUG: Check what image looks like
		# cv2.imwrite('temp.jpg', image)

		# convert image to OpenGL texture format
		bg_image = cv2.flip(image, 0)
		bg_image = Image.fromarray(bg_image)     
		ix = bg_image.size[0]
		iy = bg_image.size[1]
		bg_image = bg_image.tobytes("raw", "BGRX", 0, -1)
		# print("CHECK 3")

		# create background texture
		glBindTexture(GL_TEXTURE_2D, self.texture_background)
		glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
		glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
		glTexImage2D(GL_TEXTURE_2D, 0, 3, ix, iy, 0, GL_RGBA, GL_UNSIGNED_BYTE, bg_image)
			
		# draw background
		glBindTexture(GL_TEXTURE_2D, self.texture_background)
		glPushMatrix()
		glTranslatef(0.0,0.0,-10.0)
		self._draw_background()
		glPopMatrix()

		glutSwapBuffers()

		x, y, width, height = glGetDoublev(GL_VIEWPORT)
		width, height = int(width), int(height)

		# glReadBuffer(GL_COLOR_ATTACHMENT0)
		glPixelStorei(GL_PACK_ALIGNMENT, 1)
		data = glReadPixels(x, y, width, height, GL_RGB, GL_UNSIGNED_BYTE)
		image = Image.frombytes("RGB", (width, height), data)
		image = ImageOps.flip(image) # in my case image is flipped top-bottom for some reason
		# return image
		frame = np.array(image)
		print("Exiting")
		return frame

 
	def _draw_background(self):
		# draw background
		glBegin(GL_QUADS)
		glTexCoord2f(0.0, 1.0); glVertex3f(-4.0, -3.0, 0.0)
		glTexCoord2f(1.0, 1.0); glVertex3f( 4.0, -3.0, 0.0)
		glTexCoord2f(1.0, 0.0); glVertex3f( 4.0,  3.0, 0.0)
		glTexCoord2f(0.0, 0.0); glVertex3f(-4.0,  3.0, 0.0)
		glEnd()
		# glFlush()
 
	def main(self):
		# setup and run OpenGL
		global width
		global height
		glutInit(sys.argv)
		glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
		glutInitWindowSize(self.width, self.height)
		glutCreateWindow(b"OpenGL Offscreen")
		# glutHideWindow()
		glutDisplayFunc(self._draw_scene)
		glutIdleFunc(self._draw_scene)
		
		self._init_gl(self.width, self.height)

		# glutMainLoop()
  
# run an instance of OpenGL Glyphs 
# openGLGlyphs = OpenGLGlyphs()
# openGLGlyphs.main()