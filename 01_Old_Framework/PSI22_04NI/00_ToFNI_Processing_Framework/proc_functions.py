# -*- coding: utf-8 -*-
"""
Created on Wed Jun  8 16:29:16 2022

@author: carreon_r
"""

import os, glob, time
import numpy as np
from tqdm import tqdm
from astropy.io import fits
import matplotlib.pyplot as plt
import datetime

from img_proc_functions import *
#from img_utils_mod import *



# =============================================================================
#                         select_directory
# =============================================================================
def select_directory(var_name, base_dir=''):
    '''
    This function is meant to be used together with the '%load' magic in jupyter
    notebook to provide an interactive interface for directory selection.

    Parameters
    ----------
    var_name : str
        String with the name of the variable which will contain the resulting path in the notebook
    base_dir : str, optional
        directory relative to which the directory path is specified (absolute path is used if omitted)

    Returns
    -------
    str
        statement to be inserted in the jupyter code cell to assign the selected path to this variable

    '''
        # import necessary packages
    import os
    import tkinter
    from tkinter import filedialog
    
        # Create Tk root
    root = tkinter.Tk()
    
        # Hide the main window
    root.withdraw()
    root.call('wm', 'attributes', '.', '-topmost', True)
    
        # If a base path is not specified, select and return the absolute path
    if base_dir == '':
        dir = filedialog.askdirectory()
        
        # If a base path is specified, use it as starting directory and return
        # the selected directory relative to this base path
    else: 
        dir = os.path.relpath(filedialog.askdirectory(initialdir=base_dir), start=base_dir)
    
        # generate a statement to be inserted in the jupyter notebook
    return var_name + ' = r\"' + os.path.normpath(dir) + '\"'



# =============================================================================
#                         sequence_separator
# =============================================================================


def sequence_separator(sequence, check):

    from itertools import islice, zip_longest
    
    subgroup = []
    
    for i, j in zip_longest(sequence, islice(sequence, 1, None)):
        
        if check(i, j):
            
            yield subgroup
            subgroup = []
            subgroup.append(i)
            yield subgroup
            subgroup = []
            
            
        else:
            subgroup.append(i)
    yield subgroup
    
    
    


# =============================================================================
#                         get_depth_path
# =============================================================================
def get_depth_path(path, depth=0):
    '''
    Gives the depth of the given folder (number of subdirectories).
    This function is used in 'prep_stack_dict' to construct automatically the dictionary with the given directory

    Parameters
    ----------
    path : str
        base directory
    depth : int
        counter for the directory depth.

    Returns
    -------
    depth: int
        integer depth value for the base folder 
    sub_dirs: str
        key for searching in all the folders and subfolders used in 'prep_stack_dict'

    '''
    
        # Search in the directory 
    for root, dirs, files in os.walk(path):
        
            # if the next folder is a subfolder,add to the sum
        if dirs:
            depth+=1
            
                # check for next subfolders until there are no more
            return max(get_depth_path(os.path.join(root, d), depth) for d in dirs)
        # initialize variable
    sub_dirs = []
    
        # depending on the depth calculated before, construct the automatic searching parameter
    for i in range(depth):
        
            # if there is no more subdirectories, append the final contruct
        if i == 0 :
            sub_dirs.append('/')
            
            # for each level or subdirectory, append the search key for all of them
        else:
            sub_dirs.append('*/')
    
        # returns an integer value for the depth and the a string key to be inserted in prep_stack_dict
    return  depth, "".join(sub_dirs)




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
#                             keep_key
# =============================================================================
def keep_key (dictionary, list_keep = '' ):
    '''
    Given a list of strings (key names), keeps the key and its values in a dictionary

    Parameters
    ----------
    dictionary : TYPE
         target dictionary to keep the parameters
    list_keep : list of str
        list of keys strings that will remain in the dictionary

    Returns
    -------
    None.

    '''
        # search the names of a given list of keys, then it keep them and remove the others
    for key in dictionary.copy():
        
            # keep the key
        if key not in list_keep:
            dictionary.pop(key, None)
    return 


# =============================================================================
#                            remove_key
# =============================================================================
def remove_key (dictionary, list_remove = '' ):
    '''
    Given a list of strings (key names), removes the key and its values in a dictionary

    Parameters
    ----------
    dictionary : dict
        target dictionary to remove the parameters
    list_remove : list of str
        list of keys strings that will be removed from the dictionary

    Returns
    -------
    None.

    '''
        # search the names of a given list of keys, then it removes them and keep the others
    for key in dictionary.copy():
        
            # remove the key
        if key in list_remove:
            dictionary.pop(key, None)
    return


# =============================================================================
#                            exec_proc
# =============================================================================
def exec_proc(src_img, seq, start_before=0, start_after=0, stop_before=0, stop_after=0, seq_name = 'Sequence', **kwargs):
    '''
    This function applies a defined sequence of image processing steps to an image.
    Each processing step should be a function accepting an image (2D array) as
        the first parameter, plus an undefined count of named parameters, and returning
        the processed image.
    The processing steps are applied in the order defined in the 'seq' array. It is
        possible to apply only a subset of the sequence by using the parameters 'start_before',
        'start_after', 'stop_before' and 'stop_after'.
        
    This function is normally not called directly from the notebook, but is used
        as a sub-function of other processing steps


    Parameters
    ----------
    src_img : 2D array
        2D array containing the source image
    seq : list
        array with a list of processing functions to be applied
    start_before : int
        indicates that the starting point of the processing sequence is just before this function (this parameter
        has priority over 'start_after')
    start_after : int
        indicates that the starting point of the processing sequence is just after this function
    stop_before :int
        indicates that the ending point of the processing sequence is just before this function (this parameter
        has priority over 'stop_after')
    stop_after : int
        indicates that the ending point of the processing sequence is just after this function
    **kwargs : dict
        collection of additional named parameters

    Returns
    -------
    img : 2D array
        returns the modified image according to the arrange of the given sequence

    '''
    
    from copy import deepcopy
    
        # if 'start_before' or 'start_after' is defined, identify at which step to start,
        # otherwise start at the first step of the sequence
    if start_before != 0:
        first_step = seq.index(start_before)
    elif start_after != 0:
        first_step = seq.index(start_after) + 1
    else:
        first_step = 0
        
        # if 'stop_before' or 'stop_after' is defined, identify at which step to stop,
        # otherwise stop at the last step of the sequence
    if stop_before != 0:
        last_step = seq.index(stop_before)
    elif stop_after != 0:
        last_step = seq.index(stop_after) + 1
    else:
        last_step = len(seq)
        
        # extract the selected subset of the processing sequence
    proc_seq = seq[first_step:last_step]
    
        # create an copy of the source image
    # img = src_img[0].copy()
    # header = src_img[1]
    img = deepcopy(src_img)
        # apply succesively all processing steps to the image
    for step in proc_seq:
        img = step(img, **kwargs)
        # return the processed image
    
    # seq_list = str([func.__name__ for func in proc_seq])
    # update_header (header, update_type = 'HISTORY', update_list = [seq_name + ': ' + seq_list, 'Date Processed (seq): ' + str(datetime.datetime.now())])
                   
    return img




# =============================================================================
#                         exec_proc_dict
# =============================================================================
def exec_proc_dict(stack_dict, sequence = '', count_time = False, **kwargs):
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
        for idx, imgs_tof in zip (tqdm(range(len(values)), desc = 'Processing '),values):
            
            seq_imgs = []
            
            for img in imgs_tof:
                
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
#                         exec_avg_dict
# =============================================================================
def exec_avg_dict(stack_dict, sequence = [stack_avg], count_time = False, **kwargs):
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
        
        seq_values = stack_avg(values, **kwargs)
            
        new_dict[key] = seq_values

        # finish the timer
    end = time.time()
    
        # in case that precise information about the time is required, an option to print the total required time is available
    if count_time:
        print('Total time: %ds' %(end - start))
    
    return new_dict





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
#                         weighting_func
# =============================================================================


def find_nearest_lower_value(key, sorted_li):
    if key <= sorted(sorted_li)[0]:
        value = sorted(sorted_li)[0]
    else:
        value = max(i for i in sorted_li if i <= key)
    return value

def find_nearest_upper_value(key, sorted_li):
    if key >= sorted(sorted_li)[-1]:
        value = sorted(sorted_li)[-1]
    else:
        value = min(i for i in sorted_li if i >= key)
    return value



def weighting_func (src_dir, **kwargs):
    '''
    This function manages the timestamps.txt file created in the overlap correction step.

    Parameters
    ----------
    scr_dir : str
        Takes the same source directory from the process. it is where the timestamps.txt is

    Returns
    -------
    Weights : DataFrame
        DataFrame with the weightings for each folder

    '''
        # import libraries
    import pandas as pd
    import warnings
    
        # disable warnings because of possible bad characters in the header
    warnings.filterwarnings("ignore")
        
        # Reads the timestamps.txt file created in the overlap correction step and order the indexes according to the timestamps
    Timestamps = pd.read_csv(src_dir + '/timestamps.txt')
    Timestamps = Timestamps.sort_values(by=['Modification (s)'], ascending=True)
    Timestamps = Timestamps.reset_index(drop=True)
    
        # copies the DataFrame and mask it to contain just the OBs
    OB_df = Timestamps[Timestamps['Folder'].str.contains('ob',case=False)]
    
        # copies the DataFrame and mask it to contain everything BUT the OBs
    Weights = Timestamps[~Timestamps['Folder'].str.contains('ob', case=False)]
    
        # takes the TRUE indices for both OBs and no OBs
    idx_ob = OB_df['Folder'].index
    idx_w = Weights['Folder'].index
    
        #convert the OB data frame into a list for easier search
    OB_list = OB_df['Modification (s)'].to_list()
    
    for i in range (len(idx_w)):
        
            # find the lower and upper OBs from an experiment
        lower_OB = find_nearest_lower_value(Weights['Modification (s)'][idx_w[i]], OB_list)
        upper_OB = find_nearest_upper_value(Weights['Modification (s)'][idx_w[i]], OB_list)
        
            # if the value for OB found is the same as the one in the experiment, then there is no OB and sets the OB registration to 1
        if lower_OB == upper_OB:
            
            Weights.loc[idx_w[i],'w1'] = 1
            Weights.loc[idx_w[i],'w2'] = 0

            Weights.loc[idx_w[i],'OB1'] = OB_df['Folder'][idx_ob[-1]]
            Weights.loc[idx_w[i],'OB2'] = OB_df['Folder'][idx_ob[-1]]
            
                # if there is OBs before and after, then takes the timestamps to create the anti-scrubbing weights
        else:
            
            Weights.loc[idx_w[i],'w1'] = (upper_OB - Weights['Modification (s)'][idx_w[i]]) / (upper_OB - lower_OB)
            Weights.loc[idx_w[i],'w2'] = (Weights['Modification (s)'][idx_w[i]] - lower_OB) / (upper_OB - lower_OB)
            
            Weights.loc[idx_w[i],'OB1'] = Timestamps['Folder'][OB_df.index[OB_df['Modification (s)'] == lower_OB].values[0]]
            Weights.loc[idx_w[i],'OB2'] = Timestamps['Folder'][OB_df.index[OB_df['Modification (s)'] == upper_OB].values[0]]
        
        # remove unnecessary columns in the target DataFrame
    Weights.drop(Weights.iloc[:, 1:5], inplace=True, axis=1)
    
    return Weights




# =============================================================================
#                         get_idx_DF
# =============================================================================
def get_idx_DF (DataFrame, value):
    '''
    Search a specific value in a DataFrame and returns the true indices where the values is found

    Parameters
    ----------
    DataFrame : pandas DataFrame
        base DataFrame 
    value : str, int, float
        target value

    Returns
    -------
    list_pos : TYPE
        DESCRIPTION.

    '''
    list_pos = list()
    
        # Get bool dataframe with True at positions where the given value exists
    result = DataFrame.isin([value])
    
        # Get list of columns that contains the value
    series_obj = result.any()
    col_names = list(series_obj[series_obj == True].index)
    
        # Iterate over list of columns and fetch the rows indexes where value exists
    for col in col_names:
        rows = list(result[col][result[col] == True].index)
        for row in rows:
            list_pos.append((row, col))
            
        # Return a list of tuples indicating the positions of value in the DataFrame
    return list_pos




# =============================================================================
#                        keep_key_weights
# =============================================================================
def keep_key_weights (dictionary, weights_DataFrame, keep_folder = []):
    '''
    keep_folder is a list of string values that correspond to the folders where the samples are.
    given the keep_folder list, there are specific OBs needed for the scrubbing correction of each experiment.
    This function mantains the target experiment and keep at the same time the OBs required for future processes

    Parameters
    ----------
    dictionary : dictionary
        {key:value}
    weights_DataFrame : pandas DataFrame 
        DataFrame containing experiment's OB weights 
    keep_folder : list of strings
        target keys/folders to keep in the process. The default is [].

    Returns
    -------
    the dictionary with just the target (wanted) folders/ keys

    '''
        # to add non-existent value in a list is easier to do it with a set
    ob_list = set([])
    
        # if specific folders were given, work with those
    if keep_folder!= []:
        
            # for each folder in the list
        for folder in keep_folder:

                # get the index of the folder name
            index = get_idx_DF (weights_DataFrame, folder)

                # with the index, extract the OB's names and add them into the set
            ob_list.add(weights_DataFrame.loc[index[0][0]][3])
            ob_list.add(weights_DataFrame.loc[index[0][0]][4])
    
            # transform the set into a list
        ob_list = list(ob_list)
    
            # keeps the values 
        keep_key (dictionary, keep_folder+ob_list)
    return



# =============================================================================
#                        scrubbing_corr_dict
# =============================================================================
def scrubbing_corr_dict (stack_dict, weights_DataFrame, **kwargs):
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
            #for imgs_tof in value:
            for idx, imgs_tof in zip (tqdm(range(len(value)), desc = 'Processing Scrubbing Correction'),value):
                scrubb_values = []
                
                for img in imgs_tof:
                    
                    scrubb_values.append(scrubbing_corr (img, ob_01_img, ob_02_img, weight_01,weight_02, **kwargs))
                folder_values.append(scrubb_values)
            new_dict [key] = folder_values

        # gives the new (corrected) dictionary
    return new_dict




# =============================================================================
#                       img_registration_dict
# =============================================================================

def img_registration_dict (stack_dict, ref = (np.zeros([512,512]), np.ones([1,1])), rois_list ='', dof=['tx','ty','sx','sy'] , M = '',  **kwargs):
    
    new_dict = {}
    proc_dict = stack_dict.copy()
    
    for key, value in proc_dict.items():
        folder_values = []
        
        #for imgs_tof in value:
        for idx, imgs_tof in zip (tqdm(range(len(value)), desc = 'Processing Image Registration'),value):
            reg_values = []
            
            for img in imgs_tof:
                
                corr_img = img_registration (img, ref, rois_list = rois_list, dof = dof, M = M, **kwargs)
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
        
        #for imgs_tof in values:
        for idx, imgs_tof in zip (tqdm(range(len(value)), desc = 'Processing SBKG Correction'),value):
            img_values = []
            sbkg_values = []
            
            for img in imgs_tof:
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
#                    TFC_correction_dict
# =============================================================================

def TFC_correction_dict (stack_dict, ref_tof_values, nca = [0,0,0,0], **Kwargs):

    new_dict = {}
    proc_dict = stack_dict.copy()
    for key, value in proc_dict.items():
        folder_values = []
        
        #for imgs_tof in value:
        for idx, imgs_tof in zip (tqdm(range(len(value)), desc = 'Processing TFC Correction'),value):
            TFC_values = []
            
            for img, ref in zip(imgs_tof, ref_tof_imgs):
                
                corr_img = TFC_corr(img, ref, nca=nca, **kwargs)
                TFC_values.append(corr_img)
                
            folder_values. append(TFC_values)
            
        new_dict [key] = folder_values
        
    return new_dict




# =============================================================================
#                        save_dict
# =============================================================================

def save_dict (stack_dict, dst_dir, img_type = 'transmission', start_img_numb = 0, start_pulse_numb = 0, overwrite = False, **kwargs):

        # takes every key and its values in the dictionary
    for key, value in stack_dict.items():
        pulse_idx = start_pulse_numb
            # takes each value in the subfolder (values)
        for pulse_numb, imgs_tof in zip (tqdm(range(len(value)), desc = 'Saving Images'),value):
            
            tof_pulse = 'Pulse_' + format(pulse_idx, '02d')
            idx = start_img_numb
            
            for img in imgs_tof:
                
                img_final = img[0]
                hdr_final = update_header (img[1], update_type = 'HISTORY', update_list = ['Process Finished and Saved : ' + str(datetime.datetime.now())])
                
                    # creates the saving path 
                file_name = os.path.join(dst_dir, key, tof_pulse, key + '_' + img_type + '_' + format(idx, '05d') + '.fits')
                
                save_img = (img_final, hdr_final)
                    # utilize pyerre's function to save each image in the folder
                write_img(save_img, file_name, base_dir='', overwrite = overwrite)
                
                idx+=1
            pulse_idx+=1
    return



# =============================================================================
#                        save_cont_dict
# =============================================================================

def save_cont_dict (stack_dict, dst_dir, img_type = 'transmission', start_img_numb = 0, start_pulse_numb = 0, overwrite = False, **kwargs):

        # takes every key and its values in the dictionary
    for key, value in stack_dict.items():
        
            # takes each value in the subfolder (values)
        for pulse_numb, imgs_tof in zip (tqdm(range(len(value)), desc = 'Saving Images'),value):
            
            tof_pulse = 'Pulse_' + format(start_pulse_numb, '02d')
            idx = start_img_numb
            
            for img in imgs_tof:
                
                img_final = img[0]
                hdr_final = update_header (img[1], update_type = 'HISTORY', update_list = ['Process Finished and Saved : ' + str(datetime.datetime.now())])
                
                    # creates the saving path 
                file_name = os.path.join(dst_dir, key, tof_pulse, key + '_' + img_type + '_' + format(idx, '05d') + '.fits')
                
                save_img = (img_final, hdr_final)
                    # utilize pyerre's function to save each image in the folder
                write_img(save_img, file_name, base_dir='', overwrite = overwrite)
                
                idx+=1
            start_pulse_numb+=1
    return



# =============================================================================
#                        slice_vals_dict
# =============================================================================

def slice_vals_dict (stack_dict, start_slice = 0, end_slice = '', **kwargs):

    new_dict = {}
    proc_dict = stack_dict.copy()
    for key, value in proc_dict.items():
        slice_set = []
        for imgs_tof in value:
                
            slice_set.append(slice_tof_set (imgs_tof, start_slice = start_slice, end_slice = end_slice))
            
        new_dict [key] = slice_set
        
    return new_dict










































