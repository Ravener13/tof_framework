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
src_dir = r"J:\700 Campaigns - internal\2021\PSI21_22NI\200_processed\01_Transmission_results\exp301_full"

# %load select_directory('dst_dir')
dst_dir = r"J:\700 Campaigns - internal\2021\PSI21_22NI\200_processed\02_stitched_results\temps_full_transmission"


# proc_folder01 = [key for key in trans_imgs_dict.keys() if 'batch01' in key]
# proc_folder02 = [key for key in trans_imgs_dict.keys() if 'batch02' in key]
# proc_folder03 = [key for key in trans_imgs_dict.keys() if 'batch03' in key]

proc_folder = []

trans_imgs_dict = prep_stack_dict(src_dir)
save_batch(trans_imgs_dict, proc_folder, dst_dir, idx = 0)
