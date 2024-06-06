import os
import socket
import threading
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

# Global thread counter
thread_counter = 0
thread_lock = threading.Lock()

# Cek apakah server berjalan
@app.route("/")
def home():
    return "App is running"

# Download TIF file handler
def handle_download_tif(thread_id, lat, lng):
    print(f"Thread {thread_id} is handling the download.")
    download(lng, lat)
    print("Converting...")
    convert(1, 2, 3, 'utils/tif_from_sentinel', 'utils/jpg_from_sentinel')
    wd = os.getcwd()
    img_path = os.path.join(wd, 'utils', 'jpg_from_sentinel', 'sentinel2_preprocessed.jpg')
    return img_path

@app.route('/downloadTif', methods=['POST'])
def download_tif():
    data = request.get_json()
    lat = data.get('latitude')
    lng = data.get('longitude')
    
    global thread_counter
    with thread_lock:
        thread_counter += 1
        thread_id = thread_counter
    
    thread = threading.Thread(target=handle_download_tif, args=(thread_id, lat, lng))
    thread.start()
    return jsonify({"status": "Processing", "thread_id": thread_id}), 202

# Convert TIF file from sentinel handler
def handle_convert_tif_sentinel(thread_id, values):
    print(f"Thread {thread_id} is handling the conversion.")
    band1, band2, band3 = values
    print("Converting...")
    convert(band1, band2, band3, 'utils/tif_from_sentinel', 'utils/jpg_from_sentinel')
    wd = os.getcwd()
    img_path = os.path.join(wd, 'utils', 'jpg_from_sentinel', 'sentinel2_preprocessed.jpg')
    return img_path

@app.route('/convertTifSentinel', methods=['POST'])
def convert_tif_sentinel():
    data = request.get_json()
    values = data.get('values')
    if not values or len(values) != 3:
        return "Invalid input", 400
    
    global thread_counter
    with thread_lock:
        thread_counter += 1
        thread_id = thread_counter
    
    thread = threading.Thread(target=handle_convert_tif_sentinel, args=(thread_id, values))
    thread.start()
    return jsonify({"status": "Processing", "thread_id": thread_id}), 202

# Upload TIF file handler
def handle_upload_tif(thread_id, file):
    print(f"Thread {thread_id} is handling the upload.")
    file.save(os.path.join('utils/tif_from_upload', 'upload_image.tif'))
    convert(1, 2, 3, 'utils/tif_from_upload', 'utils/jpg_from_upload', 'upload_image.tif')
    wd = os.getcwd()
    img_path = os.path.join(wd, 'utils', 'jpg_from_upload', 'upload_preprocessed.jpg')
    return img_path

@app.route('/uploadTif', methods=['POST'])
def upload_tif():
    if 'tifFile' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['tifFile']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file and file.filename.endswith('.tif'):
        global thread_counter
        with thread_lock:
            thread_counter += 1
            thread_id = thread_counter
        
        thread = threading.Thread(target=handle_upload_tif, args=(thread_id, file))
        thread.start()
        return jsonify({"status": "Processing", "thread_id": thread_id}), 202
    return jsonify({"error": "Invalid file type"}), 400

# Convert TIF file from upload handler
def handle_convert_tif_upload(thread_id, values):
    print(f"Thread {thread_id} is handling the conversion.")
    band1, band2, band3 = values
    print("Converting...")
    convert(band1, band2, band3, 'utils/tif_from_upload', 'utils/jpg_from_upload', 'upload_image.tif')
    wd = os.getcwd()
    img_path = os.path.join(wd, 'utils', 'jpg_from_upload', 'upload_preprocessed.jpg')
    return img_path

@app.route('/convertTifUpload', methods=['POST'])
def convert_tif_upload():
    data = request.get_json()
    values = data.get('values')
    if not values or len(values) != 3:
        return "Invalid input", 400
    
    global thread_counter
    with thread_lock:
        thread_counter += 1
        thread_id = thread_counter
    
    thread = threading.Thread(target=handle_convert_tif_upload, args=(thread_id, values))
    thread.start()
    return jsonify({"status": "Processing", "thread_id": thread_id}), 202

# Mask TIF file from sentinel handler
def handle_mask_tif_sentinel(thread_id):
    print(f"Thread {thread_id} is handling the mask.")
    model_name = 'yolov5m'
    source_path = os.path.join(os.getcwd(), 'utils', 'tif_from_sentinel')
    predict_from_path(source_path, model_name)
    wd = os.getcwd()
    img_path = os.path.join(wd, 'utils', 'masks', 'mask.jpg')
    return img_path

@app.route('/maskTifSentinel', methods=['POST'])
def mask_tif_sentinel():
    global thread_counter
    with thread_lock:
        thread_counter += 1
        thread_id = thread_counter
    
    thread = threading.Thread(target=handle_mask_tif_sentinel, args=(thread_id,))
    thread.start()
    return jsonify({"status": "Processing", "thread_id": thread_id}), 202

# Mask TIF file from upload handler
def handle_mask_tif_upload(thread_id):
    print(f"Thread {thread_id} is handling the mask.")
    model_name = 'yolov5m'
    source_path = os.path.join(os.getcwd(), 'utils', 'tif_from_upload')
    predict_from_path(source_path, model_name)
    wd = os.getcwd()
    img_path = os.path.join(wd, 'utils', 'masks', 'mask.jpg')
    return img_path

@app.route('/maskTifUpload', methods=['POST'])
def mask_tif_upload():
    global thread_counter
    with thread_lock:
        thread_counter += 1
        thread_id = thread_counter
    
    thread = threading.Thread(target=handle_mask_tif_upload, args=(thread_id,))
    thread.start()
    return jsonify({"status": "Processing", "thread_id": thread_id}), 202

if __name__ == "__main__":
    app.run(host=ip_address, port=5000, debug=False)
