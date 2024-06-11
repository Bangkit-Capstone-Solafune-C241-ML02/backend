import os
import tifffile
import numpy as np
from PIL import Image

def normalize(channel):
    min_val, max_val = np.min(channel), np.max(channel)
    normalized_channel = ((channel - min_val) / (max_val - min_val)) * 255
    return normalized_channel

def preprocess(image, b1, b2, b3):
    band1 = normalize(image[:, :, b1])
    band2 = normalize(image[:, :, b2])
    band3 = normalize(image[:, :, b3])

    image_array = np.stack([band3, band2, band1], axis=-1).astype('uint8')
    preprocessed_image = Image.fromarray(image_array).resize(
        (image_array.shape[0] * 10, image_array.shape[1] * 10),
        Image.NEAREST
    )

    return preprocessed_image

def convert(b1, b2, b3, source_folder, target_folder,filename,thread_id,client_ip):
    # Define the paths
    wd = os.getcwd()
    if filename == 'upload_image.tif':
        tif_path = os.path.join(wd, source_folder, f'upload_image_{thread_id}_{client_ip}.tif')
        jpg_filename = f'upload_preprocessed_{thread_id}_{client_ip}.jpg'
    else:
        tif_path = os.path.join(wd, source_folder, f'sentinel2_image_{thread_id}_{client_ip}.tif')
        jpg_filename = f'sentinel2_preprocessed_{thread_id}_{client_ip}.jpg'

    jpg_path = os.path.join(wd, target_folder, jpg_filename)

    # Load the tif file, preprocess, convert, and save it
    images = tifffile.imread(tif_path)
    images = preprocess(images, b1, b2, b3)
    images.save(jpg_path)
    print(f"Converted {tif_path} to {jpg_path}")
