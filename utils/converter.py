import os
import tifffile
import numpy as np
from PIL import Image

def normalize(channel) :
    min_val, max_val = np.min(channel), np.max(channel)

    normalized_channel = ( (channel - min_val) / (max_val - min_val) ) * 255
    return normalized_channel

def preprocess(image) :
    band1 = normalize(image[:, :, 1])
    band2 = normalize(image[:, :, 2])
    band3 = normalize(image[:, :, 3])

    image_array = np.stack([band3, band2, band1], axis=-1).astype('uint8')
    preprocessed_image = Image.fromarray(image_array).resize(
      (image_array.shape[1] * 25, image_array.shape[0] * 25),
      Image.NEAREST)

    return preprocessed_image

def convert():
  # Define the paths
  wd = os.getcwd()
  tif_path = os.path.join(wd, 'utils','tif','sentinel2_image.tif')
  jpg_path = os.path.join(wd, 'utils','jpg','sentinel2_preprocessed.jpg')

  # Load the tif file, prprocess, convert, and save it
  images = tifffile.imread(tif_path)
  images = preprocess(images)
  images.save(jpg_path)