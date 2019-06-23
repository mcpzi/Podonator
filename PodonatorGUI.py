from pyforms.basewidget import BaseWidget
from pyforms.controls   import ControlDir
from pyforms.controls   import ControlButton
from pyforms.controls   import ControlNumber
import sys
import getopt
from pathlib import Path
import PodonatorLib

'''
usage:
    PodonatorGUI.py
'''

class PodonatorGUI(BaseWidget):
    def __init__(self, *args, **kwargs):

        super().__init__('Podonator v1.0')
        self.test_camera_flag = False
        #Definition of the forms fields
        self._outputfolder  = ControlDir('Répertoire de sortie', default=str(Path().absolute()))
        self._outputfolder.value = str(Path().absolute())
        self._runbutton  = ControlButton('Acquisition')
        self._cameraleft = ControlNumber("ID caméra gauche", default=0, decimals=0)
        self._cameraright = ControlNumber("ID caméra droite", default=1, decimals=0)

        #Define the event that will be called when the run button is processed
        self._runbutton.value = self.run_event
        self._outputfolder.changed_event = self.__outputFolderSelectionEvent
        #Define the organization of the Form Controls
        self._formset = [
            ('','_outputfolder',''),
            ('','_cameraleft','','_cameraright',''),
            ('','_runbutton','')
        ]

        return

    def __outputFolderSelectionEvent(self):
        outputFolder=self._outputfolder.value

    def run_event(self):
        #args, optlist = getopt.getopt(sys.argv[1:], '', ['left_camera_id=', 'right_camera_id='])
        #args = dict(args)
        #args.setdefault('--left_camera_id', 0)
        #args.setdefault('--right_camera_id', 1)
        #left_camera_id = int(args.get('--left_camera_id'))
        #right_camera_id = int(args.get('--right_camera_id'))
        if self.test_camera_flag == False:
            if not PodonatorLib.test_camera(int(self._cameraleft.value)):
                self.critical("ERROR: No input from left camera, check camera ID", title="Error")
            if not PodonatorLib.test_camera(int(self._cameraright.value)):
                self.critical("ERROR: No input from right camera, check camera ID", title="Error")
            if PodonatorLib.test_camera(int(self._cameraleft.value)) and PodonatorLib.test_camera(int(self._cameraright.value)):
                self.test_camera_flag = True
        if self.test_camera_flag == True:
            PodonatorLib.podonator(self._outputfolder.value, int(self._cameraleft.value), int(self._cameraright.value))
        return

if __name__ == '__main__':

    from pyforms import start_app
    start_app(PodonatorGUI, geometry=(100, 100, 400, 150))
