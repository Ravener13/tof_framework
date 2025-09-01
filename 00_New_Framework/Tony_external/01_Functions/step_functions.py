# -*- coding: utf-8 -*-
"""
Created on Fri Jun 17 20:36:05 2022

@author: carreon_r
"""
import os, glob, time
import numpy as np
from tqdm import tqdm, trange
from astropy.io import fits
import matplotlib.pyplot as plt
import datetime, time
from copy import deepcopy

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
    
    proc_param = deepcopy(param_dict)
    proc_dict = deepcopy(stack_dict)
    
    sep_list = ['stack_averaging','binning_frames', 'binning_acquisitions']
    seq = sequence_separator (pre_proc_seq, sep_list)
    
    for idx in range (len(seq)):
        func_names = str([func.__name__ for func in seq[idx]])
        
        if 'stack_averaging' in func_names:
            proc_dict = exec_averaging_dict(proc_dict, sequence = seq[idx], **proc_param)
        elif 'binning_frames' in func_names:
            proc_dict = exec_bin_frames_dict(proc_dict, sequence = seq[idx] , **proc_param)
        elif 'binning_acquisitions' in func_names:
            proc_dict = exec_bin_aquisitions_dict(proc_dict, sequence = seq[idx] , **proc_param)
        else:
            proc_dict = exec_filters_dict(proc_dict, sequence = seq[idx] , **proc_param)
    
    return proc_dict



# =============================================================================
#                        processing_step
# =============================================================================

                         
def processing_step (proc_dict, proc_seq, param_dict, **kwargs):
    
    from functools import partial
    
    proc_param = {}
    stack_dict = deepcopy(proc_dict)
    
    proc_param ['stack_dict'] = eval('stack_dict')
    proc_param.update(param_dict)
    
    for function in proc_seq:
        
            # Get the function name
        key = function.__name__
            # generate the callable function with a given set of parameters
        proc_function = {key : partial(function, **proc_param)}

            # Operate the function 
        new_dict_result = proc_function[key]()
        
            #update parameters 
        proc_param ['stack_dict'] = new_dict_result
        
            # update parameters inside the for loop
        #parameters = proc_param
        
    processed_dict = proc_param ['stack_dict']
    
    return processed_dict



# =============================================================================
#                        saving_step
# =============================================================================

# stack_dict

def saving_step (stack_dict, dst_dir, img_name = 'test', save_energies = False, **kwargs):
    
    save_proc_dict = deepcopy(stack_dict)
    value = [values for values in save_proc_dict.values()]
    
    if save_energies:
        print('Saving images as HE and LE stacks')
        save_energies_dict (save_proc_dict, dst_dir, img_name = img_name, **kwargs)
        
    elif len(value[0]) > 1:
        print('Saving images as a time series of acquisitions')
        save_continuous_dict (save_proc_dict, dst_dir, img_name = img_name, **kwargs)
        
    else:
        print('Saving images as a single acquisition')
        save_dict (save_proc_dict, dst_dir, img_name = img_name, **kwargs)
    


# =============================================================================
#                        full_processing
# =============================================================================

    # the weights_DataFrame should be already in the parameters
def full_processing (src_dir, dst_dir, proc_folder, sequence, proc_parameters, img_name = 'transmission', save = True, testing = False, **kwargs):
    
    import time
    start = time.time()
    
    param_dict = deepcopy(proc_parameters)
    
    if testing:
        proc_dict, weights_DataFrame = testing_mode_step (src_dir, proc_folder = proc_folder, **param_dict)
    
    else:
        proc_dict, weights_DataFrame = reading_step (src_dir, proc_folder = proc_folder, **param_dict)
    
    param_dict.update(weights_DataFrame)
        
    functions_dict = {'scrubbing_correction_dict' : scrubbing_correction_dict,
                      'image_registration_dict': image_registration_dict,
                      'SBKG_correction_dict': SBKG_correction_dict,
                      'TFC_correction_dict': TFC_correction_dict,
                      }
    
    for folder in proc_folder:  
        print('Experiment ' + folder + ' in process...')
        for function in sequence:
            
            if function.__name__ not in functions_dict.keys():
                
                proc_dict = pre_processing_step (proc_dict, pre_proc_seq = [function], param_dict = param_dict, **kwargs)
                
            else:
                proc_dict = processing_step (proc_dict, proc_seq = [function], param_dict = param_dict, **kwargs)
        
        if save:
            saving_step (proc_dict, dst_dir, img_name = img_name, **param_dict)
            end = time.time()
            print('Total time: %ds' %(end - start))
            return proc_dict
        else:
            end = time.time()
            print('Total time: %ds' %(end - start))
            return proc_dict


#add_to_dict(proc_parameters,['start_acq_numb','start_img_numb','threshold', 'HE_LE'],[10, 100, 0, (True, [15,30],[30,50])])

# src_dir = r"J:\900 Varia\2021\000_tony_data\03_Processed_step_by_step\00_Overlap_correction\exp1XX"
# dst_dir = r"J:\900 Varia\2021\000_tony_data\03_Processed_step_by_step\01_New_transmission_results"
# ref_folder = ['01_so_ref']
# proc_folder = ['02_exp102_00']
# ref_test_dict, ref_test_param = testing_mode_step (src_dir, proc_folder = ref_folder, keep_acq_numb = 1)
# pre_proc_seq = [outlier_removal, stack_averaging]
# add_to_dict(ref_test_param,['threshold'], [0])
# ref_test_dict = pre_processing_step (ref_test_dict, pre_proc_seq, param_dict = ref_test_param)

# proc_seq = [scrubbing_correction_dict, SBKG_correction_dict]
# BB_mask = get_img(src_dir + '/bb_mask_exp_full.fits')
# add_to_dict(ref_test_param,['BB_mask'], [BB_mask])
# ref_test_dict = processing_step (ref_test_dict, proc_seq, param_dict = ref_test_param)

# dst_dir_test = dst_dir + '/ref_avg'
# saving_step (ref_test_dict, dst_dir_test, img_name = 'ref_avg')

# #################################
# nca = [408, 399, 43, 10]
# exp_test_dict, exp_test_param = testing_mode_step (src_dir, proc_folder = proc_folder, keep_acq_numb= 1)
# pre_proc_seq = [outlier_removal, stack_averaging]
# add_to_dict(exp_test_param,['threshold'], [0])
# exp_test_dict = pre_processing_step (exp_test_dict, pre_proc_seq, param_dict = exp_test_param)

# proc_seq = [scrubbing_correction_dict]
# exp_test_dict = processing_step (exp_test_dict, proc_seq, param_dict = exp_test_param)

# # dst_dir_test = dst_dir + '/00_after_scrubbing'
# # saving_step (exp_test_dict, dst_dir_test, img_name = 'exp_after_scrubb')


# img = extract_img_dict(exp_test_dict, proc_folder[0], img_number = 50)
# reg_img = get_img(src_dir + '/reg_img_LE_full.fits')
# reg_rois_list = [([24, 350, 30, 135], 'v'), ([432, 350, 30, 135], 'v')]
# show_img_rois(img[0], dr = [(reg_rois_list, 'yellow')])

# img_reg_corr, M = img_registration (img, reg_img, reg_rois_list = reg_rois_list, dof=['ty'])
# show_img(img_reg_corr[0]/img[0], cmap = 'gray')
# print(M)

# BB_mask = get_img(src_dir + '/bb_mask_exp_full.fits')
# add_to_dict(exp_test_param,['M', 'dof', 'ref_dict', 'BB_mask'], [M, ['ty'], ref_test_dict, BB_mask])
# proc_seq = [image_registration_dict]
# exp_test_dict = processing_step (exp_test_dict, proc_seq, param_dict = exp_test_param)

# # dst_dir_test = dst_dir + '/01_after_img_reg'
# # saving_step (exp_test_dict, dst_dir_test, img_name = 'exp_after_img_reg')


# #add_to_dict(exp_test_param,['save_sbkg_dict'], [True])
# proc_seq = [SBKG_correction_dict]
# exp_test_dict  = processing_step (exp_test_dict, proc_seq, param_dict = exp_test_param)

# # dst_dir_test = dst_dir + '/02_after_sbkg'
# # saving_step (exp_test_dict, dst_dir_test, img_name = 'exp_after_sbkg')


# proc_seq = [ TFC_correction_dict]
# add_to_dict(exp_test_param,['nca', 'use_ref'], [nca, True])
# exp_test_dict = processing_step (exp_test_dict, proc_seq, param_dict = exp_test_param)

# # dst_dir_test = dst_dir + '/03_after_TFC'
# # saving_step (exp_test_dict, dst_dir_test, img_name = 'exp_after_TFC')


# dst_dir_test = dst_dir + '/sbkg_imgs'
# saving_step (sbkg_dict, dst_dir_test, img_name = 'sbkg_img')


















