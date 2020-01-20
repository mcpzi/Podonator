# Podonator

Podonator is a small tool for DIY Orthotics scanners based on two webcams. It will handle camera calibration and image correction to output at-scale and print-ready images. It's fully open-source and based on OpenCV.

## Setup

### Hardware
This script will need two USB cameras to capture images and then apply necessary correction for lens distortion and geometry. Change the parameter values of ```--left_camera_id``` and ```--right_camera_id``` if you don't see the proper streams.

### Software
Use at least Python3 >=3.7 and install the following libraries using pip : 
```
pip install Pillow (6.2.1)
pip install opencv-python (4.1.2.30)
pip install PyQt5 (5.14.1)
```

If you want to use Podonator as a standalone .exe please to do following :
```
pip install pyinstaller (3.6)
pyinstaller .\PodonatorGUI.py --onefile --windowed --icon .\950-512.ico -n Podonator
```
If you want to keep the size of the .exe small (~70MB), make sure to use a specific Python VENV where only the above libraries are installed.


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
It will output the values for K and d, just copy and paste those values in ```PodonatorLib.py```. Note : The script will only read PNG images by default, if you're using jpeg then change the parameter value in line 20.

### Perspective correction
Perspective correction will be necessary if the cameras are tilted. Follow the procedure below to determine and apply the correction :
1. Cut a rectangle out of a cardboard, its length and width should cover all feet sizes
2. Place the cardboard on the orthotics scanner so that it is visible by camera 1
3. Capture the image from the corresponding camera with a regular image capture tool (do not apply any image correction)
4. Open the image and get the coordinates of each corner of the rectangle (use XnView or Paint.NET for example)
5. Change the values in ```PodonatorLib.py``` : reference_cam1 = np.float32([[x1, y1],[x2, y2],[x3, y3],[x4, y4]]) where x1, y1 are the coordinates of the top left corner, x2, y2 the top right corner, x3, y3 the bottom left corner and x4, y4 the bottom right corner
6. Repeat the procedure for camera 2 and change the values of reference_cam2

## Usage

### GUI Version

Run ```PodonatorGUI.py``` the output path and camera IDs are set inside the GUI. Rename to ```PodonatorGUI.pyw``` to get rid of the console window (but you won't see any console output). Click on "Acquire" the press the Space bar to capture the images or press Esc to exit.

### CLI
Run the script (use the parameters below if needed), press the Space bar to capture the images or press Esc to exit.
```
usage:
    Podonator.py [--left_camera_id] [--right_camera_id] [<output path>]
    or
    PodonatorGUI.py

default values:
    --left_camera_id  : 0
    --right_camera_id : 1
    <output path>     : .
```

Credits to https://hackaday.io/hacker/13659-hanno for initial idea and OpenCV tutorials for fisheye lens distortion correction
