import os
from utils.dummy_datagen import create_dummy_data
from shutil import rmtree

def predict(validation_path, model_path, data_path) :
    os.system(f'python {validation_path} --weights {model_path} --data {data_path} --conf-thres 0.45')


def predict_from_path(source_path, model_name, dummy_main_path=None) :
    wd = os.getcwd() # Get working directory

    # Default dummy main path
    if not dummy_main_path :
        dummy_main_path = os.path.join(wd, 'utils')
    
    # Define the paths
    model_path = os.path.join(wd, 'utils', 'yolov5', 'runs', 'train-seg', model_name, 'weights', 'best.pt') # Best model path
    validation_path = os.path.join(wd, 'utils', 'yolov5', 'segment', 'val.py') # Validation script path
    data_path = os.path.join(wd, 'utils', 'predict', 'config', 'config.yaml') # Model config path
    
    create_dummy_data(dummy_main_path, source_path)

    # Run the validation script
    predict(validation_path, model_path, data_path)

    rmtree(os.path.join(dummy_main_path, 'predict')) # Delete dummy folder after predict
    rmtree(os.path.join(wd, 'utils', 'yolov5', 'runs', 'val-seg')) # Delete validation results after predict

    