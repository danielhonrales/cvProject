from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import cv2
from PIL import Image, ImageOps
import numpy as np
import VideoStream
from OBJLoader import *
import mymish as obj_det
from keras.models import load_model  # TensorFlow is required for Keras to work

class OpenGLGlyphs:

	# constants
	INVERSE_MATRIX = np.array([[ 1.0, 1.0, 1.0, 1.0],
								[-1.0,-1.0,-1.0,-1.0],
								[-1.0,-1.0,-1.0,-1.0],
								[ 1.0, 1.0, 1.0, 1.0]])

	width, height = 1280, 720

	def __init__(self):
		# initialise webcam and start thread
		self.webcam = VideoStream.VideoStream((self.width,self.height),10,2,0).start()
  
		# init model
		model_path = os.path.join(os.getcwd(), "classifier", "keras_Model.h5")
		label_path = os.path.join(os.getcwd(), "classifier", "labels.txt")
		self.model = load_model(model_path, compile=False)
		self.class_names = open(label_path, "r").readlines()

		# initialise texture
		self.texture_background = None
  
		# init models
		self.cuboneModel = None
		self.charmeleonModel = None
		self.classification = {
			'class': 'None',
			'confidence': 0
		}

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

		# Load model objs
		print('Loading models')
		self.cuboneModel = OBJ(os.path.join("Models", "cubone"), "cubone.obj")
		#self.charmeleonModel = OBJ(os.path.join("Models", "charmeleon"), "charmeleon.obj")

		# assign texture
		glEnable(GL_TEXTURE_2D)
		self.texture_background = glGenTextures(1)

	def _draw_scene(self):
		#print('Drawing scene')
		# print("DRAWING")
		glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
		# print("CHECK 1")
		glLoadIdentity()
		# print("CHECK 2")

		# get image from webcam
		success, image = self.webcam.read()
		if not success:
			print("broke")
			return

		# DEBUG: Check what image looks like
		cv2.imwrite(os.path.join('images', 'temp.jpg'), image)
  
  		# Get frame with card and extrinsics
		#print('Finding cards')
		procImage, cards, extrinsics = self.gen_frames(image)

		# convert image to OpenGL texture format
		#print('Drawing background')
		cv2.imwrite(os.path.join('images', 'detected.jpg'), procImage)
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

		# Project and Render 3D model
		if len(cards) > 0:
			print(f'Rendering 3D pokemon model of {self.classification["class"].lower()}')
			#self.render3dModel(cards, extrinsics, self.classification['class'].lower())
			# Hardsetting cubone temporarily
			self.render3dModel(cards, extrinsics, 'cubone')

		glutSwapBuffers()

		x, y, width, height = glGetDoublev(GL_VIEWPORT)
		width, height = int(width), int(height)
		# glReadBuffer(GL_COLOR_ATTACHMENT0)
		glPixelStorei(GL_PACK_ALIGNMENT, 1)
		data = glReadPixels(x, y, width, height, GL_RGB, GL_UNSIGNED_BYTE)
		image = Image.frombytes("RGB", (width, height), data)
		image = ImageOps.flip(image) # in my case image is flipped top-bottom for some reason\
		
		# return image
		frame = cv2.cvtColor(np.array(image), cv2.COLOR_BGR2RGB)
  
		if len(cards) > 0:
			# DEBUG: Check what image looks like
			cv2.imwrite(os.path.join('images', 'final.jpg'), frame)
		# print("Exiting")
		return frame

	def render3dModel(self, cards, extrinsics, pokemonClass):
		if len(cards) == 0:
			return

		(rvecs, tvecs) = extrinsics[0]

		# build view matrix
		rmtx = cv2.Rodrigues(rvecs)[0]

		view_matrix = np.array([[rmtx[0][0],rmtx[0][1],rmtx[0][2],tvecs[0][0]],
								[rmtx[1][0],rmtx[1][1],rmtx[1][2],tvecs[1][0]],
								[rmtx[2][0],rmtx[2][1],rmtx[2][2],tvecs[2][0]],
								[0.0       ,0.0       ,0.0       ,1.0    	 ]])
  
		view_matrix = view_matrix * self.INVERSE_MATRIX
 
		view_matrix = np.transpose(view_matrix)
		print(view_matrix)

		# load view matrix and draw shape
		glPushMatrix()
		glLoadMatrixd(view_matrix)

		glTranslatef(.8,0.6,0.0)
		glRotatef(135.0, 0.0, 1.0, 0.0)
		glRotatef(180.0, 0.0, 0.0, 1.0)

		name = pokemonClass.lower()
		if name == 'cubone':
			glCallList(self.cuboneModel.gl_list)
		elif name == 'charmeleon':
			glCallList(self.charmeleonModel.gl_list)

		glPopMatrix()
 
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

		glutMainLoop()
  
	############################################################################################
	# Generates frames from camera
	def gen_frames(self, frame):
		# Get Image with Bounding Box
		frame, cards, extrinsics = self.object_detection(frame)
		# Get type of card
		if len(cards) > 0:
			self.classifier(cards[0].subimage)

		# Stream results
		return frame, cards, extrinsics
 
	# Returns frame after changing it
	# Intended to be used to add bounding boxes
	# RETURNS: frame, cards [frame with bounding box, list of cards detected]
	def object_detection(self, frame):  
		pre_proc = obj_det.preprocess_image(frame) 
		cnts_sort, cnt_is_card, cnt_extrinsics = obj_det.find_cards(pre_proc, frame)

		# cv.imshow("pre_proc",pre_proc)
		cards = []
		extrinsics = []
		if len(cnts_sort) != 0:       
			k = 0

			for i in range(len(cnts_sort)):
				if (cnt_is_card[i] == True):
					cards.append(obj_det.cardpoc(cnts_sort[i],frame))
					extrinsics.append(cnt_extrinsics[0]) # Should but cnt_extrinsics[i], but something breaks 
					k = k + 1

			if (len(cards) != 0):
				temp_cnts = []
				for i in range(len(cards)):
					temp_cnts.append(cards[i].outline)
				cv2.drawContours(frame,temp_cnts, -1, (255,0,0), 2)
				# cv.imshow("warp display",cards[i].subimage)

		# cv.imshow("Card Detector",frame)
		return [frame, cards, extrinsics]
  
	# Receives bounded box area of frame and returns prediction
	def classifier(self, box):
		# Create the array of the right shape to feed into the keras model
		# The 'length' or number of images you can put into the array is
		# determined by the first position in the shape tuple, in this case 1
		data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)

		# resizing the image to be at least 224x224 and then cropping from the center
		size = (224, 224)
		# You may need to convert the color.
		box = cv2.cvtColor(box, cv2.COLOR_BGR2RGB)
		image = Image.fromarray(box)
		image = ImageOps.fit(image, size, Image.Resampling.LANCZOS)

		# turn the image into a numpy array
		image_array = np.asarray(image)

		# Normalize the image
		normalized_image_array = (image_array.astype(np.float32) / 127.5) - 1

		# Load the image into the array
		data[0] = normalized_image_array

		# Predicts the model
		prediction = self.model.predict(data)
		index = np.argmax(prediction)
		class_name = self.class_names[index]
		confidence_score = prediction[0][index]

		# Print prediction and confidence score
		print("Class:", class_name[2:], end="")
		print("Confidence Score:", confidence_score)

		classification = {}
		classification["class"] = str(class_name[2:])
		classification["confidence"] = str(confidence_score)
		self.classification = classification


		return classification
	
# run an instance of OpenGL Glyphs 
openGLGlyphs = OpenGLGlyphs()
openGLGlyphs.main()