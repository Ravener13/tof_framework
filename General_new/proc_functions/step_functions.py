# -*- coding: utf-8 -*-
"""
Created on Fri Jun 17 20:36:05 2022

@author: carreon_r
"""
import os, glob, time
import numpy as np
from tqdm import tqdm
from astropy.io import fits
import matplotlib.pyplot as plt
import datetime

from img_functions import *
from proc_functions import *
from dict_functions import *


# src_dir = r"J:\900 Varia\2021\000_tony_data\03_Processed_step_by_step\00_Overlap_correction\test"
# dst_dir = r'J:\900 Varia\2021\000_tony_data\03_Processed_step_by_step\01_transmission_results\test'

# =============================================================================
#                        reading_step
# =============================================================================

def reading_step (src_dir, proc_folder = [], **kwargs):
    
    param_dict = {}
    
    stack_dict = prep_stack_dict (src_dir)
    weights_DataFrame = weighting_func (src_dir)
    
    keep_folder = proc_folder 
    keep_key_weights (stack_dict, weights_DataFrame, keep_folder)
    
    get_imgs_dict(stack_dict)
    
    param_dict ['weights_DataFrame'] = weights_DataFrame
    
    return stack_dict, param_dict



# =============================================================================
#                        testing_mode_step
# =============================================================================

def testing_mode_step (src_dir, proc_folder = [], keep_acq_numb = 1, **kwargs):
    
    param_dict = {}
    
    test_dict = prep_stack_dict (src_dir)
    weights_DataFrame = weighting_func (src_dir)
    
    keep_folder = proc_folder 
    keep_key_weights (test_dict, weights_DataFrame, keep_folder)
    
    for key, value in test_dict.items():
        
        if len(value) < keep_acq_numb:
            test_dict [key] = value
        else:
            test_dict [key] = value[0 : keep_acq_numb]
        
    get_imgs_dict(test_dict)
    
    param_dict ['weights_DataFrame'] = weights_DataFrame
    
    return test_dict, param_dict


# =============================================================================
#                        pre_processing_step
# =============================================================================


# pre_proc_seq = [crop_img, outlier_removal, binning_frames, ws_filter, outlier_removal,  stack_avg]
# param_dict = dict (roi_crop = [1, 332, 509, 129], threshold = 0, start_img = 6, binning_factor = 5, ws_filter_size = 2)


def pre_processing_step (stack_dict, pre_proc_seq, param_dict, **kwargs):
    
    proc_dict = stack_dict.copy()
    
    sep_list = ['stack_averaging','binning_frames', 'binning_acquisitions']
    seq = sequence_separator (pre_proc_seq, sep_list)
    
    for idx in range (len(seq)):
        func_names = str([func.__name__ for func in seq[idx]])
        
        if 'stack_averaging' in func_names:
            proc_dict = exec_averaging_dict(proc_dict, sequence = seq[idx], **param_dict)
        elif 'binning_frames' in func_names:
            proc_dict = exec_bin_frames_dict(proc_dict, sequence = seq[idx] , **param_dict)
        elif 'binning_acquisitions' in func_names:
            proc_dict = exec_bin_aquisitions_dict(proc_dict, sequence = seq[idx] , **param_dict)
        else:
            proc_dict = exec_filters_dict(proc_dict, sequence = seq[idx] , **param_dict)
    
    return proc_dict



# =============================================================================
#                        processing_step
# =============================================================================


# stack_dict
# weights_DataFrame
# reg_img
# rois_list
# BB_mask
# TFC_ref_img
# nca

# proc_seq = ['scrubbing_correction_dict']
# list_proc_param = ['weights_DataFrame', 'ref_avg_img', 'BB_mask']


                         
def processing_step (proc_dict, proc_seq, param_dict, **kwargs):
    
    from functools import partial
    
    proc_param = {}
    stack_dict = proc_dict.copy()
    
    proc_param ['stack_dict'] = eval('stack_dict')
    proc_param.update(param_dict)
    
       
    #proc_function = {'scrubbing_correction': partial(scrubbing_correction_dict, **param_proc)}
    
    # fuctions_dict = {'scrubbing_correction_dict' : scrubbing_correction_dict,
    #                  'image_registration_dict': image_registration_dict,
    #                  'SBKG_correction_dict': SBKG_correction_dict,
    #                  'TFC_correction_dict': TFC_correction_dict,
    #                  }
    
    parameters = proc_param
    for function in proc_seq:
        
            # generate the callable function with a given set of parameters
        proc_function = {function.__name__ : partial(function, **parameters)}
        
            # Operate the function 
        new_dict_result = proc_function[function]()
        
            #replace the old dictionary with the new result
        proc_param ['stack_dict'] = new_dict_result
        
            # update parameters inside the for loop
        parameters = proc_param
        
    proc_dict = parameters ['stack_dict']
    
    return proc_dict



# =============================================================================
#                        saving_step
# =============================================================================

# stack_dict

def saving_step (stack_dict, dst_dir, img_name = 'test', **kwargs):
    
    value = [values for values in stack_dict.values()]
        
    if len(value[0]) > 1:
        print('Saving images as a time series of acquisitions')
        save_continuous_dict (stack_dict, dst_dir, img_name = img_name, **kwargs)
    
    else:
        print('Saving images as a single acquisition')
        save_dict (stack_dict, dst_dir, img_name = img_name, **kwargs)
    





