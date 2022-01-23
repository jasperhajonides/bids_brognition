# BIDS Formatting
### In short, what is BIDS?
Neuroimaging experiments result in complicated data that can be arranged in many different ways. So far there is no consensus how to organize and share data obtained in neuroimaging experiments. Even two researchers working in the same lab can opt to arrange their data in a different way. Lack of consensus (or a standard) leads to misunderstandings and time wasted on rearranging data or rewriting scripts expecting certain structure. With the Brain Imaging Data Structure (BIDS), we describe a simple and easy to adopt way of organizing neuroimaging and behavioural data.


BIDS uses the following file tree:

![alt text](https://github.com/jasperhajonides/bids_brognition/blob/main/ims/bids_tree.png)

 
Where “source” contains the raw data straight from the acquisition computer. This is saved because in cases the file format of the raw data is converted into a more commonly used format.  
The folder “raw” contains the BIDS file structure that we will create below.
In the “derivatives” folder you can put your (fully) preprocessed files or any other data that has been cleaned up.
Furthermore, you could/should add folders like “scripts”, where you put your preprocessing and analysis scripts, “presentation”, for your Psychtoolbox/PsychoPy/Presentation/… scripts that you used to display stimuli in your study. 

