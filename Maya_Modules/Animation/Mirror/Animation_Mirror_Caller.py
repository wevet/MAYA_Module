# -*- coding: utf-8 -*-
# !/usr/bin/env mayapy # note I have this as an alias

import argparse
import sys
import os

import maya.standalone
maya.standalone.initialize(name='python')


import maya.cmds as cmds
from PySide2 import QtCore, QtWidgets
from shiboken2 import wrapInstance
import maya.mel as mel

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

class Animation_Mirror_Caller:

    def __init__(self):
        self.app = None
        self.source_directory = None
        self.mirror_mode = 3
        self.file_list = []
        self.PREFIX = "_Mirror"
        self.stand_alone = False

    def main(self, args):
        print("----------------------search file begin-----------------------------")

        for arg in args:
            print("arg => {}".format(arg))

        self.source_directory = args[1]
        self.mirror_mode = int(args[2])
        self.file_list = self._get_list_directory_files()

        self.app = QtWidgets.QApplication.instance()
        self.stand_alone = self.app is None

        """
        if not QtWidgets.QApplication.instance():
            self.app = QtWidgets.QApplication(sys.argv)
        else:
            self.app = QtWidgets.QApplication.instance()
        """

        if self.stand_alone:
            self.app = QtWidgets.QApplication(sys.argv)
            print("created QApplication => {}".format(self.app))

        cmds.loadPlugin("fbxmaya.mll")
        plugins = cmds.unknownPlugin(query=True, list=True) or []
        if plugins:
            for plugin in plugins:
                cmds.unknownPlugin(plugin, remove=True)
                print("unload plugin => {}".format(plugin))

        self._duplicate_mirror_animation_files()
        if self.stand_alone:
            sys.exit(self.app.exec_())

        print("----------------------search file end-----------------------------")

    def _duplicate_mirror_animation_files(self):
        for file in self.file_list:
            file_path = os.path.join(self.source_directory, file).replace('\\', '/')
            print("Execute the following ma file. => {}".format(file_path))
            print("cmds => {}".format(cmds))

            # open file
            cmds.file(file_path, o=True, type='mayaAscii', force=True)
            asset_file_path = cmds.file(q=True, sn=True)
            new_file_name = os.path.basename(asset_file_path)
            scene_name = os.path.splitext(os.path.basename(cmds.file(q=True, sn=True)))[0]
            base_directory = asset_file_path.split(new_file_name)[-2]
            new_scene_name = scene_name + self.PREFIX
            print("asset_file_path => {}".format(asset_file_path))
            print("filename => {}".format(new_file_name))
            print("scene_name => {}".format(scene_name))
            print("new_scene_name => {}".format(new_scene_name))
            print("base_directory => {}".format(base_directory))
            # NOTE
            # If the default is 24 fps, change to 60 fps
            cmds.currentUnit(time='60fps')

            print('## QDialog => {}'.format(QtWidgets.QDialog))

            # @TODO
            # Cannot create a QWidget without QApplication
            import Animation_Mirror as Mirror
            window = Mirror.show_main_window()
            window.mirror_control(self.mirror_mode)

            # @TODO
            # rename bug
            cmds.file(rename=base_directory + new_scene_name + ".ma")
            #cmds.file(rename=base_directory + new_scene_name)
            cmds.file(save=True, type='mayaAscii', force=True)
        pass

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
    caller = Animation_Mirror_Caller()
    caller.main(sys.argv)

maya.standalone.uninitialize()



