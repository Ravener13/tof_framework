# -*- coding: utf-8 -*-
"""
Created on Wed Aug  9 13:15:08 2023

@author: carreon_r
"""


import os
import numpy as np
from astropy.io import fits


def get_img(file_name, base_dir='', squeeze=True):
    
    from astropy.io import fits
    import os
    import warnings
    import matplotlib.pyplot as plt
    import numpy as np
    
        # get the file extension to identify the type
    _ , ext = os.path.splitext(file_name)
    
        # case of FITS files
    if ext == '.fits':
        
            # disable warnings because of possible bad characters in the header
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            
                # open the file and get the image data
            with fits.open(os.path.join(base_dir, file_name)) as hdul:
                
                img = hdul[0].data
        
                # reverse the y coordinates (for consistency with ImageJ)
            img = np.flip(img, 0)
    
        # case of TIFF files
    elif ext == '.tif':
        
            # get the image
        img = plt.imread(os.path.join(base_dir, file_name))
        
        # general case
    else:
        
            # get the image
        img = plt.imread(os.path.join(base_dir, file_name))
    
        # if the 'squeeze' option is on, remove dimensions with size 1
    if squeeze:
        img = np.squeeze(img)
    
        # return the data
    return img




def read_fits(folder_path):
    image_dict = {}
    
    if any(os.path.isdir(os.path.join(folder_path, item)) for item in os.listdir(folder_path)):
        subfolders = [subfolder for subfolder in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, subfolder))]
        
        for subfolder in subfolders:
            subfolder_path = os.path.join(folder_path, subfolder)
            image_dict[subfolder] = {}
            
            file_list = os.listdir(subfolder_path)
            fits_files = [file for file in file_list if file.endswith('.fits')]
            
            for fits_file in fits_files:
                file_path = os.path.join(subfolder_path, fits_file)
                
                #with fits.open(file_path) as hdul:
                #    image_data = hdul[0].data
                #    image_dict[subfolder][fits_file] = image_data
                image_data = get_img(file_path)
                image_dict[subfolder][fits_file] = image_data
                
    else:
        file_list = os.listdir(folder_path)
        fits_files = [file for file in file_list if file.endswith('.fits')]
        
        for fits_file in fits_files:
            file_path = os.path.join(folder_path, fits_file)
            
            #with fits.open(file_path) as hdul:
            #    image_data = hdul[0].data
           #     image_dict[fits_file] = image_data
            image_data = get_img(file_path)
            image_dict[fits_file] = image_data
    
    return image_dict




def calc_trans(int_dict, ob_dict):
    trans_dict = {}

    for parent_key, child_dict in int_dict.items():
        trans_dict[parent_key] = {}  # Create a nested dictionary for the parent
        
        child_arrays = list(child_dict.values())  # Get the child arrays
        ob_arrays = list(ob_dict.values())  # Get the ob_dict arrays
        
        for i, (child_key, child_array) in enumerate(child_dict.items()):
            ob_array = ob_arrays[i]  # Get the corresponding ob_dict array
            trans_array = child_array / ob_array  # Calculate the division
            
            trans_dict[parent_key][child_key] = trans_array  # Store in the trans_dict
    
    return trans_dict



def save_fits(res_imgs_dict, output_folder):
    
    for parent_folder, child_dict in res_imgs_dict.items():
        os.makedirs(output_folder, exist_ok=True)
        
        for i,(key, value) in enumerate(child_dict.items()):
            
            file_name = os.path.join(output_folder, parent_folder, f'{parent_folder}_trans_{i:05d}.fits')
            
            write_img(value, file_name)



################################################################################


def BE_height_mapping(folder_path, min_range, max_range): 
    
    res_dict = {}

    subfolders = [subfolder for subfolder in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, subfolder))]

    for subfolder in subfolders:
        subfolder_path = os.path.join(folder_path, subfolder)
        parent_folder = os.path.basename(folder_path)
        key = f"{parent_folder}_{subfolder}"
        res_dict[key] = {}

        file_list = os.listdir(subfolder_path)
        fits_files = sorted([file for file in file_list if file.endswith('.fits')])
        
        min_img = []
        max_img = []
        
        for fits_file in fits_files:
            file_path = os.path.join(subfolder_path, fits_file)
            
            img_number = int(fits_file.split('_')[-1].split('.')[0])
            
            if img_number in min_range:
                
                img = get_img(file_path)
                #with fits.open(file_path) as hdul:
                #    img = hdul[0].data
                min_img.append(img)
            
            if img_number in max_range:
                img = get_img(file_path)
                #with fits.open(file_path) as hdul:
                #    img = hdul[0].data
                max_img.append(img)
        
        avg_min_img = np.nanmean(min_img, axis=0)
        avg_max_img = np.nanmean(max_img, axis=0)
        
        res_img = avg_max_img - avg_min_img
        res_dict[key]['res_img'] = res_img
    
    return res_dict


def write_img(img, file_name, base_dir='', overwrite=False):
    
    import os
    from astropy.io import fits
    
        # compute the destination file name
    dst_name = os.path.join(base_dir, file_name)
    
        # get the destination directory
    dst_name_dir, _ = os.path.split(dst_name)
    
        # and create this destination directory if it does not exist
    if not os.path.exists(dst_name_dir):
        os.makedirs(os.path.join(dst_name_dir,''))
    
            # save the processed image
    try:                        
        hdu = fits.PrimaryHDU(np.flip(img,0))
        #hdu.header = img[1]
        hdu.writeto(dst_name, overwrite=overwrite)
        
        # output the error message if necessary
    except Exception as detail:
        print("Could not write the destination image:", detail) 
        
        
        
def save_dict_fits(res_imgs_dict, output_folder):
    
    for parent_folder, child_dict in res_imgs_dict.items():
        os.makedirs(output_folder, exist_ok=True)
        
        for key, value in child_dict.items():
            
            file_name = os.path.join(output_folder, f'{parent_folder}.fits')
            
            write_img(value, file_name)
                

############################################################################


def remove_neg(folder_path):
    image_dict = {}
    
    # Get a list of all .FITS files in the folder
    fits_files = [file for file in os.listdir(folder_path) if file.endswith('.fits')]
    
    parent_path, folder_name = os.path.split(folder_path)
    filtered_folder_path = os.path.join(parent_path, f"{folder_name}_filtered")
    os.makedirs(filtered_folder_path, exist_ok=True)
    
    for i, fits_file in enumerate(fits_files):
        
        file_path = os.path.join(folder_path, fits_file)
        
        image_data = get_img(file_path)
        
        filtered_image_data = np.maximum(image_data, 0)
    
        # Save the image dictionary
        output_file_name = f"{fits_file[:-5]}_{i:05d}.fits"
        output_file_path = os.path.join(filtered_folder_path, output_file_name)
    
        write_img(filtered_image_data, output_file_path)
    return 



############################################################################
####                    to get the transmission pixel-wise
############################################################################



folder_path =  r'J:\700 Campaigns - internal\2022\PSI22_04NI\00_Processed\01_Transmission_results\000_exp3000_trans\01_LP30_oper_20C_15min_avg_test'

out_path = r'J:\700 Campaigns - internal\2022\PSI22_04NI\00_Processed\01_Transmission_results\000_exp3000_trans\01_LP30_oper_20C_15min_avg_test\trans_frame_wise'

ob_path =  r'J:\700 Campaigns - internal\2022\PSI22_04NI\00_Processed\01_Transmission_results\000_OBs_merged\00_pre_oper_binned'
ob_dict = read_fits(ob_path)

    

for subfolder_path in os.listdir(folder_path):
    subfolder_full_path = os.path.join(folder_path, subfolder_path)
    
    if os.path.isdir(subfolder_full_path):
        int_dict = read_fits(subfolder_full_path)
        trans_dict = calc_trans(int_dict, ob_dict)
        
        output_folder = os.path.join(out_path, subfolder_path)
        os.makedirs(output_folder, exist_ok=True)
        
        save_fits(trans_dict, output_folder)




############################################################################
#                   to get the maps
############################################################################



folder_path = r'J:\700 Campaigns - internal\2022\PSI22_04NI\00_Processed\01_Transmission_results\000_exp3000_trans\01_LP30_oper_20C_15min_avg_test\trans_frame_wise'

l_min = 189
l_max = 193

h_min = 196
h_max = 200


min_range = range(l_min, l_max) #starting range (max 143)
max_range = range(h_min, h_max) #ending range (min 152)

res_imgs_dict = {}

for subfolder_path in os.listdir(folder_path):
    subfolder_path_path = os.path.join(folder_path, subfolder_path)
    res_dict = BE_height_mapping(subfolder_path_path, min_range, max_range)
    res_imgs_dict.update(res_dict)


output_folder = r'J:\700 Campaigns - internal\2022\PSI22_04NI\00_Processed\01_Transmission_results\000_exp3000_trans\01_LP30_oper_20C_15min_avg_test\heigh_maps\testLiC6_'+ str(l_min)+'_'+str(l_max)+'_n_'+str(h_min)+'_'+str(h_max)

save_dict_fits(res_imgs_dict, output_folder)



############################################################################
#                   to filter negative values in the maps 
############################################################################

folder_path = output_folder

remove_neg(folder_path)
