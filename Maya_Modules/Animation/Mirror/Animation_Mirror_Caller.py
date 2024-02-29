# -*- coding: utf-8 -*-
# !/usr/bin/env mayapy # note I have this as an alias

import argparse
import sys
import os


import maya.cmds as cmds
from PySide2 import QtCore, QtWidgets, QtGui



"""
Python class to automate Animation Mirror
1.Select Directory
2.Select mirror mode.
3.Run bat file
"""

MAYA_LOCATION = "C:/Program Files/Autodesk/Maya2020"
PYTHON_LOCATION = MAYA_LOCATION + "/Python/Lib/site-packages"

os.environ["MAYA_LOCATION"] = MAYA_LOCATION
os.environ["PYTHONPATH"] = PYTHON_LOCATION

sys.path.append(MAYA_LOCATION)
sys.path.append(PYTHON_LOCATION)
sys.path.append(MAYA_LOCATION+"/bin")
sys.path.append(MAYA_LOCATION+"/lib")
sys.path.append(MAYA_LOCATION+"/Python")
sys.path.append(MAYA_LOCATION+"/Python/DLLs")
sys.path.append(MAYA_LOCATION+"/Python/Lib")
sys.path.append(MAYA_LOCATION+"/Python/Lib/plat-win")
sys.path.append(MAYA_LOCATION+"/Python/Lib/lib-tk")
print('\n'.join(sys.path))

K_MAYA_EXE = r'C:\Program Files\Autodesk\Maya2020\bin\maya.exe'
K_MAYA_BATCH_EXE = r'C:\Program Files\Autodesk\Maya2020\bin\mayabatch.exe'



class Animation_Mirror_Caller:

    def __init__(self):
        self.source_directory = None
        self.file_list = []
        self.mirror_mode = 3
        self.mirror_axis = "X"

    def main(self, args):
        print("----------------------search file begin-----------------------------")

        for arg in args:
            print("arg => {}".format(arg))

        self.source_directory = args[1]
        self.mirror_mode = int(args[2])
        self.mirror_axis = args[3]
        self.file_list = self._get_list_directory_files()

        path = os.getcwd()
        cmd = 'SET MAYA_UI_LANGUAGE=ja_JP' + '\n'
        #cmd += 'SET MAYA_PLUG_IN_PATH=C:dir'+'\n'
        #cmd += 'SET MAYA_MODULE_PATH=C:dir'+'\n'
        #cmd += 'SET MAYA_SCRIPT_PATH=C:dir'+'\n'
        cmd += 'SET PYTHONPATH=%s' % path + '\n'

        for file in self.file_list:
            file_path = os.path.join(self.source_directory, file).replace('\\', '/')
            print("Execute the following ma file. => {}".format(file_path))

            replace_path = os.path.join(self.source_directory, file).replace('\\', '/')
            root, ext = os.path.splitext(replace_path)
            log_path = os.path.join(self.source_directory, 'Log', file).replace(ext, '.log')
            cmd += '\n'
            cmd += 'SET MAYA_CMD_FILE_OUTPUT={0}'.format(log_path) + '\n'
            cmd += '"{0}"'.format(K_MAYA_BATCH_EXE) + ' -command'
            cmd += ' "python(\\"from Animation_Mirror import Animation_Mirror_Model; model = Animation_Mirror_Model(); model.start_run(\'{}\', {}, {})\\")"'.format(file_path, self.mirror_mode, self.mirror_axis)
            pass

        dir_path, current_path_name = os.path.split(__file__)
        path = os.path.join(dir_path, 'animation_mirror_run.bat')
        self._save_bat_file(path, cmd)
        print("----------------------search file end-----------------------------")

    @staticmethod
    def _save_bat_file(path, cmd):
        with open(path, "w") as file:
            file.write(cmd)

    def _check_directory(self):
        if os.path.isdir(os.path.join(self.source_directory, 'Log')) is False:
            os.makedirs(os.path.join(self.source_directory, 'Log'))

    def _get_list_directory_files(self):
        file_list = []
        for file_name in os.listdir(self.source_directory):
            file_path = os.path.join(self.source_directory, file_name)
            if os.path.isfile(file_path):
                file_list.append(file_name)
        return file_list


if __name__ == '__main__':
    # args 1 run python file name
    # args 2 directory
    # args 3 mirror mode index
    # args 4 mirror axis
    caller = Animation_Mirror_Caller()
    caller.main(sys.argv)





