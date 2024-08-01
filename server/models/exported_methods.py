from PIL import Image
import pickle
import numpy as np
import keras
from sklearn import svm
import cv2

global rec_model


def load_model():
    global rec_model
    # load the svm model
    rec_model = keras.models.load_model('models/keras_model.keras')


def convert_to_probability_dictionary(probabilities):
    # convert the probabilities to a dictionary
    probability_dict = {}
    for i in range(len(probabilities)):
        probability_dict[i] = float(probabilities[i])
    return probability_dict


def convert_img_to_binary_array(pixels):
    # get the pixel values of the image
    binary_array = []
    for pixel in pixels:
        if pixel[0] >= 128 and pixel[1] >= 128 and pixel[2] >= 128:
            binary_array.append(1)
        else:
            binary_array.append(0)
    return binary_array


def convert_image(image):
    print(image.shape)
    # Resize the image to 40x40 if it's not already
    if image.shape[:2] != (40, 40):
        image = cv2.resize(image, (40, 40), interpolation=cv2.INTER_AREA)

    # Convert to grayscale if the image has more than one channel
    if len(image.shape) > 2:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Convert to black and white (0 or 255)
    _, bw_image = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY)

    # Normalize to 0 or 1 for the neural network
    normalized_image = (bw_image / 255).astype(np.float32)

    # Reshape to add channel dimension
    reshaped_image = normalized_image.reshape(1, 40, 40, 1)

    return reshaped_image


def predict_image(img):
    img = convert_image(np.array(img))
    predicted = rec_model.predict([img])
    print(convert_to_probability_dictionary(predicted[0]))
    return convert_to_probability_dictionary(predicted[0])
