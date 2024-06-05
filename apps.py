from utils.predict import predict_from_path
import tifffile as tiff
import os

model_name = 'exp50'
source_path = os.path.join(os.getcwd(), 'utils', 'tif_from_sentinel')
predict_from_path(source_path, model_name)