from keras.models import load_model  # TensorFlow is required for Keras to work
from PIL import Image, ImageOps  # Install pillow instead of PIL
import cv2 as cv
from flask import Flask, render_template, Response, jsonify
import numpy as np

model = load_model("model/keras_Model.h5", compile=False)
class_names = open("model/labels.txt", "r").readlines()
camera = cv.VideoCapture(0)
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
	classification["class"] = str(class_name[2:])
	classification["confidence"] = str(confidence_score)
	return classification

# Returns frame after changing it
# Intended to be used to add bounding boxes
def object_detection(frame):
	# frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
	return frame

# Returns frame after changing it
# Intended to add add AR effects
def ar_effects(frame):
	# frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
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
			frame = object_detection(frame)
			# Get type of card 
			classifier(frame)
			# Add AR effects
			# frame = ar_effects(frame)

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