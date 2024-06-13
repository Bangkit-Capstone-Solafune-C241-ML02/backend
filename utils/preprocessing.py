import os
import tifffile as tiff
import numpy as np
import cv2

def get_file_names(path) :
    if os.name == 'nt':
        return [path.split('\\')[-1]]
    else :
        return [path.split('/')[-1]]

def read_images(file_path) :
    images = tiff.imread(file_path)

    return [images]


def select_band(band, path) :
    images = read_images(path)

    extracted_channel = []

    for image in images :
        extracted_channel.append(image[:, :, band] * 10000)

    return extracted_channel

def norm_min_max(image) :
    min_val, max_val = np.min(image), np.max(image)
    normalized_img = ( (image - min_val) / (max_val - min_val) ) * 255

    return normalized_img

def create_paint(image, mask) :
    channels = []
    for i in range(1, 4) :
        channels.append(norm_min_max(image[:, :, i]))

    rgb_image = np.stack(channels, axis=-1).astype(np.uint8)
    h, w, c = rgb_image.shape
    
    if h < 32 :
        rgb_image = cv2.resize(rgb_image, (w * 10, h * 10), interpolation=cv2.INTER_NEAREST)

    elif h < 64 :
        rgb_image = cv2.resize(rgb_image, (w * 5, h * 5), interpolation=cv2.INTER_NEAREST)

    elif h < 128 :
        rgb_image = cv2.resize(rgb_image, (w * 3, h * 3), interpolation=cv2.INTER_NEAREST)
    
    else :
        rgb_image = cv2.resize(rgb_image, (w, h), interpolation=cv2.INTER_NEAREST)

    if np.max(mask) > 0 :
        
        _, mask_binary = cv2.threshold(mask, 50, 255, cv2.THRESH_BINARY)
        mask_binary = mask_binary[:, :, 0]

        highlight_color = [0, 0, 255]
        alpha = 0.4

        highlighted_image = rgb_image.copy()
        for c in range(3) :
            highlighted_image[:, :, c] = np.where(mask_binary == 255, highlight_color[c], rgb_image[:, :, c])

        painted_image = cv2.addWeighted(rgb_image, 1 - alpha, highlighted_image, alpha, 0)

        return painted_image        

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
        
        image = cv2.resize(image, (W * 1, H * 1), interpolation=cv2.INTER_CUBIC)
        
        file_path = os.path.join(export_path, file_names[i])
        tiff.imwrite(file_path, image)


def preprocess(file_path) :
    # Python list for containing every channels from image
    ch_num = [0,1,2,3,4,5,6,7,8,9,10,11]
    channels = []
    for i in ch_num :
        ch = select_band(i, file_path)
        channels.append(ch)

    for i in range(1, 4) :
        for j in range(1, 4) :
            if i != j :
                ch = formula(channels[i], channels[j])
                channels.append(ch)

    for i in range(10, 12) :
        for j in range(10, 12) :
            if i != j :
                ch = formula(channels[i], channels[j])
                channels.append(ch)

    
    images = [np.stack([channels[i][j] for i in range(len(channels))], axis=-1, dtype=np.float32) for j in range(len(channels[0]))]

    preprocessed_images = []
    for image in images :
        preprocessed_images.append(norm_min_max(image))
    
    return preprocessed_images
    
        