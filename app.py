from flask import Flask, render_template, Response, jsonify
from keras.models import load_model  # TensorFlow is required for Keras to work
from PIL import Image, ImageOps  # Install pillow instead of PIL
from termcolor import colored
import mymish as obj_det
import numpy as np
import VideoStream
import cv2 as cv
import os
import OpenGLTest as ar

###################################
#           CAMERA PORT           #
#     USE 0 FOR DEFAULT CAMERA    #
# USE 1 FOR CONTINUITY CAM ON MAC #
PORT = 0
###################################

model_path = os.path.join(os.getcwd(), "classifier", "keras_Model.h5")
label_path = os.path.join(os.getcwd(), "classifier", "labels.txt")

model = load_model(model_path, compile=False)
class_names = open(label_path, "r").readlines()
ar_obj = ar.OpenGLGlyphs()
camera = VideoStream.VideoStream((1280,720),10,2,PORT).start()
# camera = cv.VideoCapture(PORT)
if not camera.isOpened():
	print(colored("Camera not found", "green"), colored("Exiting...", "red"), sep="\n") 
	os._exit(1) # Exits all threads (important if using VideoStream.py)
app = Flask(__name__)
classification = {"confidence": "Unconfident", "class": "Test"}

# Receives bounded box area of frame and returns prediction
def classifier(box):
	# Create the array of the right shape to feed into the keras model
	# The 'length' or number of images you can put into the array is
	# determined by the first position in the shape tuple, in this case 1
	data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)

	# resizing the image to be at least 224x224 and then cropping from the center
	size = (224, 224)
	# You may need to convert the color.
	box = cv.cvtColor(box, cv.COLOR_BGR2RGB)
	image = Image.fromarray(box)
	image = ImageOps.fit(image, size, Image.Resampling.LANCZOS)

	# turn the image into a numpy array
	image_array = np.asarray(image)

	# Normalize the image
	normalized_image_array = (image_array.astype(np.float32) / 127.5) - 1

	# Load the image into the array
	data[0] = normalized_image_array

	# Predicts the model
	prediction = model.predict(data)
	index = np.argmax(prediction)
	class_name = class_names[index]
	confidence_score = prediction[0][index]

	# Print prediction and confidence score
	print("Class:", class_name[2:], end="")
	print("Confidence Score:", confidence_score)

	global classification
	# FIX THIS: Temp forcing charmeleon
	classification["class"] = "charmeleon"
	# classification["class"] = str(class_name[2:])
	classification["confidence"] = str(confidence_score)


	return classification

# Returns frame after changing it
# Intended to be used to add bounding boxes
# RETURNS: frame, cards [frame with bounding box, list of cards detected]
def object_detection(frame):  
	pre_proc = obj_det.preprocess_image(frame)    
	cnts_sort, cnt_is_card, cnt_extrinsics = obj_det.find_cards(pre_proc)

    # cv.imshow("pre_proc",pre_proc)
	cards = []
	extrinsics = []
	if len(cnts_sort) != 0:       
		k = 0

		for i in range(len(cnts_sort)):
			if (cnt_is_card[i] == True):
				cards.append(obj_det.cardpoc(cnts_sort[i],frame))
				extrinsics.append(cnt_extrinsics[i])
				k = k + 1

		if (len(cards) != 0):
			temp_cnts = []
			for i in range(len(cards)):
				temp_cnts.append(cards[i].outline)
			cv.drawContours(frame,temp_cnts, -1, (255,0,0), 2)
			# cv.imshow("warp display",cards[i].subimage)

	# cv.imshow("Card Detector",frame)
	return [frame, cards, extrinsics]

# Returns frame after changing it
# Intended to add add AR effects
def ar_effects(frame, extrinsics):
	print("AR START")
	frame = ar_obj._draw_scene(frame, extrinsics)
	cv.imwrite('ar_test.jpg', frame)
	# frame = cv.cvtColor(frame, cv.COLOR_RGB2BGR)
	return frame

# Generates frames from camera
def gen_frames():
	while True:
		success, frame = camera.read()  # read the camera frame
		if not success:
			print("broke")
			break
		else:
			# Get Image with Bounding Box
			frame, cards, extrinsics = object_detection(frame)
			# Get type of card
			if len(cards) > 0:
				classifier(cards[0].subimage)
				# Create new model info files
				with open('classification.txt', 'w+') as file:
					file.write(classification['class'].lower())
					file.close()
				cv.imwrite('frame.jpg', frame)
        
				# Add AR effects
				frame = ar_effects(frame, extrinsics[0])

			# Stream results
			ret, buffer = cv.imencode('.jpg', frame)
			frame = buffer.tobytes()
			yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result


# Video feed
@app.route('/video_feed')
def video_feed():
	return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# Classification API
@app.route('/classification')
def api_datapoint():
	return jsonify(classification)

# Home page
@app.route('/')
def index():
	return render_template('index.html')

if __name__ == "__main__":
	app.run(port="8000", debug=True)

# Run app
# flask --app app run   