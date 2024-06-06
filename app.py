import os
import socket
import threading
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

# Global thread counter
thread_counter = 0
thread_lock = threading.Lock()

# Cek apakah server berjalan
@app.route("/")
def home():
    return "App is running"

def handle_download_tif(lat, lng, result, thread_id, client_ip):
    print(f"Thread {thread_id} is handling the download.")
    download(lng, lat, thread_id, client_ip)
    print("Converting...")
    convert(1, 2, 3, f'utils/tif_from_sentinel_{thread_id}_{client_ip}', f'utils/jpg_from_sentinel_{thread_id}_{client_ip}')
    wd = os.getcwd()
    img_path = os.path.join(wd, f'utils/jpg_from_sentinel_{thread_id}_{client_ip}', 'sentinel2_preprocessed.jpg')
    result['img_path'] = img_path

@app.route('/downloadTif', methods=['POST'])
def download_tif():
    data = request.get_json()
    lat = data.get('latitude')
    lng = data.get('longitude')
    
    global thread_counter
    with thread_lock:
        thread_counter += 1
        thread_id = thread_counter
    
    client_ip = request.remote_addr
    result = {}
    thread = threading.Thread(target=handle_download_tif, args=(lat, lng, result, thread_id, client_ip))
    thread.start()
    thread.join()
    
    return send_file(result['img_path'], mimetype='image/jpeg'), 200

def handle_convert_tif_sentinel(values, result, thread_id, client_ip):
    print(f"Thread {thread_id} is handling the conversion.")
    band1, band2, band3 = values
    print("Converting...")
    convert(band1, band2, band3, f'utils/tif_from_sentinel_{thread_id}_{client_ip}', f'utils/jpg_from_sentinel_{thread_id}_{client_ip}')
    wd = os.getcwd()
    img_path = os.path.join(wd, f'utils/jpg_from_sentinel_{thread_id}_{client_ip}', 'sentinel2_preprocessed.jpg')
    result['img_path'] = img_path

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
    
    client_ip = request.remote_addr
    result = {}
    thread = threading.Thread(target=handle_convert_tif_sentinel, args=(values, result, thread_id, client_ip))
    thread.start()
    thread.join()
    
    return send_file(result['img_path'], mimetype='image/jpeg'), 200

def handle_upload_tif(file, result, thread_id, client_ip):
    print(f"Thread {thread_id} is handling the upload.")
    file.save(os.path.join(f'utils/tif_from_upload_{thread_id}_{client_ip}', 'upload_image.tif'))
    convert(1, 2, 3, f'utils/tif_from_upload_{thread_id}_{client_ip}', f'utils/jpg_from_upload_{thread_id}_{client_ip}', 'upload_image.tif')
    wd = os.getcwd()
    img_path = os.path.join(wd, f'utils/jpg_from_upload_{thread_id}_{client_ip}', 'upload_preprocessed.jpg')
    result['img_path'] = img_path

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
        
        client_ip = request.remote_addr
        result = {}
        thread = threading.Thread(target=handle_upload_tif, args=(file, result, thread_id, client_ip))
        thread.start()
        thread.join()
        
        return send_file(result['img_path'], mimetype='image/jpeg'), 200
    return jsonify({"error": "Invalid file type"}), 400

def handle_convert_tif_upload(values, result, thread_id, client_ip):
    print(f"Thread {thread_id} is handling the conversion.")
    band1, band2, band3 = values
    print("Converting...")
    convert(band1, band2, band3, f'utils/tif_from_upload_{thread_id}_{client_ip}', f'utils/jpg_from_upload_{thread_id}_{client_ip}', 'upload_image.tif')
    wd = os.getcwd()
    img_path = os.path.join(wd, f'utils/jpg_from_upload_{thread_id}_{client_ip}', 'upload_preprocessed.jpg')
    result['img_path'] = img_path

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
    
    client_ip = request.remote_addr
    result = {}
    thread = threading.Thread(target=handle_convert_tif_upload, args=(values, result, thread_id, client_ip))
    thread.start()
    thread.join()
    
    return send_file(result['img_path'], mimetype='image/jpeg'), 200

def handle_mask_tif_sentinel(result, thread_id, client_ip):
    print(f"Thread {thread_id} is handling the mask.")
    model_name = 'yolov5m'
    source_path = os.path.join(os.getcwd(), f'utils/tif_from_sentinel_{thread_id}_{client_ip}')
    predict_from_path(source_path, model_name)
    wd = os.getcwd()
    img_path = os.path.join(wd, f'utils/masks_{thread_id}_{client_ip}', 'mask.jpg')
    result['img_path'] = img_path

@app.route('/maskTifSentinel', methods=['POST'])
def mask_tif_sentinel():
    global thread_counter
    with thread_lock:
        thread_counter += 1
        thread_id = thread_counter
    
    client_ip = request.remote_addr
    result = {}
    thread = threading.Thread(target=handle_mask_tif_sentinel, args=(result, thread_id, client_ip))
    thread.start()
    thread.join()
    
    return send_file(result['img_path'], mimetype='image/jpeg'), 200

def handle_mask_tif_upload(result, thread_id, client_ip):
    print(f"Thread {thread_id} is handling the mask.")
    model_name = 'yolov5m'
    source_path = os.path.join(os.getcwd(), f'utils/tif_from_upload_{thread_id}_{client_ip}')
    predict_from_path(source_path, model_name)
    wd = os.getcwd()
    img_path = os.path.join(wd, f'utils/masks_{thread_id}_{client_ip}', 'mask.jpg')
    result['img_path'] = img_path

@app.route('/maskTifUpload', methods=['POST'])
def mask_tif_upload():
    global thread_counter
    with thread_lock:
        thread_counter += 1
        thread_id = thread_counter
    
    client_ip = request.remote_addr
    result = {}
    thread = threading.Thread(target=handle_mask_tif_upload, args=(result, thread_id, client_ip))
    thread.start()
    thread.join()
    
    return send_file(result['img_path'], mimetype='image/jpeg'), 200

if __name__ == "__main__":
    app.run(host=ip_address, port=5000, debug=False)
