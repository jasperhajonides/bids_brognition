#!/usr/bin/env python
import os
import json
import os.path as op
import shutil

from mne_bids.utils import _write_tsv, _write_json
from collections import OrderedDict
from mne_bids.tsv_handler import (_from_tsv, _contains_row,
                                  _combine_rows)
from mne_bids.path import _mkdir_p
from mne_bids import BIDSPath
from mne_bids.config import (ALLOWED_DATATYPE_EXTENSIONS, REFERENCES,
                             CONVERT_FORMATS)

from mne_bids.write import _readme, _participants_json, make_dataset_description
from mne.utils import logger
                       
REFERENCES['beh'] = 'Jasper Hajonides 2021, edited from mne_bids'
ALLOWED_DATATYPE_EXTENSIONS['beh'] = ['.tsv','.csv','.txt']

def EEG_json_details(filename):
    """Add details for json file accompanying eeg data"""
    f = open(filename)
     
    # returns JSON object as
    # a dictionary
    data = json.load(f)
    data['TaskName'] = 'FeatObj'
    data['Manufacturer'] = 'Synamps amplifier, Compumedics NeuroScan, EasyCap electrodes'
    data['PowerLineFrequency'] = 50
    data['InstitutionName'] = 'OHBA, University of Oxford'
    data['EEGPlacementScheme'] = '10-20'
    data['SoftwareFilters'] = {"Anti-aliasing filter": {"half-amplitude cutoff (Hz)": 400}}
    data['EEGReference'] = 'RM'
    data['EEGChannelCount'] = 61
    data['EOGChannelCount'] = 2
    data['MiscChannelCount'] = 1
    print(data)
    
    with open(filename, 'w') as ff:
        json.dump(data, ff,sort_keys=False, indent=4)
        
              
def beh_json_details(filename):
    """Add details for json file accompanying behavioural data"""
     
    # returns JSON object as
    # a dictionary
    data = {}
    data["Error"] = 'Circular difference between the participants response and the correct value (in radians). Note that orientations are mapped between 0-pi and colours are also in 0-pi space.'
    data['feat_report'] = 'Feature that is reported in that trial, 1=orientation, 2= colour.'
    data['side_report'] = 'Side that is probed, 1=left, 2=right.'
    data['retrocue'] = 'Information in retrocue, 1=informative, 2=neutral retrocue.'
    data['target'] = 'Correct response value for that trial (0-pi).'
    data['distractor_type'] = 'Feature dimension of the distractor, 1=orientation, 2=colour'
    data['distractor_radian'] = 'Feature value of the distractor (0-pi) where all colour values are also mapped on a 0-pi range.'
    data['left_orientation'] = 'Orientation of the left gabor grating presented at the start of the trial.'
    data['right_orientation'] = 'Orientation of the right gabor grating presented at the start of the trial.'
    data['left_colour'] = 'Colour of the left gabor grating presented at the start of the trial. Mapped on a 0-pi range.'
    data['right_colour'] = 'Colour of the right gabor grating presented at the start of the trial. Mapped on a 0-pi range.'
    data['run'] = 'Run that the trial is part of.'
    data['response'] = 'Final probe orientation when participant confirmed their response (0-pi)'
    data['RT'] = 'Time between the presentation of the probe and the first button press of the participant.'
    data['trial_nr'] = 'Trial count.'  
    print(data)
    
    _write_json(filename, data, overwrite=True)
        
        

def _participants_tsv(raw, subject_id, fname, overwrite=False,
                      verbose=True):
    """Create a participants.tsv file and save it.

    This will append any new participant data to the current list if it
    exists. Otherwise a new file will be created with the provided information.

    Parameters
    ----------
    raw : mne.io.Raw
        The data as MNE-Python Raw object.
    subject_id : str
        The subject name in BIDS compatible format ('01', '02', etc.)
    fname : str | mne_bids.BIDSPath
        Filename to save the participants.tsv to.
    overwrite : bool
        Whether to overwrite the existing file.
        Defaults to False.
        If there is already data for the given `subject_id` and overwrite is
        False, an error will be raised.
    verbose : bool
        Set verbose output to True or False.

    """
    subject_id = 'sub-' + subject_id
    data = OrderedDict(participant_id=[subject_id])

    if "age" in raw:
        subject_age = raw['age']
    else:
        subject_age = "n/a"
    if "sex" in raw:
        sex = raw['sex']
    else:
        sex='n/a'    
    if "hand" in raw:
        hand=raw['hand']
    else:
        hand='n/a'
   


    data.update({'age': [subject_age], 'sex': [sex], 'hand': [hand]})

    if os.path.exists(fname):
        orig_data = _from_tsv(fname)
        # whether the new data exists identically in the previous data
        exact_included = _contains_row(orig_data,
                                       {'participant_id': subject_id,
                                        'age': subject_age,
                                        'sex': sex,
                                        'hand': hand})
        # whether the subject id is in the previous data
        sid_included = subject_id in orig_data['participant_id']
        # if the subject data provided is different to the currently existing
        # data and overwrite is not True raise an error
        if (sid_included and not exact_included) and not overwrite:
            raise FileExistsError(f'"{subject_id}" already exists in '  # noqa: E501 F821
                                  f'the participant list. Please set '
                                  f'overwrite to True.')

        # Append any columns the original data did not have
        # that mne-bids is trying to write. This handles
        # the edge case where users write participants data for
        # a subset of `hand`, `age` and `sex`.
        for key in data.keys():
            if key in orig_data:
                continue

            # add 'n/a' if any missing columns
            orig_data[key] = ['n/a'] * len(next(iter(data.values())))

        # Append any additional columns that original data had.
        # Keep the original order of the data by looping over
        # the original OrderedDict keys
        col_name = 'participant_id'
        for key in orig_data.keys():
            if key in data:
                continue

            # add original value for any user-appended columns
            # that were not handled by mne-bids
            p_id = data[col_name][0]
            if p_id in orig_data[col_name]:
                row_idx = orig_data[col_name].index(p_id)
                data[key] = [orig_data[key][row_idx]]

        # otherwise add the new data as new row
        data = _combine_rows(orig_data, data, 'participant_id')

    # overwrite is forced to True as all issues with overwrite == False have
    # been handled by this point
    _write_tsv(fname, data, True, verbose)


def write_raw_bids_beh(raw_fname, bids_path,
                   overwrite=False, verbose=True):
    """Save raw data to a BIDS-compliant folder structure.

    .. warning:: * The original file is simply copied over if the original
                   file format is BIDS-supported for that datatype. Otherwise,
                   this function will convert to a BIDS-supported file format
                   while warning the user. For EEG and iEEG data, conversion
                   will be to BrainVision format; for MEG, conversion will be
                   to FIFF.

                 * ``mne-bids`` will infer the manufacturer information
                   from the file extension. If your file format is non-standard
                   for the manufacturer, please update the manufacturer field
                   in the sidecars manually.

    Parameters
    ----------
    raw_fname : string
        The full path to the raw data file (.csv, .tsv, .txt)
    bids_path : mne_bids.BIDSPath
        The file to write. The `mne_bids.BIDSPath` instance passed here
        **must** have the ``.root`` attribute set. If the ``.datatype``
        attribute is not set, it will be inferred from the recording data type
        found in ``raw``. In case of multiple data types, the ``.datatype``
        attribute must be set.
        Example::

            bids_path = BIDSPath(subject='01', session='01', task='testing',
                                 acquisition='01', run='01', datatype='meg',
                                 root='/data/BIDS')

        This will write the following files in the correct subfolder ``root``::

            sub-01_ses-01_task-testing_acq-01_run-01_meg.fif
            sub-01_ses-01_task-testing_acq-01_run-01_meg.json
            sub-01_ses-01_task-testing_acq-01_run-01_channels.tsv
            sub-01_ses-01_acq-01_coordsystem.json

        and the following one if ``events_data`` is not ``None``::

            sub-01_ses-01_task-testing_acq-01_run-01_events.tsv

        and add a line to the following files::

            participants.tsv
            scans.tsv

        Note that the extension is automatically inferred from the raw
        object.
  
    overwrite : bool
        Whether to overwrite existing files or data in files.
        Defaults to ``False``.

        If ``True``, any existing files with the same BIDS parameters
        will be overwritten with the exception of the ``*_participants.tsv``
        and ``*_scans.tsv`` files. For these files, parts of pre-existing data
        that match the current data will be replaced. For
        ``*_participants.tsv``, specifically, age, sex and hand fields will be
        overwritten, while any manually added fields in ``participants.json``
        and ``participants.tsv`` by a user will be retained.
        If ``False``, no existing data will be overwritten or
        replaced.
    verbose : bool
        If ``True``, this will print a snippet of the sidecar files. Otherwise,
        no content will be printed.

    Returns
    -------
    bids_path : mne_bids.BIDSPath
        The path of the created data file.


    """
  

    if not isinstance(bids_path, BIDSPath):
        raise RuntimeError('"bids_path" must be a BIDSPath object. Please '
                           'instantiate using mne_bids.BIDSPath().')


    # Check if the root is available
    if bids_path.root is None:
        raise ValueError('The root of the "bids_path" must be set. '
                         'Please use `bids_path.update(root="<root>")` '
                         'to set the root of the BIDS folder to read.')


    convert = False  # flag if converting not copying
   

    # Initialize BIDS path
    datatype = bids_path.datatype
    ext = '.tsv'
    bids_path = (bids_path.copy()
                 .update(datatype=datatype, suffix=datatype, extension=ext))

    data_path = bids_path.mkdir().directory

    # create *_scans.tsv
    session_path = BIDSPath(subject=bids_path.subject,
                            session=bids_path.session, root=bids_path.root)

    # For the remaining files, we can use BIDSPath to alter.
    readme_fname = op.join(bids_path.root, 'README')
    participants_tsv_fname = op.join(bids_path.root, 'participants.tsv')
    participants_json_fname = participants_tsv_fname.replace('.tsv',
                                                             '.json')

    sidecar_path = bids_path.copy().update(suffix=bids_path.datatype,
                                           extension='.json')

    

    # save readme file unless it already exists
    # XXX: can include README overwrite in future if using a template API
    # XXX: see https://github.com/mne-tools/mne-bids/issues/551
    _readme(bids_path.datatype, readme_fname, False, verbose)

    # save all participants meta data
    _participants_tsv(raw_fname, bids_path.subject, participants_tsv_fname,
                      overwrite, verbose)
    _participants_json(participants_json_fname, True, verbose)



    # make dataset description and add template data if it does not
    # already exist. Always set overwrite to False here. If users
    # want to edit their dataset_description, they can directly call
    # this function.
    make_dataset_description(bids_path.root, name=" ", overwrite=False,
                             verbose=verbose)

    # create parent directories if needed
    _mkdir_p(os.path.dirname(data_path))

    if os.path.exists(bids_path.fpath):
        if overwrite:
            # Need to load data before removing its source
            if bids_path.fpath.is_dir():
                shutil.rmtree(bids_path.fpath)
            else:
                bids_path.fpath.unlink()
        else:
            raise FileExistsError(
                f'"{bids_path.fpath}" already exists. '  # noqa: F821
                'Please set overwrite to True.')

    # If not already converting for anonymization, we may still need to do it
    # if current format not BIDS compliant
    if not convert:
        convert = ext not in ALLOWED_DATATYPE_EXTENSIONS[bids_path.datatype]

     
   
    if not convert and verbose:
        logger.info(f'Copying data files to {bids_path.fpath.name}')




    #copy file to destination directory.
    shutil.copyfile(raw_fname, bids_path)



    return bids_path

