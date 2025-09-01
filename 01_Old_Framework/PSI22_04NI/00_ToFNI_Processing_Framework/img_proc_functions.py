# -*- coding: utf-8 -*-
"""
Created on Thu Jun  9 14:28:37 2022

@author: carreon_r
"""

import os, glob, time
import numpy as np
from tqdm import tqdm
from astropy.io import fits
import matplotlib.pyplot as plt
from skimage.filters import gaussian, median, meijering
from skimage.morphology import disk
import scipy.signal as sp
import datetime

# ------------------------------------------------------------------
#                            get_img
# ------------------------------------------------------------------
                            
# loads an image and returns it as an numpy array     
# In case of a FITS image, the astropy package is used for reading
# (future implementation will return the FITS header as well)
# In case of a TIFF or other image, the general "imread" function
# from the 'matplotlib.pyplot' package is used                       

# Parameters:
#   file_name = file name including the path relative to the base directory
#   base_dir = path of the base directory (default is '', in which case
#       'file_name' should contain an absolute path)      
#
# Return value:
#   img = array containing the image data                      
                            
# ------------------------------------------------------------------

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
                timestamp = hdul[0].header
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
    return img, timestamp

# =============================================================================
#                         slice_tof_set
# =============================================================================
def slice_tof_set (tof_set, start_slice = 0, end_slice = '', **kwargs):
    '''
    Slices a list of values to given parameters

    Parameters
    ----------
    list : list
        list of values
    start_slice : int
        starting slice parameter. The default is 0.
    end_slice : int
        ending slice parameter. The default is ''.

    Returns
    -------
    list
        sliced list.

    '''
        # if there is no specification for end_slice, it takes the whole list of values
    if end_slice  == '':
        end_slice = len(tof_set)
        
    return tof_set[start_slice:end_slice]



# =============================================================================
#                         crop_img
# =============================================================================
                            
# Return a sub region from an image                  

# Parameters:
#   img = array containing the image data
#   roi = rectangle (x1, y1, x2, y2) defining the region of interest      
#
# Return value:
#   sub image for the defined region of interest                     
# ------------------------------------------------------------------
    
def crop_img(src_img, roi_crop, **kwargs):

    img = src_img[0].copy()
    hdr = src_img[1]
    
        # if no ROI is defined, select the full image
    if roi_crop == 0:
        img_corr = img
        
        # otherwise, select the corresponding data
    else:
        img_corr = img[roi_crop[1]:roi_crop[1]+roi_crop[3],roi_crop[0]:roi_crop[0]+roi_crop[2]]
        
    hdr = update_header (hdr, update_type = 'HISTORY', update_list = ['Process: Crop image. ROI cropped = ' + str(roi_crop)])
        # return the data
    return (img_corr, hdr)



# =============================================================================
#                           binning_tof
# =============================================================================

def binning_tof (tof_folder, start_img = 0, binning_factor = 10, **kwargs):
        
        #create a new folder for image results
    bin_cache = []
    binned_list = []
    idx_count = 0
    
        # create the array to match with the desired indices
    list_idx = np.arange(start_img, len(tof_folder), binning_factor)
        
        # start the binning process
    for img in tof_folder[start_img:]:
        
        bin_cache.append(img)
    
        if len(bin_cache) == binning_factor:
            
            img_bin = np.mean(bin_cache,axis = 0)
            binned_list.append(img_bin)
            idx_count+=1
            bin_cache = []

    return binned_list



# =============================================================================
#                         ws_filter
# =============================================================================
def ws_filter(src_img, ws_filter_size, **kwargs):
    
    img = src_img[0].copy()
    hdr = src_img[1]
    hdr = update_header (hdr, update_type = 'HISTORY', update_list = ['Process: WS fiter. Filter size = ' + str(ws_filter_size)])
    img_corr = sp.medfilt2d(img.astype('float32'), ws_filter_size)
    return (img_corr, hdr)



# =============================================================================
#                         outlier_removal
# =============================================================================
def outlier_removal (src_img, threshold, **kwargs):
    import warnings
        # disable warnings because of possible bad characters in the header
    warnings.filterwarnings("ignore")
    
    img = src_img[0].copy()
    hdr = src_img[1]
    
    mask_x = np.where(img <= threshold)[0]
    mask_y = np.where(img <= threshold)[1]
    for x, y in zip(mask_x, mask_y) :
        slice = img[max(0, x-1):x+1, max(0,y-1):y+1] # assuming you want 5x5 square
        img[x,y] = np.mean([i for i in slice.flatten() if i > threshold])  # threshold is 0
        
    hdr = update_header (hdr, update_type = 'HISTORY', update_list = ['Process: Outlier removal. Threshold = ' + str(threshold)])
    return (img, hdr)


# =============================================================================
#                         update_header
# =============================================================================
def update_header (header, update_type = 'COMMENT', update_list = [''],  **Kwargs):
    
    for update in update_list:
        
        header [update_type] = update
        
    return header

# =============================================================================
#                         stack_avg
# =============================================================================
def stack_avg(folders_2_avg, **kwargs):
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

        hdr = update_header (hdr, update_type = 'HISTORY', update_list = ['Process: Pulse average. X-axis '])
        avg_list.append((img, hdr))
    
    return [avg_list]



# =============================================================================
#                        scrubbing_corr
# =============================================================================
def scrubbing_corr (src_img, ob_01_img, ob_02_img, weight_01 = 0.5, weight_02 = 0.5, **kwargs):
    '''
    Does the scrubbing correction with the calculated OBs weighting 

    Parameters
    ----------
    src_img : 2D numpy array
        target image
    ob_01_img : 2D numpy array
        fisrt OB to be taken into account
    ob_02_img : 2D numpy array
        second OB to be taken into account
    weight_01 : int
        weight for first OB. The default is 0.5.
    weight_02 : int
        weight for second OB. The default is 0.5.

    Returns
    -------
    2D numpy array
        image corrected

    '''
        # divide the image by its weightened OBs
    img = src_img [0].copy()
    hdr = src_img[1]
    hdr = update_header (hdr, update_type = 'HISTORY', update_list = ['Process: Scrubbing correction'])
    img_corr = (img/(ob_01_img * weight_01 + ob_02_img * weight_02))
    return (img_corr, hdr)



# =============================================================================
#                         img_align
# =============================================================================
def oversample_img(img, factor=10, order=1):
    import scipy.interpolate
    """
    Resamples an image with sub-pixel resolution

    Parameters
    ----------
    img : 2D numpy array
        Source image.
    factor : integer, optional
        Resampling factor. The default is 10.
    order : integer, optional
        order of interpolation. The default is 1, corresponding to
        bilinear interpolation.

    Returns
    -------
    img_int : 2D numpy array
        Resampled image.

    """
        # get the size of the original image
    szx = img.shape[0]
    szy = img.shape[1]

        # create an interpolation function of the desired order
    intf = scipy.interpolate.RectBivariateSpline(range(szx), range(szy), img, \
                                              kx=order, ky=order)
    
        # apply the interpolation function to a grid with sub-pixel resolution
    img_int = intf(np.arange(szx*factor)/factor, np.arange(szy*factor)/factor)
    
        # return the interpolated image
    return img_int

import numpy as np
import scipy as sp
import cv2 
#from img_utils_mod import oversample_img

def img_align(src_img, ref_img, rois_list, max_shift=10, subpix=15, dof=['tx','ty','sx','sy'], debug_data={}, **kwargs):
    
    meas_shifts = []
    
    debug_data['corr_maps'] = []
    debug_data['meas_shifts'] = []
    
    A = np.empty([0,6])
    B = np.empty([0,1])
    
    ########################## cropping ROIs in ref,src images with extra boundary K
    for i, roi_def in enumerate(rois_list):
        
            # check if the roi definition is a tuple. In this case,
            # the first element contains the ROi coordinates, and the
            # second a string defining the type (horizontal, vertical or both)
        if isinstance(roi_def, tuple):
            roi = roi_def[0]
            roi_type = roi_def[1]
            # if not a tuple, the element contains only the coordinates anf the
            # type is implicitely 'both'
        else:
            roi = roi_def
            roi_type = 'both'
        
            # compute the horizontal and vertical margins as a function of the type
        if roi_type in ['v', 'vert', 'vertical']:
            kx = 0
            ky = max_shift
        elif roi_type in ['h', 'horiz', 'horizontal']:
            kx = max_shift
            ky = 0
        else: 
            kx = max_shift
            ky = max_shift

            # get the sub-region in the reference image
        crop_ref_int16 = ref_img[roi[1]:roi[1]+roi[3], roi[0]:roi[0]+roi[2]]
        
            # get the sub-region in the image to be aligned, including the margins
            # TODO: avoid erros if these margins get over the border
        crop_shift_int16 = src_img[roi[1]-ky:roi[1]+roi[3]+ky, roi[0]-kx:roi[0]+roi[2]+kx]

    ######################### resample the images with sub-pixel resolution and template matching
    
            # resample the images
        crop_shift_r = oversample_img(crop_shift_int16, factor=subpix)
        crop_ref_r = oversample_img(crop_ref_int16, factor=subpix)
            
            # convert to floating point
        crop_ref = np.asarray(crop_ref_r, dtype = np.float32)
        crop_shift = np.asarray(crop_shift_r, dtype = np.float32)
        
            # perform the template matching
        res = cv2.matchTemplate(crop_shift, crop_ref, cv2.TM_CCORR_NORMED)
        
            # find the position with aximum correlation
        shifts = np.array(cv2.minMaxLoc(res)[3])/subpix - np.array([kx,ky])
        
            # add to the results
        meas_shifts.append(shifts)
        
            # store for debugging purpose
        debug_data['corr_maps'].append(res)
        debug_data['meas_shifts'].append(shifts)
        
    ######################## add the corresponding equations
    
        # (order of variables in B: r11 r12 r21 r22 tx ty)
        
            # if the type is both or horizontal, add the equation from the horizontal shift
        if not roi_type in ['v', 'vert', 'vertical']:
            line_A = np.array([roi[0]+roi[2]/2, roi[1]+roi[3]/2, 0, 0, 1, 0]) #x parts for A
            line_B = shifts[0] + roi[0]+roi[2]/2 #x parts for B
            A = np.vstack((A, line_A))
            B = np.vstack((B, line_B))
        
            # if the type is both or vertical, add the equation from the vertical shift
        if not roi_type in ['h', 'horiz', 'horizontal']:
            line_A = np.array([0, 0, roi[0]+roi[2]/2, roi[1]+roi[3]/2, 0, 1]) #y parts for A
            line_B = shifts[1] + roi[1]+roi[3]/2 #y parts for B
            A = np.vstack((A, line_A))
            B = np.vstack((B, line_B))
            
    ########################## constrains for displacement only 
        
    dof_list = [x in dof for x in ['zx','sx','sy','zy','tx','ty']]
    def_vals = [1.0, 0.0, 0.0, 1.0, 0.0, 0.0]
        
        # remove the columns in A corresponding to fixed variables
    for i in reversed(range(6)):
        if not dof_list[i]:
            col_val = A[:,i]
            B = B - def_vals[i]*np.reshape(col_val, B.shape)
            A = np.delete(A, i, 1)
        
        
    debug_data['A'] = A
    debug_data['B'] = B
    
    ########################## solve for M matrix 
    if A.shape[0] > A.shape[1]:
        AT = A.transpose()
        C1 = np.linalg.inv(np.dot(AT,A))
        C2 = np.dot(C1, AT)
        C3 = np.dot(C2, B)
        
    elif A.shape[0] == A.shape[1]:
        C3 = np.linalg.solve(A, B)
        
    else:
        raise ValueError("Needs more ROIs")
        
    ic = 0
    C = np.zeros(6)
    
    for i in range(6):
        if dof_list[i]:
            C[i] = C3[ic]
            ic += 1
        else:
            C[i] = def_vals[i]
        
    
    debug_data['C'] = C
    
    ########################## finding M according to constrains
    """if 'v' in const and 'h' in const:
        M = np.array([[1,C[0,0],C[2,0]], [C[1,0],1,C[3,0]], [0,0,1]]) #not sure about the orders here
        
    elif 'v' in const:
        M = np.array([[C[0,0],C[2,0],C[3,0]], [C[1,0],1,C[4,0]], [0,0,1]])
      
    elif 'h' in const:
        M = np.array([[1,C[1,0],C[3,0]], [C[0,0],C[2,0],C[4,0]], [0,0,1]])
        
    else:"""
    M = np.array([[C[3],C[2],C[5]], [C[1],C[0],C[4]], [0,0,1]])    
    
    debug_data['M'] = M 
    
    #rows, cols = img.shape[0], img.shape[1] 
    
    #corrected_img = sp.ndimage.affine_transform(img, M, order=1)

    return M #corrected_img




# =============================================================================
#                       img_registration
# =============================================================================


def img_registration (src_img, ref, rois_list ='', dof=['tx','ty','sx','sy'], M = '', **kwargs):
    '''
    This function takes an image that requires registration (rotation, translation) and compares it with a reference image to make the 
    necessary operations and correct any displacements that ocurred during the experiments.

    Returns
    -------
    full parameters and a 2D array
        DESCRIPTION.

    '''
    import os
    import scipy as sp
    import scipy.misc
    import imreg_dft as ird
    import numpy as np
    from skimage import data, io
    from skimage.feature import register_translation
    # from skimage.feature.register_translation import _upsampled_dft
    from scipy.ndimage import fourier_shift
    from skimage.registration import phase_cross_correlation
    
        # ignores warning messages
    np.seterr(all='ignore')
    
    img = src_img[0].copy()
    hdr = src_img[1]
    if M == '':
        M = img_align(img, ref[0], rois_list, max_shift=15, subpix=15, dof=dof, debug_data={})
        
    reg_img = sp.ndimage.affine_transform(img, M, order=1)
    
    hdr = update_header (hdr, update_type = 'HISTORY', update_list = ['Process: Image registration. Registration matrix (M): ' + str(M.tolist())])
    
    return (reg_img, hdr)



# =============================================================================
#                          create_SBKG_Wmask
# =============================================================================
def SBKG_Wmask (src_img, BB_mask_img, **kwargs):
    """
    Creates a SBKG image from a base image and its respective BB mask

    Parameters
    ----------
    img : 2D array
        source image, base to create the sbkg 
    BB_mask_img : 2D BB mask image. array
        BB mask corresponding to the source image
        
    Returns
    -------
    2D array corresponding to the sbkg image for correction
    
    """
        # initialize libraries
    from skimage.measure import label
    from scipy.interpolate import Rbf
    
    img = src_img [0].copy()
    hdr = src_img[1]
    
    img = np.nan_to_num(img)
    
    BB_mask_img_data = BB_mask_img[0].copy()
    
        # extract the image shape
    s_row = img.shape[0]
    s_col = BB_mask_img_data.shape[1]
    
        # identify and enumerate each BB in the mask
    msk_reg = label(BB_mask_img_data)
    
        # take the max number of BBs in the image
    bb_count = np.max(msk_reg)
    
        # initialize the region value variables
    xvals = np.zeros(bb_count)
    yvals = np.zeros(bb_count)
    ivals = np.zeros(bb_count)
    
        # create a matrix of values corresponding to the images shape
    xb = np.matmul(np.ones(s_row).reshape(-1,1),np.arange(s_col,dtype='float').reshape(1,s_col))
    yb = np.matmul(np.arange(s_row).reshape(-1,1),np.ones(s_col,dtype='float').reshape(1,s_col))
    
    for i in range (bb_count):
            # for each BB take all the values that satisfy the requirement in the loop 
        reg = np.where(msk_reg == i+1)
        
            # vector construction for x/y and the values per region in the base image
        xvals [i] = round(np.nanmean(xb[reg]))
        yvals [i] = round(np.nanmean(yb[reg]))
        ivals [i] = np.nanmean(img[reg])

        # prepare vectors for linear least squared regression
    A = np.array([xvals*0+1, xvals, yvals]).T
    B = ivals.flatten()
    
        # linear least square approximation for linear regression 
    coeff, _, _, _ = np.linalg.lstsq(A, B,rcond=None)
    
        # extract the coefficient
    vl = coeff[0] + coeff[1]*xvals + coeff[2]*yvals
    vli = coeff[0] + coeff[1]*xb + coeff[2]*yb
    
        # interpolate values for the SBKG image constrcution 
    rbfi2 = Rbf(xvals, yvals, ivals-vl, function='thin_plate')

    SBKG_img = rbfi2(xb, yb) + vli
    hdr = update_header (hdr, update_type = 'COMMENT', update_list = ['SBKG Image created on: ' + str(datetime.datetime.now())])
    
    return (SBKG_img, hdr)



# =============================================================================
#                         subtract_SBKG
# =============================================================================
def subtract_SBKG(src_img, SBKG_img, **kwargs):
    img = src_img[0].copy()
    hdr = src_img[1]
    sbkg_img = SBKG_img[0]
    
    img_corr = (img - sbkg_img)
    hdr = update_header (hdr, update_type = 'HISTORY', update_list = ['Process: SBKG correction'])
    
    return (img_corr, hdr)


# =============================================================================
#                           TFC_corr
# =============================================================================
def TFC_corr(src_img, ref_img, nca=[0,0,0,0], **kwargs):

    img = src_img[0].copy()
    hdr = src_img[1]
    ref = ref_img[0].copy()
    
    if sum(nca) == 0:
        TFC = 1.0
    else:
        TFC = np.average(crop_img(ref, nca)) / np.average(crop_img(img, nca))
    
    img_corr = (img/ref)*TFC
    hdr = update_header (hdr, update_type = 'HISTORY', update_list = ['Process: TFC correction'])
    
    return (img_corr, hdr)



# =============================================================================
#                           write_img
# =============================================================================
                            
# Writes a FITS image. If the destination path does not exist, create it                 

# Parameters:
#   img = image to write (2D numpy array)
#   file_name = file name including the path relative to the base directory
#   base_dir = path of the base directory (default is '', in which case
#       'file_name' should contain an absolute path)      
#
# Return value:
#   img = array containing the image data                      
                            
# ------------------------------------------------------------------

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
        hdu = fits.PrimaryHDU(np.flip(img[0],0))
        hdu.header = img[1]
        hdu.writeto(dst_name, overwrite=overwrite)
        
        # output the error message if necessary
    except Exception as detail:
        print("Could not write the destination image:", detail) 
    


# ------------------------------------------------------------------
#                            prep_img_for_display
# ------------------------------------------------------------------
                            
# Scale and image intensity to display it based on percentile values.
# The data in the range between the lower and higher percentiles is mapped
# to an output data between 0.0 and 1.0. Additionally, the size of the
# image can be channged by applying a zoom factor.                    

# Parameters:
#   img = array containing the image data
#   zf = zoom factor (default 1.0)                        
#   lp = lower percentile (default 5%)                      
#   lp = higher percentile (default 95%)  
#
# Return value:
#   disp_img = array containing the rescaled data                          
# ------------------------------------------------------------------
    
def prep_img_for_display(img, zf=1, lp=5, hp=95, stretch=[1.0,1.0]):
    
    import numpy as np
    from scipy.ndimage.interpolation import zoom
    import warnings
    
        # get the min and max values for the defined percentiles
    scale_min = np.percentile(np.nan_to_num(img), lp)
    scale_max = np.percentile(np.nan_to_num(img), hp)
    
        # define the offset and scale based on the min and max values
    offset = scale_min
    if scale_max != scale_min:
        scale = 1.0/float(scale_max-scale_min)
    else:
        scale = 1.0
    
        # disable warnings because of potential disturbing warnings in the zoom function
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        
            # rescale the intensities and resize the image
        disp_img = zoom(scale*(img-offset), np.flip(zf*np.array(stretch),0))
    
        #return the data (replacing the NaN values)
    return np.nan_to_num(disp_img)


# ------------------------------------------------------------------
#                            show_img
# ------------------------------------------------------------------
                            
# Display an image using matplotlib                  

# Parameters:
#   img = array containing the image data 
#   title = title to display above the image
#   wmax = width (in pixels) up to which the image is maginfied
#   dr = array of rectangles to display on top of the image. Each
#       element is a tuple defined as (rectangle, color)
#
# Return value:
#   None                       
# ------------------------------------------------------------------
    
def show_img(img, title='', wmax=750, dr=[], stretch=[1.0,1.0], keep_fig=False,
             nrows=1, ncols=1, index=1, do_show=True, font_size=9, cmap='gray'):
    
    import matplotlib
    import matplotlib.pyplot as plt  
    
    global current_fig
    
        # update the font size for the title
    matplotlib.rcParams.update({'font.size': font_size})
    
        # rescale the intensities for display
    disp_img = prep_img_for_display(img, stretch=stretch)
    
        # get the image size and compute the display resolution
    szx = disp_img.shape[1]
    szy = disp_img.shape[0]
    dpi_img = 50.0*(szx*ncols)/min((szx*ncols),wmax)
    
        # create the plot with the desired size
    if not keep_fig:
        f = plt.figure(figsize = (szx*ncols/dpi_img, szy*nrows/dpi_img), dpi=100)
        current_fig = f
    else:
        f = current_fig
    sp = f.add_subplot(nrows, ncols, index)
    
        # include the image
    sp.imshow(disp_img, cmap=cmap, vmin=0.0, vmax=1.0, interpolation='none')
    
        # if necessary, write the title
    if title != '':
        sp.set_title(title)
        
        # hide the axes
    sp.axis('off')

        # draw all rectangles    
    for rects, col in dr:
        if type(rects[0]) == list or (isinstance(rects[0], tuple)):
            rlist = rects
            show_num = True
        else:
            rlist = [rects]
            show_num = False
        
        for i, rect_def in enumerate(rlist):
            if isinstance(rect_def, tuple):
                rect = rect_def[0]
                name = str(i+1) + ' (' + rect_def[1] + ')'
                pass
            else:
                rect = rect_def
                name = str(i+1)
            rx = rect[0]*stretch[0]
            ry = rect[1]*stretch[1]
            rw = rect[2]*stretch[0]
            rh = rect[3]*stretch[1]
            rect_fill = matplotlib.patches.Rectangle((rx,ry), rw, rh, color=col, 
                                                  fill=True, alpha=0.25)
            rect_border = matplotlib.patches.Rectangle((rx,ry), rw, rh, color=col, fill=False)
            sp.add_patch(rect_fill)
            sp.add_patch(rect_border)
            if show_num:
                sp.text(rx+rw/2, ry+rh/2, name, color='black', fontsize='medium',
                        fontweight='bold', ha='center', va='center', backgroundcolor=col)
        
        # display the plot
    if do_show:
        plt.show()
        
        
def img_roi_selector(img, default=None, title='ROI selector',
                     multiple=False, roi_names=[], options=[], cmap = 'gray'):
    
    import pyqtgraph as pg
    from PyQt5.QtCore import QRectF
    import PyQt5.QtCore
    from PyQt5.QtWidgets import QPushButton, QWidget, QHBoxLayout, QVBoxLayout, QApplication
    from matplotlib import cm
    global app
    
    roi_list = []
    roi_label_list = []
    roi_opt_list = []
    
    flex_list = multiple and roi_names == []
    
    def updateLabels():
        
        for i, label in enumerate(roi_label_list):
            if roi_names != []:
                txt = roi_names[i]
            else:
                txt = str(i+1)
            if options != []:
                txt = txt + ' (' + options[roi_opt_list[i]] + ')'
            label.setText(txt)
    
    def addRoi(x0, y0, w, h, option=''):
    
            # create the ROI and add it to the view
        roi = pg.ROI([x0,y0], [w,h], maxBounds=QRectF(0,0,szx,szy), scaleSnap=True, 
                     translateSnap=True, pen=pg.mkPen('r', width=2), rotatable=False,
                     removable=flex_list)
        roi.handlePen = pg.mkPen('r', width=2)
        view.addItem(roi)
        
            # add all 8 resizing handles to the ROI
        roi.addScaleHandle([1, 0.5], [0, 0.5])
        roi.addScaleHandle([0, 0.5], [1, 0.5])
        roi.addScaleHandle([0.5, 0], [0.5, 1])
        roi.addScaleHandle([0.5, 1], [0.5, 0])
        roi.addScaleHandle([1, 1], [0, 0])
        roi.addScaleHandle([0, 0], [1, 1])
        roi.addScaleHandle([1, 0], [0, 1])
        roi.addScaleHandle([0, 1], [1, 0])
            
        if flex_list:
            roi.sigRemoveRequested.connect(roiRemoveRequested)
            
        if options != []:
            roi.setAcceptedMouseButtons(PyQt5.QtCore.Qt.LeftButton)
            roi.sigClicked.connect(roiClicked)
        
        if multiple:
            roi_label = pg.TextItem('', color='r', border=pg.mkPen('r'),
                                    fill=pg.mkBrush(255,255,255,192))
            view.addItem(roi_label)
            roi_label.setParentItem(roi)
            roi_label_list.append(roi_label)
            
        roi_list.append(roi)
        if options != []:
            if option == '':
                opt_index = 0
            else:
                opt_index = options.index(option)
            roi_opt_list.append(opt_index)
        
        updateLabels()
        
        # function responding to the OK button
    def addRoiButtonPressed():
        if options == []:
            addRoi(*default_roi)
        else:
            addRoi(*(default_roi[0]), default_roi[1])

        # function responding to the OK button
    def okButtonPressed():
        app.quit()
    
        # function responding to the Cancel button
    def cancelButtonPressed():
            # quit with an empty ROI value
        roi_list = []
        app.quit()
    
        # function responding to the Cancel button
    def roiRemoveRequested(roi):
        
        i = roi_list.index(roi)
        view.removeItem(roi_list[i])
        view.removeItem(roi_label_list[i])
        roi_list.pop(i)
        roi_label_list.pop(i)
        
        updateLabels()
        
    def roiClicked(roi):
        
        i = roi_list.index(roi)
        roi_opt_list[i] = (roi_opt_list[i] + 1) % len(options)
        
        updateLabels()
        
    
        # get the image size
    szy, szx = img.shape
    
    if options == []:
        default_roi = [int(szx/2-szx/20), int(szy/2-szy/20), int(szx/10), int(szy/10)]
    else:
        default_roi = ([int(szx/2-szx/20), int(szy/2-szy/20), int(szx/10), int(szy/10)], '')
        

        # create the applications
    if app == 0:
        app = QApplication([])
    
        # create the main window
    main = QWidget()
    main.setWindowTitle(title)
    
        # create the graphics layout (to display the image)
    pg.setConfigOptions(imageAxisOrder='row-major')
    glw = pg.GraphicsLayoutWidget(size=(1000,1000*szy/szx), border=True)
    w1 = glw.addLayout(row=0, col=0)
    view = w1.addViewBox(row=0, col=0, lockAspect=True)
    
        # add the image to the layout
    img_item = pg.ImageItem(img, levels=[0,1])
    
        # Get the colormap
    colormap = cm.get_cmap(cmap)  
    colormap._init()
    lut = (colormap._lut * 255).view(np.ndarray)  # Convert matplotlib colormap from 0-1 to 0 -255 for Qt
    
    # Apply the colormap
    img_item.setLookupTable(lut)

    view.addItem(img_item)
    
        # case of multiple ROI selector
    if multiple:
            # case of open list (no names specified)
        if roi_names == []:
                # if a defualt ROI list is given, place them
                # (otherwise we start with zero ROIs)
            if default != None:
                for roi in default:
                    if options == []:
                        addRoi(*roi)
                    else:
                        addRoi(*(roi[0]), roi[1])
                    
            # case of named list (fixed length)
        else:
            for i, roi in enumerate(roi_names):
                if default != None and i < len(default):
                    init_roi = default[i]
                else:
                    init_roi = default_roi
                if options == []:
                    addRoi(*init_roi)
                else:
                    addRoi(*(init_roi[0]), init_roi[1])
    
        # case of single ROI selector
    else:
            # if a default position/size is given, use it
        if default != None:
            init_roi = default
            # otherwise place the ROi in the middle, with 10% of the image size
        else:
            init_roi = default_roi
            
            # create the ROI
        addRoi(*init_roi)
    
        # disable auto range in x and y directions
    view.disableAutoRange('xy')
    view.autoRange()

        # create the OK and Cancel buttons
    okButton = QPushButton("OK")
    cancelButton = QPushButton("Cancel")
    if flex_list:
        addRoiButton = QPushButton("Add ROI")
    
        # connect the buttons to their handling functions
    okButton.clicked.connect(okButtonPressed)
    cancelButton.clicked.connect(cancelButtonPressed)
    if flex_list:
        addRoiButton.clicked.connect(addRoiButtonPressed)

        # create a horizontal layout with the buttons
    hbox = QHBoxLayout()
    if flex_list:
        hbox.addWidget(addRoiButton)
    hbox.addStretch(1)
    hbox.addWidget(okButton)
    hbox.addWidget(cancelButton)

        # create a vertical layout with the image view and the
        # buttons layout below
    vbox = QVBoxLayout()
    vbox.addWidget(glw)
    vbox.addLayout(hbox)

        # set this vertical layout as main widget
    main.setLayout(vbox)
    
        # show the main window
    main.show()

        # start the vent loop
    app.exec_()
    
        # set the return value to the selected ROI(s) and quit
    if multiple:
        if options != []:
            retval = []
            for i, roi in enumerate(roi_list):
                retval.append(([int(roi.pos()[0]), int(roi.pos()[1]),
                          int(roi.size()[0]), int(roi.size()[1])], options[roi_opt_list[i]]))
                
        else:
            retval = [[int(roi.pos()[0]), int(roi.pos()[1]),
                      int(roi.size()[0]), int(roi.size()[1])] for roi in roi_list]
    else:
        retval = [int(roi_list[0].pos()[0]), int(roi_list[0].pos()[1]),
                  int(roi_list[0].size()[0]), int(roi_list[0].size()[1])]
        
        # return the ROI
    return retval



# =============================================================================
#                         select_multiple_rois
# =============================================================================
def select_multiple_rois(var_name, img, just_rois=False, cmap = 'gray', **kwargs):
    '''
    This function provides an interactive interface for selecting a rectangular region of interest in an image.
    This function is meant to be used with the `%load`  magic in jupyter.
    
    The difference with 'select_rois' is that this function assign all the ROIs selected to only one variable name

    Parameters
    ----------
    var_name : str
        strs or list with the names assigned that want to be assigned to the ROIs
    src_img : str
        image directory and name
    img : 2D numpy array
        source image
    base_dir : str, optional
        directory relative to which the 'src_dir' variable is specified (absolute path is used if omitted) 

    Returns
    -------
    variables
        Variable name = [[x,y,w,h], [x2,y2,w2,h2],...]

    '''
            # import necessary packages
    
        # if one variable is given ie. string, it convert it into a list to enter the names and ROIs loop
    if type(var_name) == list:
        
            # generate the window title
        title = 'Please select following ROIs: ' + ','.join(var_name)
        
            # perform the interactive rectangular ROI selection
        roi_def = img_roi_selector(img, title=title, 
                multiple=True, roi_names=var_name, cmap=cmap)
        
            # if an empty ROI is returned, this means the input was canceled
        if roi_def == None:
            raise ValueError('Interactive input canceled by the user')
        # when you want to extract just the rois info
        if just_rois:
            return roi_def
            # generate a statement to be inserted in the jupyter notebook
        return ( 'ROIs_'+ var_name + ' = ' + str(roi_def))
    
    else:
        
            # generate the window title
        title = 'Please define one or more ROIs for ' + var_name
        
            # perform the interactive rectangular ROI selection
        roi_def = img_roi_selector(img, title=title, 
                                   multiple=True, cmap=cmap)
        
            # if an empty ROI is returned, this means the input was canceled
        if roi_def == None:
            raise ValueError('Interactive input canceled by the user')
        
            # when you want to extract just the rois info
        if just_rois:
            return roi_def
        
            # return the list of values in a legible format for %load magic
        return ( var_name + ' = ' + str(roi_def))
    



# ------------------------------------------------------------------
#                            show_img_rois
# ------------------------------------------------------------------
                            
# Display an image using matplotlib                  

# Parameters:
#   img = array containing the image data 
#   title = title to display above the image
#   wmax = width (in pixels) up to which the image is maginfied
#   dr = array of rectangles to display on top of the image. Each
#       element is a tuple defined as (rectangle, color)
#
# Return value:
#   None                       
# ------------------------------------------------------------------
    
def show_img_rois(img, title='', wmax=750, dr=[], stretch=[1.0,1.0], keep_fig=False,
             nrows=1, ncols=1, index=1, do_show=True, font_size=9):
    
    import matplotlib
    import matplotlib.pyplot as plt  
    
    global current_fig
    
        # update the font size for the title
    matplotlib.rcParams.update({'font.size': font_size})
    
        # rescale the intensities for display
    disp_img = prep_img_for_display(img, stretch=stretch)
    
        # get the image size and compute the display resolution
    szx = disp_img.shape[1]
    szy = disp_img.shape[0]
    dpi_img = 50.0*(szx*ncols)/min((szx*ncols),wmax)
    
        # create the plot with the desired size
    if not keep_fig:
        f = plt.figure(figsize = (szx*ncols/dpi_img, szy*nrows/dpi_img), dpi=100)
        current_fig = f
    else:
        f = current_fig
    sp = f.add_subplot(nrows, ncols, index)
    
        # include the image
    sp.imshow(disp_img, cmap='gray', vmin=0.0, vmax=1.0, interpolation='none')
    
        # if necessary, write the title
    if title != '':
        sp.set_title(title)
        
        # hide the axes
    sp.axis('off')

        # draw all rectangles    
    for rects, col in dr:
        if type(rects[0]) == list or (isinstance(rects[0], tuple)):
            rlist = rects
            show_num = True
        else:
            rlist = [rects]
            show_num = False
        
        for i, rect_def in enumerate(rlist):
            if isinstance(rect_def, tuple):
                rect = rect_def[0]
                name = str(i+1) + ' (' + rect_def[1] + ')'
                pass
            else:
                rect = rect_def
                name = str(i+1)
            rx = rect[0]*stretch[0]
            ry = rect[1]*stretch[1]
            rw = rect[2]*stretch[0]
            rh = rect[3]*stretch[1]
            rect_fill = matplotlib.patches.Rectangle((rx,ry), rw, rh, color=col, 
                                                  fill=True, alpha=0.25)
            rect_border = matplotlib.patches.Rectangle((rx,ry), rw, rh, color=col, fill=False)
            sp.add_patch(rect_fill)
            sp.add_patch(rect_border)
            if show_num:
                sp.text(rx+rw/2, ry+rh/2, name, color='black', fontsize='medium',
                        fontweight='bold', ha='center', va='center', backgroundcolor=col)
        
        # display the plot
    if do_show:
        plt.show()
