import os
import socket
import threading
import uuid
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from utils.downloader import download
from utils.converter import convert
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

# Function to handle TIF download and conversion
def handle_download_and_convert(lat, lng, response):
    # Create unique directory for this request
    unique_id = str(uuid.uuid4())
    unique_dir = os.path.join('utils', 'temp', unique_id)
    os.makedirs(unique_dir, exist_ok=True)

    # Download the TIF file
    tif_path = download(lng, lat)

    # Convert TIF file to jpg
    print("Converting...")
    jpg_path = convert(1, 2, 3, os.path.dirname(tif_path), unique_dir)

    # Store the result in the response dictionary
    response['file_path'] = jpg_path

# Endpoint untuk download dan convert TIF file
@app.route('/downloadTif', methods=['POST'])
def download_tif():
    data = request.get_json()
    lat = data.get('latitude')
    lng = data.get('longitude')

    # Create a response dictionary to store result
    response = {}

    # Create and start a thread
    thread = threading.Thread(target=handle_download_and_convert, args=(lat, lng, response))
    thread.start()
    thread.join()

    # Return the response
    if 'file_path' in response:
        return send_file(response['file_path'], mimetype='image/jpeg'), 200
    else:
        return jsonify({"error": "Download and conversion failed"}), 500

# Function to handle file upload and conversion
def handle_upload_and_convert(file, band1, band2, band3, response):
    # Create unique directory for this request
    unique_id = str(uuid.uuid4())
    unique_dir = os.path.join('utils', 'temp', unique_id)
    os.makedirs(unique_dir, exist_ok=True)

    # Save the file
    tif_path = os.path.join(unique_dir, file.filename)
    file.save(tif_path)

    # Convert TIF file to jpg
    print("Converting...")
    jpg_path = convert(band1, band2, band3, unique_dir, unique_dir, file.filename)

    # Store the result in the response dictionary
    response['file_path'] = jpg_path

# Endpoint untuk upload dan convert TIF file
@app.route('/uploadTif', methods=['POST'])
def upload_tif():
    if 'tifFile' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['tifFile']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and file.filename.lower().endswith(('.tif', '.tiff')):
        data = request.get_json()
        values = data.get('values', [1, 2, 3])  # Default to bands 1, 2, 3 if not provided

        # Create a response dictionary to store result
        response = {}

        # Create and start a thread
        thread = threading.Thread(target=handle_upload_and_convert, args=(file, values[0], values[1], values[2], response))
        thread.start()
        thread.join()

        # Return the response
        if 'file_path' in response:
            return send_file(response['file_path'], mimetype='image/jpeg'), 200
        else:
            return jsonify({"error": "Upload and conversion failed"}), 500

    return jsonify({"error": "Invalid file type"}), 400

# Function to handle masking and prediction
def handle_mask_and_predict(source_folder, model_name, response):
    # Create unique directory for this request
    unique_id = str(uuid.uuid4())
    unique_dir = os.path.join('utils', 'temp', unique_id)
    os.makedirs(unique_dir, exist_ok=True)

    # Predict the image
    predict_from_path(source_folder, model_name, unique_dir)

    # Store the result in the response dictionary
    mask_path = os.path.join(unique_dir, 'mask.jpg')
    response['file_path'] = mask_path

# Endpoint untuk mask TIF file dari Sentinel
@app.route('/maskTifSentinel', methods=['POST'])
def mask_tif_sentinel():
    model_name = 'yolov5m'
    source_folder = os.path.join(os.getcwd(), 'utils', 'tif_from_sentinel')

    # Create a response dictionary to store result
    response = {}

    # Create and start a thread
    thread = threading.Thread(target=handle_mask_and_predict, args=(source_folder, model_name, response))
    thread.start()
    thread.join()

    # Return the response
    if 'file_path' in response:
        return send_file(response['file_path'], mimetype='image/jpeg'), 200
    else:
        return jsonify({"error": "Masking and prediction failed"}), 500

# Endpoint untuk mask TIF file dari Upload
@app.route('/maskTifUpload', methods=['POST'])
def mask_tif_upload():
    model_name = 'yolov5m'
    source_folder = os.path.join(os.getcwd(), 'utils', 'tif_from_upload')

    # Create a response dictionary to store result
    response = {}

    # Create and start a thread
    thread = threading.Thread(target=handle_mask_and_predict, args=(source_folder, model_name, response))
    thread.start()
    thread.join()

    # Return the response
    if 'file_path' in response:
        return send_file(response['file_path'], mimetype='image/jpeg'), 200
    else:
        return jsonify({"error": "Masking and prediction failed"}), 500

if __name__ == "__main__":
    app.run(host=ip_address, port=5000, debug=False)
