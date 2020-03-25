# Getting started

You can use iCVMapp3r through the graphical user interface (GUI) or command line:

## For GUI

To start the GUI, type

    icvmapper

A GUI that looks like the image below should appear. You can hover any of buttons in the GUI to see a brief description of the command.

![Graphical user interface for the Dasher application](images/icvmapper_gui.png)

You can get the command usage info by click the "Help" box on any of the pop-up windows.

![Help screen for graphical user interface for Dasher application](images/icvmapper_help.png)

## For Command Line

You can see all the icvmapper commands by typing either of the following lines:

    icvmapper -h
    icvmapper --help

Once you know the command you want to know from the list, you can see more information about the command. For example, to learn more about seg_hfb:

    icvmapper seg_icv -h
    icvmapper seg_icv --help

## Intracranial volumes
To extract ICV use the GUI (Stats/ICV) or command line:

    icvmapper stats_icv -h

## QC
QC files are automatically generated in a sub-folder within the subject folder.
They are .png images that show a series of slices in the brain to
help you quickly evaluate if your command worked successfully,
especially if you have run multiple subjects.
They can also be created through the GUI or command line:

    icvmapper seg_qc -h

The QC image should look like this:

![Quality control image for icv segmentation](images/icv_seg_qc.png)


## Logs
Log files are automatically generated in a sub-folder within the subject folder.
They are .txt files that contain information regarding the command
and can be useful if something did not work successfully.

## File conversion

Convert Analyze to Nifti (or vice versa)

    icvmapper filetype

    Required arguments:
    -i , --in_img    input image, ex:MM.img
    -o , --out_img   output image, ex:MM.nii

    Example:
    icvmapper filetype --in_img subject_T1.img --out_img subject_T1.nii.gz


