import numpy as np
import cv2 as cv
import datetime
import sys
import getopt
from pathlib import Path
import os
import webbrowser
from PIL import Image

# Change values below for image modification if necessary
mirror = False
rotate = True
image_ratio = 0.4369 # L325/W142
image_dpi = 148

# Use the calibration.py script to define the values below for each camera
# Define camera matrix K for camera 1
K1 = np.array([[805.6337330782276, 0.0, 956.9882395246467], [0.0, 816.8205144586113, 518.6594662094939], [0.0, 0.0, 1.0]])

# Define distortion coefficients d for camera 1
d1 = np.array([[-0.06934545703899442], [0.2681174500565983], [-0.7915276083705534], [0.7514919779408756]])

# Define camera matrix K for camera 2
K2 = np.array([[805.6337330782276, 0.0, 956.9882395246467], [0.0, 816.8205144586113, 518.6594662094939], [0.0, 0.0, 1.0]])

# Define distortion coefficients d for camera 2
d2 = np.array([[-0.06934545703899442], [0.2681174500565983], [-0.7915276083705534], [0.7514919779408756]])


# Gets an image stream from a camera and apply mirroring or 90 degrees CW rotation if necessary
# Returns the stream with applied corrections
def get_camera_image(mirror, cam):
    ret_val, img = cam.read()
    if not ret_val:
        sys.exit("ERROR : One or more cameras unavailable")
    if mirror:
        img = cv.flip(img, 1)
    return img

# Shows the stream from the cameras and allows for image capture
# Returns the two captured images (one per camera)
def show_images(cam1, cam2, rotate):
    toggle = True
    while toggle:
        img1 = get_camera_image(mirror, cam1)
        img2 = get_camera_image(mirror, cam2)
        if rotate == True:
            #Concatenate the two streams in a single image
            img = np.concatenate((cv.rotate(img1, cv.ROTATE_90_CLOCKWISE), cv.rotate(img2, cv.ROTATE_90_COUNTERCLOCKWISE)), axis=1)
            #Image resolution to display
            dim = (1080,960)
        else:
            img = np.concatenate((img1, img2), axis=0)
            dim = (960,1080)
        img = cv.resize(img, dim, interpolation = cv.INTER_AREA)
        cv.imshow("Podoscope Preview - Spacebar to acquire or Esc to cancel", img)
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
    # Generate look-up tables for remapping the camera image
    mapx, mapy = cv.fisheye.initUndistortRectifyMap(K, d, np.eye(3), K, (w, h), cv.CV_16SC2)
    # Remap the original image to a new image
    newimg = cv.remap(img, mapx, mapy, interpolation=cv.INTER_LINEAR, borderMode=cv.BORDER_CONSTANT)
    #Perspective correction
    pts1 = np.float32([[290, 341],[1562, 317],[72, 943],[1834, 907]])
    pts2 = np.float32([[0, 0],[w, 0],[0, h],[w, h]])
    M = cv.getPerspectiveTransform(pts1, pts2)
    newimg = cv.warpPerspective(newimg, M, (w, h))
    newimg = cv.resize(newimg, (w, int(round(w * image_ratio))))
    return newimg


# Test if the camera is connected
# Returns False if not, True otherwise
def test_camera(camera_id):
    cam = cv.VideoCapture(camera_id)
    ret_val, image = cam.read()
    if not ret_val:
        return False
    cam.release()
    return True

def podonator(output_dir, left_camera_id, right_camera_id):
    #Define image format
    file_ext=".jpg"
    os.chdir(str(Path(output_dir)))
    cam1 = cv.VideoCapture(left_camera_id, cv.CAP_DSHOW)
    cam2 = cv.VideoCapture(right_camera_id, cv.CAP_DSHOW)
    cam1.set(cv.CAP_PROP_FRAME_WIDTH, 1920)
    cam1.set(cv.CAP_PROP_FRAME_HEIGHT, 1080)
    cam2.set(cv.CAP_PROP_FRAME_WIDTH, 1920)
    cam2.set(cv.CAP_PROP_FRAME_HEIGHT, 1080)
    #Launch image preview and capture
    raw_img1, raw_img2 = show_images(cam1, cam2, rotate)
    #Undistort and correct perspective
    correct_img1 = unwrap_image(raw_img1, K1, d1)
    correct_img2 = unwrap_image(raw_img2, K2, d2)
    if rotate == True:
        correct_img1 = cv.rotate(correct_img1, cv.ROTATE_90_CLOCKWISE)
        correct_img2 = cv.rotate(correct_img2, cv.ROTATE_90_COUNTERCLOCKWISE)
    now=datetime.datetime.now()
    img_name=now.strftime("%Y-%m-%d-%H%M%S")
    cv.imwrite(img_name+"_G"+file_ext, correct_img1)
    cv.imwrite(img_name+"_D"+file_ext, correct_img2)
    #Adjust image DPI for printing
    im = Image.open(img_name+"_G"+file_ext)
    im.save(img_name+"_G"+file_ext, dpi=(image_dpi, image_dpi))
    im = Image.open(img_name+"_D"+file_ext)
    im.save(img_name+"_D"+file_ext, dpi=(image_dpi, image_dpi))
    #Open the file browser in the output folder
    webbrowser.open(str(Path(output_dir)))
    return
