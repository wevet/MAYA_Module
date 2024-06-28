# -*- coding: utf-8 -*-

import os
import sys

import json
import maya.mel as mel
import pymel.core as pm
import maya.cmds as cmds
from functools import partial
import maya.OpenMayaUI as omui
from shiboken2 import wrapInstance
from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtWidgets import *
from PySide2.QtCore import *
import time
import math


class HIK_Automation:
    def __init__(self):
        self.file_name = None
        self.base_file_name = None
        self.base_directory = None
        pass

    @staticmethod
    def _custom_import(fbx_file_path):
        mel.eval('FBXImportSetLockedAttribute -v false')
        cmds.file(fbx_file_path, i=True, type='FBX', gr=True, mergeNamespacesOnClash=True, importTimeRange="override")

        cmds.currentUnit(time='60fps')
        fps = mel.eval('currentTimeUnitToFPS')
        print(fps)
        pass

    @staticmethod
    def _editor_import():
        path_list = cmds.fileDialog2(fm=1, ds=2, ff=('FBX(*.fbx)'))
        if not path_list:
            return

        mel.eval('FBXImportSetLockedAttribute -v false')
        cmds.file(path_list[0], i=True, gr=True, mergeNamespacesOnClash=True, importTimeRange="override")
        print("import path => {0}".format(path_list[0]))

        cmds.currentUnit(time='60fps')
        fps = mel.eval('currentTimeUnitToFPS')
        print(fps)
        pass

    @staticmethod
    def _setup_human_ik_definition():
        mel.eval('HIKCharacterControlsTool ;')
        mel.eval('hikCreateDefinition();')

        mel.eval('setCharacterObject("pelvis","Character1",1,0);')
        mel.eval('setCharacterObject("spine_01","Character1",8,0);')
        mel.eval('setCharacterObject("spine_02","Character1",23,0);')
        mel.eval('setCharacterObject("spine_03","Character1",24,0);')
        mel.eval('setCharacterObject("spine_04","Character1",25,0);')
        mel.eval('setCharacterObject("spine_05","Character1",26,0);')
        mel.eval('setCharacterObject("neck_01","Character1",20,0);')
        mel.eval('setCharacterObject("neck_02","Character1",32,0);')
        mel.eval('setCharacterObject("head","Character1",15,0);')
        mel.eval('setCharacterObject("clavicle_l","Character1",18,0);')
        mel.eval('setCharacterObject("upperarm_l","Character1",9,0);')
        mel.eval('setCharacterObject("lowerarm_l","Character1",10,0);')
        mel.eval('setCharacterObject("hand_l","Character1",11,0);')

        mel.eval('setCharacterObject("thumb_01_l", "Character1", 50, 0);')
        mel.eval('setCharacterObject("thumb_02_l", "Character1", 51, 0);')
        mel.eval('setCharacterObject("thumb_03_l", "Character1", 52, 0);')

        mel.eval('setCharacterObject("index_metacarpal_l", "Character1", 147, 0);')
        mel.eval('setCharacterObject("index_01_l", "Character1", 54, 0);')
        mel.eval('setCharacterObject("index_02_l", "Character1", 55, 0);')
        mel.eval('setCharacterObject("index_03_l", "Character1", 56, 0);')

        mel.eval('setCharacterObject("middle_metacarpal_l", "Character1", 148, 0);')
        mel.eval('setCharacterObject("middle_01_l", "Character1", 58, 0);')
        mel.eval('setCharacterObject("middle_02_l", "Character1", 59, 0);')
        mel.eval('setCharacterObject("middle_03_l", "Character1", 60, 0);')

        mel.eval('setCharacterObject("ring_metacarpal_l", "Character1", 149, 0);')
        mel.eval('setCharacterObject("ring_01_l", "Character1", 62, 0);')
        mel.eval('setCharacterObject("ring_02_l", "Character1", 63, 0);')
        mel.eval('setCharacterObject("ring_03_l", "Character1", 64, 0);')

        mel.eval('setCharacterObject("pinky_metacarpal_l", "Character1", 150, 0);')
        mel.eval('setCharacterObject("pinky_01_l", "Character1", 66, 0);')
        mel.eval('setCharacterObject("pinky_02_l", "Character1", 67, 0);')
        mel.eval('setCharacterObject("pinky_03_l", "Character1", 68, 0);')

        mel.eval('setCharacterObject("clavicle_r", "Character1", 19, 0);')
        mel.eval('setCharacterObject("upperarm_r", "Character1", 12, 0);')
        mel.eval('setCharacterObject("lowerarm_r", "Character1", 13, 0);')
        mel.eval('setCharacterObject("hand_r", "Character1", 14, 0);')

        mel.eval('setCharacterObject("thumb_01_r", "Character1", 74, 0);')
        mel.eval('setCharacterObject("thumb_02_r", "Character1", 75, 0);')
        mel.eval('setCharacterObject("thumb_03_r", "Character1", 76, 0);')

        mel.eval('setCharacterObject("index_metacarpal_r", "Character1", 153, 0);')
        mel.eval('setCharacterObject("index_01_r", "Character1", 78, 0);')
        mel.eval('setCharacterObject("index_02_r", "Character1", 79, 0);')
        mel.eval('setCharacterObject("index_03_r", "Character1", 80, 0);')

        mel.eval('setCharacterObject("middle_metacarpal_r", "Character1", 154, 0);')
        mel.eval('setCharacterObject("middle_01_r", "Character1", 82, 0);')
        mel.eval('setCharacterObject("middle_02_r", "Character1", 83, 0);')
        mel.eval('setCharacterObject("middle_03_r", "Character1", 84, 0);')

        mel.eval('setCharacterObject("ring_metacarpal_r", "Character1", 155, 0);')
        mel.eval('setCharacterObject("ring_01_r", "Character1", 86, 0);')
        mel.eval('setCharacterObject("ring_02_r", "Character1", 87, 0);')
        mel.eval('setCharacterObject("ring_03_r", "Character1", 88, 0);')

        mel.eval('setCharacterObject("pinky_metacarpal_r", "Character1", 156, 0);')
        mel.eval('setCharacterObject("pinky_01_r", "Character1", 90, 0);')
        mel.eval('setCharacterObject("pinky_02_r", "Character1", 91, 0);')
        mel.eval('setCharacterObject("pinky_03_r", "Character1", 92, 0);')

        mel.eval('setCharacterObject("thigh_l", "Character1", 2, 0);')
        mel.eval('setCharacterObject("thigh_r", "Character1", 5, 0);')
        mel.eval('setCharacterObject("calf_l", "Character1", 3, 0);')
        mel.eval('setCharacterObject("calf_r", "Character1", 6, 0);')
        mel.eval('setCharacterObject("foot_l", "Character1", 4, 0);')
        mel.eval('setCharacterObject("foot_r", "Character1", 7, 0);')
        mel.eval('setCharacterObject("ball_l", "Character1", 16, 0);')

        mel.eval('hikCreateControlRig;')
        mel.eval('modelEditor -e -joints true modelPanel4;')
        #mel.eval('optionVar -intValue keyFullBody 1; hikSetKeyingMode( ); hikUpdateControlRigButtonState;')
        pass

    @staticmethod
    def _handle_load_plugins():
        if not cmds.pluginInfo('fbxmaya', q=True, loaded=True):
            cmds.loadPlugin('fbxmaya')

        if mel.eval('optionVar -q "FileDialogStyle"') == 1:
            mel.eval('optionVar -iv FileDialogStyle 2 ;')
            mel.eval('savePrefsChanges;')
            cmds.unloadPlugin('fbxmaya')
            cmds.loadPlugin('fbxmaya', qt=True)

    def start(self, fbx_file_path):

        self._handle_load_plugins()

        # namespaceなしでImport
        # default poseを-10fで設定する
        if fbx_file_path is None:
            self._editor_import()
        else:
            self._custom_import(fbx_file_path)

        k_cur_time = -10
        cmds.playbackOptions(edit=1, minTime=k_cur_time)
        cmds.currentTime(k_cur_time)

        self._setup_human_ik_definition()

        if fbx_file_path is not None:
            cmds.file(save=True, force=True, type='mayaAscii')

        # poseの初期化
        # A-poseに切り替えるのでstudio libraryのposeを使うとよさそう
        joints = cmds.ls(type="joint")
        pass


def run(file_path):
    print('## fbx File >> {}'.format(file_path))
    #新規sceneを作成
    cmds.file(new=True, force=True)

    temp = [file_path]

    base_file_name = os.path.basename(temp[0])
    file_name = base_file_name.replace(".FBX", "")
    base_directory = os.path.dirname(temp[0])

    cmds.file(rename='{}/{}'.format(base_directory, file_name))
    cmds.file(save=True, type='mayaAscii', force=True)

    automation = HIK_Automation()
    automation.start(temp)

    print("file_name => {}".format(file_name))
    print("file_path => {}".format(temp))

    # exeで処理していた場合は終了
    if not cmds.about(batch=1):
        cmds.evalDeferred('from maya import cmds;cmds.quit(f=1)')


if __name__ == '__main__':
    automation = HIK_Automation()
    automation.start(None)
    pass

