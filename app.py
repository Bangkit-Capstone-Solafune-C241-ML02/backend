from flask import Flask, jsonify, request, Response
import os
import socket
import tifffile

host_name = socket.gethostname()
ip_address = socket.gethostbyname(host_name)

app = Flask(__name__)

# Membaca file TIFF dan mengembalikan bentuk (shape)
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

    image_array = np.stack([band1, band2, band3], axis=-1).astype('uint8')
    preprocessed_image = tifffile.Image.fromarray(image_array)

    return preprocessed_image


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
        file = preprocess(file)
        file.save(temp_file_path, format='JPEG')

        # Get the shape of the TIFF file
        shape, error = get_tiff_shape(temp_file_path)

        # Delete the temporary file
        os.remove(temp_file_path)

        if error:
            if error == "File not found":
                return jsonify({'error': error}), 404
            else:
                return jsonify({'error': error}), 500
        else:
            return jsonify({'message': 'Image received', 'shape': shape}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(host=ip_address, port=5000, debug=True)
