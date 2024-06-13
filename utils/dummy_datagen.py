import os
import shutil
import tifffile as tiff
from utils.preprocessing import preprocess, export_images

def create_dummy_folder(dummy_main_path, uid) :
    """
    Function to create the folder that mimmick the trainig and validation folder structure of yolov5
    Folder Structure :
    
    masks
    |    |-sentinel_2_mask.jpg
    |    |-sentinel_2_image_x.jpg
    |
    painted_iamge
    |    |-sentinel_2_mask.jpg
    |    |-sentinel_2_image_x.jpg
    |
    predict
    |-preprocessed # Placeholder folder for preprocessed image
    |    |-sentinel_2_image_0.tif
    |    |-sentinel_2_image_x.tif
    |
    |-config
    |    |-config.yaml
    |
    |-train
    |    |-images
    |    |    |-sentinel_2_image_0.tif
    |    |    |-sentinel_2_image_x.tif
    |    |
    |    |-labels
    |         |-sentinel_2_image_0.txt
    |         |-sentinel_2_image_x.txt
    |   
    |-val
         |-images
         |    |-sentinel_2_image_0.tif
         |    |-sentinel_2_image_x.tif
         |
         |-labels
              |-sentinel_2_image_0.txt
              |-sentinel_2_image_x.txt

    """
    # Main folder
    masks_folder_path = os.path.join(dummy_main_path, f'mask_{uid}')
    painted_image_folder_path = os.path.join(dummy_main_path, f'painted_image_{uid}')
    dummy_folder_path = os.path.join(dummy_main_path, f'predict_{uid}')
    # Train, Val, Config, Preprocessed folder
    train_folder_path = os.path.join(dummy_folder_path, 'train')
    val_folder_path = os.path.join(dummy_folder_path, 'val')
    config_folder_path = os.path.join(dummy_folder_path, 'config')
    preprocessed_folder_path = os.path.join(dummy_folder_path, 'preprocessed')
    # Images and Labels folder
    train_image_folder_path = os.path.join(train_folder_path, 'images')
    train_label_folder_path = os.path.join(train_folder_path, 'labels')
    val_image_folder_path = os.path.join(val_folder_path, 'images')
    val_label_folder_path = os.path.join(val_folder_path, 'labels')

    # Create Folder
    os.makedirs(masks_folder_path, exist_ok=True) # Masks folder
    os.makedirs(dummy_folder_path, exist_ok=True) # Main folder
    os.makedirs(painted_image_folder_path, exist_ok=True) # Painted image folder

    os.makedirs(train_folder_path, exist_ok=True) # Train folder
    os.makedirs(val_folder_path, exist_ok=True) # Val folder
    os.makedirs(config_folder_path, exist_ok=True) # Config folder
    os.makedirs(preprocessed_folder_path, exist_ok=True) # Preprocessed folder

    os.makedirs(train_image_folder_path, exist_ok=True) # Train images folder
    os.makedirs(train_label_folder_path, exist_ok=True) # Train labels folder
    os.makedirs(val_image_folder_path, exist_ok=True) # Val images folder
    os.makedirs(val_label_folder_path, exist_ok=True) # Val labels folder

    # Folder path dictionary
    folder_path = {
        'rgb'
        'painted_image' : painted_image_folder_path,
        'masks' : masks_folder_path,
        'dummy' : dummy_folder_path,
        'train' : train_folder_path,
        'val' : val_folder_path,
        'config' : config_folder_path,
        'preprocessed' : preprocessed_folder_path,
        'train_image' : train_image_folder_path,
        'train_label' : train_label_folder_path,
        'val_image' : val_image_folder_path,
        'val_label' : val_label_folder_path
    }

    return folder_path

def write_dummy_config(dummy_folder_path) :
    """
    Function to create a dummy config to specify the train and validation data to the yolov5 validation mode
    """

    # Define the yaml config
    config =  f"""path: {dummy_folder_path}
train: train
val: val

nc: 1
names: ['solarpanel']"""

    # Specify config path on the dummy folder
    config_path = os.path.join(dummy_folder_path, 'config')

    # Write the config
    with open(os.path.join(config_path, f'config.yaml'), 'w') as yaml :
        yaml.write(config)
    
def delete_dummy_folder(main_path, uid) :
    """
    Delete the whole dummy folder after a predict
    """
    # Define the dummy folder
    dummy_folder_path = os.path.join(main_path, f'predict_{uid}')

    try :
        # If the folder exist, delete it
        if os.path.exists(dummy_folder_path) :
            shutil.rmtree(dummy_folder_path)
    except Exception as e :
        print(f'Error while deleting file: {e}')

def write_tiff(source_path, destination_path) :
    file_names = sorted(os.listdir(source_path))

    for file_name in file_names :
        source_copy = os.path.join(source_path, file_name)
        destination_copy = os.path.join(destination_path, file_name)

        shutil.copy(source_copy, destination_copy)

def write_dummy_label(source_path, destination_path) :
    file_names = [file.replace('tif', 'txt') for file in sorted(os.listdir(source_path))]

    # Fake dummy label
    dummy_labels = "0 0.05652173913043478 0.375 0.043478260869565216 0.3875 0.043478260869565216 0.39166666666666666 0.034782608695652174 0.4 0.034782608695652174 0.4041666666666667 0.021739130434782608 0.4166666666666667 0.008695652173913044 0.4166666666666667 0.004347826086956522 0.42083333333333334 0.0 0.4166666666666667 0.0 0.49166666666666664 0.021739130434782608 0.49166666666666664 0.0391304347826087 0.5083333333333333 0.0391304347826087 0.5125 0.043478260869565216 0.5166666666666667 0.043478260869565216 0.5208333333333334 0.04782608695652174 0.525 0.04782608695652174 0.5291666666666667 0.05217391304347826 0.5291666666666667 0.05652173913043478 0.5333333333333333 0.06521739130434782 0.5333333333333333 0.06956521739130435 0.5375 0.07391304347826087 0.5375 0.08695652173913043 0.55 0.08695652173913043 0.5541666666666667 0.09130434782608696 0.5583333333333333 0.09130434782608696 0.5666666666666667 0.08695652173913043 0.5708333333333333 0.08695652173913043 0.575 0.0782608695652174 0.5833333333333334 0.07391304347826087 0.5833333333333334 0.06956521739130435 0.5875 0.06086956521739131 0.5875 0.05652173913043478 0.5833333333333334 0.05217391304347826 0.5833333333333334 0.0391304347826087 0.5708333333333333 0.0391304347826087 0.5666666666666667 0.034782608695652174 0.5625 0.034782608695652174 0.5541666666666667 0.02608695652173913 0.5458333333333333 0.0 0.5458333333333333 0.0 0.8708333333333333 0.13043478260869565 0.8708333333333333 0.13478260869565217 0.875 0.1391304347826087 0.8708333333333333 0.15217391304347827 0.8708333333333333 0.16956521739130434 0.8541666666666666 0.16956521739130434 0.85 0.19130434782608696 0.8291666666666667 0.1956521739130435 0.8291666666666667 0.21304347826086956 0.8125 0.21304347826086956 0.8083333333333333 0.23478260869565218 0.7875 0.2826086956521739 0.7875 0.28695652173913044 0.7833333333333333 0.29130434782608694 0.7833333333333333 0.2956521739130435 0.7791666666666667 0.2956521739130435 0.775 0.3 0.7708333333333334 0.3 0.7625 0.30434782608695654 0.7583333333333333 0.30434782608695654 0.7375 0.3 0.7333333333333333 0.3 0.725 0.2826086956521739 0.7083333333333334 0.2782608695652174 0.7083333333333334 0.2565217391304348 0.6875 0.2565217391304348 0.6416666666666667 0.2391304347826087 0.625 0.23478260869565218 0.625 0.21304347826086956 0.6041666666666666 0.21304347826086956 0.5583333333333333 0.1956521739130435 0.5416666666666666 0.19130434782608696 0.5416666666666666 0.16956521739130434 0.5208333333333334 0.16956521739130434 0.5166666666666667 0.15217391304347827 0.5 0.14782608695652175 0.5 0.12608695652173912 0.4791666666666667 0.12608695652173912 0.43333333333333335 0.10869565217391304 0.4166666666666667 0.10434782608695652 0.4166666666666667 0.09130434782608696 0.4041666666666667 0.09130434782608696 0.4 0.08260869565217391 0.39166666666666666 0.08260869565217391 0.3875 0.06956521739130435 0.375"

    for file_name in file_names :
        file_path = os.path.join(destination_path, file_name)
        
        # Write the dummy label
        with open(file_path, 'w') as data :
            data.write(dummy_labels)


def create_dummy_data(dummy_main_path, source_path, uid, from_sentinel=True) :
    folder_path = create_dummy_folder(dummy_main_path, uid)

    if from_sentinel :
        image_path = os.path.join(source_path, f'sentinel2_image_{uid}.tif')
    else :
        image_path = os.path.join(source_path, f'upload_image_{uid}.tif')

    images = preprocess(image_path)
    export_images(images, image_path, folder_path['preprocessed'])

    write_tiff(folder_path['preprocessed'], folder_path['train_image'])
    write_tiff(folder_path['preprocessed'], folder_path['val_image'])

    write_dummy_label(folder_path['preprocessed'], folder_path['train_label'])
    write_dummy_label(folder_path['preprocessed'], folder_path['val_label'])

    write_dummy_config(folder_path['dummy'])
    


    

