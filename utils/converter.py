import os
import tifffile
import numpy as np
from PIL import Image
from cv2 import threshold, THRESH_BINARY, imread

def normalize(channel):
    min_val, max_val = np.min(channel), np.max(channel)
    normalized_channel = ((channel - min_val) / (max_val - min_val)) * 255
    return normalized_channel

def preprocess(image, b1, b2, b3):
    band1 = normalize(image[:, :, b1])
    band2 = normalize(image[:, :, b2])
    band3 = normalize(image[:, :, b3])

    image_array = np.stack([band3, band2, band1], axis=-1).astype('uint8')

    h, w, c = image_array.shape

    if h < 32 :
        preprocessed_image = Image.fromarray(image_array).resize(
            (h * 10, w * 10),
            Image.NEAREST
        )

    elif h < 64 :
        preprocessed_image = Image.fromarray(image_array).resize(
            (h * 5, w * 5),
            Image.NEAREST
        )

    elif h < 128 :
        preprocessed_image = Image.fromarray(image_array).resize(
            (h * 3, w * 3),
            Image.NEAREST
        )
    
    else :
        preprocessed_image = Image.fromarray(image_array).resize(
            (h * 1, w * 1),
            Image.NEAREST
        )

    return preprocessed_image

def convert(b1, b2, b3, source_folder, target_folder, uid, filename=None):
    # Define the paths
    wd = os.getcwd()
    if filename == 'upload_image.tif':
        tif_path = os.path.join(wd, source_folder, f'sentinel2_image_{uid}.tif')
        jpg_filename = f'sentinel2_preprocessed_{uid}.jpg'
    else:
        tif_path = os.path.join(wd, source_folder, f'sentinel2_image_{uid}.tif')
        jpg_filename = f'sentinel2_preprocessed_{uid}.jpg'

    jpg_path = os.path.join(wd, target_folder, jpg_filename)

    # Load the tif file, preprocess, convert, and save it
    images = tifffile.imread(tif_path)
    images = preprocess(images, b1, b2, b3)
    images.save(jpg_path)
    print(f"Converted {tif_path} to {jpg_path}")

def count_pixel(mask_path) :
    mask = imread(mask_path)

    _, binary_mask = threshold(mask, 50, 255, THRESH_BINARY)
    binary_mask = binary_mask.astype(np.uint8)
    binary_mask = binary_mask[:, :, 0] // 255
    count = np.sum(binary_mask)

    return count


def count_area(mask_path) : #m^2 detected solar panel
    pixel_detected = count_pixel(mask_path)
    spatial_resolution = 10 # in meters

    area = pixel_detected * (spatial_resolution)
    return area

def count_power(mask_path) : # Estimated watt generated from the solar panel
    area = count_area(mask_path)
    w = 80.4 #(w / m^2)
    power = (area * w) / 1000

    return round(power, 2)
