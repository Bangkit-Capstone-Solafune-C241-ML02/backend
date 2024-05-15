from flask import Flask, jsonify, request
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
        return str(e)

# Contoh penggunaan
file_path = "example.tiff"  # Ganti dengan path ke file TIFF yang sesuai
shape = get_tiff_shape(file_path)
print("Shape of TIFF file:", shape)


@app.route("/")
def home():
    return "App is running"

@app.route('/predict', methods=['POST'])
def predict_image():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})

    file = request.files['file']

    # Check if the file is a TIFF image
    if file.filename == '' or not file.filename.endswith('.tif'):
        return jsonify({'error': 'Invalid file format. Please provide a TIF image.'})

    try:
        # Save the file temporarily
        temp_file_path = 'temp.tif'
        file.save(temp_file_path)

        # Get the shape of the TIFF file
        shape, error = get_tiff_shape(temp_file_path)

        # Delete the temporary file
        os.remove(temp_file_path)

        if error:
            return jsonify({'error': error})
        else:
            return jsonify({'message': 'Image received','shape': shape})
    except Exception as e:
        return jsonify({'error': str(e)})


if __name__ == "__main__":
    app.run(host=ip_address, port=5000,debug=True)