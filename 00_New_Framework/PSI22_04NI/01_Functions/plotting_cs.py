# -*- coding: utf-8 -*-
"""
Created on Fri Sep 23 11:27:33 2022

@author: carreon_r
"""

import os, glob, time
import pandas as pd
from img_functions import *
from proc_functions import *
from dict_functions import *
from scipy.signal import savgol_filter
from matplotlib.widgets import Slider


thickness = 0.056
h2o = {'abbv': 'H2O','composition' : {'H':2.0, 'O':1.0},'density':0.997, 'thickness': thickness}
ec = {'abbv': 'EC', 'composition' : {'C':3.0, 'H':4.0, 'O':3.0},'density':1.32, 'thickness': thickness}
dmc = {'abbv': 'DMC','composition' : {'C':3.0, 'H':6.0, 'O':3.0}, 'density':1.07, 'thickness': thickness}
dec = {'abbv': 'DEC','composition' : {'C':5.0, 'H':10.0, 'O':3.0}, 'density':0.975, 'thickness': thickness}
lipf6 = {'abbv': 'LiPF6','composition' : {'LI':1.0, 'P':1.0, 'F':6.0}, 'density':1.5, 'thickness': thickness}
ec_dmc_11v = {'abbv': 'EC_DMC (1:1v)','molecules' : [ec,0.5,dmc,0.5], 'density':1.28, 'thickness': thickness}
ec_dmc_11w = {'abbv': 'EC_DMC (1:1w)','molecules' : [ec,0.447511501,dmc,0.552488499], 'density':1.2335, 'thickness': thickness}
ec_dec_11v = {'abbv': 'EC_DEC (1:1v)','molecules' : [ec,0.5,dec,0.5], 'density':1.1785, 'thickness': thickness}
ec_dec_37w = {'abbv': 'EC_DEC (3:7w)','molecules' : [ec,0.240305619,dec,0.759694381], 'density':1.0705, 'thickness': thickness}
lp30 = {'abbv': 'LP30','molecules' : [ec, 0.406359477,dmc, 0.501683056, lipf6, 0.091957467], 'density':1.2795, 'thickness': thickness}
lp40 = {'abbv': 'LP40','molecules' : [ec, 0.447925137,dec, 0.447925137, lipf6, 0.104149725], 'density':1.2635, 'thickness': thickness}
lp47 = {'abbv': 'LP47','molecules' : [ec, 0.218207723,dec, 0.689834809, lipf6 ,0.091957467], 'density':1.1685, 'thickness': thickness}
ec_dec_sol = {'abbv': 'EC_DEC (sol)','molecules' : [ec,0.5,dec,0.5], 'density':1.1785, 'thickness': thickness}
pe = {'abbv': 'PE', 'composition' : {'C':1.0, 'H':2.0},'density':0.92, 'thickness': thickness}



def play_savgol_smoothing (array, window, order):
    
    from scipy.signal import savgol_filter
    from matplotlib.widgets import Slider
    
    
    arr = 10
    window = 3
    order = 2
    if window <= order:
        window = order +1
        
    if window%2 == 0:
        window = window+1
    
    x = np.arange(0,len(arr))
    
    arr_f = savgol_filter(arr, window, order)
        
    #plotting
    fig = plt.figure()
    ax = fig.subplots()
    p = ax.plot(x,arr, '-*')
    p, = ax.plot(x, arr_f, 'g') #comma after p is important to make it interactive
    plt.subplots_adjust(bottom=0.3) #to give space for the slider
    
    # defining the slider
    ax_slide = plt.axes([0.2,0.15,0.7,0.03]) #([xpos, ypos,width, height])
    win_len = Slider(ax_slide, 'Window', valmin = 1, valmax = len(arr), valinit = window, valstep = 2)
    or_slide = plt.axes([0.2,0.05,0.7,0.03])
    poly_ord = Slider(or_slide, 'Order', valmin = 1, valmax = 6, valinit = order, valstep = 1)
    
    # updating function for plot
    def update(val):
        current_val_window = int(win_len.val)
        current_val_order = (int(poly_ord.val))
        new_y = savgol_filter(arr, current_val_window, current_val_order)
        p.set_ydata(new_y)
        fig.canvas.draw() #redraw the figure
    
    # when to call the update function
    win_len.on_changed(update)
    poly_ord.on_changed(update)
    plt.show()



# =============================================================================
#                         img_roi_selector
# =============================================================================
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
        return ( 'ROIs_'+ var_name + ' = ' + str(roi_def))




# =============================================================================
#                              get_roi_values
# =============================================================================
# this function creates an excel sheet of transmission values by taking ROI values
def get_roi_values (dictionary, rois_dict, spectra_file, save_path ='', binning = 1, flight_path = 1, start_slice = 0, end_slice='', name_xlsx = 'Transmission_values.xlsx', save_results = False, **kwargs):
    
    import numpy as np
    import pandas as pd
    
    Values = pd.DataFrame()
    table_wvl = pd.DataFrame()
    
    for roi_name, rois in rois_dict.items():
            # get the real name of the folder connected with the regions of interest
        roi_name  = roi_name.split('ROIs_')[1]
        
            # prepare the dictionary and the table to include the results
        subfolder = dictionary.get(roi_name)
        
        for folder_img in subfolder:
            
            results_vec = np.zeros([len(folder_img), len(rois)])
            
            for ndx, img in enumerate (folder_img):
                
                for idx, roi_val in enumerate(rois):
                    
                    results_vec[ndx,idx] = np.nanmean(crop_img(img, roi_val)[0])
            
            for k in range(results_vec.shape[1]):
                Values['Values_' + roi_name + '_roi_' + str(k+1)] = results_vec[:,k]
                
        # Reads the spectra, creates the table and calculate the equivalent wavelengths in Angstroms
    table_spectra = pd.read_csv(spectra_file,header=None, usecols=[0], sep='\t', names=['Arrival Time'])
    table_wvl["Wavelength [Å]"] = (3956.034/(flight_path/table_spectra["Arrival Time"]))
    
        #if the transmission results were sliced and/or binned, this will take it into account and calculate the new table by the binning weight (1 is no binning)
    if end_slice == '':        
        end_slice= len(table_wvl)
        
    table_wvl = table_wvl.groupby(np.arange(len(table_wvl))//binning).mean()
    table_wvl = table_wvl [start_slice:end_slice]
        
        # since we modify the indexes in the dataframe (binning and/or slicing) we must reset the index
    table_wvl = table_wvl.reset_index(drop = True)
    
        # add the results obtained from the transmission in the ROIs selcted
    table_val_rois = pd.concat([table_wvl, Values], axis =1)
        
        # Send to the results to the directory from which you extracted the transmission images
    if save_results:
        table_val_rois.to_excel(save_path + '/' + name_xlsx)
         
    return table_val_rois


# =============================================================================
#                              get_roi_values_acqs
# =============================================================================
# this function creates an excel sheet of transmission values by taking ROI values
def get_roi_values_acqs (dictionary, rois_dict, spectra_file, save_path ='', binning = 1, flight_path = 1, start_slice = 0, end_slice='', name_xlsx = 'Transmission_values.xlsx', save_results = False, **kwargs):
    
    import numpy as np
    import pandas as pd
    
    Values = pd.DataFrame()
    table_wvl = pd.DataFrame()
    
    for roi_name, rois in rois_dict.items():
            # get the real name of the folder connected with the regions of interest
        roi_name  = roi_name.split('ROIs_')[1]
        
            # prepare the dictionary and the table to include the results
        subfolder = dictionary.get(roi_name)
        
        for acq_num, folder_img in enumerate(subfolder):
            
            results_vec = np.zeros([len(folder_img), len(rois)])
            
            for ndx, img in enumerate (folder_img):
                
                for idx, roi_val in enumerate(rois):
                    
                    results_vec[ndx,idx] = np.nanmean(crop_img(img, roi_val)[0])
            
            for k in range(results_vec.shape[1]):
                Values['Values_' + roi_name + '_roi_' + str(k+1) + '_acq' + str(acq_num)] = results_vec[:,k]
                
        # Reads the spectra, creates the table and calculate the equivalent wavelengths in Angstroms
    table_spectra = pd.read_csv(spectra_file,header=None, usecols=[0], sep='\t', names=['Arrival Time'])
    table_wvl["Wavelength [Å]"] = (3956.034/(flight_path/table_spectra["Arrival Time"]))
    
        #if the transmission results were sliced and/or binned, this will take it into account and calculate the new table by the binning weight (1 is no binning)
    if end_slice == '':        
        end_slice= len(table_wvl)
        
    table_wvl = table_wvl.groupby(np.arange(len(table_wvl))//binning).mean()
    table_wvl = table_wvl [start_slice:end_slice]
        
        # since we modify the indexes in the dataframe (binning and/or slicing) we must reset the index
    table_wvl = table_wvl.reset_index(drop = True)
    
        # add the results obtained from the transmission in the ROIs selcted
    table_val_rois = pd.concat([table_wvl, Values], axis =1)
        
        # Send to the results to the directory from which you extracted the transmission images
    if save_results:
        table_val_rois.to_excel(save_path + '/' + name_xlsx)
         
    return table_val_rois


# =============================================================================
#                              calc_tot_conc_compound
# =============================================================================
def calc_tot_conc_compound (compound_composition_dict, molecular_weights_data,**kwargs):
    avogadro = 6.02214076e23
    atoms = [key for key in compound_composition_dict.get('composition').keys()]
    number_atoms = [key for key in compound_composition_dict.get('composition').values()]
        # calculate the molecular weight with the number of atoms and their respective atomic weight
    tot_weight = 0
    for atom, number in zip (atoms, number_atoms):
        tot_weight += molecular_weights_data.iloc[0][atom]*number
        
        # calculate the total concentration 
    return (compound_composition_dict.get('density')/tot_weight)*avogadro



# =============================================================================
#                              calc_atom_conc_4_cs
# =============================================================================
def calc_atom_conc_4_cs (compound_composition_dict, list_atom_references, compound_conc, vol_fraction, target_atom, **kwargs):

    new_references = list_atom_references.copy()
    
    for atom in list(new_references):
        
        if atom not in compound_composition_dict.keys():
            del new_references[atom] 

        # calculate the cross sections and the concentration per atom in the compound and sum the values. This is done per atom in the compound
    atom_conc_cs_table = []
    conc_target_atom = []
    
    for atom_cs in list(new_references):
        
        if atom_cs == target_atom:
            conc_target_atom.append(compound_composition_dict[atom_cs]*compound_conc*vol_fraction)
        else:
            atom_conc_cs_table.append(list(new_references[atom_cs]*compound_composition_dict[atom_cs]*compound_conc*vol_fraction))
            
        #give the dataframe with the calculated concentration and cross section per atom in a compound
    atom_conc_cs_table=list(sum(map(np.array, atom_conc_cs_table)))
    return atom_conc_cs_table, conc_target_atom



# =============================================================================
#                       dataframe_to_savgol
# =============================================================================
def dataframe_to_savgol(data, window, order):
    '''
    Savitzky-Golay Filter
    window must be odd and greater than order
    '''
    
    from scipy.signal import savgol_filter
    
    data_smooth = pd.DataFrame()
    
    for column in data:
        arr = np.array(data[column].iloc[:])
        
        arr_smooth = savgol_filter(arr, window, order)
        
        data_smooth [column] = arr_smooth
        
    return data_smooth




# =============================================================================
#                       get_CS_from_trans
# =============================================================================
def get_CS_from_trans (transmission_values_tab, compounds_dict, requested_cs, **kwargs):
    
        # import libraries
    import numpy as np
    import pandas as pd
    import collections, functools, operator
    
    barns = 1e+24 # because we decided to divide instead of multiply but 1 barn = 1E-24cm^2
    avogadro = 6.02214076e23
        # final results table
    cs_result_tab = pd.DataFrame()
    cs_result_tab["Wavelength [Å]"] = transmission_values_tab["Wavelength [Å]"]
    
        # get the current working directory
    current_dir = os.path.dirname(os.path.realpath(__file__))   
        # get the reference data for wavelength and cross sections
    H_CS = pd.read_csv(current_dir+ r'\Ref_cs\H.txt', usecols=[1,2], sep='\t', names=['Wavelength [Å]', 'CS [barns]'], header=None, skiprows=1)
    H_ref_cs = H_CS.sort_values('Wavelength [Å]')
    O_CS = pd.read_csv(current_dir+ r'\Ref_cs\O.txt', usecols=[1,2], sep='\t', names=['Wavelength [Å]', 'CS [barns]'], header=None, skiprows=1)
    O_ref_cs = O_CS.sort_values('Wavelength [Å]')
    C_CS = pd.read_csv(current_dir+ r'\Ref_cs\C.txt', usecols=[1,2], sep='\t', names=['Wavelength [Å]', 'CS [barns]'], header=None, skiprows=1)
    C_ref_cs = C_CS.sort_values('Wavelength [Å]')
    LI_CS = pd.read_csv(current_dir+ r'\Ref_cs\Li_nat.txt', usecols=[1,2], sep='\t', names=['Wavelength [Å]', 'CS [barns]'], header=None, skiprows=1)
    LI_ref_cs = LI_CS.sort_values('Wavelength [Å]')
    P_CS = pd.read_csv(current_dir+ r'\Ref_cs\P.txt', usecols=[1,2], sep='\t', names=['Wavelength [Å]', 'CS [barns]'], header=None, skiprows=1)
    P_ref_cs = P_CS.sort_values('Wavelength [Å]')
    F_CS = pd.read_csv(current_dir+ r'\Ref_cs\F.txt', usecols=[1,2], sep='\t', names=['Wavelength [Å]', 'CS [barns]'], header=None, skiprows=1)
    F_ref_cs = F_CS.sort_values('Wavelength [Å]')
    molecular_weights_data = pd.read_csv(current_dir+'\Ref_cs\mol_weights.txt', sep='\t')

    
        # firts position is first ROI... Read the compound vector 
    for column, compound in zip(transmission_values_tab.loc[:, transmission_values_tab.columns != 'Wavelength [Å]'], compounds_dict):
            # out of the compounds, read the composition
        
        if compound.get('molecules'):
            partial_concentration = []
            total_atoms = []
            solvent_dict={}
            for indx, molecule in enumerate(compound.get('molecules')):
                
                if type(molecule) == dict:
                    total_atoms.append([key for key in molecule.get('composition').keys()])
                    solvent_dict[molecule.get('abbv')] = solvent_dict.get(molecule.get('abbv'), calc_tot_conc_compound (molecule, molecular_weights_data))
                    
                    atoms = [key for key in molecule.get('composition').keys()]
                    number_atoms = [key for key in molecule.get('composition').values()]
                    # calculate the molecular weight with the number of atoms and their respective atomic weight
                    tot_weight = 0
                    for atom, number in zip (atoms, number_atoms):
                        tot_weight += molecular_weights_data.iloc[0][atom]*number
                
                    # calculate the total concentration 
                    partial_concentration.append(((molecule.get('density')/tot_weight)*avogadro)*compound.get('molecules')[indx+1])

            tot_concentration = sum(partial_concentration)
            
            atoms = [key for key in dict(functools.reduce(operator.add, map(collections.Counter, total_atoms)))]
            
                # cross section references table for the selected compound
            cs_references_tab = pd.DataFrame()
            cs_references_tab["Wavelength [Å]"] = transmission_values_tab["Wavelength [Å]"]
            
                # generate the table of reference cross section with the required atoms
            for  atom in atoms:
                name_library = atom + '_ref_cs'
                cs_atom_lib = eval(name_library)
                cs_references_tab[atom] = [np.interp (wvl, list(cs_atom_lib["Wavelength [Å]"]), list(cs_atom_lib["CS [barns]"]))/barns for wvl in list(cs_references_tab["Wavelength [Å]"])]
        
            for cs_req in requested_cs:
                
        #THIS PART IS FOR CALCULATIONG THE TOTAL CROSS_SECTIONS
                cs_req = cs_req.split(" ", 1)[0].upper()
                if cs_req == 'TOTAL' :
                    # calculate the total cross sections
                    new_col_name = column.split('_')[1:]
                    cs_result_tab['CS_tot_'+compound.get('abbv')+ '_'+ '_'.join(new_col_name)] = (-np.log(transmission_values_tab[column])/(compound.get('thickness')*tot_concentration))*barns

        # THIS PART IS FOR CALCULATIONG THE H CROSS_SECTIONS
                else:
                    
                    target_atom = cs_req
                    conc_cs_ref_tab = pd.DataFrame()
                    conc_target_atom = []
                    for i, pure_solvent in enumerate(compound.get('molecules')):
                        
                        if type(pure_solvent) == dict:
                            conc_cs_ref_tab [pure_solvent['abbv']], conc_target_atom_compound  = calc_atom_conc_4_cs (pure_solvent.get('composition'), cs_references_tab, solvent_dict[pure_solvent['abbv']], compound.get('molecules')[i+1], target_atom = target_atom)
                            conc_target_atom.extend(conc_target_atom_compound)
                            
                    conc_cs_ref_tab = conc_cs_ref_tab.sum(axis=1)
                    conc_target_atom = sum(conc_target_atom)

                        # calculate the other atom cross sections according to their wavelength 
                    new_col_name = column.split('_')[1:]
                    cs_result_tab['CS_'+target_atom+'_'+compound.get('abbv')+ '_'+ '_'.join(new_col_name)] = (((-np.log(transmission_values_tab[column])/compound.get('thickness'))-conc_cs_ref_tab)/conc_target_atom)*barns

        else:
            tot_number_atoms = compound.get('composition')
            atoms = [key for key in tot_number_atoms.keys()]
            number_atoms = [key for key in tot_number_atoms.values()]
                # calculate the molecular weight with the number of atoms and their respective atomic weight
            tot_weight = 0
            for atom, number in zip (atoms, number_atoms):
                tot_weight += molecular_weights_data.iloc[0][atom]*number
                
                # calculate the total concentration 
            tot_concentration = (compound.get('density')/tot_weight)*avogadro
            
            
                # cross section references table for the selected compound
            cs_references_tab = pd.DataFrame()
            cs_references_tab["Wavelength [Å]"] = transmission_values_tab["Wavelength [Å]"]
            
                # generate the table of reference cross section with the required atoms
            for  atom in atoms:
                name_library = atom + '_ref_cs'
                cs_atom_lib = eval(name_library)
                cs_references_tab[atom] = [np.interp (wvl, list(cs_atom_lib["Wavelength [Å]"]), list(cs_atom_lib["CS [barns]"]))/barns for wvl in list(cs_references_tab["Wavelength [Å]"])]
            
    
            
        #THIS PART IS FOR CALCULATIONG THE TOTAL CROSS_SECTIONS
            if 'total cs'  in requested_cs:
                # calculate the total cross sections
                new_col_name = column.split('_')[1:]
                cs_result_tab['CS_tot_'+compound.get('abbv')+ '_'+ '_'.join(new_col_name)] = (-np.log(transmission_values_tab[column])/(compound.get('thickness')*tot_concentration))*barns
    
        # THIS PART IS FOR CALCULATIONG THE H CROSS_SECTIONS
            if 'h cs'  in requested_cs:
                
                if 'H' in atoms:
                        # remove the target atom and leave the remaining for calculation
                    new_references = cs_references_tab.copy()
                    del new_references["H"]
                    del new_references["Wavelength [Å]"]
                    
                        # calculate the cross sections and the concentration per atom in the compound and sum the values. This is done per atom in the compound
                    atom_conc_cs = []
                    for atom_cs in list(new_references):
                        atom_conc_cs.append(list(new_references[atom_cs]*compound.get ('composition')[atom_cs]*tot_concentration))
                    new_references['CS_n_conc']=sum(map(np.array, atom_conc_cs))
                    
                    # calculate the other atom cross sections according to their wavelength 
                    new_col_name = column.split('_')[1:]
                    cs_result_tab['CS_H_'+compound.get('abbv')+ '_'+ '_'.join(new_col_name)] = (((-np.log(transmission_values_tab[column])/compound.get('thickness'))-(new_references['CS_n_conc']))/(compound.get ('composition')['H']*tot_concentration))*barns
                else:
                    print('No H found in this molecule. Please revise your composition tree')
                
            
        # generate a statement to be inserted in the jupyter notebook
    return cs_result_tab



# =============================================================================
#                       prepare_intensity_data
# =============================================================================
def prepare_trans_data(data_imgs, data_ref = None, data_output = '', compounds_dict = [], **kwargs):
    # this code considers that the first column is the wavelength
    
    data_wvl = data_imgs.iloc[:,0]
    
    if data_ref is not None:
        table_trans = data_imgs.iloc[:, 1:].divide(data_ref.iloc[:, 1:], axis = 'rows')  #first column is wavelength

        
    else: # iloc[rows, column] [:,1:]: all rows, from column 1 and on
        print('Data_imgs variable taken as transmission images')
        table_trans = data_imgs.iloc[:, 1:] #first column is wavelength
        
    if data_output == '':
        return print ('Output instructions needed')
    
    if data_output == 'transmission':
        table_trans.columns = table_trans.columns.str.replace("Values_", "Transmission_")
        data_result = pd.concat([data_wvl, table_trans], axis = 1)
        return data_result
        
    if data_output == 'optical density':
        table_trans.columns = table_trans.columns.str.replace("Values_", "Opt Den_")
        data_opt_den = -np.log(table_trans)
        data_result = pd.concat([data_wvl, data_opt_den], axis = 1)
        return data_result
    
    if data_output == 'total cs':
        data_trans = pd.concat([data_wvl, table_trans], axis = 1)
        data_total_cs = get_CS_from_trans (data_trans, compounds_dict, requested_cs = [data_output])
        #data_result = pd.concat([data_wvl, data_total_cs], axis = 1)
        return data_total_cs
    
    if data_output == 'h cs':
        data_trans = pd.concat([data_wvl, table_trans], axis = 1)
        data_h_cs = get_CS_from_trans (data_trans, compounds_dict, requested_cs = [data_output])
        #data_result = pd.concat([data_wvl, data_h_cs], axis = 1)
        return data_h_cs



# =============================================================================
#                       normalize_to_PE
# =============================================================================
def normalize_to_PE (dataFrame, name_wvl = 'Wavelength [Å]'):
    
    PE_cs = [ 31.28,  33.05,  35.04,  36.97,  39.04,  41.07,  43.01,  44.86, 46.49,  48.11,  49.55,  51.25,  52.91,  54.29,  55.56,  56.4 ,
            57.65,  59.05,  60.28,  61.22,  62.17,  63.43,  64.25,  65.21, 65.98,  66.92,  67.67,  68.72,  69.46,  70.25,  71.07,  71.86,
            72.58,  73.53,  74.25,  75.13,  75.8 ,  76.62,  77.34,  78.08, 78.74,  79.37,  79.94,  80.77,  81.28,  81.98,  82.56,  83.14,
            83.88,  84.29,  84.89,  85.35,  85.68,  86.1 ,  86.5 ,  87.04, 87.39,  87.97,  88.31,  88.74,  89.26,  89.68,  90.11,  90.57,
            90.84,  91.36,  91.67,  92.07,  92.26,  92.74,  93.08,  93.77, 93.97,  94.5 ,  94.94,  95.11,  95.49,  95.97,  96.17,  96.87,
            97.11,  97.45,  97.83,  98.38,  98.63,  98.73,  99.23,  99.79, 100.02, 100.24, 100.77, 102.57, 103.42, 104.8 , 106.4 , 106.89,
           108.58, 108.85, 109.24, 109.27, 110.24, 111.12, 111.88, 113.03]
    
    wvl = [0.76, 0.82, 0.88, 0.94, 1.  , 1.05, 1.11, 1.17, 1.23, 1.29, 1.34, 1.41, 1.48, 1.54, 1.6 , 1.66, 1.71, 1.78, 1.85, 1.91, 1.97, 2.05,
           2.1 , 2.17, 2.24, 2.31, 2.38, 2.46, 2.53, 2.6 , 2.68, 2.75, 2.83, 2.9 , 2.97, 3.06, 3.12, 3.2 , 3.26, 3.34, 3.4 , 3.48, 3.54, 3.63,
           3.68, 3.75, 3.82, 3.88, 3.95, 4.02, 4.08, 4.15, 4.22, 4.28, 4.34, 4.41, 4.47, 4.53, 4.59, 4.65, 4.73, 4.79, 4.84, 4.9 , 4.96, 5.04,
           5.1 , 5.16, 5.22, 5.27, 5.33, 5.42, 5.47, 5.53, 5.59, 5.65, 5.71, 5.76, 5.82, 5.9 , 5.96, 6.02, 6.08, 6.14, 6.19, 6.25, 6.31, 6.37,
           6.42, 6.48, 6.54, 6.75, 6.98, 7.22, 7.47, 7.7 , 7.93, 8.16, 8.42, 8.66, 8.89, 9.12, 9.35, 9.58]
    
    data_wvl = dataFrame.iloc[:,0]
    
    new_x = list(dataFrame['Wavelength [Å]'])
    new_y_PE = pd.DataFrame({'PE_vals': np.interp(new_x, wvl, PE_cs)})
    
        # get all columns except the one that contains the wavelemgth information
    df_data = dataFrame.loc[:, dataFrame.columns != 'Wavelength [Å]']
    
    df_PE_norm = df_data.iloc[:,:].divide(new_y_PE.iloc[:,0], axis = 'rows')
    
    df_result = pd.concat([data_wvl, df_PE_norm], axis = 1)
    
    return df_result



# =============================================================================
#                       normalize_3A
# =============================================================================
def normalize_3A (dataFrame, name_wvl = 'Wavelength [Å]'):
   
    result_data = pd.DataFrame()
    data_wvl = dataFrame[name_wvl]
    
    idx = dataFrame[name_wvl].sub(3).abs().idxmin()
    
        # get all columns except the one that contains the wavelemgth information
    data = dataFrame.loc[:, dataFrame.columns != name_wvl]
    
        # divide all the dataframe by the sum of the rows in the range
    for column in data:
        data_sum = data[column].loc[idx]
        result_data[column] = data[column]/data_sum
        
    df_result = pd.concat([data_wvl, result_data], axis = 1)
    
    return df_result



# =============================================================================
#                       normalize_to_range
# =============================================================================
def normalize_to_range (dataFrame, idx_range = [3,4] , name_wvl = 'Wavelength [Å]'):
    
    result_data = pd.DataFrame()
    data_wvl = dataFrame[name_wvl]
    
    idx1 = dataFrame[name_wvl].sub(idx_range[0]).abs().idxmin()
    idx2 = dataFrame[name_wvl].sub(idx_range[1]).abs().idxmin()
    
        # get all columns except the one that contains the wavelemgth information
    data = dataFrame.loc[:, dataFrame.columns != name_wvl]
    
        # divide all the dataframe by the sum of the rows in the range
    for column in data:
        data_sum = data[column].loc[idx1:idx2].mean()
        result_data[column] = data[column]/data_sum
        
    df_result = pd.concat([data_wvl, result_data], axis = 1)
    
    return df_result










LP30_ref =[ 33.80477597, 35.73791922,  37.72521368,  39.95340843, 42.16605503, 44.07781613,  45.96039016,  47.77901147, 49.18895628,  50.80134311,  52.009891  ,  53.52880977,
        55.08178536, 56.47078696,  57.59346782,  58.31287695, 59.49599516, 60.79720576,  61.92608727,  62.7926954 , 63.61617686,  64.83462385,  65.38920248,  66.28195128,
        67.16844709, 67.94284104,  68.81515426,  69.88220773, 70.7742071 , 71.5636553 ,  72.50728311,  73.46616097, 74.29257551,  75.39238692,  76.1236388 ,  77.26894749,
        77.97217813, 78.97257215,  79.76871987,  80.66740243, 81.38458125, 82.13640596,  82.83757925,  83.75585617, 84.26575744,  85.00727745,  85.64709704,  86.1287295 ,
        86.97071806, 87.58109213,  88.23510478,  88.9899521 , 89.87709829, 90.47398779,  91.12315429,  91.93039854, 92.65729556,  93.5136624 ,  93.98582853,  94.70008405,
        95.57593433, 96.07675553,  96.89452027,  97.50926323, 98.06774922, 99.11568308,  99.65931389, 100.253475  , 100.8566091 , 101.5854221 , 102.0623321 , 103.019035  ,
       103.6766484, 104.2022832 , 104.8046995 , 105.3464915 , 105.9071292, 106.7231752 , 107.1999307 , 108.0909888 , 108.7729693 , 109.2092783 , 109.8513938 , 110.7638734 ,
       111.0330754, 111.7627275 , 112.3960615 , 112.8140476 , 113.2841871, 113.9135051 , 114.5385699 , 116.76 , 118.67 , 120.59 , 123.02 , 124.74 , 126.55, 128.22, 130.1, 
       132.15, 132.92, 134.6, 136.1, 137.83]


LP30_norm = [1.08056031, 1.08147146, 1.07651523, 1.08080405, 1.08015091, 1.07334941, 1.06847865, 1.065159  , 1.02379686, 1.02168152, 1.01566566, 1.01048611, 1.00730208, 1.00632796, 1.00305073,
       1.00028139, 0.99859581, 0.99610831, 0.99391899, 0.99237784, 0.99013515, 0.98897462, 0.98476794, 0.98345998, 0.98502651, 0.98228317, 0.98386744, 0.98395521, 0.98586846, 0.98571141,
       0.98708317, 0.98917747, 0.99033202, 0.99202722, 0.99200873, 0.99506594, 0.99524612, 0.99726358, 0.99794978, 0.99958348, 1.00010187, 1.00133381, 1.00259312, 1.00334714, 1.00304385,
       1.00333976, 1.00368625, 1.00228701, 1.00314956, 1.00530624, 1.00563366, 1.00884774, 1.01490788, 1.01674767, 1.01922223, 1.02191465, 1.02590801, 1.02856858, 1.02971339, 1.03252669,
       1.03602673, 1.03655492, 1.04038671, 1.04164937, 1.04453475, 1.04973518, 1.05184656, 1.0535542 , 1.05773103, 1.05981695, 1.06096289, 1.06294966, 1.06755062, 1.06687413, 1.06812373,
       1.07166099, 1.07313924, 1.07593882, 1.07851186, 1.07964732, 1.08376367, 1.0842748 , 1.08649997, 1.08940134, 1.08920436, 1.09527664, 1.09595727, 1.09380512, 1.09583173, 1.09951258,
       1.09973016, 1.10146677, 1.1101909 , 1.11335958, 1.11866955, 1.12909123, 1.12766842, 1.13980245, 1.15228956, 1.17020801, 1.1666521 , 1.17200912, 1.17698897, 1.1798877 ]






