# Podonator

## Setup

### Hardware

This script will need two USB cameras to capture images and then apply necessary correction for lens distortion and geometry. Change the parameter values of ```--left_camera_id``` and ```--right_camera_id``` if you don't see the proper streams.

### Calibration
To obtain the camera matrix and the distortion coefficients you can use the calibrate.py script which comes with OpenCV (in the 'samples' folder). The script is basically a wrapper around OpenCVs camera calibration functionality and takes several snapshots from the calibration object as an input. Take pictures (at least 6) with the target in several different positions and orientations (not always coplanar with the camera) with each camera. Follow the procedure below to determine the values of the matrix and distortion values of each camera then edit the PodonatorLib script to apply them (use the camera matrix value for the value of K and the distortion coefficients for d). Do this for __each__ camera !

#### For normal lenses
Rename the calibration pictures to match a sequence pattern. Use the pictures to determine if you need to use the mirroring parameter and, if you do so, apply the transformation to the pictures before running the calibration script and change the parameter value in PodonatorLib.py.

Run the calibration script by issuing the following command in a shell :
```
python calibrate.py "calibration_pictures/image_*.jpg"
```

It will output the calibration parameters for our camera, namely the root-mean-square error (RMS) of our parameter estimation, the camera matrix and the distortion coefficients:
```
RMS: 0.171988082483
camera matrix:
[[ 611.18384754    0.          515.31108992]
 [   0.          611.06728767  402.07541332]
 [   0.            0.            1.        ]]
distortion coefficients:  [-0.36824145  0.2848545   0.00079123  0.00064924 -0.16345661]
```

#### For fisheye lenses
Copy the ```fisheyeCalibration.py``` script to the folder containing the calibration pictures. This folder should __only__ contain the calibration script and the calibration pictures. Then, run the calibration script by issuing the following command in a shell :
```
python fisheyeCalibration.py
```
The script will only read PNG images by default, if you're using jpeg then change the parameter value in line 20.

## Usage
Run the script (use the parameters below if needed), press the Space bar to capture the images or use Esc to exit.
```
usage:
    Podonator.py [--left_camera_id] [--right_camera_id] [<output path>]
    or
    PodonatorGUI.py [--left_camera_id] [--right_camera_id]

default values:
    --left_camera_id  : 0
    --right_camera_id : 1
    <output path>     : .
```

When running the GUI version of the script the output path is only set inside the GUI (default is current folder).

Credits to https://hackaday.io/hacker/13659-hanno
