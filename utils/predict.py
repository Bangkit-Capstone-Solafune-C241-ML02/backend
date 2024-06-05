import os
from utils.dummy_datagen import create_dummy_data
from shutil import rmtree


def predict_from_path(source_path, model_name, dummy_main_path=None) :
    wd = os.getcwd()

    
    if not dummy_main_path :
        dummy_main_path = os.path.join(wd, 'utils')
        
    model_path = os.path.join(wd, 'utils', 'yolov5', 'runs', 'train-seg', model_name, 'weights', 'best.pt')
    validation_path = os.path.join(wd, 'utils', 'yolov5', 'segment', 'val.py')
    data_path = os.path.join(wd, 'utils', 'predict', 'config', 'config.yaml')
    dummy_folder_path = os.path.join(wd, 'utils')
    
    create_dummy_data(dummy_main_path, source_path)


    os.system(f'python {validation_path} --weights {model_path} --data {data_path} --conf-thres 0.45')

    
    rmtree(os.path.join(dummy_folder_path, 'predict'))
    rmtree(os.path.join(wd, 'utils', 'yolov5', 'runs', 'val-seg'))

    