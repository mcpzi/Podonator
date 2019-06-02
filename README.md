# CameraPodo

## Setup

### Hardware

This script will need two USB cameras to capture images and then apply necessary correction for lens distortion and geometry. Change the parameter value of ```cv.VideoCapture(0)``` if you don't see the proper streams.

### Calibration
To obtain the camera matrix and the distortion coefficients you can use the calibrate.py script which comes with OpenCV (in the 'samples' folder). The script is basically a wrapper around OpenCVs camera calibration functionality and takes several snapshots from the calibration object as an input. After having run the script by issuing the following command in a shell :
```
python calibrate.py "calibration_samples/image_*.jpg"
```

The calibration parameters for our camera, namely the root-mean-square error (RMS) of our parameter estimation, the camera matrix and the distortion coefficients can be obtained:

RMS: 0.171988082483
camera matrix:
[[ 611.18384754    0.          515.31108992]
 [   0.          611.06728767  402.07541332]
 [   0.            0.            1.        ]]
distortion coefficients:  [-0.36824145  0.2848545   0.00079123  0.00064924 -0.16345661]


Use the camera matrix value for K and the distortion coefficients for d. Do this for __each__ camera !

## Usage

Run the script, press the Space bar to capture the images or use Esc to exit. The final image (with the two pictures side by side) will be generated in the same folder as the script.

Credits to https://hackaday.io/hacker/13659-hanno
