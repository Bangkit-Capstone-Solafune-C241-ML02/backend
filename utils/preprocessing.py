import os
import tifffile as tiff
import numpy as np
import cv2

def get_file_names(path) :
    return sorted([i for i in os.listdir(path) if i[0] != '.'])

def read_images(path) :
    file_names = get_file_names(path)

    images = []
    for file_name in file_names :
        file_path = os.path.join(path, file_name)
        
        image = tiff.imread(file_path)

        images.append(np.array(image, dtype=np.float32))
    
    return images


def select_band(band, path, preprocess=None) :
    images = read_images(path)

    extracted_channel = []

    for image in images :
        extracted_channel.append(image[:, :, band])

    if preprocess == 'min_max' :
        min, max = find_min_max(extracted_channel)
        extracted_channel = norm_min_max(extracted_channel, min, max)

    return extracted_channel


def find_min_max(arr) :
    min_val = np.min(arr[0])
    max_val = np.max(arr[0])

    for img in arr:
        min_val = np.minimum(min_val, np.min(img))
        max_val = np.maximum(max_val, np.max(img))

    return min_val, max_val


def norm_min_max(arr, min=None, max=None) :
    normalized_img = []

    if min == None or max == None :
        min, max = find_min_max(arr)

    for img in arr :
        img = (img - min) / (max - min)
        normalized_img.append(img)

    return normalized_img


def rescale(arr, ch=None) :
    
    rescaled_img = []

    min_max_bands = {
        0 : (0, 3609),
        1 : (22.180136, 7627.1133),
        2 : (104.0, 8188.0),
        3 : (80.08951, 9220.0),
        4 : (109.74214, 7533.0),
        5 : (66.0, 7251.0),
        6 : (65.5, 7193.0),
        7 : (87.7459, 10516.0),
        8 : (74.0, 7076.0),
        9 : (90.4, 5163.5),
        10 : (96.06991, 7075.5),
        11 : (82.5, 6870.0)
    }

    if ch != None :
        # min, max = 0, 65536
        min, max = min_max_bands[ch]
    else :
        min, max = -1, 1
        
    for img in arr :    
        img = ( (img - min)/(max-min) ) * 255
        img[img < 0] = 0
        rescaled_img.append(img)

    return rescaled_img


def formula(bandA, bandB) :
    new_band = []
    for i in range(len(bandA)) :
        a, b = bandA[i], bandB[i]
        processed_band = (a-b) / ((a+b) + 1e-10)
        
        new_band.append(processed_band)

    return new_band


def export_images(images, source_path, export_path) :
    file_names = get_file_names(source_path)


    for i in range(len(file_names)) :
        image = images[i]
        H, W, C = image.shape
        
        image = cv2.resize(image, (W * 10, H * 10), interpolation=cv2.INTER_CUBIC)
        
        file_path = os.path.join(export_path, file_names[i])
        tiff.imwrite(file_path, image)


def preprocess(folder_path) :
    # Python list for containing every channels from image
    ch_num = [0,1,2,3,4,5,6,7,8,9,10,11]
    channels = []
    for i in ch_num :
        ch = rescale(select_band(i, folder_path), ch=i)
        channels.append(ch)

    for i in range(1, 4) :
        for j in range(1, 4) :
            if i != j :
                ch = rescale(formula(channels[i], channels[j]))
                channels.append(ch)

    for i in range(10, 12) :
        for j in range(10, 12) :
            if i != j :
                ch = rescale(formula(channels[i], channels[j]))
                channels.append(ch)

    
    images = [np.stack([channels[i][j] for i in range(len(channels))], axis=-1, dtype=np.float32) for j in range(len(channels[0]))]
    
    return images
    
        