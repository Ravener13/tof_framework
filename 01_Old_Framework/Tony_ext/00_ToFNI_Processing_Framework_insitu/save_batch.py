# -*- coding: utf-8 -*-
"""
Created on Thu Aug  5 16:26:52 2021

@author: carreon_r
"""

from stack_proc_func import *
from img_utils_mod import *
import pandas as pd


### NOTE: This is just for images saved with header

def save_batch(trans_imgs_dict, proc_folder, dst_dir, idx = 0):
    
    new_dict = trans_imgs_dict.copy()
    
    if proc_folder == []:
        proc_folder = [*trans_imgs_dict]
    
    keep_key(new_dict,proc_folder)
    
    for key,values in new_dict.items():
        
        list_img = [i for i in values[0]]
        
        img = np.zeros(get_img(list_img[0])[0].shape)
        
        header = get_img(list_img[int(len(list_img)/2)])[1]
        
        for item in list_img:
            
            img = img + get_img(item)[0]
        
        img = np.nan_to_num(img/len(list_img))
        
        file_name = os.path.join(dst_dir, format(idx, '03d') + '_transmission_pulse_' + key + '.fits' )
        
        img_final = (np.flip(img,0), header)
        write_img(img_final, file_name, base_dir='', overwrite=False)
        
        idx += 1
    return




# %load select_directory('src_dir')
src_dir = r"J:\900 Varia\2021\000_tony_data\03_Processed\01_transmission_results\exp1XX\02_exp102_04"

# %load select_directory('dst_dir')
dst_dir = r"J:\900 Varia\2021\000_tony_data\03_Processed\02_Stitched_transmission\exp1XX"

proc_folder = []

trans_imgs_dict = prep_stack_dict(src_dir)
save_batch(trans_imgs_dict, proc_folder, dst_dir, idx = 115)




#____________________________________________________________________________________________
### This is for insitu experiments where you have a dictionary in a dictionary

def save_batch_folders(trans_imgs_dict, proc_folder, dst_dir, idx = 0):
    
    new_dict = trans_imgs_dict.copy()
    
    if proc_folder == []:
        proc_folder = [*trans_imgs_dict]
    
    keep_key(new_dict,proc_folder)
    
    for key,folder in new_dict.items():
        
        folder_idx = 0
        
        for values in folder:
            
            list_img = [i for i in values]
            
            img = np.zeros(get_img(list_img[0])[0].shape)
            
            header = get_img(list_img[int(len(list_img)/2)])[1]
            
            for item in list_img:
                
                img = img + get_img(item)[0]
            
            img = np.nan_to_num(img/len(list_img))
            
            file_name = os.path.join(dst_dir, format(idx, '03d') + '_transmission_pulse_' + key + '_folder_' + format(folder_idx, '02d') + '.fits' )
            
            img_final = (np.flip(img,0), header)
            write_img(img_final, file_name, base_dir='', overwrite=False)
        
            idx += 1
            
            folder_idx += 1
    return



# %load select_directory('src_dir')
src_dir = r"J:\900 Varia\2021\000_tony_data\03_Processed\01_transmission_results\exp3XX_ws_filter"

# %load select_directory('dst_dir')
dst_dir = r"J:\900 Varia\2021\000_tony_data\03_Processed\02_Stitched_transmission\exp3XX_ws_filter"

proc_folder = []

trans_imgs_dict = prep_stack_dict(src_dir)
save_batch_folders(trans_imgs_dict, proc_folder, dst_dir, idx = 0)