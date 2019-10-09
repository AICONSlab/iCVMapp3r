# Local Install

## Python
For the main required Python packages (numpy, scipy, etc.) we recommend using
[Anaconda for Python 3.6](https://www.continuum.io/downloads)

## Installing package and dependencies for iCVMapp3r locally

1. Clone repository

        git clone https://github.com/mgoubran/iCVMapp3r.git iCVMapp3r

        (or install zip file and uncompress)

        cd iCVMapp3r

    If you want to create a virtual environment where iCVMapp3r can be run,

        conda create -n icvmapper python=3.6 anaconda
        source activate icvmapper
    
    To end the session,
    
        source deactivate
    
    To remove the environment
    
        conda env remove --name icvmapper

2. Install dependencies
    
        pip install git+https://www.github.com/keras-team/keras-contrib.git
    
    If the computer you are using has a GPU:
        
        pip install -e .[icvmapper_gpu]

    If not:
    
        pip install -e .[icvmapper]

3. Test the installation by running

        icvmapper --help
        
   To confirm that the command line function works, and
   
        icvmapper
        
   To launch the interactive GUI.

## Download deep models

Download the models from [this link](https://drive.google.com/open?id=10aVCDurd_mcB49mJfwm658IZg33u0pd2) and place them in the "models" directory

## For tab completion
    pip3 install argcomplete
    activate-global-python-argcomplete

## Updating iCVMapp3r
To update iCVMapp3r, navigate to the directory where iCVMapp3r was cloned and run

    git pull
    pip install -e .[{option}] -process-dependency-links
    
where "option" is dependent on whether or not you have a GPU (see package installation steps above)
