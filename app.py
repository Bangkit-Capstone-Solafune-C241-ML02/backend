from flask import Flask, jsonify, request
import os
import socket

host_name = socket.gethostname()
ip_address = socket.gethostbyname(host_name)

app = Flask(__name__)


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

    # try:
    #     image = Image.open(file)
    #     image_tensor = preprocess_image(image)
    #     prediction = predict(image_tensor)
    #     return jsonify({'prediction': prediction})
    # except Exception as e:
    #     return jsonify({'error': str(e)})

    return jsonify({'message': 'Image received'})


if __name__ == "__main__":
    app.run(host=ip_address, port=5000,debug=True)