import sys
from pathlib import Path
from PyQt5.QtWidgets import (QWidget, QLabel, QLineEdit, QSpinBox,\
    QPushButton, QGridLayout, QApplication, QFileDialog, QErrorMessage)
from PyQt5 import QtCore
from PyQt5 import QtGui
import PodonatorLib

class podonatorWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.test_camera_flag = False
        pathEditLabel = QLabel("Path")
        pathEditLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.outputFolder = str(Path().absolute())
        self.pathEdit = QLineEdit(self.outputFolder)
        pathEditButton = QPushButton("Browse...")
        camLIDLabel = QLabel("Left Camera ID")
        self.camLID = QSpinBox(self)
        self.camLID.setValue(0)
        camLIDLabel.setAlignment(QtCore.Qt.AlignCenter)
        camRIDLabel = QLabel("Right Camera ID")
        self.camRID = QSpinBox(self)
        self.camRID.setValue(1)
        camRIDLabel.setAlignment(QtCore.Qt.AlignCenter)
        acquireButton = QPushButton("Acquire")
        layout = QGridLayout()
        layout.setSpacing(10)
        layout.addWidget(pathEditLabel, 1, 0)
        layout.addWidget(self.pathEdit, 1, 1, 1, 2)
        layout.addWidget(pathEditButton, 1, 3)
        layout.addWidget(camLIDLabel, 2, 0)
        layout.addWidget(self.camLID, 2, 1)
        layout.addWidget(camRIDLabel, 2, 2)
        layout.addWidget(self.camRID, 2, 3)
        layout.addWidget(acquireButton, 3, 0, 1, 4)
        self.setLayout(layout)
        acquireButton.clicked.connect(self.acquireAction)
        pathEditButton.clicked.connect(self.browseAction)
        self.critical = QErrorMessage()
        self.critical.setWindowTitle("Error")

    def acquireAction(self):
        if not self.test_camera_flag:
            if not PodonatorLib.test_camera(int(self.camLID.text())):
                self.critical.showMessage("ERROR: No input from left camera, check camera ID")
                self.critical.exec_()
            if not PodonatorLib.test_camera(int(self.camRID.text())):
                self.critical.showMessage("ERROR: No input from right camera, check camera ID")
                self.critical.exec_()
            if PodonatorLib.test_camera(int(self.camLID.text())) and PodonatorLib.test_camera(int(self.camRID.text())):
                self.test_camera_flag = True
        if self.test_camera_flag:
            self.outputFolder = str(Path(self.pathEdit.text()))
            PodonatorLib.podonator(self.outputFolder, int(self.camLID.text()), int(self.camRID.text()))
        return

    def browseAction(self):
        self.outputFolder = str(Path(QFileDialog.getExistingDirectory(self, "Output folder")))
        self.pathEdit.setText(self.outputFolder)

if __name__ == "__main__":
    podonator = QApplication([])
    podonatorGUI = podonatorWidget()
    podonatorGUI.setWindowTitle("Podonator v1.0")
    # Window icon management
    try:
        scriptDir = Path(sys._MEIPASS) # Running as packaged with PyInstaller # pylint: disable=W0212
    except AttributeError:
        scriptDir = Path(__file__).parent # Running with Python interpreter
    iconFileName = scriptDir.joinpath("950-512.png")
    podonatorGUI.setWindowIcon(QtGui.QIcon(str(iconFileName)))
    # Window size
    podonatorGUI.resize(500, 150)
    podonatorGUI.show()

    sys.exit(podonator.exec_())
