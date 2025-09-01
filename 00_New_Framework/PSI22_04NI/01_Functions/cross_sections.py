# -*- coding: utf-8 -*-
"""
Created on Mon Aug  8 10:35:05 2022

@author: carreon_r
"""
import os, glob, time
import pandas as pd
from img_functions import *
from proc_functions import *
from dict_functions import *


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

def get_roi_values (dictionary, rois_dict, spectra_file, save_path ='', binning = 1, flight_path = 1, start_slice = '', end_slice='', name_xlsx = 'Transmission_values.xlsx', save_results = False, **kwargs):
    
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
#                       get_cross_sections
# =============================================================================

def get_cross_sections (transmission_values_tab, compounds_dict, requested_cs , dst_dir = '' , save_table = False, name_xlsx = 'CS_results.xlsx', **kwargs):
    
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
                cs_req = cs_req.split("_", 1)[0].upper()
                if cs_req == 'TOTAL' :
                    # calculate the total cross sections
                    #cs_result_tab['CS_tot_'+compound.get('abbv')] = (-np.log(transmission_values_tab[column]/casing_data.iloc[:, 1])/(compound.get('thickness')*tot_concentration))*barns
                    cs_result_tab['CS_tot_'+compound.get('abbv')+ '_'+ column] = (-np.log(transmission_values_tab[column])/(compound.get('thickness')*tot_concentration))*barns

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
                    #cs_result_tab['CS_'+target_atom+'_in_'+compound.get('abbv')] = ((((-np.log(transmission_values_tab[column]/casing_data.iloc[:, 1]))/compound.get('thickness'))-(conc_cs_ref_tab))/(conc_target_atom))*barns
                    cs_result_tab['CS_'+target_atom+'_in_'+compound.get('abbv')+ '_'+ column] = (((-np.log(transmission_values_tab[column])/compound.get('thickness'))-conc_cs_ref_tab)/conc_target_atom)*barns

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
            if 'total_cs'  in requested_cs:
                # calculate the total cross sections
                #cs_result_tab['CS_tot_'+compound.get('abbv')] = (-np.log(transmission_values_tab[column]/casing_data.iloc[:, 1])/(compound.get('thickness')*tot_concentration))*barns
                cs_result_tab['CS_tot_'+compound.get('abbv')+ '_'+ column] = (-np.log(transmission_values_tab[column])/(compound.get('thickness')*tot_concentration))*barns
    
        # THIS PART IS FOR CALCULATIONG THE H CROSS_SECTIONS
            if 'h_cs'  in requested_cs:
                
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
                    #cs_result_tab['CS_H_in_'+compound.get('abbv')] = ((((-np.log(transmission_values_tab[column]/casing_data.iloc[:, 1]))/compound.get('thickness'))-(new_references['CS_n_conc']))/(compound.get ('composition')['H']*tot_concentration))*barns
                    cs_result_tab['CS_H_in_'+compound.get('abbv')+ '_'+ column] = (((-np.log(transmission_values_tab[column])/compound.get('thickness'))-(new_references['CS_n_conc']))/(compound.get ('composition')['H']*tot_concentration))*barns
                else:
                    print('No H found in this molecule. Please revise your composition tree')
                    
                    
                    
        # THIS PART IS FOR CALCULATIONG THE O CROSS_SECTIONS
            if 'o_cs'  in requested_cs:
                
                if 'O' in atoms:
                        # remove the target atom and leave the remaining for calculation
                    new_references = cs_references_tab.copy()
                    del new_references["O"]
                    del new_references["Wavelength [Å]"]
                    
                        # calculate the cross sections and the concentration per atom in the compound and sum the values. This is done per atom in the compound
                    atom_conc_cs = []
                    for atom_cs in list(new_references):
                        atom_conc_cs.append(list(new_references[atom_cs]*compound.get ('composition')[atom_cs]*tot_concentration))
                    new_references['CS_n_conc']=sum(map(np.array, atom_conc_cs))
                    
                    # calculate the other atom cross sections according to their wavelength 
                    #cs_result_tab['CS_O_in_'+compound.get('abbv')] = ((((-np.log(transmission_values_tab[column]/casing_data.iloc[:, 1]))/compound.get('thickness'))-(new_references['CS_n_conc']))/(compound.get ('composition')['O']*tot_concentration))*barns
                    cs_result_tab['CS_O_in_'+compound.get('abbv')+ '_'+ column] = (((-np.log(transmission_values_tab[column])/compound.get('thickness'))-(new_references['CS_n_conc']))/(compound.get ('composition')['O']*tot_concentration))*barns
                else:
                    print('No O found in this molecule. Please revise your composition tree')
                    
        # THIS PART IS FOR CALCULATIONG THE C CROSS_SECTIONS
            if 'c_cs'  in requested_cs:
                
                if 'C' in atoms:
                        # remove the target atom and leave the remaining for calculation
                    new_references = cs_references_tab.copy()
                    del new_references["C"]
                    del new_references["Wavelength [Å]"]
                    
                        # calculate the cross sections and the concentration per atom in the compound and sum the values. This is done per atom in the compound
                    atom_conc_cs = []
                    for atom_cs in list(new_references):
                        atom_conc_cs.append(list(new_references[atom_cs]*compound.get ('composition')[atom_cs]*tot_concentration))
                    new_references['CS_n_conc']=sum(map(np.array, atom_conc_cs))
                    
                    # calculate the other atom cross sections according to their wavelength 
                    #cs_result_tab['CS_C_in_'+compound.get('abbv')] = ((((-np.log(transmission_values_tab[column]/casing_data.iloc[:, 1]))/compound.get('thickness'))-(new_references['CS_n_conc']))/(compound.get ('composition')['C']*tot_concentration))*barns
                    cs_result_tab['CS_C_in_'+compound.get('abbv')+ '_'+ column] = (((-np.log(transmission_values_tab[column])/compound.get('thickness'))-(new_references['CS_n_conc']))/(compound.get ('composition')['C']*tot_concentration))*barns
                else:
                    print('No C found in this molecule. Please revise your composition tree')
                    
        # THIS PART IS FOR CALCULATIONG THE Li CROSS_SECTIONS
            if 'li_cs'  in requested_cs:
                
                if 'li' in atoms:
                        # remove the target atom and leave the remaining for calculation
                    new_references = cs_references_tab.copy()
                    del new_references["li"]
                    del new_references["Wavelength [Å]"]
                    
                        # calculate the cross sections and the concentration per atom in the compound and sum the values. This is done per atom in the compound
                    atom_conc_cs = []
                    for atom_cs in list(new_references):
                        atom_conc_cs.append(list(new_references[atom_cs]*compound.get ('composition')[atom_cs]*tot_concentration))
                    new_references['CS_n_conc']=sum(map(np.array, atom_conc_cs))
                    
                    # calculate the other atom cross sections according to their wavelength 
                    #cs_result_tab['CS_Li_in_'+compound.get('abbv')] = ((((-np.log(transmission_values_tab[column]/casing_data.iloc[:, 1]))/compound.get('thickness'))-(new_references['CS_n_conc']))/(compound.get ('composition')['Li']*tot_concentration))*barns
                    cs_result_tab['CS_Li_in_'+compound.get('abbv')+ '_'+ column] = (((-np.log(transmission_values_tab[column])/compound.get('thickness'))-(new_references['CS_n_conc']))/(compound.get ('composition')['Li']*tot_concentration))*barns
                else:
                    print('No Li found in this molecule. Please revise your composition tree')
            
    if save_table:
        cs_result_tab.to_excel(dst_dir + '/' + name_xlsx)
        # generate a statement to be inserted in the jupyter notebook
    return cs_result_tab



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




def normalize_3A (dataFrame, name_wvl = 'Wavelength [Å]'):
    
    idx = dataFrame[name_wvl].sub(3).abs().idxmin()
    
        # get all columns except the one that contains the wavelemgth information
    DF_cs = dataFrame.loc[:, dataFrame.columns != name_wvl]
    
        # # get the row losest to 3A except the one that contains the wavelemgth information
    row = dataFrame.loc[[idx], dataFrame.columns != name_wvl]
    
        # divide all the dataframe by the row containing the 3A 
    DF_norm = DF_cs.div(row.iloc[0])
    DF_norm.insert(0, name_wvl,dataFrame[name_wvl])
    
    return DF_norm
    
    
def normalize_3A_PE (dataFrame, PE_list_vals, name_wvl = 'Wavelength [Å]'):
    
    PE_DF = pd.DataFrame (PE_list_vals, columns = ['PE_norm'])
    
        # get all columns except the one that contains the wavelemgth information
    DF_cs = dataFrame.loc[:, dataFrame.columns != name_wvl]
    
    DF_norm = DF_cs.iloc[:,:].div(PE_DF.PE_norm, axis=0)
    DF_norm.insert(0, name_wvl, dataFrame[name_wvl])
    
    return DF_norm



def divide_DF (num_df, den_df, name_wvl = 'Wavelength [Å]'):
    
        # this will remove the first column (in the case of cross-section, the wavelength)
    num_df_raw = num_df.iloc[: , 1:]
    den_df_raw = den_df.iloc[: , 1:]
    
    DF_div = num_df_raw.iloc[:,:].div(den_df_raw, axis=0)
    DF_div.insert(0, name_wvl, num_df[name_wvl])
    
    return DF_div


#IMPORTANT: if you want to overwrite or create a new file, mode is 'w' (write). Otherwise, 'a' is for appending
def save_DF (path, dataframe, df_name = 'my_df.xlsx', sheet_name = 'new_sheet', mode = 'a', overwrite = False, **kwargs):
    
    import os
    import pandas as pd
    
        # compute the destination file name
    dst_name = os.path.join(path, df_name)
    
        # get the destination directory
    dst_name_dir, _ = os.path.split(dst_name)
    
        # and create this destination directory if it does not exist
    if not os.path.exists(dst_name_dir):
        os.makedirs(os.path.join(dst_name_dir,''))
    
    if os.path.isfile(dst_name) and mode == 'w' and overwrite == False:
        print('WARNING... Trying to overwrite an existing file')
        print('     If you want to overwrite, change overwrite = True.')
        print('     If you want to append to an existing file, change mode = a.')
        
        return
    
    else:
            
        writer = pd.ExcelWriter(dst_name, engine =  'openpyxl', mode = mode)
        
        if 'xlsx' in df_name:
            
            dataframe.to_excel(writer, sheet_name =sheet_name)
            
        elif 'csv' in df_name:
            dataframe.to_csv(writer, sheet_name =sheet_name)
        
        else:
            print('df_name must contain an extension. Either .xlsx or .csv')

        return writer.save()



