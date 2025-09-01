# -*- coding: utf-8 -*-
"""
Created on Wed Jun  8 16:29:16 2022

@author: carreon_r
"""
import os
import numpy as np
from tqdm import tqdm
from copy import deepcopy
 
from img_functions import *




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


def sequence_separator (sequence, list_sep):
    
    new_sequence = []
    buffer = []
    
    for idx, func in enumerate (sequence):
        
        if func.__name__ not in list_sep:
            buffer.append(func)
            if idx == len(sequence)-1:
                new_sequence.append(list(buffer))
        else:
            new_sequence.append(list(buffer))
            new_sequence.append([func])
            buffer = []
            
    return list(filter(None, new_sequence))
    


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
#                         update_header
# =============================================================================
def update_header (header, update_type = 'COMMENT', update_list = [''],  **Kwargs):
    
    for update in update_list:
        
        header [update_type] = update
        
    return header



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
    hdr = src_img[1]
        # apply succesively all processing steps to the image
    for step in proc_seq:
        img = step(img, **kwargs)
        # return the processed image
    
    seq_list = str([func.__name__ for func in proc_seq])
    hdr = update_header (hdr, update_type = 'HISTORY', update_list = [seq_name + ': ' + seq_list])
                   
    return (img[0], hdr)



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
#                         stack_avg
# =============================================================================
def stack_averaging(folders_2_avg, **kwargs):
    '''
    Base function to average image stacks after their overlap correction.
    This function is meant to be used with 'exec_averaging' as one of the sequence functions

    Parameters
    ----------
    folders_2_avg : list of arrays
        can be a list of images or a list of directories with their individual address.

    Returns
    -------
    base folder with all the images averaged

    '''
        # import libraries
    import numpy as np
    
    avg_list = []
    
    list_imgs = [[item[0] for item in sub_val] for sub_val in folders_2_avg]
    list_hdrs = [[item[1] for item in sub_val] for sub_val in folders_2_avg]
    
    mean_imgs = list(np.nanmean(list_imgs, axis=0))
    middle_hdr = list_hdrs[int(len(list_hdrs)/2)]
    
    for img, hdr in zip (mean_imgs, middle_hdr):

        hdr = update_header (hdr, update_type = 'HISTORY', update_list = ['Sequence: Pulse average. X-axis (acquisitions)'])
        avg_list.append((img, hdr))
    
    return [avg_list]




# =============================================================================
#                           binning_frames
# =============================================================================

def binning_frames (acqs_folder, start_img = 0, frames_binning_factor = 1, HE_LE = (False, [15,30],[30,50]), **kwargs):
        
        #create a new folder for image results
    img_bin_cache = []
    hdr_bin_cache =[]
    binned_list = []
    
    if HE_LE [0]:
        
        binned_list = separate_energies (acqs_folder, HE_slice = HE_LE[1], LE_slice = HE_LE[2])
        
    else:
            # start the binning process
        for src_img in acqs_folder[start_img:]:
            
            img = src_img[0].copy()
            hdr = src_img[1]
            img_bin_cache.append(img)
            hdr_bin_cache.append(hdr)
            if len(img_bin_cache) == frames_binning_factor:
                
                img_bin = np.nanmean(img_bin_cache,axis = 0)
                hdr_bin = hdr_bin_cache[int(len(hdr_bin_cache)/2)]
                hdr_bin = update_header (hdr_bin, update_type = 'HISTORY', update_list = 
                                         ['Sequence: Frames binning. Binning: ' + str(frames_binning_factor) + '. Starting image: ' + str(start_img)])
                    
                binned_list.append((img_bin, hdr_bin))
                img_bin_cache = []
                hdr_bin_cache = []
    

    return binned_list



# =============================================================================
#                           binning_acquisitions
# =============================================================================

def binning_acquisitions (dict_values, acquisitions_binning_factor = 2, **kwargs):
    
    bin_buffer_imgs = []
    bin_buffer_hdrs = []
    folder_values = []
    
    list_imgs = [[item[0] for item in sub_val] for sub_val in dict_values]
    list_hdrs = [[item[1] for item in sub_val] for sub_val in dict_values]
    
        # start the binning process
    for idx, imgs_acq, hdrs_acq in zip (tqdm(range(len(list_imgs)), desc = 'Processing Binning Acquisitions'),list_imgs, list_hdrs):
        
        bin_buffer_imgs.append(imgs_acq)
        bin_buffer_hdrs.append(hdrs_acq)
        bin_set =[]
        
        if len(bin_buffer_imgs) == acquisitions_binning_factor:
            
            img_bin = list((np.nanmean(bin_buffer_imgs, axis=0)))
            hdr_bin = bin_buffer_hdrs[int(len(bin_buffer_hdrs)/2)]
            
            
            for img, hdr in zip(img_bin, hdr_bin):
                hdr = update_header (hdr, update_type = 'HISTORY', update_list = 
                                     ['Sequence: Acquisitions binning. Binning: ' + str(acquisitions_binning_factor)])
                bin_set.append((img,hdr))
            
            bin_buffer_imgs = []
            bin_buffer_hdrs = []
            
            folder_values.append(bin_set)
        
    return folder_values




# =============================================================================
#                        separate_energies
# =============================================================================
def separate_energies (frames_folder, HE_slice = [15, 30], LE_slice = [30,50], **kwargs):
    
    list_imgs = [src_img[0] for src_img in frames_folder]
    list_hdrs = [src_img[1] for src_img in frames_folder]
    
    HE_avg = np.nanmean(list_imgs[HE_slice[0]:HE_slice[1]], axis = 0)
    LE_avg = np.nanmean(list_imgs[LE_slice[0]:LE_slice[1]], axis = 0)
    
    HE_hdr = list_hdrs[int((HE_slice[0]+HE_slice[1])/2)]
    LE_hdr = list_hdrs[int((LE_slice[0]+LE_slice[1])/2)]
        # takes each value in the subfolder (values)
    HE_hdr= update_header (HE_hdr, update_type = 'HISTORY', update_list = ['Sequence: Separate energies. HE image: ' + str(HE_slice)])
    LE_hdr= update_header (LE_hdr, update_type = 'HISTORY', update_list = ['Sequence: Separate energies. LE image: ' + str(LE_slice)])
    
    folder_values = [(HE_avg, HE_hdr), (LE_avg, LE_hdr)]
    
    return folder_values



















