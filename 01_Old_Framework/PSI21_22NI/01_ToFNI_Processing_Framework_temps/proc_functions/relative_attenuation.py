
from stack_proc_func import *
from img_utils_mod import *
#from plot_cross_sections import *
import pandas as pd




# =============================================================================
#                          get_relative_att_stack
# =============================================================================
    
def get_relative_att_stack (trans_imgs_dict, dst_dir, HE_n_LE, proc_folder = [], start_numb = 0):
    
    import warnings
    warnings.filterwarnings("ignore")
    
        # for the case where no specific folders are given, works with all folders
    if proc_folder == []:
        
            # unpacks the key arguments and transform them into a list
        proc_folder = [*trans_imgs_dict]
        
        # constructs the list of targeted folders and reference
    keep_key(trans_imgs_dict,proc_folder)
    
    HE = HE_n_LE[0]
    LE = HE_n_LE[1]
    
    idx = start_numb
    
    for key, values in trans_imgs_dict.items():
        
            # find the border values according to the given boundaries HE and LE
        borders_HE = [item for item in values[0] if format(HE[0], '05d') in item or format(HE[1], '05d') in item]
        borders_LE = [item for item in values[0] if format(LE[0], '05d') in item or format(LE[1], '05d') in item]
        
            #give all the values (including borders) 
        list_HE = [i for i in values[0] if i >= borders_HE[0] and i <= borders_HE[1]]
        list_LE = [i for i in values[0] if i >= borders_LE[0] and i <= borders_LE[1]]
        
            # initialize the averga of images with a matrix of zeros with the img shape
        img_HE = np.zeros(get_img(list_HE[0]).shape)
        img_LE = np.zeros(get_img(list_LE[0]).shape)
        
            # get the average image for HE and LE
        for loc_HE, loc_LE in zip(list_HE,list_LE):
            
            img_HE = img_HE + get_img(loc_HE)
            img_LE = img_LE + get_img(loc_LE)

        img_HE = np.log(img_HE/len(list_HE))
        img_LE = np.log(img_LE/len(list_LE))
        
            # get the relative attenuation image for each point PIXEL WISE
        att_rel_img = np.nan_to_num(img_LE/img_HE)
           
        file_name = os.path.join(dst_dir, key + '_rel_att_img_' + format(idx, '05d') + '.fits' )
            
            #pack the image with the average value of the timestamps
        #att_rel_img = (att_rel_img, header)
            
        write_img(np.flip(att_rel_img, 0), file_name, base_dir='', overwrite=False)
        # slice the dictionary into HE and LE
        
        idx += 1
        
    return
