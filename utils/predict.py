import os
from utils.dummy_datagen import create_dummy_data
from utils.preprocessing import create_paint
from shutil import rmtree
from tifffile import imread as tiffimread
from cv2 import imread as cv2imread
from cv2 import imwrite as cv2imwrite

def predict(validation_path, model_path, data_path) :
    os.system(f'python {validation_path} --weights {model_path} --data {data_path} --conf-thres 0.25')


def export_painted_mask(dummy_main_path, source_path) :
    for file_name in [i for i in os.listdir(source_path) if i[0] != '.'] :
        tiff_path = os.path.join(source_path, file_name)
        mask_path = os.path.join(dummy_main_path, 'masks', 'mask.jpg')
        save_path = os.path.join(dummy_main_path, 'painted_image', file_name.replace('.tif', '.jpg'))

        tiff_image = tiffimread(tiff_path)
        mask_image = cv2imread(mask_path)

        painted_image = create_paint(tiff_image, mask_image)
        cv2imwrite(save_path, painted_image)

def clear_folder(folder_path) :
    for folder in [i for i in os.listdir(folder_path) if i[0] != '.'] :
        try :
            rmtree(os.path.join(folder_path, folder))
        except :
            os.remove(os.path.join(folder_path, folder))

def predict_from_path(source_path, model_name, dummy_main_path=None) :
    wd = os.getcwd() # Get working directory

    # Default dummy main path
    if not dummy_main_path :
        dummy_main_path = os.path.join(wd, 'utils')
    
    # Define the paths
    model_path = os.path.join(wd, 'utils', 'yolov5', 'runs', 'train-seg', model_name, 'weights', 'best.pt') # Best model path
    validation_path = os.path.join(wd, 'utils', 'yolov5', 'segment', 'val.py') # Validation script path
    val_seg_path = os.path.join(wd, 'utils', 'yolov5', 'runs', 'val-seg') # Validation results path
    mask_path = os.path.join(dummy_main_path, 'masks') # Mask path
    painted_mask = os.path.join(dummy_main_path, 'painted_image') # Painted mask path
    data_path = os.path.join(wd, 'utils', 'predict', 'config', 'config.yaml') # Model config path

    clear_folder(mask_path) # Clear mask folder
    clear_folder(painted_mask) # Clear painted mask folder
    
    create_dummy_data(dummy_main_path, source_path)

    # Run the validation script
    predict(validation_path, model_path, data_path)
    export_painted_mask(dummy_main_path, source_path)


    rmtree(os.path.join(dummy_main_path, 'predict')) # Delete dummy folder after predict
    clear_folder(val_seg_path) # Clear validation results folder
    


    