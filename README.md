    Project:
    
        "Environment.yml" file: 
        
            It is for setting conda environment in terminal to install the necessary packages. 
        
            To create the conda environment you need to first install anaconda (if you are installing on Windows, you might need to check "Add Anaconda to my PATH environment variable" option during installation process). After installation, you need to run the following command in a terminal to create environment: 
                conda env create -f environment.yml
            and to activate it: 
                conda activate video_extract_env. 
            After activating the environment you should be able to run correctly the Python script in your chosen directory. 
    
        "Video_editing.py" Python script: 
        
            Creates two folders- one with screenshots, the second one with 10 second video segments with the same entry timestamps in name (the 10 second video segments will also have the end timestamp in the name). The only thing that requires modification in the file is path to the video. You can also change both the intervals (currently 5 minutes) and video duration (now set to 10 seconds) in the script. 