# KALMUS

KALMUS is a Python package for the computational analysis of colors in films. It addresses how to best describe a film's color.  This package is optimized for two purposes:  (1) various ways to measure, calculate and compare a film's color and (2) various ways to visualize a film's color.

# API Documentation

# Instruction
Once the package is installed. The functionalities of the KALMUS are accessible through the Graphic user interface (GUI) and imported kalmus module.

- To start the KALMUS in GUI, use the command `kalmus-gui`. The initiation process may take minutes to be finished.
- To import the kalmus module in the python script, use `import kalmus`.

# Precomputed Barcodes

Precomputed barcodes are accessible upon requests. Please email the Project maintainer Yida Chen <yc015@bucknell.edu> about your needs. 

# Acknowledgment

The authors wish to thank the Mellon Foundation, the Dalal Family Foundation, and the Bucknell University Humanities Center for their support on this project.
The project is released under the open-source MIT License.

# Update Log

### Update 1.3.6
**Changes**
- The internal package structure is refactored.
    - The utility files, including artist, measure_utils, and visualization
    utils, are in kalmus.utils. To import artist for example, `import kalmus.utils.artist`.
    - The barcodes related class files, including Barcode and BarcodeGenerator, 
    are in barcodes module now. To import Barcode for example, `import kalmus.barcodes.Barcode`.
    - The tkinter windows class files are further modularized.
    
---
### Update 1.3.5
**Changes**  
- The project source codes now cloud be found on our GitHub page, <https://github.com/KALMUS-Color-Toolkit/KALMUS>.
- If you clone the project to the local, you may start the program by running the script kalmus.py. `python kalmus.py`  

---
### Update 1.3.4

**Add features**

- New *optional parameter* **save frame rate** in the barcode generation. Now, if users select to save the frames during
the generation of the barcode, they can choose how many seconds to save one frame. The default save frame rate is saving
one frame every 4 seconds.

- New *option* and *optional parameter* **Rescale frame** in the barcode generation. Users can choose whether to rescale 
the input frame (reducing or enlarging the image size) during the barcode generation by a factor given by users.  
The rescaling the input frame to a smaller size can substantially expedite the generation process. This option is highly
recommend for the input video with resolution higher than 1K standard.  
However, for the video with resolution lower than 1K, the time for rescaling the frame may outweigh the benefit in 
accelerating the barcode generation.

**Changes**

- Now, instead of closing themselves once the process succeeded, the Generate Barcode window will give user the 
success message when the barcode is generated, and the window will not be closed. Meanwhile, only one generate barcode 
can be opened at a time, and users need to close the Generate Barcode window before exiting the program.
- Load JSON window, Save JSON window, Save Image Window, and Output CSV window now also give users success message when 
the process is finished. Load JSON window will indicate the name (key) of the barcode loaded into the memory in its
 message. Save JSON window, Save Image Window, and Output CSV window will indicate where the JSON, Image, and CSV files
 are saved on the machine.

**Fixes**

- The blocking issue of the Generate Barcode after users quit the KALMUS software has been fixed. Now, when users close 
the Generate Barcode Window and Main Window of the KALMUS GUI, all the other windows will be closed automatically and 
the allocated resources for their threads will be released. 

---
### update 1.3.3

**Add features**

- More indicative **Error Detection/Exception Handling** in KALMUS graphic user interface.  
Now in the generate barcode, Load JSON window, Save JSON window, and Save Barcode Image window 
error or warning message box with issue message will pop up if any handled/unresolved exception occurred in the process.
- kalmus-gui now **asks users** whether they are sure to quit the KALMUS when they try to close the main window by the Quit 
button or Close button on the Window Manager bar.

**Changes**

- Layout of **Inspect Barcode** window has been redesigned. Now buttons are all on the same row, and the displayed 
barcode image are more compact with respect to the window.
- KALMUS GUI now loads different formats of icon image under different OS environment. (.ico format for Windows and
 POSIX Mac, .xbm for POSIX system)
- Now the histogram plots in the Main window will also be auto-rescaled after 
loading new barcodes into the main window.
- Threaded Barcode generation. Barcode generation now won't block the mainloop process of the KALMUS GUI.

**Fixes**

- Dependencies fixes. The required versions of dependent modules **matplotlib** and **scikit-image** now retreat to
more stable releases. **matplotlib**==3.2.2 and **scikit-image**==0.16.2
- Barcodes with less than 160 frames now can be correctly loaded and displayed in the KALMUS GUI.

- Unexpected print statements in the barcode generation has been removed.

---
### Update 1.3.1

**Add features**

 - **Check Meta Info** now also shows the input video length (time), video frame rate (FPS), generated barcode's start time, and end time in 
 the input video. Notice that these four pieces of information are determined from the input video file and are hence 
 **immutable** faithful parameters of the video & barcode.

**Changes**

- The default behavior of the **Save Frames** in the generation of the barcode is changed. The upper bound of saved frames 
for a barcode is 900 frames. The default sampled rate is saving one frame every 4 seconds, the sampled rate will be 
reduced if the resultant saved frames exceed the bound.
- In the **Reshape Barcode**, parameters **Scale Width/Height by (ratio)** and **Resize Width/Height to (pixels)** are 
no longer required.  
If one of the parameters is not specified, rescaling/resizing will assume the barcode is unchanged 
in that dimension. If both dimensions (x and y) are not specified, the rescaling/resizing won't process.  
For reshaping, Frames per Column as the only parameter is still required, and the reshaping won't process 
unless the parameter is given.
- In the **Save JSON**, the JSON file path field is no longer required. If the path is not given, the default filename of 
the saved barcode will be used, and the JSON file (barcode) will be saved in the current working directory.  
We still recommend users to specify the JSON file path to avoid potential filename conflicts.

**Fixes**

- Unexpected print statement when *Checking time* at a brightness barcode is now removed.
- **Reshape, Resize, or Rescale** a barcode will no longer break the frame-pixel (or time-pixel) relation which the function *Check time 
at a pixel* relies on. Thus, users will no need to **Recalibrate** the barcode to fix the time-pixel relationship after 
**Reshape/Resize/Rescale**.  
**Calibrate** now should only be used to update the time information of the barcode generated by the KALMUS 
in the 1.3.0 version and before. The mutability of the Barcode's start time/end time, and Frame rate are no longer needed, 
and the **Calibrate** may be removed from the KALMUS GUI in the future version. 
- *Auto Rescale* the barcode plots after loading the new barcode with different sizes (in x, y, or both dimensions) or 
reshaping/resizing/rescaling the currently plotted barcodes.

---
### Update 1.3.0

**Add features**

- *Check time at a barcode's pixel*. Users now can double clicks on a pixel in the displayed barcode to check the position, frame index, and time of the corresponding frame in the original film. All these timestamps will be showed in a separate window.
- If the barcode saved the frames during the generation, users may click the **Display** button in the new window to check 5 frames around that time point.
- The correct time relies on the assumption that each pixel in the barcode is corresponding to a sampled frame.  
If the barcode image has been reshaped/scaled, users can use the **Calibrate** button to recalibrate the frame-pixel relationship.  
The Frame per Second (fps) is used particularly for the downward compatibility to the barcodes generated in the previous version of KALMUS, and should not be used for the barcode generated after version 1.3.0.
- Color barcode and Brightness barcode have distinguished behavior when checking the time point.

**Fixes**

- In the Barcode Generator window, the frame acquisition parameters **Start at (frames), Start at (mins:secs), Total frames, End at (mins:secs)** are no longer required fields.  
(1) The Generator assumes the barcode starts at the beginning of the film when leaving **Start at** entry blank or typing `Start` in the entry.  
(2) The Generator assumes the barcode ends at the end of the film when leaving **Total frames or End at** entry blank or typing `End` in the entry.  
(3) The **Sampled frame rate (frames or seconds)** is still required.