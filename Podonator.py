import numpy as np
import cv2 as cv
import datetime
import sys
import getopt
from pathlib import Path
import os
import webbrowser


'''
usage:
    Podonator.py [--left_camera_id] [--right_camera_id] [<output path>]

default values:
    --left_camera_id  : 0
    --right_camera_id : 1
    <output path>     : .
'''

# Change values below for image modification if necessary
mirror = False
rotationCW = True

# Use the calibration.py script to define the values below for each camera
# Define camera matrix K for camera 1
K1 = np.array([[673.9683892, 0., 343.68638231],
                  [0., 676.08466459, 245.31865398],
                  [0., 0., 1.]])

# Define distortion coefficients d for camera 1
d1 = np.array([5.44787247e-02, 1.23043244e-01, -4.52559581e-04, 5.47011732e-03, -6.83110234e-01])

# Define camera matrix K for camera 2
K2 = np.array([[673.9683892, 0., 343.68638231],
                  [0., 676.08466459, 245.31865398],
                  [0., 0., 1.]])

# Define distortion coefficients d for camera 2
d2 = np.array([5.44787247e-02, 1.23043244e-01, -4.52559581e-04, 5.47011732e-03, -6.83110234e-01])


# Gets an image stream from a camera and apply mirroring or 90 degrees CW rotation if necessary
# Returns the stream with applied corrections
def get_camera_image(mirror, rotationCW, cam):
        ret_val, img = cam.read()
        if not ret_val:
            sys.exit("ERROR : One or more cameras unavailable")
        if mirror:
            img = cv.flip(img, 1)
        if rotationCW:
            img=cv.rotate(img, cv.ROTATE_90_CLOCKWISE)
        return img

# Shows the stream from the cameras and allows for image capture
# Returns the two captured images (one per camera)
def show_images(cam1, cam2):
    toggle = True
    while toggle:
        img1 = get_camera_image(mirror, rotationCW, cam1)
        img2 = get_camera_image(mirror, rotationCW, cam2)
        #Concatenate the two streams in a single image
        cv.imshow("Podoscope", np.concatenate((img1, img2), axis=1))
        keypress = cv.waitKey(1)
        if keypress%256 == 27:
            #ESC pressed
            sys.exit("Cancelled")
        elif keypress%256 == 32:
            #SPACE pressed
            toggle = False
            print ("Images acquired")
    cam1.release()
    cam2.release()
    cv.destroyAllWindows()
    return img1, img2

# Applies correction for lens distortion (K and D parameters obtained through OpenCV calibration for each camera)
# Returns the image with applied lens distortion correction
def unwrap_image(img, K, d):
    # Read the image and get its size
    h, w = img.shape[:2]

    # Generate new camera matrix from parameters
    newcameramatrix, roi = cv.getOptimalNewCameraMatrix(K, d, (w,h), 0)

    # Generate look-up tables for remapping the camera image
    mapx, mapy = cv.initUndistortRectifyMap(K, d, None, newcameramatrix, (w, h), 5)

    # Remap the original image to a new image
    newimg = cv.remap(img, mapx, mapy, cv.INTER_LINEAR)
    return newimg

def main():

    #Defines image format
    file_ext=".jpg"
    args, output_dir = getopt.getopt(sys.argv[1:], '', ['left_camera_id=', 'right_camera_id='])
    args = dict(args)
    args.setdefault('--left_camera_id', 0)
    args.setdefault('--right_camera_id', 1)
    if not output_dir:
        output_dir = '.'
    else:
        output_dir=output_dir[0]
        Path(output_dir).mkdir(exist_ok=True)
        os.chdir(str(Path(output_dir)))
    left_camera_id = int(args.get('--left_camera_id'))
    right_camera_id = int(args.get('--right_camera_id'))

    cam1 = cv.VideoCapture(left_camera_id)
    cam2 = cv.VideoCapture(right_camera_id)
    raw_img1, raw_img2 = show_images(cam1, cam2)
    correct_img1 = unwrap_image(raw_img1, K1, d1)
    correct_img2 = unwrap_image(raw_img2, K2, d2)
    final_img = np.concatenate((correct_img1, correct_img2), axis=1)
    now=datetime.datetime.now()
    img_name=now.strftime("%Y-%m-%d-%H%M%S")
    cv.imwrite(img_name+file_ext, final_img)
    #Opens the file browser in the output folder
    webbrowser.open(str(Path(output_dir)))
    return

if __name__ == '__main__':
    main()
