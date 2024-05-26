import os
import socket
from flask import Flask, jsonify, request, Response, send_file
from flask_cors import CORS
from utils.downloader import *
from utils.converter import *

# Get alamat IP
host_name = socket.gethostname()
ip_address = socket.gethostbyname(host_name)

# Inisialisasi Flask
app = Flask(__name__)
CORS(app)

# Cek apakah server berjalan
@app.route("/")
def home():
    return "App is running"

# Download TIF file
@app.route('/downloadTif', methods=['POST'])
def download_tif():
    # Get the latitude and longitude from the request
    data = request.get_json()
    lat = data.get('latitude')
    lng = data.get('longitude')

    # Download the TIF file
    download(lng, lat)

    # Convert TIF file to jpg
    print("Converting...")
    convert(1,2,3)

    # Return the response
    wd = os.getcwd()
    img_path = os.path.join(wd, 'utils','jpg','sentinel2_preprocessed.jpg')
    return send_file(img_path, mimetype='image/jpeg'),200

# Convert TIF file
@app.route('/convertTif', methods=['POST'])
def convert_tif():
    
    data = request.get_json()
    values = data.get('values')
    if not values or len(values) != 3:
        return "Invalid input", 400

    band1, band2, band3 = values

    # Convert TIF file to jpg
    print("Converting...")
    convert(band1, band2, band3)

    # Return the response
    wd = os.getcwd()
    img_path = os.path.join(wd, 'utils', 'jpg', 'sentinel2_preprocessed.jpg')
    return send_file(img_path, mimetype='image/jpeg'), 200

if __name__ == "__main__":
    app.run(host=ip_address, port=5000, debug=False)
