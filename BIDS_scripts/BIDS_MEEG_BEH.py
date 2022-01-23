#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 24 10:45:51 2021

@author: jasperhvdm
"""

# install MNE_BIDS!!! pip install mne_bids

import sys  
import json
import numpy as np
import pandas as pd
import mne
from mne import Epochs, pick_types, events_from_annotations
from mne_bids import write_raw_bids, BIDSPath, print_dir_tree

sys.path.append('/Users/jasperhvdm/Documents/Scripts/BIDS_scripts/')
from write_manual_bids import *

rootdir = '/Users/jasperhvdm/Documents/DPhil/BIDS/new_project'


#%% file formats
 M/EEG we input .fif files
 behavioural data we input .txt, .csv, .tsv data


#Read .data
raw = mne.io.read_raw_eeglab('/Users/jasperhvdm/Documents/DPhil/BIDS/sourcedata/FeatObj_S04.set')
#Write .fif
raw.save('/Users/jasperhvdm/Documents/DPhil/BIDS/sourcedata/test_epo_04.fif')

####################################################
#%%########## WRITE EEG BIDS ######################
###################################################


raw = mne.io.read_raw_fif('/Users/jasperhvdm/Documents/DPhil/BIDS/sourcedata/test_epo_04.fif', verbose=False)
raw.info['line_freq'] = 50  # Specify power line frequency as required by BIDS.

# add events
events_from_annot, event_dict = mne.events_from_annotations(raw)

bids_path = BIDSPath(subject='02', task='featobj',
                             acquisition='01', datatype='eeg',
                             root=rootdir) # acquisition='01', session='01', run='01'


write_raw_bids(raw, bids_path=bids_path, 
               overwrite=True, 
               allow_preload=False,
               event_id=event_dict,
               events_data=events_from_annot)


# Add EEG info --- Editting JSON file
filename = op.join(bids_path.directory,bids_path.basename+'_eeg.json')
# edit this for your own experiment
EEG_json_details(filename)

####################################################
#%%########## WRITE MEG BIDS ######################
###################################################


# read in .fif
raw = mne.io.read_raw_fif('/Users/jasperhvdm/Documents/DPhil/BIDS/sourcedata/av_task_BL_raw.fif', verbose=False)
raw.info['line_freq'] = 50  # Specify power line frequency as required by BIDS.

# # generate path
bids_path = BIDSPath(subject='02', task='featobj',
                             acquisition='01', datatype='meg',
                             root=rootdir) #session='01', run='01'

write_raw_bids(raw, 
               bids_path=bids_path, 
               overwrite=True, 
               allow_preload=False)

####################################################
#%%########## WRITE BEHAVIOURAL BIDS ######################
###################################################

bids_path = BIDSPath(subject='02', task='featobj',
                             acquisition='01', datatype='beh',
                             root=rootdir) #session='01', run='01'

raw_fname = '/Users/jasperhvdm/Documents/DPhil/BIDS/sourcedata/tsv_subj_S04_data.csv'
write_raw_bids_beh(raw_fname, bids_path,
                   overwrite=True, verbose=True)

# Add behavioural variable info --- Editting JSON file
# edit this for your own experiment
filename = op.join(bids_path.directory,bids_path.basename+'_beh.json')
beh_json_details(filename)

# --- note:
# BIDS validator doesn't like behavioural files because its an imaging data storage tool.
# to prevent errors you should add a .bidsignore.txt file with two lines in there:
#   *beh.json
#   *beh.tsv
# Now it wont throw errors for these files.

####################################################
#%%########## WRITE MRI BIDS ######################
###################################################

# tbd

#%%########## WRITE Dataset description ######################

make_dataset_description(rootdir, 'dataset_description', 
                         data_license='Creative Commons Attribution 4.0 International License.',
                         authors=['Jasper E. Hajonides van der Meulen','Freek van Ede',
                                  'Mark G. Stokes','Anna C. Nobre'], 
                         acknowledgements=None, 
                         how_to_acknowledge='Hajonides, J. E., van Ede, F., Stokes, M. G., & Nobre, A. C. (2020). Comparing the prioritization of items and feature-dimensions in visual working memory. Journal of vision, 20(8), 25-25.',
                         funding=['ACCESS2WM','220020405','ES/S015477/1','MR/J009024/1',
                                  'BB/M010732/1','220020448','104571/Z/14/Z','203139/Z/16/Z'], 
                         references_and_links=None, 
                         doi=None, 
                         dataset_type='raw', 
                         overwrite=True, 
                         verbose=True)

