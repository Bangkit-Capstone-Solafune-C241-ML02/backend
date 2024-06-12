import os
import socket
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from utils.downloader import *
from utils.converter import *
from utils.predict import predict_from_path

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
    uid = data.get('uid', 'defaultUID')

    # Download the TIF file
    download(lng, lat, uid)

    # Convert TIF file to jpg
    print("Converting...")
    convert(1, 2, 3, 'utils/tif_from_sentinel', 'utils/jpg_from_sentinel', uid)

    # Return the response
    wd = os.getcwd()
    img_path = os.path.join(wd, 'utils', 'jpg_from_sentinel', f'sentinel2_preprocessed_{uid}.jpg')
    return send_file(img_path, mimetype='image/jpeg'), 200

# Convert TIF file from sentinel
@app.route('/convertTifSentinel', methods=['POST'])
def convert_tif_sentinel():
    
    data = request.get_json()
    values = data.get('values')
    if not values or len(values) != 3:
        return "Invalid input", 400

    band1, band2, band3 = values

    # Convert TIF file to jpg
    print("Converting...")
    convert(band1, band2, band3, 'utils/tif_from_sentinel', 'utils/jpg_from_sentinel')

    # Return the response
    wd = os.getcwd()
    img_path = os.path.join(wd, 'utils', 'jpg_from_sentinel', 'sentinel2_preprocessed.jpg')
    return send_file(img_path, mimetype='image/jpeg'), 200

# Upload TIF file
@app.route('/uploadTif', methods=['POST'])
def upload_tif():
    if 'tifFile' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['tifFile']

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and file.filename.lower().endswith('.tif') or file.filename.lower().endswith('.tiff'):
        # Save the file
        wd = os.getcwd()
        save_path = os.path.join(wd, 'utils', 'tif_from_upload', 'upload_image.tif')

        # If the file is .tiff, change the extension to .tif
        if file.filename.lower().endswith('.tiff'):
            filename = file.filename.rsplit('.', 1)[0] + '.tif'
            save_path = os.path.join(wd, 'utils', 'tif_from_upload', filename)

        file.save(save_path)

        # Convert TIF file to jpg
        print("Converting...")
        convert(1, 2, 3, 'utils/tif_from_upload', 'utils/jpg_from_upload', 'upload_image.tif')

        # Return the converted image as response
        img_path = os.path.join(wd, 'utils', 'jpg_from_upload', 'upload_preprocessed.jpg')
        return send_file(img_path, mimetype='image/jpeg'), 200

    return jsonify({"error": "Invalid file type"}), 400

# Convert TIF file from upload
@app.route('/convertTifUpload', methods=['POST'])
def convert_tif_upload():
    
    data = request.get_json()
    values = data.get('values')
    if not values or len(values) != 3:
        return "Invalid input", 400

    band1, band2, band3 = values

    # Convert TIF file to jpg
    print("Converting...")
    convert(band1, band2, band3, 'utils/tif_from_upload', 'utils/jpg_from_upload','upload_image.tif')

    # Return the response
    wd = os.getcwd()
    img_path = os.path.join(wd, 'utils', 'jpg_from_upload', 'upload_preprocessed.jpg')
    return send_file(img_path, mimetype='image/jpeg'), 200

# Mask TIF file from sentinel
@app.route('/maskTifSentinel', methods=['POST'])
def mask_tif_sentinel():
    # Predict the image
    model_name = 'new_model'
    source_path = os.path.join(os.getcwd(), 'utils', 'tif_from_sentinel')
    predict_from_path(source_path, model_name)

    # Return the response
    wd = os.getcwd()
    img_path = os.path.join(wd, 'utils', 'masks', 'mask.jpg')
    return send_file(img_path, mimetype='image/jpeg'), 200

# Mask TIF file from upload
@app.route('/maskTifUpload', methods=['POST'])
def mask_tif_upload():
    # Predict the image
    model_name = 'new_model'
    source_path = os.path.join(os.getcwd(), 'utils', 'tif_from_upload')
    predict_from_path(source_path, model_name)

    # Return the response
    wd = os.getcwd()
    img_path = os.path.join(wd, 'utils', 'masks', 'mask.jpg')
    return send_file(img_path, mimetype='image/jpeg'), 200

# Painting TIF File from sentinel
@app.route('/paintingTifSentinel', methods=['POST'])
def paint_tif_sentinel():
    # Return the response
    wd = os.getcwd()
    img_path = os.path.join(wd, 'utils', 'painted_image', 'sentinel2_image.jpg')
    return send_file(img_path, mimetype='image/jpeg'), 200

# Painting TIF File from upload
@app.route('/paintingTifUpload', methods=['POST'])
def paint_tif_upload():
    # Return the response
    wd = os.getcwd()
    img_path = os.path.join(wd, 'utils', 'painted_image', 'upload_image.jpg')
    return send_file(img_path, mimetype='image/jpeg'), 200

if __name__ == "__main__":
    app.run(host=ip_address, port=5000, debug=True)
