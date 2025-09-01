# -*- coding: utf-8 -*-
"""
Created on Thu Aug  5 16:26:52 2021

@author: carreon_r
"""

from img_functions import *
from proc_functions import *
from dict_functions import *


%load select_directory('src_dir')
%load select_directory('dst_dir')

trans_imgs_dict = prep_stack_dict(src_dir)

proc_folder01 = [key for key in trans_imgs_dict.keys() if 'batch01' in key]
proc_folder02 = [key for key in trans_imgs_dict.keys() if 'batch02' in key]
proc_folder03 = [key for key in trans_imgs_dict.keys() if 'batch03' in key]


proc_folder = proc_folder01
#proc_folder = proc_folder02
#proc_folder = proc_folder03

def save_batch(trans_imgs_dict, proc_folder, dst_dir, start_slice = 0, end_slice= ''):
    
    new_dict = trans_imgs_dict.copy()
    keep_key(new_dict,proc_folder)
    
    get_imgs_dict(new_dict)
    
    for key,values in new_dict.items():
        
        avg_img = avg_frames_dict (values, output_type = 'img', start_slice = start_slice, end_slice = end_slice)
       
        file_name = os.path.join(dst_dir, key + '_avg_transmission.fits' )
        write_img(avg_img, file_name, base_dir='', overwrite=False)
        
    return