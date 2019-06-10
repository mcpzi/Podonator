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

# Use the calibration.py script to define the values below for each camera
# Define camera matrix K for camera 1
K1 = np.array([[728.6058065554909, 0.0, 944.7599470057236], [0.0, 717.4035218893431, 512.8725335118967], [0.0, 0.0, 1.0]])

# Define distortion coefficients d for camera 1
d1 = np.array([[-0.008902607891725171], [0.09267206754490831], [-0.15736471202694802], [0.08299570424850797]])

# Define camera matrix K for camera 2
K2 = np.array([[728.6058065554909, 0.0, 944.7599470057236], [0.0, 717.4035218893431, 512.8725335118967], [0.0, 0.0, 1.0]])

# Define distortion coefficients d for camera 2
d2 = np.array([[-0.008902607891725171], [0.09267206754490831], [-0.15736471202694802], [0.08299570424850797]])


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
def show_images(cam1, cam2, rotation):
    toggle = True
    while toggle:
        img1 = get_camera_image(mirror, cam1)
        img2 = get_camera_image(mirror, cam2)
        if rotate == True:
            #Concatenate the two streams in a single image
            img = np.concatenate((cv.rotate(img, cv.ROTATE_90_CLOCKWISE), cv.rotate(img, cv.ROTATE_90_COUNTERCLOCKWISE)), axis=1)
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
    newimg = cv2.remap(img, mapx, mapy, interpolation=cv.INTER_LINEAR, borderMode=cv.BORDER_CONSTANT)
    #Adding padding to left and right to compensate perspective
    top, bottom = 0, 0
    delta_w = 2500 - 1920
    left, right = delta_w//2, delta_w-(delta_w//2)
    color = [0, 0, 0]
    newimg = cv2.copyMakeBorder(newimg_img, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color)
    #Perspective correction
    pts1 = np.float32([[587,184],[1907,178],[82,1047],[2497,1048]])
    pts2 = np.float32([[0,0],[2500,0],[0,1080],[2500,1080]])
    M = cv2.getPerspectiveTransform(pts1,pts2)
    newimg = cv2.warpPerspective(new_im,M,(2500,1080))
    newimg = cv2.resize(newimg, (1920, 1080))
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
    cam1 = cv.VideoCapture(left_camera_id)
    cam2 = cv.VideoCapture(right_camera_id)
    cam1.set(cv.CAP_PROP_FRAME_WIDTH, 1920)
    cam1.set(cv.CAP_PROP_FRAME_HEIGHT, 1080)
    cam2.set(cv.CAP_PROP_FRAME_WIDTH, 1920)
    cam2.set(cv.CAP_PROP_FRAME_HEIGHT, 1080)
    #Launch image preview and capture
    raw_img1, raw_img2 = show_images(cam1, cam2)
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
    im.save(img_name+"_G"+file_ext, dpi=(152,152))
    im = Image.open(img_name+"_D"+file_ext)
    im.save(img_name+"_D"+file_ext, dpi=(152,152))
    #Open the file browser in the output folder
    webbrowser.open(str(Path(output_dir)))
    return
