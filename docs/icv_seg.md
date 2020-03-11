# Segmentation tutorials

## GUI

Watch this video tutorial:

[![IMAGE ALT TEXT](https://img.youtube.com/vi/QF-1oIQ4eRA/0.jpg)](https://youtu.be/QF-1oIQ4eRA "ICV Seg")

-----

Or follow the steps below:

After opening the iCVMapper GUI, click "ICV" under the "Segmentation" tab. Wait for a new pop-up window to appear. The window should look like the image below.

![icv pop up window](images/icv_1.PNG)

Click "Select t1w" and chose your T1 image. Click "Run".
Type your desired output name in the "out" box.
Your output file will automatically appear in your t1w folder.


## Command Line

    icvmapper seg_icv
    
    Optional arguments:
    -s , --subj       input subject
    -t1 , --t1w       input T1-weighted
    -b, --bias        bias field correct image before segmentation
    -o , --out        output prediction
    -f, --force       overwrite existing segmentation
    -ss , --session   input session for longitudinal studies
    
    Examples:
    icvmapper seg_icv -s subjectname -b
    icvmapper seg_icv -t1 subject_T1_nu.nii.gz -o subject_icv.nii.gz

The output should look like this.:

![icv segmentation](images/3d_snap_resize.png)