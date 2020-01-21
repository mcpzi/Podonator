""" Main Podonator library, contains all camera calibration and image correction functions"""
import sys
import datetime
import os
import webbrowser
from pathlib import Path
import numpy as np
import cv2 as cv
from PIL import Image

# Change values below for image modification if necessary
mirror = False
rotate = True
image_dpi = 148
image_ratio = 0.4369 # L325/W142
#Define image format
file_ext = ".jpg"

# Use the calibration.py script to define the values below for each camera
# Define camera matrix K for camera 1
K1 = np.array([[805.6337330782276, 0.0, 956.9882395246467], [0.0, 816.8205144586113, 518.6594662094939], [0.0, 0.0, 1.0]])

# Define distortion coefficients d for camera 1
d1 = np.array([[-0.06934545703899442], [0.2681174500565983], [-0.7915276083705534], [0.7514919779408756]])

# Define camera matrix K for camera 2
K2 = np.array([[728.6058065554909, 0.0, 944.7599470057236], [0.0, 717.4035218893431, 512.8725335118967], [0.0, 0.0, 1.0]])

# Define distortion coefficients d for camera 2
d2 = np.array([[-0.008902607891725171], [0.09267206754490831], [-0.15736471202694802], [0.08299570424850797]])

# Reference points for camera 1
reference_cam1 = np.float32([[290, 341], [1562, 317], [72, 943], [1834, 907]])

# Reference points for camera 2
reference_cam2 = np.float32([[290, 341], [1562, 317], [72, 943], [1834, 907]])

# Test if the camera is connected
# Returns False if not, True otherwise
def test_camera(camera_id):
    """Camera testing"""
    cam = cv.VideoCapture(camera_id)
    #ret_val, image = cam.read()
    #if not ret_val:
        #return False
    if cam is None or not cam.isOpened():
        return False
    cam.release()
    return True

def init_camera(camera_id):
    """Camera initialization"""
    cam = cv.VideoCapture(camera_id, cv.CAP_DSHOW)
    cam.set(cv.CAP_PROP_FRAME_WIDTH, 1920)
    cam.set(cv.CAP_PROP_FRAME_HEIGHT, 1080)
    cam.set(cv.CAP_PROP_FPS, 5)
    return cam

def get_camera_image(mirror_bool, cam):
    """Gets an image stream from a camera and apply mirroring or 90 degrees CW rotation if necessary
    Returns the stream with applied corrections"""
    ret_val, img = cam.read()
    if not ret_val:
        sys.exit("ERROR : One or more cameras unavailable")
    if mirror_bool:
        img = cv.flip(img, 1)
    return img


def show_images(cam1, cam2, rotate_bool):
    """Shows the stream from the cameras and allows for image capture
    Returns the two captured images (one per camera)"""
    toggle = True
    gen_output = False
    while toggle:
        img1 = get_camera_image(mirror, cam1)
        img2 = get_camera_image(mirror, cam2)
        #Undistort
        u_img1 = undistort_image(img1, K1, d1)
        u_img2 = undistort_image(img2, K2, d2)
        #Perspective correction
        up_img1 = perpective_correction(u_img1, reference_cam1)
        up_img2 = perpective_correction(u_img2, reference_cam2)
        if rotate_bool:
            #Concatenate the two streams in a single image
            img = np.concatenate((cv.rotate(up_img1, cv.ROTATE_90_CLOCKWISE), cv.rotate(up_img2, cv.ROTATE_90_COUNTERCLOCKWISE)), axis=1)
            #Image resolution to display
            dim = (int(round(960 * image_ratio))*2, 960)
        else:
            img = np.concatenate((img1, img2), axis=0)
            dim = (960, int(round(960 * image_ratio))*2)
        img = cv.resize(img, dim, interpolation=cv.INTER_AREA)
        cv.imshow("Podoscope Preview - Spacebar to acquire or Esc to cancel", img)
        keypress = cv.waitKey(1)
        if keypress%256 == 27:
            #ESC pressed
            #sys.exit("Cancelled")
            toggle = False
            gen_output = False
            print("Cancelled")
        elif keypress%256 == 32:
            #SPACE pressed
            toggle = False
            gen_output = True
            print("Images acquired")
    return up_img1, up_img2, gen_output

def undistort_image(img, K, d):
    """Applies correction for lens distortion (K and D parameters obtained through OpenCV calibration for each camera)
    Returns the image with applied lens distortion correction"""
    # Read the image and get its size
    h, w = img.shape[:2]
    # Generate look-up tables for remapping the camera image
    mapx, mapy = cv.fisheye.initUndistortRectifyMap(K, d, np.eye(3), K, (w, h), cv.CV_16SC2) # pylint: disable=no-member
    # Remap the original image to a new image
    newimg = cv.remap(img, mapx, mapy, interpolation=cv.INTER_LINEAR, borderMode=cv.BORDER_CONSTANT)
    return newimg

def perpective_correction(img, reference):
    """Perspective correction"""
    h, w = img.shape[:2]
    target = np.float32([[0, 0], [w, 0], [0, h], [w, h]])
    M = cv.getPerspectiveTransform(reference, target)
    newimg = cv.warpPerspective(img, M, (w, h))
    newimg = cv.resize(newimg, (w, int(round(w * image_ratio))))
    return newimg

def output_images(img1, img2, naming_pattern, file_extension, image_dpi_value):
    """Image generation"""
    cv.imwrite(naming_pattern+"_G"+file_extension, img1)
    cv.imwrite(naming_pattern+"_D"+file_extension, img2)
    #Adjust image DPI for printing
    im = Image.open(naming_pattern+"_G"+file_extension)
    im.save(naming_pattern+"_G"+file_extension, dpi=(image_dpi_value, image_dpi_value))
    im = Image.open(naming_pattern+"_D"+file_extension)
    im.save(naming_pattern+"_D"+file_extension, dpi=(image_dpi_value, image_dpi_value))
    return

def podonator(output_dir, left_camera_id, right_camera_id):
    """Calls all previous functions"""
    os.chdir(str(Path(output_dir)))
    #Initialize cameras
    cam1 = init_camera(left_camera_id)
    cam2 = init_camera(right_camera_id)
    #Launch image preview, capture and correction
    correct_img1, correct_img2, gen_output = show_images(cam1, cam2, rotate)
    cam1.release()
    cam2.release()
    cv.destroyAllWindows()
    if gen_output:
        #Rotate images if necessary
        if rotate:
            correct_img1 = cv.rotate(correct_img1, cv.ROTATE_90_CLOCKWISE)
            correct_img2 = cv.rotate(correct_img2, cv.ROTATE_90_COUNTERCLOCKWISE)
        now = datetime.datetime.now()
        img_name = now.strftime("%Y-%m-%d-%H%M%S")
        output_images(correct_img1, correct_img2, img_name, file_ext, image_dpi)
        #Open the file browser in the output folder
        webbrowser.open(str(Path(output_dir)))
        return
    else:
        return
