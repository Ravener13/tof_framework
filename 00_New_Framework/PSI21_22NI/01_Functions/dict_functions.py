# -*- coding: utf-8 -*-
"""
Created on Fri Jun 17 20:12:20 2022

@author: carreon_r
"""

import numpy as np
from tqdm import tqdm
import datetime
import time
from copy import *

from img_functions import *
from proc_functions import *
from dict_functions import *


# =============================================================================
#                         prepare_stack_dict
# =============================================================================
def prep_stack_dict (base_dir):
    '''
    Creates a dictionary with the folder names as key argument and subfolders as values.
    The values are image addresses that serve as path to read them.

    Parameters
    ----------
    base_dir : str. 
        base directory for retrieving the paths.

    Returns
    -------
    stack_dict : dict
        Dictionary with first folders as key arguments and list of lists as values.

    '''
        # Import libraries
    import os,glob
    from astropy.io import fits
    
        # function to know how deep to search in the folders and subfolders
    depth, str_key = get_depth_path(base_dir)
    
        # take the folder names and sort them 
    folder_names = [item for item in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, item))]
    folder_names.sort()
    
        # initialize the dictionary
    stack_dict={}
        
        # if the depth is 2 the folder structure is direct and no modi
    if depth ==2:
        for name in folder_names:
            stack_dict['{}'.format(name)] = [glob.glob(d + '/*.fits') for d in glob.glob(os.path.join(base_dir,name) + str_key)]
            
    else:
        depth -=1
        
        if depth == 2:
            
            for name in folder_names:
                stack_dict['{}'.format(name)] = {}
                new_dir = base_dir + '/' + name
                depth, str_key = get_depth_path(new_dir)
                subfolder_names = [item for item in os.listdir(new_dir) if os.path.isdir(os.path.join(new_dir, item))]
                subfolder_names.sort()
                
                for subname in subfolder_names:
                    
                    stack_dict[name] ['{}'.format(subname)] = [glob.glob(d + '/*.fits') for d in glob.glob(os.path.join(new_dir,subname) + str_key)]
        else:
            return print ('Folder structure too big, please remove one level of depth in to proceed')

        # return a dictionary of image addresses
    return stack_dict




# =============================================================================
#                         get_imgs_dict
# =============================================================================
def get_imgs_dict(stack_dict, **kwargs):
    
    keys = [item for item in stack_dict.keys()]
    values = [item for item in stack_dict.values()]
    for idx, key,value in zip (tqdm(range(len(stack_dict)), desc = 'Reading Images'),keys, values):

        val_imgs = [[get_img(item) for item in sub_val] for sub_val in value]
        
        stack_dict [key] = val_imgs
        



# =============================================================================
#                         exec_filters_dict
# =============================================================================
def exec_filters_dict(stack_dict, sequence = '', count_time = False, **kwargs):
    '''
    Averages image stacks after the overlap correction
    A sequence is required, this sequence can contain any function for image enhancement (filtering, outlier removal, etc.).
    The function 'stack_avg' does the averaging, thus it is required to be in any position inide the sequence

    Parameters
    ----------
    stack_dict : dict
        dictionary with all the image addresses to average. This can be obtained from 'prep_stack_dict'
    seq : list of functions
        list of image enhancement functions for their processing in order.
    **kwargs : extra arguments. dict
        extra arguments carried on for future processings

    Returns
    -------
    None. Keeps the list with the averaged images to continue the processing steps

    '''
    
        # import libraries
    import time
    from tqdm import tqdm
        
        # starts a timer in acse you want to know the process total time
    start = time.time()
    
    new_dict = {}
    seq = sequence.copy()
    proc_dict = stack_dict.copy()
    
        #read the dictionary's keys and values
    for key,values in proc_dict.items():
        
        seq_values =[]
    
            # read the first subfolder and start a visual processing time
        for idx, imgs_acq in zip (tqdm(range(len(values)), desc = 'Processing Filetring '),values):
            
            seq_imgs = []
            
            for img in imgs_acq:
                
                seq_imgs.append(exec_proc(img, seq,  **kwargs))
            
            seq_values.append(seq_imgs)
            
        new_dict [key] = seq_values

        # finish the timer
    end = time.time()
    
        # in case that precise information about the time is required, an option to print the total required time is available
    if count_time:
        print('Total time: %ds' %(end - start))
    
    return new_dict




# =============================================================================
#                         exec_averaging_dict
# =============================================================================
def exec_averaging_dict(stack_dict, sequence = [stack_averaging], count_time = False, **kwargs):
    '''
    Averages image stacks after the overlap correction
    A sequence is required, this sequence can contain any function for image enhancement (filtering, outlier removal, etc.).
    The function 'stack_avg' does the averaging, thus it is required to be in any position inide the sequence

    Parameters
    ----------
    stack_dict : dict
        dictionary with all the image addresses to average. This can be obtained from 'prep_stack_dict'
    seq : list of functions
        list of image enhancement functions for their processing in order.
    **kwargs : extra arguments. dict
        extra arguments carried on for future processings

    Returns
    -------
    None. Keeps the list with the averaged images to continue the processing steps

    '''
        
        # starts a timer in acse you want to know the process total time
    start = time.time()
    
    new_dict = {}
    proc_dict = stack_dict.copy()
        #read the dictionary's keys and values
    for key,values in proc_dict.items():
        
        seq_values = stack_averaging(values, **kwargs)
            
        new_dict[key] = seq_values

        # finish the timer
    end = time.time()
    
        # in case that precise information about the time is required, an option to print the total required time is available
    if count_time:
        print('Total time: %ds' %(end - start))
    
    return new_dict



# =============================================================================
#                         exec_bin_frames_dict
# =============================================================================
def exec_bin_frames_dict(stack_dict, sequence = [binning_frames], count_time = False, frames_binning_factor = 1 , start_img = 0, **kwargs):
    '''
    Averages image stacks after the overlap correction
    A sequence is required, this sequence can contain any function for image enhancement (filtering, outlier removal, etc.).
    The function 'stack_avg' does the averaging, thus it is required to be in any position inide the sequence

    Parameters
    ----------
    stack_dict : dict
        dictionary with all the image addresses to average. This can be obtained from 'prep_stack_dict'
    seq : list of functions
        list of image enhancement functions for their processing in order.
    **kwargs : extra arguments. dict
        extra arguments carried on for future processings

    Returns
    -------
    None. Keeps the list with the averaged images to continue the processing steps

    '''
        
        # starts a timer in acse you want to know the process total time
    start = time.time()
    
    new_dict = {}
    proc_dict = stack_dict.copy()
        #read the dictionary's keys and values
    for key,values in proc_dict.items():
        
        seq_values = []
        
        for idx, imgs_acq in zip (tqdm(range(len(values)), desc = 'Processing Binning Frames'),values):
            
            seq_values.append(binning_frames (imgs_acq, start_img = start_img, frames_binning_factor = frames_binning_factor, **kwargs))
            
        new_dict[key] = seq_values

        # finish the timer
    end = time.time()
    
        # in case that precise information about the time is required, an option to print the total required time is available
    if count_time:
        print('Total time: %ds' %(end - start))
    
    return new_dict



# =============================================================================
#                         exec_bin_acquisitions_dict
# =============================================================================
def exec_bin_acquisitions_dict(stack_dict, sequence = [binning_acquisitions], count_time = False, acquisitions_binning_factor = 2 , **kwargs):
    '''
    Averages image stacks after the overlap correction
    A sequence is required, this sequence can contain any function for image enhancement (filtering, outlier removal, etc.).
    The function 'stack_avg' does the averaging, thus it is required to be in any position inide the sequence

    Parameters
    ----------
    stack_dict : dict
        dictionary with all the image addresses to average. This can be obtained from 'prep_stack_dict'
    seq : list of functions
        list of image enhancement functions for their processing in order.
    **kwargs : extra arguments. dict
        extra arguments carried on for future processings

    Returns
    -------
    None. Keeps the list with the averaged images to continue the processing steps

    '''
        
        # starts a timer in acse you want to know the process total time
    start = time.time()
    
    new_dict = {}
    proc_dict = stack_dict.copy()
        #read the dictionary's keys and values
    for key,values in proc_dict.items():
        
        #for idx, imgs_acq in zip (tqdm(range(len(values)), desc = 'Processing Binning Acquisitions'),values):
            
        seq_values = binning_acquisitions (values, acquisitions_binning_factor = acquisitions_binning_factor, **kwargs)
            
        new_dict[key] = seq_values

        # finish the timer
    end = time.time()
    
        # in case that precise information about the time is required, an option to print the total required time is available
    if count_time:
        print('Total time: %ds' %(end - start))
    
    return new_dict


# =============================================================================
#                        scrubbing_correction_dict
# =============================================================================
def scrubbing_correction_dict (stack_dict, weights_DataFrame, **kwargs):
    '''
    Does the scrubbing correction with the calculated OBs weighting for a given dictionary of target folders

    Parameters
    ----------
    stack_dict : dictionary
        {key:value}
    weights_DataFrame : pandas DataFrame 
        DataFrame containing experiment's OB weights 

    Returns
    -------
    new_dict : TYPE
        DESCRIPTION.

    '''
        # initialize the new dictionary
    new_dict = {}
    proc_dict = stack_dict.copy()
    for key, value in proc_dict.items():
        
        folder_values = []
            # search for the key folder within the DataFrame values
        if key in weights_DataFrame.Folder.values:
            
            new_dict [key] = {}
                # search and return the row that contain the key
            row_data = weights_DataFrame[weights_DataFrame['Folder'].str.contains(key)]
            
                # extract the values for each column, they contain the information required
            weight_01 = row_data['w1'].values[0]
            weight_02 = row_data['w2'].values[0]
            
            ob_01 =[]
            for folder in stack_dict[row_data['OB1'].values[0]]:
                for arr in folder:
                    ob_01.append(arr[0])
            ob_01_img = np.nanmean(ob_01, axis=0)

            ob_02 =[]
            for folder in stack_dict[row_data['OB2'].values[0]]:
                for arr in folder:
                    ob_02.append(arr[0])
            ob_02_img = np.nanmean(ob_02, axis=0)
            
                # with the extracted values, operate to obrain the scrubbing correction
            #for imgs_acq in value:
            for idx, imgs_acq in zip (tqdm(range(len(value)), desc = 'Processing Scrubbing Correction'),value):
                scrubb_values = []
                
                for img in imgs_acq:
                    
                    scrubb_values.append(scrubbing_corr (img, ob_01_img, ob_02_img, weight_01,weight_02, **kwargs))
                folder_values.append(scrubb_values)
            new_dict [key] = folder_values

        # gives the new (corrected) dictionary
    return new_dict




# =============================================================================
#                       image_registration_dict
# =============================================================================

def image_registration_dict (stack_dict, reg_img = (np.zeros([512,512]), np.ones([1,1])), reg_rois_list ='', dof=['tx','ty','sx','sy'] , M = '',  **kwargs):
    
    new_dict = {}
    proc_dict = stack_dict.copy()
    
    for key, value in proc_dict.items():
        folder_values = []
        
        #for imgs_acq in value:
        for idx, imgs_acq in zip (tqdm(range(len(value)), desc = 'Processing Image Registration'),value):
            reg_values = []
            
            for img in imgs_acq:
                
                corr_img,_ = img_registration (img, reg_img, reg_rois_list = reg_rois_list, dof = dof, M = M, **kwargs)
                reg_values.append(corr_img)
                
            folder_values. append(reg_values)
            
        new_dict [key] = folder_values
        
    return new_dict



# =============================================================================
#                    SBKG_correction_dict
# =============================================================================

def SBKG_correction_dict (stack_dict, BB_mask, save_sbkg_dict = False, **Kwargs):
    
        # import libraries
    from tqdm import tqdm
    
    new_dict = {}
    sbkg_dict = {}
    proc_dict = stack_dict.copy()
    
        # loops through the dictionary keys and values
    for key,value in proc_dict.items():
            # this takes care if the BB mask for the ref image is different as for the stacks
        folder_values = []
        folder_sbkg = []
        
        #for imgs_acq in values:
        for idx, imgs_acq in zip (tqdm(range(len(value)), desc = 'Processing SBKG Correction'),value):
            img_values = []
            sbkg_values = []
            
            for img in imgs_acq:
                SBKG_img = SBKG_Wmask (img, BB_mask)
                img_values.append(subtract_SBKG(img, SBKG_img))
                sbkg_values.append(SBKG_img)
        
            folder_values.append(img_values)
            folder_sbkg.append(sbkg_values)
        
        new_dict [key] = folder_values
        sbkg_dict [key] = folder_sbkg
        
    if save_sbkg_dict:
        return new_dict, sbkg_dict
    else:
        return new_dict



# =============================================================================
#                     intensity_correction_dict
# =============================================================================


def intensity_correction_dict (stack_dict, ref_dict = '', ref_img_int = '', nca = [0,0,0,0], **Kwargs):

    new_dict = {}
    proc_dict = copy(stack_dict)
    
        #this will unpack the reference dictionary to get the images. it should be one average aquisition for all the references.
        
    if ref_dict != '' and ref_img_int == '':
        
        for key in ref_dict.keys():
                
                # Ref_dict is composed usually from 1 averaged acquisition (there can be exceptions) 
            ref_img_corr = avg_frames_dict (ref_dict[key], output_type = 'img')
            
    elif ref_dict == '' and ref_img_int != '':
        ref_img_corr = ref_img_int
        
    elif ref_dict != '' and ref_img_int != '':
        print('A dictionary and a reference image was given, taking the ref_img_int to perform the intensity correction')
        ref_img_corr = ref_img_int
        
    else:
        return print('ref_img_int for intensity correction missing')
        
    for key, value in proc_dict.items():
        
        folder_values = []
        list_imgs_int = avg_frames_dict (proc_dict[key], output_type = 'frames')
        
        for idx, imgs_acq, int_img in zip (tqdm(range(len(value)), desc = 'Processing intensity Correction'), value, list_imgs_int):
            
            intensity_corr_vals = []
            if sum(nca) == 0:
                int_corr = 1.0
            else:
                int_corr = np.average(crop_img(ref_img_corr, nca)[0]) / np.average(crop_img(int_img, nca)[0])
            
            for img in imgs_acq:
                corr_img = intensity_corr(img, int_corr)
                intensity_corr_vals.append(corr_img)
                
            folder_values. append(intensity_corr_vals)
            
        new_dict [key] = folder_values
        
    return new_dict



# =============================================================================
#                     referencing_dict
# =============================================================================

def referencing_dict (stack_dict, ref_dict, **Kwargs):

    new_dict = {}
    proc_dict = copy(stack_dict)
    
        # usually the ref_dic is a single averaged acquisition, for this reason we have the double "[0]"
    ref_values = list(ref_dict.values())[0][0]
    
    for key, value in proc_dict.items():
        
        folder_values = []
        
        for idx, imgs_acq in zip (tqdm(range(len(value)), desc = 'Processing Referencing Correction'), value):
            
            referencing_vals = []
            
            for img, ref in zip(imgs_acq, ref_values):
                corr_img = referencing_corr(img, ref)
                referencing_vals.append(corr_img)
                
            folder_values. append(referencing_vals)
            
        new_dict [key] = folder_values
        
    return new_dict


# =============================================================================
#                        save_dict
# =============================================================================

def save_dict (stack_dict, dst_dir, folder_name = '', img_name = 'transmission', start_img_numb = 0, start_acq_numb = 0, overwrite = False, **kwargs):

        # takes every key and its values in the dictionary
    for key, value in stack_dict.items():
        
        acq_idx = start_acq_numb
            # takes each value in the subfolder (values)
        for acq_numb, imgs_acq in zip (tqdm(range(len(value)), desc = 'Writing Images'),value):
            
            acq_folder = 'Acquisition_' + format(acq_idx, '02d')
            idx = start_img_numb
            
            for img in imgs_acq:
                
                img_final = img[0]
                hdr_final = update_header (img[1], update_type = 'HISTORY', update_list = ['Image saved : ' + str(datetime.datetime.now())])
                
                    # creates the saving path 
                if folder_name =='':
                    folder_dir = key
                    
                file_name = os.path.join(dst_dir, folder_dir, acq_folder, key + '_' + img_name + '_' + format(idx, '05d') + '.fits')
                
                save_img = (img_final, hdr_final)
                    # utilize pyerre's function to save each image in the folder
                write_img(save_img, file_name, base_dir='', overwrite = overwrite)
                
                idx+=1
            acq_idx+=1
    return



# =============================================================================
#                        save_continuous_dict
# =============================================================================

def save_continuous_dict (stack_dict, dst_dir, folder_name = '',  img_name = 'transmission', start_img_numb = 0, start_acq_numb = 0, overwrite = False, **kwargs):

        # takes every key and its values in the dictionary
    for key, value in stack_dict.items():
        acq_idx = start_acq_numb
            # takes each value in the subfolder (values)
        for acq_numb, imgs_acq in zip (tqdm(range(len(value)), desc = 'Writing Images'),value):
            
            acq_folder = 'Acquisition_' + format(acq_idx, '02d')
            idx = start_img_numb
            
            for img in imgs_acq:
                
                img_final = img[0]
                hdr_final = update_header (img[1], update_type = 'HISTORY', update_list = ['Process Finished and Saved : ' + str(datetime.datetime.now())])
                
                    # creates the saving path 
                if folder_name =='':
                    folder_dir = key
                file_name = os.path.join(dst_dir, folder_dir, acq_folder, key + '_' + img_name + '_' + format(idx, '05d') + '.fits')
                
                save_img = (img_final, hdr_final)
                    # utilize pyerre's function to save each image in the folder
                write_img(save_img, file_name, base_dir='', overwrite = overwrite)
                
                idx+=1
            acq_idx+=1
    return


# =============================================================================
#                        save_energies_dict
# =============================================================================

def save_energies_dict (stack_dict, dst_dir, folder_name = '', img_name = 'transmission', start_img_numb = 0, overwrite = False, HE_LE = (False, [15,30],[30,50]), **kwargs):
    
    
        # takes every key and its values in the dictionary
    for key, value in stack_dict.items():
        
        idx = start_img_numb
        list_imgs_HE = []
        list_imgs_LE = []
        
            # takes each value in the subfolder (values)
        for imgs_acq in value:
            
            if len(imgs_acq) > 2: #usually we will have only 2 images  HE and LE
            
                list_imgs = [img[0] for img in imgs_acq]
                list_hdrs = [hdr[1] for hdr in imgs_acq]
                
                HE_avg = np.nanmean(list_imgs[HE_LE[1][0]:HE_LE[1][1]], axis = 0)
                LE_avg = np.nanmean(list_imgs[HE_LE[2][0]:HE_LE[2][1]], axis = 0)
                
                HE_hdr = list_hdrs[int((HE_LE[1][0]+HE_LE[1][1])/2)]
                LE_hdr = list_hdrs[int((HE_LE[2][0]+HE_LE[2][1])/2)]
                
                HE_img = (HE_avg, HE_hdr)
                LE_img = (LE_avg, LE_hdr)
                
            else:
                
                HE_img = imgs_acq[0]
                LE_img = imgs_acq[1]
            
            # hdr_final_HE = update_header (HE_img[1], update_type = 'HISTORY', update_list = ['Image saved : ' + str(datetime.datetime.now())])
            # hdr_final_LE = update_header (LE_img[1], update_type = 'HISTORY', update_list = ['Image saved : ' + str(datetime.datetime.now())])
            
            list_imgs_HE.append(HE_img)
            list_imgs_LE.append(LE_img)
    
        for n, img_HE, img_LE in zip(tqdm(range(len(value)), desc = 'Writing HE and LE Images'), list_imgs_HE, list_imgs_LE):
            
                # creates the saving path 
            if folder_name =='':
                folder_dir = key
                
            file_name_HE = os.path.join(dst_dir, folder_dir, 'HE_stack', key + '_' + img_name + '_' + format(idx, '05d') + '.fits')
            file_name_LE = os.path.join(dst_dir, folder_dir, 'LE_stack', key + '_' + img_name + '_' + format(idx, '05d') + '.fits')
            
            hdr_final_HE = update_header (img_HE[1], update_type = 'HISTORY', update_list = ['Image saved : ' + str(datetime.datetime.now())])
            hdr_final_LE = update_header (img_LE[1], update_type = 'HISTORY', update_list = ['Image saved : ' + str(datetime.datetime.now())])
            
                # utilize pyerre's function to save each image in the folder
            write_img(img_HE, file_name_HE, base_dir='', overwrite = overwrite)
            write_img(img_LE, file_name_LE, base_dir='', overwrite = overwrite)
            
            idx+=1
    return



# =============================================================================
#                        slice_values_dict
# =============================================================================

def slice_values_dict (stack_dict, start_slice = 0, end_slice = '', **kwargs):
    
    new_dict = {}
    proc_dict = stack_dict.copy()
    
    for key, value in proc_dict.items():
        
        slice_set = []
        list_imgs = [[item[0] for item in sub_val] for sub_val in value]
        list_hdrs = [[item[1] for item in sub_val] for sub_val in value]
        
        for idx, imgs_acq, hdrs_acq in zip (tqdm(range(len(value)), desc = 'Slicing dictionary'), list_imgs, list_hdrs):
            
            slice_acq = slice_acq_set (imgs_acq, start_slice = start_slice, end_slice = end_slice)
            slice_hdr = slice_acq_set (hdrs_acq, start_slice = start_slice, end_slice = end_slice)
            
            for img, hdr in zip(slice_acq, slice_hdr):
                
                hdr_final = update_header (hdr, update_type = 'HISTORY', update_list = ['Slice range : ' + str(start_slice) + ' - ' + str(end_slice)])
                slice_set.append((img, hdr_final))
                
        new_dict [key] = [slice_set]
        
    return new_dict




# =============================================================================
#                        avg_acquisition_dict
# =============================================================================

def avg_acquisition_dict (dict_values, output_type = 'acq', start_slice = 0, end_slice = '',  **kwargs):
    
    avg_list = []
    
    if end_slice == '':
        end_slice = len(dict_values[0])
    
    list_imgs = [[np.nan_to_num(item[0])for item in sub_val[start_slice:end_slice]] for sub_val in dict_values]
    list_hdrs = [[item[1] for item in sub_val[start_slice:end_slice]] for sub_val in dict_values]
    
    mean_imgs = list(np.nanmean(list_imgs, axis=0))
    middle_hdr = list_hdrs[int(len(list_hdrs)/2)]
    
    if output_type == 'acq':
        for img, hdr in zip (mean_imgs, middle_hdr):
            avg_list.append((img, hdr))
        
        return avg_list
        
    elif output_type == 'img':
        img_avg = np.nanmean(mean_imgs, axis = 0)
        hdr_avg = middle_hdr[int(len(middle_hdr)/2)] 
        
        return (img_avg, hdr_avg)
    
    else:
        return print('Error: output_type must be either <acq> or <img>')
        


# =============================================================================
#                        avg_frames_dict
# =============================================================================

def avg_frames_dict (dict_values, output_type = 'frames', start_slice = 0, end_slice = '',  **kwargs):
    
    avg_list = []
    
    if end_slice == '':
        end_slice = len(dict_values[0])
    
    list_imgs = [[np.nan_to_num(item[0])for item in sub_val[start_slice:end_slice]] for sub_val in dict_values]
    list_hdrs = [[item[1] for item in sub_val[start_slice:end_slice]] for sub_val in dict_values]
    
    mean_imgs = list(np.nanmean(list_imgs, axis=1))
    middle_hdr = [list_hdrs[idx_hdr][int(len(list_hdrs[idx_hdr])/2)] for idx_hdr in range (len(list_hdrs))]
    
    if output_type == 'frames':
        for img, hdr in zip (mean_imgs, middle_hdr):
            avg_list.append((img, hdr))
        
        return avg_list
        
    elif output_type == 'img':
        img_avg = np.nanmean(mean_imgs, axis = 0)
        hdr_avg = middle_hdr[int(len(middle_hdr)/2)] 
        
        return (img_avg, hdr_avg)
    
    else:
        return print('Error: output_type must be either <frames> or <img>')


# =============================================================================
#                        bin_acquisitions_dict
# =============================================================================

def bin_acquisitions_dict (stack_dict, bin_size = 2, **kwargs):

    new_dict = {}
    proc_dict = stack_dict.copy()
    
    for key, value in proc_dict.items():
        
        folder_values = []
        bin_buffer_imgs = []
        bin_buffer_hdr = []
        list_imgs = [[item[0] for item in sub_val] for sub_val in value]
        list_hdrs = [[item[1] for item in sub_val] for sub_val in value]
        for idx, imgs_acq, hdrs_acq in zip (tqdm(range(len(value)), desc = 'Binning dictionary'),list_imgs, list_hdrs):
            
            bin_buffer_imgs.append(imgs_acq)
            bin_buffer_hdr.append(hdrs_acq)
            
            
            if len(bin_buffer_imgs) == bin_size:
                img_bin = list((np.nanmean(bin_buffer_imgs, axis=0)))
                hdr_bin = bin_buffer_hdr[int(len(bin_buffer_hdr)/2)]
                folder_values.append([(img,hdr) for img, hdr in zip(img_bin, hdr_bin)])
                bin_buffer_imgs = []
                bin_buffer_hdr = []
            
        new_dict [key] = folder_values
        
    return new_dict



# =============================================================================
#                        add_parameter_to_dict
# =============================================================================


# def add_to_dict (parameters_dict, parameters = []): 
    
#     def updt_globals():
#         global parameters
#     def get_var_name(variable):
#          for name, value in globals().items():
#             if value is variable:
#                 return name
#     for param in parameters:

#         var_name = get_var_name(param)
#         print(var_name)
#         parameters_dict.update({var_name : param})
#     #new_param = dict((retrieve_name(name), eval(name)) for name in parameters)
#     #parameters_dict.update(new_param)


def add_to_dict(d, keys, values):
    d.update(zip(keys, values))
    
    
# =============================================================================
#                        extract_img_dict
# =============================================================================

def extract_img_dict (stack_dict, key, acq_number = 0, img_number =0, **kwargs):
    img = copy(stack_dict[key][acq_number][img_number])
    return img



# =============================================================================
#                        read_saved_dict
# =============================================================================

def read_saved_dict (src_dir, proc_folder = [], **kwargs):
    
    param_dict = {}
    
    stack_dict = prep_stack_dict (src_dir)
    
    if proc_folder == []:
        proc_folder = [*stack_dict]
        
    keep_folder = proc_folder 
    keep_key (stack_dict, keep_folder)
    
    get_imgs_dict(stack_dict)
    
    return stack_dict



# =============================================================================
#                         ob_roi_mod_dict
# =============================================================================
def ob_roi_mod_dict(stack_dict, **kwargs):

    new_dict = {}
    proc_dict = stack_dict.copy()
    
    for key, value in proc_dict.items():
        
        if '_ob' in key:
            
            folder_vals=[]
            
            for idx, imgs_acq in zip (tqdm(range(len(value)), desc = 'Processing ob mod correction'), value):
            
                referencing_vals = []
            
                for img in imgs_acq:
                    corr_img = mod_for_ob (img, roi_original=[0,0,50,512], roi_mod=[462,0,50,512])
                    referencing_vals.append(corr_img)
                    
                folder_vals. append(referencing_vals)
        
            new_dict [key] = folder_vals
        
        else:
            new_dict [key] = value
            
    return new_dict