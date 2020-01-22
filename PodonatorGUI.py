"""Podonator PyQT5 GUI"""
import sys
import datetime
import os
import webbrowser
from pathlib import Path
from PyQt5.QtWidgets import (QWidget, QLabel, QLineEdit, QSpinBox,\
    QPushButton, QGridLayout, QApplication, QFileDialog, QMessageBox,\
    QVBoxLayout)
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5.Qt import Qt
import numpy as np
import cv2 as cv
import PodonatorLib

class podonatorWidget(QWidget):
    """Main window widget"""
    def __init__(self):
        super().__init__()
        self.test_camera_flag = False
        pathEditLabel = QLabel("Output Path")
        pathEditLabel.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.outputFolder = str(Path().absolute())
        self.pathEdit = QLineEdit(self.outputFolder)
        pathEditButton = QPushButton("Browse...")
        camLIDLabel = QLabel("Left Camera ID")
        camLIDLabel.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.camLID = QSpinBox(self)
        self.camLID.setValue(0)
        camRIDLabel = QLabel("Right Camera ID")
        camRIDLabel.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.camRID = QSpinBox(self)
        self.camRID.setValue(1)
        previewButton = QPushButton("Preview")
        layout = QGridLayout()
        layout.setSpacing(10)
        layout.addWidget(pathEditLabel, 1, 0)
        layout.addWidget(self.pathEdit, 1, 1, 1, 2)
        layout.addWidget(pathEditButton, 1, 3)
        layout.addWidget(camLIDLabel, 2, 0)
        layout.addWidget(self.camLID, 2, 1)
        layout.addWidget(camRIDLabel, 2, 2)
        layout.addWidget(self.camRID, 2, 3)
        layout.addWidget(previewButton, 3, 0, 1, 4)
        self.setLayout(layout)
        previewButton.clicked.connect(self.previewAction)
        pathEditButton.clicked.connect(self.browseAction)
        self.critical = QMessageBox()
        self.critical.setIcon(QMessageBox.Critical)
        self.critical.setWindowTitle("Error")
        self.critical.setWindowIcon(getIcon())

    def previewAction(self):
        """Action to run when the Preview button is clicked"""
        if not self.test_camera_flag:
            if not PodonatorLib.test_camera(int(self.camLID.text())):
                self.critical.setText("Invalid Camera ID\nNo input from left camera, check camera ID")
                self.critical.exec_()
            if not PodonatorLib.test_camera(int(self.camRID.text())):
                self.critical.setText("Invalid Camera ID\nNo input from right camera, check camera ID")
                self.critical.exec_()
            if PodonatorLib.test_camera(int(self.camLID.text())) and PodonatorLib.test_camera(int(self.camRID.text())):
                self.test_camera_flag = True
        if self.test_camera_flag:
            self.outputFolder = str(Path(self.pathEdit.text()))
            podorun(self.outputFolder, int(self.camLID.text()), int(self.camRID.text()))

    def browseAction(self):
        """Directory browser to set the output path"""
        self.outputFolder = str(Path(QFileDialog.getExistingDirectory(self, "Output folder")))
        self.pathEdit.setText(self.outputFolder)

class imagePreview(QWidget):
    """Image preview window"""
    def __init__(self):
        super(imagePreview, self).__init__()
        self.toggle = True
        self.genOutput = False
        self.vlayout = QVBoxLayout()        # Window layout
        self.buttons = QGridLayout()
        self.disp = QLabel(self)
        self.vlayout.addWidget(self.disp)
        self.acquireButton = QPushButton("Acquire")
        self.acquireButton.setDefault(True)
        self.cancelButton = QPushButton("Cancel")
        self.buttons.addWidget(self.acquireButton, 1, 0, 1, 3)
        self.buttons.addWidget(self.cancelButton, 1, 4, 1, 1)
        self.vlayout.addLayout(self.buttons)
        self.setLayout(self.vlayout)
        self.acquireButton.clicked.connect(self.acquireAction)
        self.cancelButton.clicked.connect(self.cancelAction)
        self.setWindowIcon(getIcon())

    def keyPressEvent(self, event):
        """For capturing Escape key press event (same action as cancel button)"""
        if event.key() == Qt.Key_Escape:
            self.toggle = False

    def cancelAction(self):
        """Cancel button action"""
        self.toggle = False

    def acquireAction(self):
        """Acquire button action"""
        self.toggle = False
        self.genOutput = True

    def closeEvent(self, event):
        """Action when closing the preview window (same as cancel button)"""
        event.accept()
        self.toggle = False

def show_images(cam1, cam2, rotate_bool):
    """Shows the stream from the cameras (with full image correction) and allows for image capture returns the two captured images (one per camera)"""

    imageWindow = imagePreview()
    imageWindow.show()
    imageWindow.setWindowTitle("Podonator Preview")
    previewWindowLongSide = 960 # Number of pixels of the long side of the preview image
    while imageWindow.toggle:
        img1 = PodonatorLib.get_camera_image(PodonatorLib.mirror, cam1)
        img2 = PodonatorLib.get_camera_image(PodonatorLib.mirror, cam2)
        #Undistort
        u_img1 = PodonatorLib.undistort_image(img1, PodonatorLib.K1, PodonatorLib.d1)
        u_img2 = PodonatorLib.undistort_image(img2, PodonatorLib.K2, PodonatorLib.d2)
        #Perspective correction
        up_img1 = PodonatorLib.perpective_correction(u_img1, PodonatorLib.reference_cam1)
        up_img2 = PodonatorLib.perpective_correction(u_img2, PodonatorLib.reference_cam2)
        if rotate_bool:
            #Concatenate the two streams in a single image
            img = np.concatenate((cv.rotate(up_img1, cv.ROTATE_90_CLOCKWISE), cv.rotate(up_img2, cv.ROTATE_90_COUNTERCLOCKWISE)), axis=1)
            #Image resolution to display
            dim = (int(round(previewWindowLongSide * PodonatorLib.image_ratio))*2, previewWindowLongSide)
        else:
            img = np.concatenate((img1, img2), axis=0)
            dim = (previewWindowLongSide, int(round(previewWindowLongSide * PodonatorLib.image_ratio))*2)
        img = cv.resize(img, dim, interpolation=cv.INTER_AREA)
        #Convert to PyQt compatible colors
        img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
        h, w, ch = img.shape
        bytesPerLine = ch * w
        #Convert to PyQt compatible image
        qimg = QtGui.QImage(img.data, w, h, bytesPerLine, QtGui.QImage.Format_RGB888)
        qpximg = QtGui.QPixmap.fromImage(qimg)
        imageWindow.disp.resize(img.shape[1], img.shape[0])
        imageWindow.disp.setPixmap(qpximg)

        cv.waitKey(1)

    cam1.release()
    cam2.release()

    return up_img1, up_img2, imageWindow.genOutput

def podorun(output_dir, left_camera_id, right_camera_id):
    """Calls all previous functions"""
    os.chdir(str(Path(output_dir)))
    #Initialize cameras
    cam1 = PodonatorLib.init_camera(left_camera_id)
    cam2 = PodonatorLib.init_camera(right_camera_id)
    #Launch image preview, capture and correction
    correct_img1, correct_img2, gen_output = show_images(cam1, cam2, PodonatorLib.rotate)
    cam1.release()
    cam2.release()
    cv.destroyAllWindows()
    if gen_output:
        #Rotate images if necessary
        if PodonatorLib.rotate:
            correct_img1 = cv.rotate(correct_img1, cv.ROTATE_90_CLOCKWISE)
            correct_img2 = cv.rotate(correct_img2, cv.ROTATE_90_COUNTERCLOCKWISE)
        now = datetime.datetime.now()
        img_name = now.strftime("%Y-%m-%d-%H%M%S")
        PodonatorLib.output_images(correct_img1, correct_img2, img_name, PodonatorLib.file_ext, PodonatorLib.image_dpi)
        #Open the file browser in the output folder
        webbrowser.open(str(Path(output_dir)))
        return
    return
def getIcon():
    """Window icon management"""
    try:
        scriptDir = Path(sys._MEIPASS) # Running as packaged with PyInstaller # pylint: disable=W0212
    except AttributeError:
        scriptDir = Path(__file__).parent # Running with Python interpreter
    iconFileName = scriptDir.joinpath("950-512.png")
    qtIcon = QtGui.QIcon(str(iconFileName))
    return qtIcon

if __name__ == "__main__":
    podonator = QApplication([])
    podonatorGUI = podonatorWidget()
    podonatorGUI.setWindowTitle("Podonator v1.0")
    podonatorGUI.setWindowIcon(getIcon())
    # Window size
    podonatorGUI.resize(500, 150)
    podonatorGUI.show()

    sys.exit(podonator.exec_())
