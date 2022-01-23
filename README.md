# BIDS Formatting
### In short, what is BIDS?
Neuroimaging experiments result in complicated data that can be arranged in many different ways. So far there is no consensus how to organize and share data obtained in neuroimaging experiments. Even two researchers working in the same lab can opt to arrange their data in a different way. Lack of consensus (or a standard) leads to misunderstandings and time wasted on rearranging data or rewriting scripts expecting certain structure. With the Brain Imaging Data Structure (BIDS), we describe a simple and easy to adopt way of organizing neuroimaging and behavioural data.


BIDS uses the following file tree:

![alt text](https://github.com/jasperhajonides/bids_brognition/blob/main/ims/bids_tree.png)

 
Where “*source*” contains the raw data straight from the acquisition computer. This is saved because in cases the file format of the raw data is converted into a more commonly used format.  
The folder “*raw*” contains the BIDS file structure that we will create below.
In the “*derivatives*” folder you can put your (fully) preprocessed files or any other data that has been cleaned up.
Furthermore, you could/should add folders like “*scripts*”, where you put your preprocessing and analysis scripts, “*presentation*”, for your Psychtoolbox/PsychoPy/Presentation/… scripts that you used to display stimuli in your study. And whatever other stuff you'd like to save with it.

If we zoom in some more, we see that every subject folder in the /raw directory adheres to a formatting structure:

![alt text](https://github.com/jasperhajonides/bids_brognition/blob/main/ims/data_types.png)

And every file name also follows a predefined sequence.

![alt text](https://github.com/jasperhajonides/bids_brognition/blob/main/ims/naming_structure.png)

You do not have to worry too much about these as this will all be done for you automatically. It is good to know something about the logic of this structure!!

## Installation of file formatting packages

### tl;dr
run the following command in your terminal to install mne_bids for all dependencies.
`pip install --user -U mne-bids[full]`

### Alternatively installation

First we have to install Conda, which is a widely-used package manager. If you do not have this already (which you likely do?), you can download this here: https://www.anaconda.com/products/individual 

Next we will create an environment which contains all the packages we need for our bids formatting. The reason we create an environment is because we like to have the right versions to run the code:

> mne (>=0.24)
> numpy (>=1.16.0)
> scipy (>=1.2.0, or >=1.5.0 for certain operations with EEGLAB data)
> setuptools (>=46.4.0)

So, we create an environment called “bids_env”, by inserting the following in the terminal:

`conda create –-name=bids_env --channel conda-forge mne`

#### [good to know!]
_We have now created an environment within our terminal. This environment contains its own set of installed packages. Any time you open the terminal, you can activate this environment by typing `conda activate [name_of_enviroment]`_


And you also want to install spyder, jupyter notebook, or any other platform you like to use for python (in case you don’t like to use the terminal like a computer wiz).

`# activate environment
conda activate bids_env
#install spyder
conda install spyder
#install jupyter notebook
conda install -c anaconda jupyter`

Next, we install mne_bids, the package that we use to put the data in the right file format.

first make sure we are in the right environment plus the  

`conda activate bids_env
conda install --channel conda-forge --no-deps mne-bids`


Note that if all of this fails, you can try installing mne via another pathway (https://mne.tools/stable/install/mne_python.html) and mne_bids https://mne.tools/mne-bids/stable/install.html



## Formatting files according to BIDS.

Open the file `BIDS_MEEG_BEH.py` in this repository.
Now that that is out of the way, the fun can begin. This should be relatively straightforward:

0.	Load packages:

```python
import sys  
import json
import numpy as np
import pandas as pd
import mne
from mne import Epochs, pick_types, events_from_annotations
from mne_bids import write_raw_bids, BIDSPath, print_dir_tree

sys.path.append('/Users/jasperhvdm/Documents/Scripts/BIDS_scripts/')
from write_manual_bids import *

#define where you like your new folder to be
rootdir = './new_project'
```

Now we can do the data formatting for behavioural data, MEG data, and EEG data. For MRI data you can use a tool called BIDScoin. This is not easy to integrate so I would encourage to read their _very elaborate_ documentation: https://bidscoin.readthedocs.io/en/stable/#

## Behavioural
Depending on your task structure you might want to add or remove folders for runs, sessions, or acquisitions. In the example below we only have 1 acquisition and no sessions or runs. 











