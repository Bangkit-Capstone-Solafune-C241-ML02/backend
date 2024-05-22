from flask import Flask, jsonify, request, Response, send_file
import os
import socket

import tifffile
import numpy as np
from PIL import Image
import base64

from flask_cors import CORS

from downloader import *

from converter import *

import time


def get_tiff_shape(file_path):
    try:
        # Check if the file exists
        if not os.path.isfile(file_path):
            return None, "File not found"
        
        # Membaca file TIFF
        tiff_data = tifffile.imread(file_path)
        
        # Mendapatkan bentuk dari data TIFF
        shape = tiff_data.shape
        
        return shape, None
    except Exception as e:
        return None, str(e)

def normalize(channel) :
    min_val, max_val = np.min(channel), np.max(channel)

    normalized_channel = ( (channel - min_val) / (max_val - min_val) ) * 255
    return normalized_channel

def preprocess(image) :
    band1 = normalize(image[:, :, 2])
    band2 = normalize(image[:, :, 3])
    band3 = normalize(image[:, :, 4])

    image_array = np.stack([band3, band2, band1], axis=-1).astype('uint8')
    preprocessed_image = Image.fromarray(image_array).resize(
      (image_array.shape[1] * 25, image_array.shape[0] * 25),
      Image.NEAREST)

    return preprocessed_image

host_name = socket.gethostname()
ip_address = socket.gethostbyname(host_name)

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return "App is running"

@app.route('/predict', methods=['POST'])
def predict_image():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']

    # Check if the file is a TIFF image
    if file.filename == '' or not file.filename.endswith('.tif'):
        return jsonify({'error': 'Invalid file format. Please provide a TIF image.'}), 400

    try:
        # Save the file temporarily
        temp_file_path = 'temp.jpg'
        file = tifffile.imread(file)
        file = preprocess(file)
        file.save(temp_file_path)

        # Get the shape of the TIFF file
        # shape, error = get_tiff_shape(temp_file_path)
        error = ''

        # Delete the temporary file
        # os.remove(temp_file_path)
        image = open(temp_file_path, 'rb').read()
        image = base64.b64encode(image).decode("utf-8")

        if error:
            if error == "File not found":
                return jsonify({'error': error}), 404
            else:
                return jsonify({'error': error}), 500
        else:
            print(image)
            response = jsonify({'message': 'Image received', 'base64Image': image})
            response.headers['Access-Control-Allow-Origin'] = 'http://127.0.0.1:5500' 
            return response, 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/downloadTif', methods=['POST'])
def download_tif():
    # Get the latitude and longitude from the request
    data = request.get_json()
    lat = data.get('latitude')
    lng = data.get('longitude')


    # Download the TIF file
    download(lng, lat)
    time.sleep(10)
    # Convert TIF file to jpg
    print("Converting...")
    convert()

    img_path = './sentinel2_preprocessed2.jpg'
    return send_file(img_path, mimetype='image/jpeg'),200

if __name__ == "__main__":
    app.run(host=ip_address, port=5000, debug=False)
