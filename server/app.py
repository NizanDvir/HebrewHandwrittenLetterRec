from flask import Flask, request, jsonify
import io
import base64
from PIL import Image, ImageCms
import models.exported_methods as rec_model
from flask_cors import cross_origin

app = Flask(__name__)

# load the svm model
rec_model.load_svm_model()


@app.get('/options')
def options():
    return {
        'width': 40,
        'height': 40,
        'pixelsPerCell': 12,
    }


@app.post('/save')
@cross_origin()
def save():
    print('Saving image')
    data: object = request.json
    data_url_string: str = data['dataURL'].split(',')[1]
    data_url_bytes = io.BytesIO(
        base64.decodebytes(bytes(data_url_string, "utf-8")))
    img = Image.open(data_url_bytes)

    # get pixel values
    width, height = img.size

    # every 12 pixels is a cell
    pixels_per_cell = options()['pixelsPerCell']

    # create new image
    new_img = Image.new('RGBA', (width // pixels_per_cell,
                        height // pixels_per_cell), (255, 0, 0, 0))
    new_img_pixels = new_img.load()
    for x in range(0, width, pixels_per_cell):
        for y in range(0, height, pixels_per_cell):
            r, g, b, a = img.getpixel((x, y))
            # if alpha is 0 dont draw
            if a == 0:
                # paint white
                r, g, b = 255, 255, 255
                new_img_pixels[x // pixels_per_cell,
                               y // pixels_per_cell] = (r, g, b)
            new_img_pixels[x // pixels_per_cell,
                           y // pixels_per_cell] = (r, g, b)

    alpha_values = [0 if r < 200 else 1 for r,
                    _, _, _ in new_img.getdata()]

    new_pixels = [(pixel * 255, pixel * 255, pixel * 255)
                  for pixel in alpha_values]

    # create new image
    new_img = Image.new('RGB', (width // pixels_per_cell,
                        height // pixels_per_cell), (255, 255, 255))
    new_img.putdata(new_pixels)

    # save the image
    new_img.save('image.png')

    labels = rec_model.predict_image(img)

    response = {
        'labels': labels,
        'message': 'Image saved'
    }

    return jsonify(kwargs=response, status=200, mimetype='application/json')


if __name__ == '__main__':
    app.run(debug=True)
