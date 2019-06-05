from pyforms.basewidget import BaseWidget
from pyforms.controls   import ControlDir
from pyforms.controls   import ControlButton
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
    PodonatorGUI.py [--left_camera_id] [--right_camera_id]

default values:
    --left_camera_id  : 0
    --right_camera_id : 1
'''




class PodonatorGUI(BaseWidget):
    def __init__(self, *args, **kwargs):

        super().__init__('Podonator')
        self.flag = False
        #Definition of the forms fields
        self._outputfolder  = ControlDir('Output Folder', default=str(Path().absolute()))
        self._outputfolder.value = str(Path().absolute())
        self._runbutton  = ControlButton('Run')

        #Define the event that will be called when the run button is processed
        self._runbutton.value = self.run_event
        self._outputfolder.changed_event = self.__outputFolderSelectionEvent
        #Define the organization of the Form Controls
        self._formset = [
            ('','_outputfolder',''),
            ('','_runbutton','')
        ]

        # Change values below for image modification if necessary
        self.mirror = False
        self.rotationCW = False

        # Use the calibration.py script to define the values below for each camera
        # Define camera matrix K for camera 1
        self.K1 = np.array( [[5.97379985e+03, 0., 9.45550548e+02],
                        [0., 5.25358173e+03, 6.25005182e+02],
                        [0., 0., 1.]])

        # Define distortion coefficients d for camera 1
        self.d1 = np.array([-1.45301385e+01, 3.94029228e+02, 2.70782551e-01, -1.05196877e-01, -1.19783596e+03])

        # Define camera matrix K for camera 2
        self.K2 = np.array( [[5.97379985e+03, 0., 9.45550548e+02],
                        [0., 5.25358173e+03, 6.25005182e+02],
                        [0., 0., 1.]])

        # Define distortion coefficients d for camera 2
        self.d2 = np.array([-1.45301385e+01, 3.94029228e+02, 2.70782551e-01, -1.05196877e-01, -1.19783596e+03])
        return

    # Gets an image stream from a camera and apply mirroring or 90 degrees CW rotation if necessary
    # Returns the stream with applied corrections
    def get_camera_image(self, mirror, rotationCW, cam):
        ret_val, img = cam.read()
        #If no image is returned set flag to true to show an error in the main loop
        if not ret_val:
            self.flag = True
            return
        else:
            if mirror:
                img = cv.flip(img, 1)
            if rotationCW:
                img=cv.rotate(img, cv.ROTATE_90_CLOCKWISE)
        return img

    # Shows the stream from the cameras and allows for image capture
    # Returns the two captured images (one per camera)
    def show_images(self, cam1, cam2):
        toggle = True
        while toggle:
            img1 = self.get_camera_image(self.mirror, self.rotationCW, cam1)
            img2 = self.get_camera_image(self.mirror, self.rotationCW, cam2)
            if self.flag:
                return
            img = np.concatenate((img1, img2), axis=1)
            dim = (1280,480)
            img = cv.resize(img, dim, interpolation = cv.INTER_AREA)
            #Concatenate the two streams in a single image
            cv.imshow("Podoscope", img)
            keypress = cv.waitKey(1)
            if keypress%256 == 27:
                #ESC pressed
                self.warning("Image capture cancelled", title="Warning")
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
    def unwrap_image(self, img, K, d):
        # Read the image and get its size
        h, w = img.shape[:2]

        # Generate new camera matrix from parameters
        newcameramatrix, roi = cv.getOptimalNewCameraMatrix(K, d, (w,h), 0)

        # Generate look-up tables for remapping the camera image
        mapx, mapy = cv.initUndistortRectifyMap(K, d, None, newcameramatrix, (w, h), 5)

        # Remap the original image to a new image
        newimg = cv.remap(img, mapx, mapy, cv.INTER_LINEAR)

        #Crop and save
        x, y, w, h = roi
        newimg = newimg[y:y+h, x:x+w]
        return newimg

    def podonator(self,output_dir):
        #Defines image format
        file_ext=".jpg"
        args, optlist = getopt.getopt(sys.argv[1:], '', ['left_camera_id=', 'right_camera_id='])
        args = dict(args)
        args.setdefault('--left_camera_id', 0)
        args.setdefault('--right_camera_id', 1)
        os.chdir(str(Path(output_dir)))
        left_camera_id = int(args.get('--left_camera_id'))
        right_camera_id = int(args.get('--right_camera_id'))
        cam1 = cv.VideoCapture(left_camera_id)
        cam2 = cv.VideoCapture(right_camera_id)
        cam1.set(cv.CAP_PROP_FRAME_WIDTH, 1920)
        cam1.set(cv.CAP_PROP_FRAME_HEIGHT, 1080)
        cam2.set(cv.CAP_PROP_FRAME_WIDTH, 1920)
        cam2.set(cv.CAP_PROP_FRAME_HEIGHT, 1080)
        try:
            raw_img1, raw_img2 = self.show_images(cam1, cam2)
        except TypeError:
            print("ERROR: No input from cameras, check camera IDs")
            self.critical("ERROR: No input from cameras, check camera IDs", title="Error")
            return
        correct_img1 = self.unwrap_image(raw_img1, self.K1, self.d1)
        correct_img2 = self.unwrap_image(raw_img2, self.K2, self.d2)
        final_img = np.concatenate((correct_img1, correct_img2), axis=1)
        now=datetime.datetime.now()
        img_name=now.strftime("%Y-%m-%d-%H%M%S")
        cv.imwrite(img_name+file_ext, final_img)
        cv.imwrite(img_name+"_G"+file_ext, correct_img1)
        cv.imwrite(img_name+"_D"+file_ext, correct_img2)
        #Opens the file browser in the output folder
        webbrowser.open(str(Path(output_dir)))
        return

    def __outputFolderSelectionEvent(self):
        outputFolder=self._outputfolder.value

    def run_event(self):

        self.podonator(self._outputfolder.value)


if __name__ == '__main__':

    from pyforms import start_app
    start_app(PodonatorGUI, geometry=(100, 100, 400, 150))
