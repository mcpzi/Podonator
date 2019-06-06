import datetime
import sys
import getopt
from pathlib import Path
import os
import PodonatorLib


'''
usage:
    Podonator.py [--left_camera_id] [--right_camera_id] [<output path>]

default values:
    --left_camera_id  : 0
    --right_camera_id : 1
    <output path>     : .
'''

if __name__ == '__main__':
    #Defines image format
    file_ext=".jpg"
    args, output_dir = getopt.getopt(sys.argv[1:], '', ['left_camera_id=', 'right_camera_id='])
    args = dict(args)
    args.setdefault('--left_camera_id', 0)
    args.setdefault('--right_camera_id', 1)
    if not output_dir:
        output_dir = str(Path().absolute())
    else:
        output_dir=output_dir[0]
        Path(output_dir).mkdir(exist_ok=True)
        os.chdir(str(Path(output_dir)))
    left_camera_id = int(args.get('--left_camera_id'))
    right_camera_id = int(args.get('--right_camera_id'))
    if not PodonatorLib.test_camera(left_camera_id):
        print("ERROR: No input from left camera, check camera ID")
    if not PodonatorLib.test_camera(right_camera_id):
        print("ERROR: No input from right camera, check camera ID")
    if PodonatorLib.test_camera(left_camera_id) and PodonatorLib.test_camera(right_camera_id):
        PodonatorLib.podonator(output_dir, left_camera_id, right_camera_id)
        print("Images acquired and transformed written to ",output_dir)
