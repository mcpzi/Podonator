from pyforms.basewidget import BaseWidget
from pyforms.controls   import ControlDir
from pyforms.controls   import ControlButton
import sys
import getopt
from pathlib import Path
import PodonatorLib

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
        self.test_camera_flag = True
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

        return

    def __outputFolderSelectionEvent(self):
        outputFolder=self._outputfolder.value

    def run_event(self):
        args, optlist = getopt.getopt(sys.argv[1:], '', ['left_camera_id=', 'right_camera_id='])
        args = dict(args)
        args.setdefault('--left_camera_id', 0)
        args.setdefault('--right_camera_id', 1)
        left_camera_id = int(args.get('--left_camera_id'))
        right_camera_id = int(args.get('--right_camera_id'))
        if not PodonatorLib.test_camera(left_camera_id):
            self.critical("ERROR: No input from left camera, check camera ID", title="Error")
        if not PodonatorLib.test_camera(right_camera_id):
            self.critical("ERROR: No input from right camera, check camera ID", title="Error")
        if PodonatorLib.test_camera(left_camera_id) and PodonatorLib.test_camera(right_camera_id):
            PodonatorLib.podonator(self._outputfolder.value, left_camera_id, right_camera_id)


if __name__ == '__main__':

    from pyforms import start_app
    start_app(PodonatorGUI, geometry=(100, 100, 400, 150))
